<?php

require 'config.php';

header('content-type: application/json');
header('Access-Control-Allow-Origin: *');


$regexFilter = isset($_GET['regexFilter']) && strlen(trim($_GET['regexFilter'])) ? trim($_GET['regexFilter']) : false;
$filter = isset($_GET['filter']) && strlen(trim($_GET['filter'])) ? trim($_GET['filter']) : false;
$limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 1000;

$matchesFilters = function($fileName) use ($regexFilter, $filter) {
    return (!$filter || false !== stripos($fileName, $filter))
        && (!$regexFilter || preg_match($regexFilter, $fileName))
        && $fileName[0] !== '.'
    ;
};

$toFileDataEntry = function($fileName) {
    return array('url' => 'http://104.233.111.80/file-store/uploaded-files/' . $fileName);
};

$matchingFiles = array_filter(scandir(UPLOAD_STORAGE_DIR), $matchesFilters);
rsort($matchingFiles);
$results = array_slice($matchingFiles, 0, $limit);


echo json_encode(array_map($toFileDataEntry, $results));