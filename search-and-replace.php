<?php
/* CONFIGURATION AREA */
define('MAX_RECURSION_DEPTH', 15);
define('VERBOSE', false);
define('DEBUG', false);

$skip_tables = array();
//$whitelist_tables = array('wp_options');
/*************************/

function errorHandler($errNo, $errStr, $errFile, $errLine)
{
    $msg = "$errStr in $errFile on line $errLine";
    if($errNo != E_NOTICE)
        die($msg);
}

set_error_handler('errorHandler');

$replaced = 0;
$replaced_total = 0;
$reached_max_recursion = 0;

function recursive_search_and_replace($obj, $find, $replace, $depth = 0)
{
    global $replaced;
    global $reached_max_recursion;
    global $conn;

    //don't work on empty objects
    if(empty($obj))
        return $obj;

    //break on max recursion depth (note: this should NEVER happen)
    if($depth > MAX_RECURSION_DEPTH && !(is_string($obj)))
    {
        $reached_max_recursion++;
        if(VERBOSE)
        {
            echo "Warning: Reached max recursion depth.\n";
            var_dump($obj);
        }
        return $obj;
    }

    if(is_object($obj) || gettype($obj) == 'object')
    {
        foreach($obj as $key=>$value)
            $obj->$key = recursive_search_and_replace($value, $find, $replace, $depth+1);
    }
    else if( is_array($obj) )
    {
        foreach($obj as $key=>$value)
            $obj[$key] = recursive_search_and_replace($value, $find, $replace, $depth+1);
    }
    else if( is_string($obj) )
    {
        //this is where the actual replace happens
        $new_obj = str_replace($find, $replace, $obj);

        //have we done something?
        if($new_obj !== $obj)
        {
            $replaced++;
            if(VERBOSE)
                echo "$obj -> $new_obj\n";
        }

        //reset obj with replaced value
        $obj = $new_obj;

        if($find === $replace && strstr($obj, $find) !== false)
            $replaced++;
    }

    return $obj;
}

function prepare_for_mysql_statement($obj)
{
    $obj = str_replace("'", "''", $obj);
    $obj = str_replace("\\", "\\\\", $obj);

    return $obj;
}

function search_and_replace($database, $find, $replace)
{
    global $replaced, $reached_max_recursion, $skip_tables, $conn, $whitelist_tables;

    $replaced = 0;
    $replaced_total = 0;
    $reached_max_recursion = 0;
    $db_entries_searched = 0;
    $db_entries_serialized = 0;
    $db_entries_changed = 0;

    $time = microtime(true);

    $conn = new mysqli('localhost', 'root', '51515151', $database, 3306, '/var/mysql/mysql.sock');
    $sql = "SET NAMES 'utf8';";
    $result = $conn->query($sql);
    if($result === false)
        die("$sql failed.\n");


    $sql = "SHOW TABLES;";

    $result = $conn->query($sql);

    $tables = array();
    foreach($result->fetch_all() as $row)
        array_push($tables, $row[0]);

    //traverse all tables
    foreach($tables as $table)
    {
        $replaced = 0;
        if(in_array($table, $skip_tables) || (isset($whitelist_tables) && !in_array($table, $whitelist_tables)))
        {
            echo "Skipping $table.\n";
            continue;
        }

        //find primary key
        $sql = "SHOW KEYS FROM $table WHERE Key_name = 'PRIMARY';";
        $key_result = $conn->query($sql);
        $primary_key = @$key_result->fetch_assoc()['Column_name'];
        if($primary_key == NULL)
        {
            $sql = "SHOW KEYS FROM $table WHERE Key_name = 'UNIQUE';";
            $key_result = $conn->query($sql);
            $primary_key = @$key_result->fetch_assoc()['Column_name'];

            if($primary_key == NULL)
            {
                echo "Could not find primary or unique key, skipping $table\n";
                continue;
            }
        }

        //fetch table
        $sql = "SELECT * FROM $table;";
        echo "Traversing $table...";
        $result = $conn->query($sql);
        $result->fetch_all();

        //traverse all rows
        foreach($result as $row)
        {
            $id = $row[$primary_key];

            //traverse all keys
            foreach($row as $col=>$key)
            {
                $db_entries_searched++;

                //we are only interested in strings
                if(!is_string($key) || $col === $primary_key || is_numeric($key))
                    continue;

                //skip the case where we have serialized a false boolean value, because we cannot catch this with the unserialize return value
                if($key == 'b:0;')
                    continue;

                //try to deserialize
                $data = @unserialize($key);
                if($data === false)
                {
                    //failed to serialize
                    $serialized = false;
                    $data = $key;
                }
                else
                {
                    //managed to serialize
                    $serialized = true;
                    $db_entries_serialized++;
                }

                //search and replace the data
                $replaced_old = $replaced;
                $out = recursive_search_and_replace($data, $find, $replace);


                //create mysql query if there was something we found
                if($replaced_old < $replaced || DEBUG)
                {
                    //serialize if necessary
                    if($serialized)
                    {
                        $new_data = serialize($out);
                    }
                    else
                        $new_data = $out;

                    //escape characters
                    $new_data = prepare_for_mysql_statement($new_data);

                    $sql = "UPDATE `$table` SET $col='$new_data' WHERE $primary_key=$id;";
                    $update_result = $conn->query($sql);

                    //tell about failed result but recover
                    if($update_result === false)
                    {
                        $replaced = $replaced_old;
                        echo "\nMySQL query failed: \nmysql> $sql\nError: $conn->error\n";
                    }
                    else
                    {
                        if(VERBOSE)
                        {
                            $num_changed = $replaced - $replaced_old;
                            echo "Changed id: $id ($num_changed values)\n";
                        }
                        $db_entries_changed++;
                    }

                    //unit test: nothing should have changed in this case
                    if(DEBUG && ($find === $replace || $replaced_old === $replaced))
                    {
                        $sql = "SELECT $col FROM $table WHERE $primary_key=$id;";
                        $test_result = $conn->query($sql);

                        $test_result->fetch_all();
                        foreach($test_result as $row)
                            $new_data_fetched = $row[$col];

                        if(!empty($key) && $new_data_fetched !== $key)
                        {
                            var_dump($key);
                            var_dump($new_data_fetched);
                            die('Data should be the same.\n');
                        }
                    }

                }
            }
        }
        if($reached_max_recursion > 0)
            echo "Reached max recursion depth $reached_max_recursion times...";
        echo "Done. Replaced $replaced values\n";
        $reached_max_recursion = 0;
        $replaced_total += $replaced;
    }

    $time = (microtime(true) - $time);
    echo "Took $time seconds to search $db_entries_searched keys ($db_entries_serialized serialized) and replace $replaced_total values by updating $db_entries_changed keys.\n";
}

//var_dump($argv);
//search_and_replace('tondeo.de', 'http://tondeo.local/', 'http://tondeo.de/www/');
//search_and_replace('tondeo.de', 'http://tondeo.de/www/', 'http://tondeo.local/');
search_and_replace('tondeo.de', 'http://tondeo.local/', '/');
