<?php


error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('date.timezone', 'America/Los_Angeles');

// upload_max_filesize = 10M
// post_max_size = 10M
ini_set('memory_limit', '1G');
define('UPLOAD_STORAGE_DIR', './uploaded-files');
//define('UPLOAD_STORAGE_DIR', '/var/www/uploads');


function status_header($code) {
    header($_SERVER["SERVER_PROTOCOL"] . ' ' . $code);
}

function get_error_json($error, $extra = null) {
    return json_encode(compact('error', 'extra'));
}