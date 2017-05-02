<?php

require 'config.php';

header('content-type: application/json');
header('Access-Control-Allow-Origin: *');


$regexFilter = isset($_GET['regexFilter']) && strlen(trim($_GET['regexFilter'])) ? trim($_GET['regexFilter']) : false;
$filter = isset($_GET['filter']) && strlen(trim($_GET['filter'])) ? trim($_GET['filter']) : false;
$minDateTime = isset($_GET['minDateTime']) && strlen(trim($_GET['minDateTime'])) ? trim($_GET['minDateTime']) : false;
$maxDateTime = isset($_GET['maxDateTime']) && strlen(trim($_GET['maxDateTime'])) ? trim($_GET['maxDateTime']) : false;
$limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 1000;
$deleteMatched = isset($_GET['deleteMatched']) ? (bool) $_GET['deleteMatched'] : false;



// The filename has a datetime string date at the front.
// But, the date filters passed via url may not be a full date time, eg it might only be a year, or year-month etc...
// So, we only do the comparison based on same string length.
function cmpPartialDate($fileName, $dateTimeStr) {
    $partialFileName = substr($fileName, 0, strlen($dateTimeStr));
    return strcasecmp($partialFileName, $dateTimeStr);
}

$matchesFilters = function($fileName) use ($regexFilter, $filter, $minDateTime, $maxDateTime) {
    return (!$filter || false !== stripos($fileName, $filter))
        && (!$regexFilter || preg_match($regexFilter, $fileName))
        && (!$minDateTime || cmpPartialDate($fileName, $minDateTime) >= 0)
        && (!$maxDateTime || cmpPartialDate($fileName, $maxDateTime) <= 0)
        && $fileName[0] !== '.'
        ;
};

$toFileDataEntry = function($fileName) {
    return array('url' => 'http://104.233.111.80/file-store/uploaded-files/' . $fileName);
};

$matchingFiles = array_filter(scandir(UPLOAD_STORAGE_DIR), $matchesFilters);
rsort($matchingFiles);
$results = array_slice($matchingFiles, 0, $limit);

if ($deleteMatched) {
    foreach ($results as $result) {
        unlink(UPLOAD_STORAGE_DIR . '/' . $result);
    }
}


echo json_encode(array_map($toFileDataEntry, $results));