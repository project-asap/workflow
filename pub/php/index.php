<?php
function endsWith($haystack, $needle) {
    // search forward starting from end minus needle length characters
    return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== false);
}

if ($_POST['action'] == 'get_list') {
    $wls = array();
    if ($handle = opendir('../workflows/.')) {
        while (false !== ($entry = readdir($handle))) {
            if (endsWith($entry, '.json')) {
                array_push($wls, $entry);
            }
        }
        closedir($handle);
    }
    die(json_encode($wls));
}
$WLibrary = '../workflows/';
$date = date('Y-m-d_H:i', time());
$name = $_POST['workflow']['name'];
$fname = $WLibrary.$name.'_'.$date;
$file = fopen($fname, 'w') or die("can't open file: ".$fname);
fwrite($file, json_encode($_POST['workflow']));
fclose($file);
if ($_POST['action'] == 'analyse') {
    $output = exec('/usr/local/bin/python ../py/main.py analyse '.$fname);
//    $output = exec('python ../py/main.py analyse '.$fname);
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    echo $content;
}
elseif ($_POST['action'] == 'optimise') {
    $output = exec('/usr/local/bin/python ../py/main.py optimise '.$fname);
//    $output = exec('python ../py/main.py optimise '.$fname);
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    echo $content;
}
elseif ($_POST['action'] == 'execute') {
    $output = exec('/usr/local/bin/python ../py/main.py execute '.$fname);
//    $output = exec('python ../py/main.py execute '.$fname);
    if ($output)
        echo 'sended to IReS';
}
elseif ($_POST['action'] == 'save') {
    echo 'saved as '.$name.'_'.$date;
}
?>
