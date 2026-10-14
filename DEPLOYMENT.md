# Deploying to Bluehost

## Hosting layout

Use PHP 8.2+ with OpenSSL, sessions, and outbound authenticated SMTP supported by the host. No Composer, Node, or database is needed. PHPMailer 7.1.1 is included under `vendor/phpmailer/` with its LGPL-2.1 license and upstream commit/source information.

Keep the public and private directories as siblings. For a main domain whose document root is `public_html`, use:

```text
account-home/
├── public_html/              # contents of this project's public/
│   ├── index.html
│   ├── contact.php
│   ├── .htaccess
│   └── assets/
├── private/
│   ├── config.php
│   └── rate-limit/
└── vendor/
    └── phpmailer/
```

Confirm the domain's assigned document root in Bluehost. `contact.php` uses the parent of that root for `private/` and `vendor/`. For an addon domain, put them beside its actual document root. Avoid collisions with existing private/vendor directories; an account-home domain-specific parent containing a dedicated document root is preferable when hosting several sites. Use the production package as a layout guide, not a command to overwrite existing host files.

Upload the contents of `public/` to the document root, including `.htaccess`. Upload `vendor/phpmailer/` and `private/config.example.php` to the sibling non-public folders. Do not upload `handoff/`, tests, scripts, review screenshots, Git metadata, or documentation into the public root. Disable public directory listing. If Bluehost disallows an `.htaccess` directive, resolve it with host support rather than turning off protections blindly.

Do not place credentials in public_html. If your account cannot store files outside the public document root, obtain a supported private location/environment-variable setup from Bluehost before enabling the form. This implementation intentionally assumes a private sibling directory.

## SMTP configuration

Copy `private/config.example.php` to `private/config.php` outside the public root. Edit it securely in hosting tools, never in chat or version control. Use provider-confirmed host, username, password, and encryption. Use authenticated STARTTLS on port 587 (`tls`) or implicit TLS on port 465 (`ssl`); certificate verification remains enabled. The From address must be an approved mailbox for the authenticated account/domain. Reply-To is the validated visitor email. `to_email` is the owner's receiving address. Keep `from_name` free of line breaks.

Alternatively configure these actual server environment variables:

- `GLM_SMTP_HOST`, `GLM_SMTP_PORT`, `GLM_SMTP_ENCRYPTION`
- `GLM_SMTP_USERNAME`, `GLM_SMTP_PASSWORD`
- `GLM_FROM_EMAIL`, `GLM_FROM_NAME`, `GLM_TO_EMAIL`
- `GLM_RATE_DIR` (absolute, writable, outside the webroot; optional)

These variables are read by PHP. Environment values override the private config. Do not place credentials in client JavaScript, HTML, or a publicly downloadable `.env`. No cloud secret binding is required for the no-mail local demo; configure production SMTP on Bluehost.

Create the rate-limit directory with permissions appropriate to the PHP account, ideally 0700. Keep config files restricted to the account/PHP process, ideally 0600 where PHP executes as your user. Confirm the host's PHP session save directory is writable and private. Configure HTTPS in Bluehost and verify redirects before enabling the form; do not submit real inquiries over HTTP. The application sets Secure cookies when PHP reports HTTPS. Verify PHP's HTTPS detection for the host's proxy setup without trusting arbitrary forwarded request headers.

The endpoint accepts up to five valid attempts per remote IP per hour, across sessions and PHP workers, including unsuccessful SMTP attempts. It ignores incoming X-Forwarded-For headers. If Bluehost routes all requests through one proxy IP, request the host's trusted real-IP configuration so it does not group every visitor together. Abuse mitigation is basic; review host-level limits if traffic grows. Rate files retain hashed IPs and timestamps, not message content; periodically remove files older than two days using the host's scheduled-job facility. Session data contains only CSRF information.

## Before going live

1. Enable HTTPS and confirm navigation, assets, mobile menu, keyboard focus, and form labels on the actual domain.
2. Check that `/private/config.php`, `/vendor/`, and handoff files are not publicly reachable.
3. Verify the host applies `.htaccess` security headers and supports PHP sessions and private rate storage.
4. Configure SPF, DKIM, and DMARC as directed by the email provider. Do not guess provider settings.
5. Send one controlled real inquiry. Confirm receipt, authenticated From, visitor Reply-To, and plain-text content. The success response means the SMTP server accepted the message, not guaranteed inbox delivery.
6. Check invalid email, short/oversized message, expired CSRF, honeypot, rate limiting, and an intentionally failed SMTP connection. Public errors should stay generic and never reveal secrets.
7. Confirm mail logs do not capture inquiry contents or SMTP debug output. Error logs contain only generic configuration/rate-limiter/delivery failure descriptions.
8. Configure host backups and monitor the contact endpoint. Never use the PHP development server in production.

No live deployment or SMTP transmission was performed during this build. Bluehost-specific behavior must be tested on the hosting account.
