# Bluehost deployment and email setup

## Static site + minimal PHP
Upload HTML, CSS, JS, SVG/images and the PHP contact endpoint to the domain's Bluehost document root (commonly `public_html` or an addon domain's assigned root; confirm in hosting dashboard). No Laravel, database, or production JS build required.

## Email architecture
Use PHPMailer via authenticated SMTP with an existing mailbox/SMTP service approved by the owner. PHPMailer is a PHP library, not a hosted form-submission service. SMTP settings depend on the actual Bluehost/email provider configuration and must be confirmed, not guessed. Prefer TLS, authentication, and a domain-aligned From address. Set Reply-To to the visitor. Verify SPF/DKIM/DMARC for the sending domain according to the email provider's instructions.

## Secrets and safety
Store real SMTP credentials in a PHP configuration file **outside the public document root** where hosting layout permits, or as server environment variables. Never commit them, ship them in a ZIP, or expose them in front-end JS. Include a non-secret example config and `.gitignore` for future optional local version control. If a non-public directory is impossible, use host-specific protections and document limitations. Ensure errors and stack traces are not shown publicly.

## Testing checklist
- All routes/anchors work after upload; no localhost URLs.
- Mobile menu, responsive cards, forms, focus states, and accessibility checked.
- PHP version meets installed PHPMailer requirements.
- Valid inquiry sends successfully via SMTP; sender and Reply-To verified.
- Invalid inputs, honeypot, CSRF, rate limiting, and error handling tested.
- No credentials, sample secrets, internal documentation, or unused dev files in public webroot.
- HTTPS enabled; contact form posts over HTTPS.
- Deploy only production files; keep handoff mockups and private docs out of public webroot.
