<?php

require 'config.php';

header('content-type: application/json');
header('Access-Control-Allow-Origin: *');


$regexFilter = isset($_GET['regexFilter']) && strlen(trim($_GET['regexFilter'])) ? trim($_GET['regexFilter']) : false;
$filter = isset($_GET['filter']) && strlen(trim($_GET['filter'])) ? trim($_GET['filter']) : false;
$minDateTime = isset($_GET['minDateTime']) && strlen(trim($_GET['minDateTime'])) ? trim($_GET['minDateTime']) : false;
$maxDateTime = isset($_GET['maxDateTime']) && strlen(trim($_GET['maxDateTime'])) ? trim($_GET['maxDateTime']) : false;
$limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 1000;

$matchesFilters = function($fileName) use ($regexFilter, $filter, $minDateTime, $maxDateTime) {
    return (!$filter || false !== stripos($fileName, $filter))
        && (!$regexFilter || preg_match($regexFilter, $fileName))
        && (!$minDateTime || $minDateTime <= $fileName)
        && (!$maxDateTime || $maxDateTime >= $fileName)
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