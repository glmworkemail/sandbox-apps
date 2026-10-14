# glmDev website

A responsive single-page software engineering and AI consultancy site based on the approved handoff. Plain HTML, CSS, vanilla JavaScript, and a PHP contact endpoint; no Node runtime, database, framework, or production build.

## Local preview

Use PHP 8.2 or newer with OpenSSL and sessions enabled:

```sh
php -S 127.0.0.1:8080 -t public
```

For this Codex cloud machine, use `./scripts/serve.sh`. It selects the retained PHP 8.4 runtime when system PHP is unavailable, and creates a private local session directory. The built-in PHP server is for development only.

Visit the local address in your own development browser. Cloud onboarding does not provide a public localhost preview link. PHP sessions must have a writable private save directory. Stop the development server with Ctrl+C.

The no-credentials demo disables Send Message and explains that email is not connected. It never claims to have delivered a message. Test text is not saved anywhere by the application. Deploying and configuring SMTP are separate steps; see DEPLOYMENT.md.

## Editing

- Copy, section ordering, navigation, and conceptual dashboard: `public/index.html`.
- Colors, typography, grids, breakpoints, and illustrations: `public/assets/site.css`.
- Navigation and form interactions: `public/assets/site.js`.
- Six original service illustrations and favicon: `public/assets/*.svg`.
- Mail handling: `public/contact.php`.
- Reference mockups and original brief: `handoff/`; never deploy this folder.

There are exactly six service cards, followed by a distinct AI consulting/training band with four offerings. Work samples are explicitly representative, with illustrative interfaces. No clients, statistics, qualifications, or employee relationships were invented. All artwork is original SVG/CSS/HTML; no external asset requests or font services.

Replace illustrative work with approved projects when available; remove the representative label only when a project and its image are approved. Add an actual headshot, public email, and social links only after the owner supplies them. Keep private company data out of public assets.

## File tree

```text
sandbox-apps/
├── public/                   # ONLY this directory is publicly served
│   ├── index.html
│   ├── contact.php
│   ├── .htaccess
│   └── assets/
│       ├── site.css
│       ├── site.js
│       ├── favicon.svg
│       └── {custom,ai,automation,integration,mobile,consulting}.svg
├── private/
│   ├── config.example.php    # placeholder settings; no credentials
│   ├── config.php            # owner creates; ignored, outside webroot
│   └── rate-limit/           # generated, ignored; hashed IPs + timestamps
├── vendor/phpmailer/
│   ├── src/                  # unmodified PHPMailer 7.1.1
│   ├── LICENSE
│   └── UPSTREAM.md
├── scripts/
│   ├── serve.sh
│   └── setup-cloud.sh
├── tests/
│   ├── contact_smoke.py
│   └── browser_smoke.py
├── handoff/                  # reference documents/images, not production
├── var/                      # ignored: local sessions, review screenshots
├── README.md
├── DEPLOYMENT.md
├── CHANGELOG.md
├── TODO.md
└── VERIFICATION.md
```

## Checks

```sh
php -l public/contact.php
node --check public/assets/site.js  # optional development check; not a production dependency
python tests/contact_smoke.py
# With the development server running:
python tests/browser_smoke.py
```

Contact tests run an isolated server with no email settings. They refuse to run if a real private config is present. Python Playwright and `/usr/bin/chromium` are needed only for browser checks, and are available in this cloud environment. Generated screenshots go to ignored `var/`. See VERIFICATION.md for actual outcomes and limitations.
