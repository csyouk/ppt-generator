"""
Slide JSON Schema — 슬라이드의 종류와 구조를 고정합니다.

LLM이 만드는 JSON은 반드시 이 스키마를 따라야 하며,
빌더는 이 스키마 외의 입력을 거부합니다.
이게 디자인 일관성의 핵심입니다.
"""

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# 6가지 슬라이드 타입만 허용 (이게 일관성의 근원)
# ─────────────────────────────────────────────────────────


class TitleSlide(BaseModel):
    """표지/섹션 타이틀 슬라이드"""

    type: Literal["title"]
    title: str
    subtitle: str | None = None
    eyebrow: str | None = None  # 상단 작은 라벨 (예: "Day 1 / Session 3")


class SectionSlide(BaseModel):
    """섹션 구분 슬라이드 (다크 배경)"""

    type: Literal["section"]
    section_number: str  # 예: "01", "Part 1"
    title: str
    description: str | None = None


class ContentSlide(BaseModel):
    """일반 컨텐츠 슬라이드 — 제목 + 본문 (글머리 또는 단락)"""

    type: Literal["content"]
    title: str
    subtitle: str | None = None
    bullets: list[str] | None = None  # 글머리 항목
    paragraph: str | None = None  # 단락 텍스트 (bullets와 둘 중 하나)
    footer_note: str | None = None  # 하단 부연


class TwoColumnSlide(BaseModel):
    """2단 비교 슬라이드"""

    type: Literal["two_column"]
    title: str
    left_heading: str
    left_bullets: list[str]
    right_heading: str
    right_bullets: list[str]


class TableSlide(BaseModel):
    """Markdown 테이블 슬라이드 (이미지로 렌더링됨)"""

    type: Literal["table"]
    title: str
    subtitle: str | None = None
    markdown_table: str  # 표준 markdown 테이블 문법
    caption: str | None = None


class DiagramSlide(BaseModel):
    """Mermaid 다이어그램 슬라이드 (이미지로 렌더링됨)"""

    type: Literal["diagram"]
    title: str
    subtitle: str | None = None
    mermaid_code: str  # mermaid 코드 (graph TD / sequenceDiagram 등)
    caption: str | None = None


class CodeSlide(BaseModel):
    """코드 블록 슬라이드"""

    type: Literal["code"]
    title: str
    subtitle: str | None = None
    language: str = "python"
    code: str
    caption: str | None = None


class QuoteSlide(BaseModel):
    """강조 인용/명언 슬라이드"""

    type: Literal["quote"]
    quote: str
    attribution: str | None = None


class StatCalloutSlide(BaseModel):
    """큰 숫자/통계 강조 슬라이드 — 1~3개 stat을 나란히"""

    type: Literal["stat_callout"]
    title: str
    subtitle: str | None = None
    stats: list["Stat"]
    footer_note: str | None = None


class Stat(BaseModel):
    value: str         # 예: "16시간", "300+", "85%"
    label: str         # 예: "총 교육 시간"
    description: str | None = None  # 한 줄 부연 (선택)


class ImageTextSlide(BaseModel):
    """이미지(또는 스크린샷) + 텍스트 — 좌우 분할"""

    type: Literal["image_text"]
    title: str
    subtitle: str | None = None
    image_path: str    # 사용자가 제공한 이미지 파일 경로 (assets/ 또는 절대경로)
    image_side: Literal["left", "right"] = "right"
    bullets: list[str] | None = None
    paragraph: str | None = None
    caption: str | None = None


class StepsSlide(BaseModel):
    """단계별 흐름 — 번호 매긴 단계들 (3~5개)"""

    type: Literal["steps"]
    title: str
    subtitle: str | None = None
    steps: list["Step"]
    footer_note: str | None = None


class Step(BaseModel):
    title: str         # 단계 제목 (짧게)
    description: str   # 단계 설명 (1~2문장)


# 순환참조 해결
StatCalloutSlide.model_rebuild()
StepsSlide.model_rebuild()


# ─────────────────────────────────────────────────────────
# 슬라이드 유니온 타입
# ─────────────────────────────────────────────────────────

Slide = Annotated[
    Union[
        TitleSlide,
        SectionSlide,
        ContentSlide,
        TwoColumnSlide,
        TableSlide,
        DiagramSlide,
        CodeSlide,
        QuoteSlide,
        StatCalloutSlide,
        ImageTextSlide,
        StepsSlide,
    ],
    Field(discriminator="type"),
]


class Deck(BaseModel):
    """전체 프레젠테이션"""

    title: str
    author: str | None = None
    slides: list[Slide]


def load_deck(json_path: str) -> Deck:
    """JSON 파일 → Deck 객체 (스키마 검증 포함)"""
    import json

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    return Deck.model_validate(data)
