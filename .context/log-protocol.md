### Standard Log Template

Add front to `log/agent-log.md` after each interaction:

**CRITICAL**: You must first read the log file to find the first entry number and increment it. If the file is empty or no number is found, start with `1`.

```markdown
---

## Log Entry: [N]

### User Request
[The full, verbatim text of the user's most recent prompt goes here]

### Response Summary
[A concise, one-paragraph summary of the response you provided to the user]

### Actions Taken
- **File:** `path/to/file.py`
  - **Change:** [Description of what was changed]
  - **Reason:** [Why this change was necessary]
- **File:** `path/to/another/file.py`
  - **Change:** [Description of what was changed]
  - **Reason:** [Why this change was necessary]

[If no files were modified, state: "No files were modified for this request."]

---
```