"""
디자인 시스템 — 모든 시각 토큰의 단일 진실 공급원(SSOT).

핵심 원칙:
- 모든 슬라이드는 여기서 정의한 토큰만 사용한다.
- 슬라이드 레이아웃 코드에는 어떤 색/크기/폰트도 하드코딩하지 않는다.
- 사용자가 config.yaml의 primary 컬러 하나만 바꿔도 전체가 자동 조화된다.
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pptx.util import Inches, Pt


# ─────────────────────────────────────────────────────────
# 컬러 유틸 — primary 컬러로부터 보조 컬러 자동 생성
# ─────────────────────────────────────────────────────────


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "{:02X}{:02X}{:02X}".format(*rgb)


def lighten(hex_color: str, ratio: float) -> str:
    """ratio (0~1)만큼 흰색에 섞기"""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * ratio)
    g = int(g + (255 - g) * ratio)
    b = int(b + (255 - b) * ratio)
    return rgb_to_hex((r, g, b))


def darken(hex_color: str, ratio: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - ratio))
    g = int(g * (1 - ratio))
    b = int(b * (1 - ratio))
    return rgb_to_hex((r, g, b))


def luminance(hex_color: str) -> float:
    """간이 luminance — 가독성 판단용"""
    r, g, b = hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


# ─────────────────────────────────────────────────────────
# 디자인 토큰
# ─────────────────────────────────────────────────────────


@dataclass
class Colors:
    primary: str       # 메인 — 다크 배경, 헤딩
    accent: str        # 포인트 — 불릿, 강조
    secondary: str     # primary의 옅은 버전 (배경 강조 영역용)
    ink: str           # 본문 텍스트 (거의 검정)
    paper: str         # 배경 (거의 흰색)
    muted: str         # 부연/캡션 (회색)
    border: str        # 구분선
    on_primary: str    # primary 배경 위 텍스트 색 (자동 결정)


@dataclass
class Fonts:
    heading: str
    body: str
    mono: str


@dataclass
class Sizes:
    """폰트 크기 (Pt)"""
    title_xl: int = 44   # 표지 타이틀
    title_lg: int = 36   # 일반 슬라이드 타이틀
    title_md: int = 28   # 섹션 헤더
    body_lg: int = 20    # 큰 본문
    body: int = 16       # 일반 본문
    body_sm: int = 14    # 작은 본문
    caption: int = 11    # 캡션/footer
    eyebrow: int = 12    # eyebrow 라벨


@dataclass
class Layout:
    """레이아웃 좌표 (Inches)"""
    slide_w: float = 13.333
    slide_h: float = 7.5
    margin_x: float = 0.7
    margin_y: float = 0.5
    title_y: float = 0.55
    title_h: float = 0.9
    content_y: float = 1.95
    content_h: float = 4.8
    footer_y: float = 7.05
    footer_h: float = 0.3


@dataclass
class Theme:
    colors: Colors
    fonts: Fonts
    sizes: Sizes = field(default_factory=Sizes)
    layout: Layout = field(default_factory=Layout)
    brand_name: str = ""
    show_page_numbers: bool = True
    show_footer: bool = True


# ─────────────────────────────────────────────────────────
# config.yaml → Theme
# ─────────────────────────────────────────────────────────


def load_theme(config_path: str | Path) -> Theme:
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    brand = cfg.get("brand", {})
    primary = brand.get("primary", "#1E2761").lstrip("#")
    accent = brand.get("accent", "#F96167").lstrip("#")

    # 자동 보정: 사용자가 안 줬으면 primary 기반으로 생성
    secondary = brand.get("secondary", f"#{lighten(primary, 0.85)}").lstrip("#")
    ink = brand.get("ink", "#1A1A1A").lstrip("#")
    paper = brand.get("paper", "#FFFFFF").lstrip("#")
    muted = brand.get("muted", "#6B7280").lstrip("#")
    border = brand.get("border", "#E5E7EB").lstrip("#")

    # primary 위 텍스트 색은 luminance에 따라 자동 결정
    on_primary = "FFFFFF" if luminance(primary) < 0.55 else "1A1A1A"

    colors = Colors(
        primary=primary,
        accent=accent,
        secondary=secondary,
        ink=ink,
        paper=paper,
        muted=muted,
        border=border,
        on_primary=on_primary,
    )

    fonts_cfg = cfg.get("fonts", {})
    fonts = Fonts(
        heading=fonts_cfg.get("heading", "맑은 고딕"),
        body=fonts_cfg.get("body", "맑은 고딕"),
        mono=fonts_cfg.get("mono", "Consolas"),
    )

    slide_cfg = cfg.get("slide", {})
    layout = Layout(
        slide_w=slide_cfg.get("width_inches", 13.333),
        slide_h=slide_cfg.get("height_inches", 7.5),
    )

    return Theme(
        colors=colors,
        fonts=fonts,
        layout=layout,
        brand_name=brand.get("name", ""),
        show_page_numbers=cfg.get("show_page_numbers", True),
        show_footer=cfg.get("show_footer", True),
    )
