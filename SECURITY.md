<p align="right"><b>🇬🇧 English</b> · <a href="SECURITY.nl.md">🇳🇱 Dutch</a></p>

# Security policy

## Reporting a vulnerability

Found a security problem in DutchQuill AI? Report it **privately** instead of in a public issue.

### How to report

Use [GitHub Security Advisories](https://github.com/nickyjacobs/DutchQuill-AI/security/advisories/new) to send a
private report, or email the maintainer. Describe:

- What the problem is
- How to reproduce it
- Which files or tools are involved

### What you can expect

- Confirmation of receipt within 7 days
- An assessment of the impact and a proposed fix
- An update as soon as the fix is available

### Scope

This policy covers the code in this repository: the plugin (skills, agents, hook), the Python scripts and DutchQuill
Studio. It does not cover Anthropic's API or Claude Code itself.

## What DutchQuill itself does

- DutchQuill Studio only listens on 127.0.0.1, with a one-time token, and checks Host and Origin.
- Web requests only go to the hosts in `.claude-plugin/plugin.json` (`network.hosts`): PyPI (the one-time
  installation of the Python packages), LanguageTool (only if you switch it on) and the sources of
  `/dutchquill:bijwerken`. The [privacy policy](docs/privacy.md) lists what goes where.
- Internal addresses (localhost, private IPs) in your material are never fetched automatically.

## Dependencies

The Python packages are listed in `requirements.txt` and installed in a separate venv in the plugin's data folder.
Dependabot scans them for known vulnerabilities.

## Responsible disclosure

Don't make a vulnerability public before a fix is available. After the fix, the vulnerability is mentioned in the
release notes of the next version.
