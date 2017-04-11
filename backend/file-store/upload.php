<?php

require 'config.php';

header('content-type: application/json');
header('Access-Control-Allow-Origin: *');

if (empty($_FILES['upfile'])) {
    status_header(400);
    echo get_error_json('no file named "upfile" was found', $_FILES);
    exit;
}

$upfile = $_FILES['upfile'];


if ($upfile['error'] !== UPLOAD_ERR_OK) {
    status_header(400);
    echo get_error_json('upload error', $_FILES);
    exit;
}

$fileExt = pathinfo($upfile['name'], PATHINFO_EXTENSION);
$allowedExts = array('jpg', 'png', 'gif');
if (!in_array($fileExt, $allowedExts)) {
    status_header(400);
    echo get_error_json('bad file ext', $allowedExts);
    exit;
}

$newFileName = sprintf("%s-%s", date('Y-m-d\TH-i-s'), basename($upfile['name']));
$destFileName = sprintf("%s/%s", UPLOAD_STORAGE_DIR, $newFileName);

if (move_uploaded_file($upfile['tmp_name'], $destFileName)) {
    status_header(201);
    echo json_encode(array('success' => true, 'extra' => array('newName' => $newFileName)));
} else {
    status_header(500);
    echo get_error_json('failure');
}