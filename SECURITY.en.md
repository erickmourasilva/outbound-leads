# Security and responsible use

## Reporting a vulnerability

Please report security issues privately through GitHub: **Security → Report a vulnerability** on this repository. Do not open a public issue for vulnerabilities.

## Design notes

- The dashboard binds to `127.0.0.1` only and accepts changes only with a custom header, which blocks cross-site requests.
- Data lives in a local SQLite file (`~/.outbound-leads`). Nothing is sent to any server by this project.
- The tool never types passwords, codes or tokens. Logins are done by the operator in a visible browser window.

## Responsible use

Automated messaging may violate a platform's terms and local law (for example GDPR, Brazil's LGPD, anti-spam rules). Use a dedicated account, keep volume low, honour every opt-out, and only use public, professional information. You are responsible for how you use this software.
