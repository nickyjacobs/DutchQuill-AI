<p align="right"><a href="../privacy.md">🇳🇱 Nederlands</a> · <b>🇬🇧 English</b></p>

# Privacy

DutchQuill AI is a plugin for Claude Code and runs on your own computer. The maker of DutchQuill collects nothing:
there is no account, no telemetry, no analytics and no DutchQuill server.

## What stays on your computer

- Your texts, sources and output are in your workspace. That folder is yours.
- Your settings are in `dutchquill.yaml` in your workspace.
- The Python environment and the cache are in the plugin's data folder, under `~/.claude/plugins/data/`.
- DutchQuill Studio runs on 127.0.0.1, with a one-time key. Other devices can't reach it.

## What goes to Claude

What you share with Claude in a conversation, or let it read, goes to Anthropic, as with any other conversation in
Claude Code. [Anthropic's privacy policy](https://www.anthropic.com/legal/privacy) covers that, not this document.
DutchQuill doesn't send your text anywhere else.

## What goes to the internet, and when

| Host | When | What is sent |
|---|---|---|
| `api.languagetool.org` | Only if you switch on the online language check. It is off by default. | The text you have checked and the language code. [LanguageTool's privacy policy](https://languagetool.org/legal/privacy) applies. |
| `pypi.org`, `files.pythonhosted.org` | The first time a command needs Python, and after an update | A regular download of the Python packages. None of your text. |
| `www.scribbr.nl`, `en.wikipedia.org`, `api.github.com` | Only when you run `/dutchquill:bijwerken` | A request for public pages, with the user agent `DutchQuill-bronnencheck`. None of your text. |

The hosts the plugin may reach are listed in `.claude-plugin/plugin.json` under `network.hosts`. DutchQuill never
fetches internal addresses (localhost, private IPs) found in your material on its own.

## Removing it

Type `/plugin` in Claude Code, choose DutchQuill and remove it. Your workspace stays. You can delete the data folder
under `~/.claude/plugins/data/` afterwards; then nothing of DutchQuill is left on your computer.

## Contact

- A question or a bug: [GitHub Issues](https://github.com/nickyjacobs/DutchQuill-AI/issues).
- A security problem: report it privately, as [SECURITY.md](../../SECURITY.md) describes.

Changes to this policy are listed in the [CHANGELOG](../../CHANGELOG.md). Last updated: 2026-11-25.
