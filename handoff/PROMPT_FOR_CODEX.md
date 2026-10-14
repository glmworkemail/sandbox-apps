# Codex — build glmDev.com

You are a senior front-end developer, visual designer, and PHP engineer. Build a production-quality, responsive professional portfolio / freelance consulting website for **glmDev.com** in the current local folder.

## First: inspect the handoff
Read `CODEX_HANDOFF.md`, `CONTENT_AND_SECTIONS.md`, `BLUEHOST_DEPLOYMENT.md`, and inspect the PNG images under `design/`. The primary approved visual direction is `design/APPROVED_HOMEPAGE_REFERENCE.png`; the AI training detail is `design/AI_TRAINING_SECTION_DETAIL.png`. Preserve the general composition, airy white/blue palette, 3x2 service grid, and full-width AI Consulting & Training band. Use real HTML/CSS elements, not a screenshot-based page.

## Build requirements
- Semantic HTML5, modern CSS, vanilla JavaScript, and only minimal PHP for a contact endpoint.
- **No Laravel, Angular, React, Vue, database, Node runtime, Web3Forms, or third-party form submission service.** No GitHub requirement.
- Works on typical Bluehost shared hosting; no production build command necessary. Responsive on phone, tablet, desktop.
- Use an uncluttered, modern, bright look: white/light gray surfaces, charcoal text, vibrant accessible blue, rounded cards, subtle shadows, attractive UI illustrations. Keep copy concise.
- Include hero, six service cards, dedicated AI Consulting & Training feature, brief engineer bio and tech badges, project examples, friendly IT-support clarification, contact form, footer.
- Build working navigation, sensible hover/focus states, accessible labels, mobile menu, reduced-motion support, meaningful alt text and keyboard navigation.
- Design responsive and performant visuals; use original SVG/CSS illustrations or licensed assets, with attribution when required. Do not embed mockup screenshots as actual website sections. Avoid stock robot/brain imagery.
- Projects shown in mockup are illustrative: label as representative examples until owner provides real screenshots and approved case-study details. Do not invent clients, testimonials, quantified results, certifications, or project claims.
- Preserve ability to swap placeholder images and edit all copy easily.

## Contact form
Implement a simple contact form with name, email, and message, posting to a small PHP endpoint. Use PHPMailer with authenticated SMTP, server-side validation, anti-spam honeypot, CSRF protection (where feasible with sessions), rate limiting or other reasonable abuse mitigation, safe output, and generic error messages. Never trust client-side validation alone. Set Reply-To to the validated visitor email; send FROM using the authenticated mailbox/domain, never spoof visitor FROM. Keep credentials out of public webroot / versioned source, use an ignored server-side configuration file or environment variables. Provide an example config with fake values, clear setup documentation, and a no-credentials local demo state that **does not falsely claim an email was sent**. If PHPMailer is vendored for Bluehost deployment, document its source and license. Do not implement insecure open mail relays or rely on PHP `mail()` as the primary method.

## Deliverables
1. Actual working website source files (not merely a plan).
2. A locally previewable homepage and any small additional pages necessary; favor a polished single-page site with anchored sections unless another page adds clear value.
3. `README.md` with local preview and edit instructions; `DEPLOYMENT.md` for Bluehost; `CHANGELOG.md`; `TODO.md` listing any credentials/assets/client claims awaiting owner input.
4. Explicit file tree and verification summary. Test links, responsive breakpoints, form validation, and PHP syntax where possible. Explain what could not be tested without Bluehost SMTP credentials.

## Execution
Implement now. Make reasonable design choices rather than asking about minor details. Ask only for essential missing secrets or irreversible decisions; **never request that SMTP passwords be pasted into chat**. Do not claim a live form works until tested against configured SMTP. Keep the site easy for a .NET/Angular engineer to maintain with minimal PHP knowledge.
