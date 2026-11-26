---
description: Stop the founder-id-checker dashboard for this project (every checker/ file is left as it is)
allowed-tools: Bash(python3:*)
---

Run `python3 "${CLAUDE_PLUGIN_ROOT}/gui/serve.py" --dir . --stop` and tell the user, in one line, what
it printed. Nothing in `checker/` is changed.
