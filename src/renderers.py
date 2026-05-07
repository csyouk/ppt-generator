"""
Mermaid 다이어그램 / Markdown 테이블을 PNG로 렌더링.

- Mermaid: mmdc (mermaid-cli) 사용 (Node.js 필요)
- Markdown Table: Playwright + HTML/CSS 사용 (디자인 토큰 적용)

두 렌더러 모두 디자인 토큰을 주입받아 결과물의 색/폰트가
슬라이드 전체와 일관되게 나옵니다.
"""

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

from .design import Theme


# ─────────────────────────────────────────────────────────
# 캐시 — 같은 입력은 다시 렌더링하지 않음
# ─────────────────────────────────────────────────────────


def _cache_key(content: str, theme_signature: str, kind: str) -> str:
    h = hashlib.sha256()
    h.update(kind.encode())
    h.update(b"|")
    h.update(theme_signature.encode())
    h.update(b"|")
    h.update(content.encode())
    return h.hexdigest()[:16]


def _theme_signature(theme: Theme) -> str:
    """테마가 바뀌면 캐시 무효화"""
    c = theme.colors
    return f"{c.primary}{c.accent}{c.ink}{c.paper}{theme.fonts.heading}{theme.fonts.body}"


# ─────────────────────────────────────────────────────────
# Mermaid → PNG (mmdc)
# ─────────────────────────────────────────────────────────


def _mermaid_config(theme: Theme) -> dict:
    """mermaid에 디자인 토큰 주입"""
    c = theme.colors
    return {
        "theme": "base",
        "themeVariables": {
            "primaryColor": f"#{c.secondary}",
            "primaryTextColor": f"#{c.ink}",
            "primaryBorderColor": f"#{c.primary}",
            "lineColor": f"#{c.primary}",
            "secondaryColor": f"#{c.paper}",
            "tertiaryColor": f"#{c.paper}",
            "fontFamily": theme.fonts.body,
            "fontSize": "16px",
        },
    }


def render_mermaid(code: str, theme: Theme, cache_dir: Path) -> Path:
    """
    Mermaid 코드를 PNG로 렌더링하고 경로를 반환.
    같은 입력은 캐시에서 즉시 반환.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(code, _theme_signature(theme), "mermaid")
    out = cache_dir / f"mermaid_{key}.png"
    if out.exists():
        return out

    if not shutil.which("mmdc"):
        raise RuntimeError(
            "mmdc(mermaid-cli)가 설치되어 있지 않습니다.\n"
            "  npm install -g @mermaid-js/mermaid-cli"
        )

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        mmd = tdp / "in.mmd"
        cfg = tdp / "config.json"
        mmd.write_text(code, encoding="utf-8")
        cfg.write_text(json.dumps(_mermaid_config(theme)), encoding="utf-8")

        # 고해상도 출력 (PPT용)
        cmd = [
            "mmdc",
            "-i", str(mmd),
            "-o", str(out),
            "-c", str(cfg),
            "-b", f"#{theme.colors.paper}",
            "-w", "1600",  # 충분히 큰 폭
        ]
        # 환경변수로 puppeteer 설정 파일 지정 가능
        import os
        puppeteer_cfg = os.environ.get("PUPPETEER_CONFIG_FILE")
        if puppeteer_cfg:
            cmd.extend(["-p", puppeteer_cfg])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Mermaid 렌더링 실패:\n{result.stderr}")

    return out


# ─────────────────────────────────────────────────────────
# Markdown Table → PNG (Playwright)
# ─────────────────────────────────────────────────────────


def _table_html(md_table: str, theme: Theme) -> str:
    """markdown 테이블을 디자인 토큰 적용된 HTML로 변환"""
    html_table = markdown.markdown(md_table, extensions=["tables"])

    c = theme.colors
    f = theme.fonts
    css = f"""
    <style>
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        padding: 24px;
        font-family: '{f.body}', -apple-system, sans-serif;
        background: #{c.paper};
        color: #{c.ink};
      }}
      table {{
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 16px;
        line-height: 1.5;
      }}
      thead th {{
        background: #{c.primary};
        color: #{c.on_primary};
        font-family: '{f.heading}', -apple-system, sans-serif;
        font-weight: 600;
        text-align: left;
        padding: 14px 16px;
        border-bottom: 2px solid #{c.primary};
      }}
      thead th:first-child {{ border-top-left-radius: 8px; }}
      thead th:last-child {{ border-top-right-radius: 8px; }}
      tbody td {{
        padding: 12px 16px;
        border-bottom: 1px solid #{c.border};
        vertical-align: top;
      }}
      tbody tr:nth-child(even) td {{
        background: #{c.secondary};
      }}
      tbody tr:last-child td:first-child {{ border-bottom-left-radius: 8px; }}
      tbody tr:last-child td:last-child {{ border-bottom-right-radius: 8px; }}
      code {{
        font-family: '{f.mono}', monospace;
        background: #{c.secondary};
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 14px;
      }}
      strong {{ color: #{c.primary}; }}
    </style>
    """
    return f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body>{html_table}</body></html>"


def render_table(md_table: str, theme: Theme, cache_dir: Path) -> Path:
    """Markdown 테이블 → PNG"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(md_table, _theme_signature(theme), "table")
    out = cache_dir / f"table_{key}.png"
    if out.exists():
        return out

    html = _table_html(md_table, theme)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 200},
            device_scale_factor=2,  # retina 품질
        )
        page = ctx.new_page()
        page.set_content(html, wait_until="networkidle")
        # body 크기에 맞춰 캡쳐
        body = page.locator("body")
        body.screenshot(path=str(out), omit_background=False)
        browser.close()

    return out


# ─────────────────────────────────────────────────────────
# Code → PNG (옵션 — code 슬라이드에서 syntax highlight하고 싶을 때)
# ─────────────────────────────────────────────────────────


def render_code(code: str, language: str, theme: Theme, cache_dir: Path) -> Path:
    """코드를 syntax highlight된 PNG로 렌더링"""
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, guess_lexer

    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(f"{language}|{code}", _theme_signature(theme), "code")
    out = cache_dir / f"code_{key}.png"
    if out.exists():
        return out

    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        try:
            lexer = guess_lexer(code)
        except Exception:
            lexer = get_lexer_by_name("text")

    formatter = HtmlFormatter(style="github-dark", noclasses=True, nobackground=False)
    code_html = highlight(code, lexer, formatter)

    f = theme.fonts
    c = theme.colors
    html = f"""<!doctype html><html><head><meta charset='utf-8'>
    <style>
      body {{ margin:0; padding:24px; background:#0d1117; }}
      .highlight {{
        font-family: '{f.mono}', monospace;
        font-size: 15px;
        line-height: 1.55;
        border-radius: 8px;
        padding: 18px 22px;
      }}
      .highlight pre {{ margin: 0; }}
    </style></head><body>{code_html}</body></html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1400, "height": 200}, device_scale_factor=2
        )
        page = ctx.new_page()
        page.set_content(html, wait_until="networkidle")
        page.locator("body").screenshot(path=str(out))
        browser.close()

    return out
