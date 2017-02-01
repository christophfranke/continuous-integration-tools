<?php
/* CONFIGURATION AREA */
define('MAX_RECURSION_DEPTH', 50);
define('VERBOSE', false);
define('DEBUG', false);
define('WRITE_SQL_FILE', true);
define('PERFORMCE_MYSQL_STATEMENTS', true);
define('SEARCH_AND_REPLACE_SQL_FILE', 'output/replace.sql');
define('SEARCH_LOG_FILE', 'output/search.log');

$skip_tables = array();
//$whitelist_tables = array('wp_options');
/*************************/

//Set memory limit to 8GB to enable traversing very large tables
ini_set('memory_limit', '8192M');


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

    static $parsed;
    if($depth === 0)
        $parsed = array();

    //don't work on empty objects
    if(empty($obj))
        return $obj;

    //have we parsed this object already?
    if(is_object($obj) || gettype($obj) == 'object' || is_array($obj))
    {
        if(is_array($obj))
            $hash = 'array_' . md5( json_encode( $obj ) );
        else
            $hash = 'object_' . spl_object_hash( $obj );

        if(isset($parsed[$hash]))
            return $obj;

        //now save the hash to the parsed array, so we won't parse it again
        $parsed[$hash] = true;
    }

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
            {
                if($replace === NULL)
                    echo "found: $obj\n";
                else
                    echo "$obj -> $new_obj\n";
            }
        }

        //do the update (but not in dry run)
        if( $replace !== NULL)
            $obj = $new_obj;
    }

    return $obj;
}

function prepare_for_mysql_statement($str)
{
    $str = str_replace("'", "''", $str);
    $str = str_replace("\\", "\\\\", $str);

    return $str;
}

function search_and_replace($find, $replace, $host, $user, $password, $database, $port = 3306, $socket = '/var/mysql/mysql.sock')
{
    global $replaced, $reached_max_recursion, $skip_tables, $conn, $whitelist_tables;

    $replaced = 0;
    $replaced_total = 0;
    $reached_max_recursion = 0;
    $db_entries_searched = 0;
    $db_entries_serialized = 0;
    $db_entries_changed = 0;

    //messy timezone problems...
    date_default_timezone_set( 'Europe/Berlin' );

    $log_file_content = "Logfile created by search-and-replace-db.php on " . date('d. M Y') . " at " . date('H:i') . "\n";
    $log_file_content .= "Searching database for the term: $find\n\n";

    $out_file_content = "#Script created by search-and-replace-db.php on " . date('d. M Y') . " at " . date('H:i') . "\n";
    $out_file_content .= "#replacing $find with $replace.\n\n";
    $out_file_content .= "SET NAMES 'utf8';\n";
    $made_sql_statement = false;

    $time = microtime(true);

    $conn = new mysqli($host, $user, $password, $database, $port, $socket);
    $sql = "SET NAMES 'utf8';";
    $result = $conn->query($sql);
    if($result === false)
        die("$sql failed.\n");

    $sql = "SHOW TABLES;";

    $result = $conn->query($sql);

    $tables = array();
    foreach($result->fetch_all() as $row)
        array_push($tables, $row[0]);

    $final_skip_tables = array();
    foreach($skip_tables as $table)
    {
        $pattern = str_replace('*', '.*', $table);
        $pattern = "/^$pattern$/";
        $final_skip_tables = array_merge( $final_skip_tables, preg_grep($pattern, $tables) );
    }
    $skip_tables = $final_skip_tables;

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
        }

        //fetch table
        $sql = "SELECT * FROM $table;";
        echo "Traversing $table...";
        if(WRITE_SQL_FILE)
            $out_file_content .= "#Traversing $table...\n";
        $result = $conn->query($sql);
        $result->fetch_all();

        //traverse all rows
        $counter = 0;
        foreach($result as $row)
        {
            $counter++;
            if($primary_key == NULL)
                $id = NULL;
            else
            {
                $id = $row[$primary_key];
                if(!is_numeric($id))
                    $id = "'$id'";
            }

            if($counter % 10000 == 0)
            {
                echo ".";
                flush();
            }

            //traverse all keys
            foreach($row as $col=>$key)
            {
                $db_entries_searched++;

                //we are only interested in strings
                if(!(is_string($key) || is_numeric($key)) || $col === $primary_key)
                    continue;

                //skip the case where we have serialized a false boolean value, because we cannot catch this with the unserialize return value
                if($key == 'b:0;')
                    continue;

                //try to deserialize
                $data = @unserialize($key);
                if($data === false)
                {
                    //failed to unserialize
                    $serialized = false;
                    $data = $key;
                }
                else
                {
                    //managed to unserialize
                    $serialized = true;
                    $db_entries_serialized++;
                }

                //search and replace the data
                $replaced_old = $replaced;
                $out = recursive_search_and_replace($data, $find, $replace);

                //write to search log file if search only
                $found_in_obj = $replaced - $replaced_old;
                if($replace === NULL && $found_in_obj > 0)
                {
                    if($found_in_obj === 1)
                        $log_file_content .= "Found once";
                    else
                        $log_file_content .= "Found $found_in_obj times";
                    $log_file_content .= " with id=$id: `$table`.`$col`=$key\n";
                }


                //create mysql query if there was something we found
                if($replace !== NULL && ($replaced_old < $replaced || DEBUG))
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

                    if($primary_key == NULL)
                    {
                        $old_data = prepare_for_mysql_statement($key);
                        $where = "$col='$old_data'";
                    }
                    else
                        $where = "$primary_key=$id";
                    $sql = "UPDATE `$table` SET $col='$new_data' WHERE $where;";
                    $query_failed = false;
                    if(PERFORMCE_MYSQL_STATEMENTS)
                    {
                        //perform query
                        $update_result = $conn->query($sql);

                        //tell about failed result but recover
                        if($update_result === false)
                        {
                            $query_failed = true;
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
                    }
                    if(WRITE_SQL_FILE)
                    {
                        if($query_failed)
                        {
                            echo "MySQL update query failed. Skipping this query in SQL outfile.";
                        }
                        else
                        {
                            $out_file_content .= $sql . "\n";
                            $made_sql_statement = true;
                        }
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
        if($replace === NULL)
            echo "Done. Found $replaced values.\n";
        else
        {
            echo "Done. Replaced $replaced values.\n";
            if (WRITE_SQL_FILE)
                $out_file_content .= "#Done. Replaced $replaced values.\n";
        }
        $reached_max_recursion = 0;
        $replaced_total += $replaced;
    }

    if(WRITE_SQL_FILE)
    {
        if($made_sql_statement)
        {
            file_put_contents(SEARCH_AND_REPLACE_SQL_FILE, $out_file_content);
            echo "SQL Statements written to " . SEARCH_AND_REPLACE_SQL_FILE . "\n";
        }
        else
            echo "No SQL Statements were created. No SQL File has been written.\n";
    }

    if($replace === NULL)
    {
        if(!empty($log_file_content))
        {
            file_put_contents(SEARCH_LOG_FILE, $log_file_content);
            echo "Search results have been written to " . SEARCH_LOG_FILE . "\n";
        }
        else
            echo "Search string not found, no logfile has been created.\n";
    }

    $time = (microtime(true) - $time);
    echo "Took $time seconds to search $db_entries_searched keys ($db_entries_serialized serialized) and " . ($replace === NULL ? 'found':'replaced') . " $replaced_total values by updating $db_entries_changed keys.\n";
}
if(sizeof($argv) < 6 or sizeof($argv) > 7)
{
    echo "Usage: php search-and-replace.php <host> <user> <password> <database> <find> [replace]\n";
    echo "Parameters in <> are obligatory, parameters in [] are optional.\n";
    echo "You can use two doublequotes to declare an empty replace string. In that case, all occurences of <find> will be replaced with an empty string.\n";
    echo "If no replace is given, no changes will be made in the database (aka dry run).\n";
    exit;
}
$host = $argv[1];
$user = $argv[2];
$password = $argv[3];
$database = $argv[4];
$find = $argv[5];
if(sizeof($argv) >6)
    $replace = $argv[6];
else
    $replace = NULL;

search_and_replace($find, $replace, $host, $user, $password, $database);



