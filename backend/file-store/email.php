<?php

ini_set('display_errors', 1);
error_reporting(-1);



$to      = $_GET['to'];
$subject = $_GET['subject'];
$message = $_GET['message'];
$from = $_GET['from'];


$contents = "From: $from
To: $to
Subject: $subject
Content-Type: text/html
MIME-Version: 1.0

$message";

$f = '/tmp/email.txt';
file_put_contents($f, str_replace("\r\n", "\n", $contents));

//var_dump(shell_exec("sendmail $to < /tmp/email.txt"));
var_dump(shell_exec("sendmail $to < $f"));
var_dump(shell_exec('whoami'));
readfile($f);