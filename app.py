"""Gradio UI: natural language in, CLI command out."""
import gradio as gr

from agent import DEFAULT_OS, list_versions, nl_to_cli
from safety import parse


def run(text: str, version: str, os_name: str):
    if not text.strip():
        return "", "—"
    try:
        out = nl_to_cli(text, version, os_name)
    except Exception as e:
        return f"ERROR: {e}", "❌ API error"
    status, cmd = parse(out)
    label = {
        "command": "✅ safe command",
        "confirm": "⚠️ requires user confirmation before running",
        "refused": "⛔ refused",
    }[status]
    return out, label


with gr.Blocks(title="NL → CLI agent") as demo:
    gr.Markdown("## Natural language → CLI command")
    with gr.Row():
        version = gr.Dropdown(list_versions(), value=list_versions()[-1], label="Prompt version")
        os_name = gr.Textbox(value=DEFAULT_OS, label="Target OS / shell")
    inp = gr.Textbox(label="Instruction (Hebrew or English)", lines=3, rtl=True)
    btn = gr.Button("Convert")
    out = gr.Textbox(label="Output", interactive=False)
    status = gr.Textbox(label="Safety status", interactive=False)
    btn.click(run, [inp, version, os_name], [out, status])
    inp.submit(run, [inp, version, os_name], [out, status])

if __name__ == "__main__":
    demo.launch()
