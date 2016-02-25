<?php
$WLibrary = '../workflows/';
$date = date('Y-m-d_H:i', time());
$name = $_POST['workflow']['name'];
$fname = $WLibrary.$name.'_'.$date;
$file = fopen($fname, 'w');
fwrite($file, json_encode($_POST['workflow']));
fclose($file);
if ($_POST['action'] == 'analyse') {
    $output = exec('/usr/local/bin/python ../py/main.py analyse '.$fname);
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    echo $content;
}
elseif ($_POST['action'] == 'optimise') {
    $output = exec('/usr/local/bin/python ../py/main.py optimise '.$fname);
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    echo $content;
}
elseif ($_POST['action'] == 'execute') {
    $output = exec('/usr/local/bin/python ../py/main.py execute '.$fname);
    if ($output)
        echo 'sended to IReS';
}
elseif ($_POST['action'] == 'save') {
    echo 'saved as '.$name.'_'.$date;
}
?>
