# NL → CLI agent (prompt engineering exercise)

Converts a natural-language instruction (Hebrew/English) into a single terminal command.
The interesting part is the prompt: see `prompts/v1.txt` … `prompts/v4.txt`.

## Evaluation Results & Documentation
- **Google Sheet (`v1`–`v4`):** [View Evaluation Sheet](https://docs.google.com/spreadsheets/d/1A8b6Rm0SiCU7rmVBablQ2dwFnFu_jOjo/edit?usp=sharing&ouid=111381351575233781423&rtpof=true&sd=true)
- **Failures & Learnings:** See `FAILURES_AND_LEARNINGS.md` 

## Setup
```bash
uv sync
cat << 'EOF' > .env
GROQ_API_KEY="gsk_..."
CLI_AGENT_MODEL="openai/gpt-oss-20b"
CLI_AGENT_OS="macOS (zsh)"
EOF
uv run python app.py                 # Gradio UI
uv run python evaluate.py v1         # run all scenarios on a prompt version
uv run python make_workbook.py       # merge results/*.csv -> results/results.xlsx (import to Google Sheets)