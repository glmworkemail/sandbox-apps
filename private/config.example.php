<?php
// Copy to private/config.php, OUTSIDE the public document root.
// Placeholder values only. Obtain actual settings from your mail provider.
return [
    'host' => 'smtp.example.com',
    'port' => 587,
    'encryption' => 'tls', // tls = STARTTLS on 587; ssl = implicit TLS on 465
    'username' => 'hello@example.com',
    'password' => '',
    'from_email' => 'hello@example.com',
    'from_name' => 'glmDev website',
    'to_email' => 'hello@example.com',
    // Must be outside the document root, writable by PHP, shared across workers.
    'rate_dir' => __DIR__ . '/rate-limit',
];
