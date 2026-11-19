"""Natural language -> CLI command, using a versioned system prompt."""
import json
import os
from pathlib import Path
import ssl
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = Path(__file__).parent / "prompts"
MODEL = os.getenv("CLI_AGENT_MODEL", "llama-3.3-70b-versatile")
DEFAULT_OS = os.getenv("CLI_AGENT_OS", "macOS (zsh)")


def list_versions() -> list[str]:
    return sorted(p.stem for p in PROMPTS_DIR.glob("v*.txt"))


def load_prompt(version: str, os_name: str = DEFAULT_OS) -> str:
    text = (PROMPTS_DIR / f"{version}.txt").read_text(encoding="utf-8")
    return text.replace("{OS}", os_name)


def nl_to_cli(text: str, version: str = "v1", os_name: str = DEFAULT_OS) -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in .env")

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": load_prompt(version, os_name)},
            {"role": "user", "content": text},
        ],
        "temperature": 0,
        "max_tokens": 300,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "cli-agent/1.0",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    time.sleep(0.5)

    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < 3:
                wait = 5 * (attempt + 1)
                time.sleep(wait)
                continue
            raise RuntimeError(f"Groq HTTP {e.code}: {body}") from e

    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return (message.get("content") or "").strip()