## slugify path traversal fix (2026-04-11)

### Pattern
- Added `text = text.replace("..", "")` to strip `..` sequences
- Placed after `re.sub(r"[^\w\s-]", "", text)` and before `re.sub(r"[-\s]+", "-", text)`
- Simple string replace is sufficient — no validation library needed

### Verification
- `slugify("../../etc/passwd")` → `'etcpasswd'` (no `..` or `/`)
- `slugify("AI-powered tool")` → `'ai-powered-tool'` (existing behavior preserved)
