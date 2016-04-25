<?php
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

function startsWith($haystack, $needle) {
    // search backwards starting from haystack length characters from the end
    return $needle === "" || strrpos($haystack, $needle, -strlen($haystack)) !== false;
}

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

if (file_exists($WLibrary.$name.'_o.json')) {
    $filename = $WLibrary.$name.'_o.json';
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    die($content);
}

$file = fopen($fname, 'w') or die("can't open file: ".$fname);
fwrite($file, json_encode($_POST['workflow']));
fclose($file);
if ($_POST['action'] == 'analyse') {
    $output = exec('/usr/local/bin/python ../py/main.py analyse '.$fname);
    if (startsWith($output, 'ERROR:')) {
        http_response_code(500);
        die($output);
    }
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    die($content);
}
elseif ($_POST['action'] == 'optimise') {
    $output = exec('/usr/local/bin/python ../py/main.py optimise '.$fname);
    if (startsWith($output, 'ERROR:')) {
        http_response_code(500);
        die($output);
    }
    $filename = $output;
    $file = fopen($filename, 'r');
    $content = fread($file, filesize($filename));
    fclose($file);
    die($content);
}
elseif ($_POST['action'] == 'execute') {
    $output = exec('/usr/local/bin/python ../py/main.py execute '.$fname);
    if (startsWith($output, 'ERROR:')) {
        http_response_code(500);
        die($output);
    }
    if ($output)
        die('sended to IReS');
}
elseif ($_POST['action'] == 'save') {
    die('saved as '.$name.'_'.$date);
}
?>
