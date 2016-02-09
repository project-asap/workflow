<?php
$file = fopen('../py/workflow', 'w');
fwrite($file, json_encode($_POST['workflow']));
fclose($file);
if ($_POST['action'] == 'analyse') {
    $output = exec('/usr/local/bin/python ../py/main.py analyse');
//	$filename = '../files/workflow-analysed.json';
}
elseif ($_POST['action'] == 'optimise') {
    $output = exec('/usr/local/bin/python ../py/main.py optimise');
//	$filename = '../files/workflow-optimised.json';
}
$filename = '../py/workflow_res';
$file = fopen($filename, 'r');
$content = fread($file, filesize($filename));
fclose($file);
echo $content;
?>
