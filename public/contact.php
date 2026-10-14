<?php
declare(strict_types=1);

use PHPMailer\PHPMailer\PHPMailer;

ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function reply(int $code, array $body): never {
    http_response_code($code);
    echo json_encode($body, JSON_UNESCAPED_SLASHES);
    exit;
}
function fail(int $code, string $message): never { reply($code, ['message' => $message]); }

$method = $_SERVER['REQUEST_METHOD'] ?? '';
if (!in_array($method, ['GET', 'POST'], true)) {
    header('Allow: GET, POST');
    fail(405, 'This request is not supported.');
}
if ($method === 'POST' && (int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 20000) {
    fail(413, 'Your message is too large.');
}
$secure = !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off';
session_name('glmdev_contact');
session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
ini_set('session.use_strict_mode', '1');
if (!session_start()) fail(503, 'The contact form is currently unavailable.');
if (!isset($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(32));
if ($method === 'GET') $_SESSION['csrf_time'] = time();
$token = $_SESSION['csrf'];
$tokenTime = (int) ($_SESSION['csrf_time'] ?? 0);
session_write_close();

$configPath = dirname(__DIR__) . '/private/config.php';
$config = [];
try {
    if (is_file($configPath)) {
        $loaded = require $configPath;
        if (is_array($loaded)) $config = $loaded;
    }
} catch (Throwable $e) { error_log('glmDev: contact configuration could not be loaded.'); }
$envFields = ['host' => 'GLM_SMTP_HOST', 'port' => 'GLM_SMTP_PORT', 'encryption' => 'GLM_SMTP_ENCRYPTION', 'username' => 'GLM_SMTP_USERNAME', 'password' => 'GLM_SMTP_PASSWORD', 'from_email' => 'GLM_FROM_EMAIL', 'from_name' => 'GLM_FROM_NAME', 'to_email' => 'GLM_TO_EMAIL', 'rate_dir' => 'GLM_RATE_DIR'];
foreach ($envFields as $key => $name) {
    $value = getenv($name);
    if ($value !== false && $value !== '') $config[$key] = $value;
}
$config += ['port' => 587, 'encryption' => 'tls', 'from_name' => 'glmDev website', 'rate_dir' => dirname(__DIR__) . '/private/rate-limit'];
$ready = true;
foreach (['host', 'username', 'password', 'from_email', 'to_email'] as $key) {
    if (!isset($config[$key]) || !is_string($config[$key]) || trim($config[$key]) === '') $ready = false;
}
$port = filter_var($config['port'], FILTER_VALIDATE_INT);
if (!in_array($config['encryption'], ['tls', 'ssl'], true) || !in_array($port, [587, 465], true)) $ready = false;
foreach (['from_email', 'to_email'] as $key) if (!filter_var($config[$key] ?? '', FILTER_VALIDATE_EMAIL)) $ready = false;
$vendor = dirname(__DIR__) . '/vendor/phpmailer/src/';
if (!is_file($vendor . 'PHPMailer.php') || !extension_loaded('openssl')) $ready = false;
if ($method === 'GET') reply(200, ['csrf' => $token, 'ready' => $ready]);

function field(string $name): string {
    if (!isset($_POST[$name]) || !is_string($_POST[$name])) fail(422, 'Please check your name, email address, and project message.');
    return trim($_POST[$name]);
}
$csrf = $_POST['csrf'] ?? null;
if (!is_string($csrf) || !hash_equals($token, $csrf) || time() - $tokenTime > 3600) {
    fail(403, 'Your form session expired. Please reload the page and try again.');
}
$honeypot = $_POST['website'] ?? '';
if (!is_string($honeypot) || $honeypot !== '') fail(422, 'Your message could not be accepted.');
$name = field('name');
$email = field('email');
$message = field('message');
if ($name === '' || strlen($name) > 100 || preg_match('/[\x00-\x1f\x7f]/', $name) ||
    strlen($email) > 254 || preg_match('/[\r\n]/', $email) || !filter_var($email, FILTER_VALIDATE_EMAIL) ||
    strlen($message) < 10 || strlen($message) > 5000 || preg_match('/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/', $message) ||
    !preg_match('//u', $name . $message)) {
    fail(422, 'Please enter a valid name, email address, and message of 10–5000 bytes.');
}

// Persistent per-IP limit; do not trust client-provided forwarding headers.
// Store only hashed addresses and timestamps, never inquiry content.
$rateDir = (string) $config['rate_dir'];
try {
    if (!is_dir($rateDir) && !mkdir($rateDir, 0700, true) && !is_dir($rateDir)) throw new RuntimeException('Rate directory');
    $realRateDir = realpath($rateDir);
    $documentRoot = realpath($_SERVER['DOCUMENT_ROOT'] ?? __DIR__);
    if ($realRateDir === false || ($documentRoot && ($realRateDir === $documentRoot || str_starts_with($realRateDir, $documentRoot . DIRECTORY_SEPARATOR)))) throw new RuntimeException('Public rate directory');
    $file = $realRateDir . '/' . hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown') . '.json';
    $handle = fopen($file, 'c+');
    if ($handle === false || !flock($handle, LOCK_EX)) throw new RuntimeException('Rate lock');
    $old = json_decode(stream_get_contents($handle) ?: '[]', true);
    $now = time();
    $times = array_values(array_filter(is_array($old) ? $old : [], fn($v) => is_int($v) && $v > $now - 3600));
    if (count($times) >= 5) {
        flock($handle, LOCK_UN); fclose($handle);
        header('Retry-After: 3600');
        fail(429, 'Too many attempts. Please try again in an hour.');
    }
    $times[] = $now;
    rewind($handle); ftruncate($handle, 0);
    if (fwrite($handle, json_encode($times)) === false) throw new RuntimeException('Rate write');
    fflush($handle); flock($handle, LOCK_UN); fclose($handle);
} catch (Throwable $e) {
    error_log('glmDev: contact rate limiter unavailable.');
    fail(503, 'The contact form is currently unavailable. Please try again later.');
}
if (!$ready) fail(503, 'Email is not configured. Your message has not been sent.');

try {
    require_once $vendor . 'Exception.php';
    require_once $vendor . 'PHPMailer.php';
    require_once $vendor . 'SMTP.php';
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = $config['host'];
    $mail->Port = $port;
    $mail->SMTPAuth = true;
    $mail->Username = $config['username'];
    $mail->Password = $config['password'];
    $mail->SMTPSecure = $config['encryption'] === 'ssl' ? PHPMailer::ENCRYPTION_SMTPS : PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Timeout = 15;
    $mail->CharSet = 'UTF-8';
    $mail->setFrom($config['from_email'], (string) $config['from_name']);
    $mail->addAddress($config['to_email']);
    $mail->addReplyTo($email, $name);
    $mail->Subject = 'glmDev website inquiry';
    $mail->isHTML(false);
    $mail->Body = "Name: $name\nEmail: $email\n\nProject inquiry:\n$message";
    $mail->send();
    reply(200, ['message' => 'Your message was accepted by the mail server. Thank you for getting in touch.']);
} catch (Throwable $e) {
    // Do not log SMTP debug output, addresses, credentials, or inquiry content.
    error_log('glmDev: contact SMTP delivery failed.');
    fail(503, 'Your message could not be sent. Please try again later.');
}
