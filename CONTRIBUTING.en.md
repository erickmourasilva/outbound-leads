# Contributing

Thanks for helping. This project exists to make outbound **gradual, supervised and honest**, so contributions are judged against those principles (see the README).

## Setup

```bash
git clone https://github.com/erickmourasilva/outbound-leads && cd outbound-leads
python3 -m outbound setup --check
python3 -m unittest discover -s tests -v
```

Python 3.10+ and the standard library only. Please do not add runtime dependencies without discussing it first.

## Pull requests

- One focused change per PR, with tests. CI runs on macOS, Linux and Windows.
- Keep user data out of the repository: no real leads, handles, messages or screenshots. Use the `demo` command for examples.
- Commands must keep printing JSON, so agents can read them.

## What will not be merged

- Anything that disguises automation (simulated typing, fingerprint spoofing) or bypasses CAPTCHA, rate limits or blocks.
- Features that collect personal phone numbers, e-mails or sensitive attributes, or that scrape private or gated data.
- Defaults that send without explicit operator approval, or that raise the sending caps.

## Reporting bugs

Open an issue with the output of `python3 -m outbound doctor` and your OS. For security issues, see `SECURITY.en.md`.
