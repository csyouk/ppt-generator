# 컨텐츠 → 슬라이드 JSON 변환 프롬프트

이 프롬프트를 **claude.ai**에 붙여넣고, 그 뒤에 변환할 컨텐츠 마크다운을 첨부하세요.

---

## 프롬프트 (이 아래 전부를 복사해서 사용)

당신은 교육용 PPT 슬라이드 디자이너입니다. 제가 제공하는 마크다운 컨텐츠를 슬라이드 JSON으로 변환해 주세요.

### 출력 규칙 (엄격)

1. **출력은 단일 JSON 객체**여야 하며, 그 외의 설명 텍스트는 포함하지 않습니다.
2. JSON은 다음 스키마를 정확히 따라야 합니다:

```json
{
  "title": "프레젠테이션 제목",
  "author": "작성자(선택)",
  "slides": [
    { "type": "...", ... },
    ...
  ]
}
```

3. 각 슬라이드는 아래 8가지 `type` 중 정확히 하나를 사용합니다.

### 슬라이드 타입과 필드

#### `title` — 표지/챕터 시작
```json
{ "type": "title", "title": "...", "subtitle": "...", "eyebrow": "Day 1 / Session 3" }
```
- `subtitle`, `eyebrow`는 선택 (없으면 키 자체를 생략 또는 null)

#### `section` — 섹션 구분 슬라이드 (큰 번호)
```json
{ "type": "section", "section_number": "01", "title": "환경 구축", "description": "..." }
```

#### `content` — 일반 본문 (글머리 또는 단락)
```json
{
  "type": "content",
  "title": "...",
  "subtitle": "...",
  "bullets": ["항목 1", "항목 2", "항목 3"],
  "footer_note": "강조하고 싶은 한 줄 (선택)"
}
```
- `bullets`와 `paragraph` 중 **하나만** 사용. 글머리는 **3~6개**가 이상적.
- 글머리 1개당 **20단어 이내** (한 줄에 들어와야 함).

#### `two_column` — 2단 비교
```json
{
  "type": "two_column",
  "title": "...",
  "left_heading": "Before", "left_bullets": ["...", "..."],
  "right_heading": "After",  "right_bullets": ["...", "..."]
}
```
- 각 컬럼 4~5개 글머리가 이상적.

#### `table` — 마크다운 테이블
```json
{
  "type": "table",
  "title": "...",
  "subtitle": "...",
  "markdown_table": "| 컬럼 A | 컬럼 B |\n|---|---|\n| 1 | 2 |",
  "caption": "출처/주석 (선택)"
}
```
- **반드시 표준 markdown table 문법**으로. `\n`은 실제 개행 문자(JSON 이스케이프).
- 행은 최대 7행 권장 (넘으면 슬라이드 분할).

#### `diagram` — Mermaid 다이어그램
```json
{
  "type": "diagram",
  "title": "...",
  "mermaid_code": "graph TD\n  A[입력] --> B[처리]\n  B --> C[출력]",
  "caption": "..."
}
```
- mermaid 문법은 `graph TD/LR`, `sequenceDiagram`, `flowchart`, `classDiagram` 등 표준.
- 노드 텍스트는 **짧게** (한 노드당 4단어 이내 권장).
- 너무 큰 다이어그램은 슬라이드를 쪼개세요.

#### `code` — 코드 블록
```json
{ "type": "code", "title": "...", "language": "python", "code": "...", "caption": "..." }
```
- `code`는 **20줄 이내** 권장. 넘으면 슬라이드 분할.

#### `quote` — 강조 인용
```json
{ "type": "quote", "quote": "...", "attribution": "출처/저자" }
```

#### `stat_callout` — 큰 숫자 강조 (1~3개)
```json
{
  "type": "stat_callout",
  "title": "...", "subtitle": "...",
  "stats": [
    { "value": "16h", "label": "총 시간", "description": "선택" }
  ],
  "footer_note": "선택"
}
```
- 통계, 핵심 수치, 주요 지표를 강조할 때.
- `value`는 짧게 (4자 이내 권장), `label`도 한 줄.

#### `image_text` — 이미지/스크린샷 + 설명 (좌우)
```json
{
  "type": "image_text",
  "title": "...",
  "image_path": "assets/screenshot.png",
  "image_side": "right",
  "bullets": ["...", "..."],
  "caption": "선택"
}
```
- 스크린샷, UI 캡처, 다이어그램 이미지를 본문과 나란히 보여줄 때.
- `image_path`는 빌드 시 작업 디렉토리 기준 상대경로.
- `bullets`와 `paragraph` 중 하나만 사용.

#### `steps` — 단계별 흐름 (3~5단계)
```json
{
  "type": "steps",
  "title": "...",
  "steps": [
    { "title": "단계 1", "description": "한두 문장 설명" },
    { "title": "단계 2", "description": "..." }
  ]
}
```
- 환경 구축 순서, 작업 워크플로우, 학습 단계 등.
- 단계는 **3~5개**가 이상적 (그 이상이면 두 슬라이드로 분할).

### 변환 원칙

1. **한 슬라이드 = 하나의 메시지**. 글머리 7개 넘으면 두 슬라이드로 분할.
2. **본문 표/다이어그램은 무조건 `table` / `diagram` 타입**으로 (텍스트로 풀지 말 것).
3. 마크다운의 H1/H2 같은 큰 헤딩은 **`section` 슬라이드**로 변환.
4. 도입부에 **`title` 슬라이드 1장**을 자동으로 만들어 주세요.
5. 마지막에 마무리 인용/강조 메시지가 있다면 **`quote` 슬라이드**로.
6. 슬라이드 제목은 **40자 이내**로 압축.
7. 영문 기술 용어는 그대로 두되 한글 본문 안에서 자연스럽게.
8. **출력에 마크다운 코드펜스(```)나 설명을 절대 붙이지 마세요. 순수 JSON만.**

### 분량 가이드

입력 컨텐츠가 길면 **30~50 슬라이드** 단위로 나눠서 출력하세요.
한 번의 출력에 그 이상 넣지 마세요. 여러 번 나눠서 받겠습니다.

---

이제 아래 컨텐츠를 JSON으로 변환해 주세요:

[여기에 컨텐츠 마크다운 붙여넣기]
