---
description: Open the founder-id-checker dashboard, a live, read-only web page of this project's checker/ folder (the verdict, the months, the fixes, channels, customers, papers, the board and every document)
argument-hint: "[--port 8765] [--export file.html]"
allowed-tools: Bash(python3:*)
---

Open the check-up dashboard for this project.

1. If `$ARGUMENTS` contains `--export <file>`, run
   `python3 "${CLAUDE_PLUGIN_ROOT}/gui/serve.py" --dir . --export <file>` in the foreground, then tell the
   user the file works offline in any browser and can be sent to a partner or a bank. Stop here.
2. Otherwise start the server **in the background** (Bash with `run_in_background: true`):
   `python3 "${CLAUDE_PLUGIN_ROOT}/gui/serve.py" --dir . --open $ARGUMENTS`
   and read its first line for the address (it moves to the next free port if 8765 is taken).
3. Tell the user the address in one line, that the page updates by itself while the checker skills run,
   that it only reads `checker/` and never changes a file, and that `/checker-gui-stop` ends it.

If there is no `checker/` folder yet, still start it (the page says what to run first) and suggest
`/checker-intake`. To try it without a business: `python3 "${CLAUDE_PLUGIN_ROOT}/gui/demo.py" <empty folder>`.
