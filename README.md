# PPT Builder — 디자인 일관성 보장 PPT 생성 파이프라인

300페이지 규모의 PPT 교안을 디자인 일관성을 유지하며 만들기 위한 도구.
**컨텐츠 작성에만 집중**하고, 변환·디자인은 자동화하는 워크플로우.

## 핵심 아이디어

- LLM은 **컨텐츠 → 슬라이드 JSON**까지만 담당
- **JSON → PPTX**는 결정론적 코드가 처리
- 디자인 토큰(컬러, 폰트, 레이아웃)은 한 곳(`config.yaml`)에서 관리
- 같은 타입의 슬라이드는 같은 함수를 거치므로 픽셀 단위로 일관

## 워크플로우

```
[1] content.md 작성
        ↓
[2] claude.ai에서 prompts/slide_json_prompt.md 사용해 JSON 변환
    (긴 컨텐츠는 챕터별로 나눠서 chapter1.json, chapter2.json ...)
        ↓
[3] python -m src.build -i chapter*.json -o output.pptx
        ↓
    output.pptx 완성
```

## 설치

### 시스템 요구사항

- Python 3.10+
- Node.js 18+ (mermaid CLI용)
- Playwright용 Chromium

### 설치 명령

```bash
# 1) Python 패키지
pip install python-pptx pydantic pyyaml markdown playwright pillow pygments
playwright install chromium

# 2) Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
```

### 한글 폰트

`config.yaml`의 `fonts.heading`/`fonts.body`에 시스템에 설치된 폰트명을 적어주세요.
Pretendard, 맑은 고딕, Noto Sans KR 등.

## 사용법

### 1. 브랜드 설정

`config.yaml` 편집 — primary 컬러 하나만 정해도 나머지는 자동 보정됩니다:

```yaml
brand:
  name: "비개발자 웹+AI 교육"
  primary: "#1E2761"
  accent: "#F96167"
fonts:
  heading: "Pretendard"
  body: "Pretendard"
```

### 2. 컨텐츠 → JSON 변환 (수동)

1. `prompts/slide_json_prompt.md`의 내용을 복사
2. claude.ai 새 채팅에 붙여넣기
3. 그 뒤에 변환할 마크다운 컨텐츠 첨부
4. 받은 JSON을 `chapters/01_intro.json` 같이 저장
5. 챕터별로 반복 (한 번에 30~50 슬라이드 권장)

### 3. PPTX 빌드

```bash
# 단일 파일
python -m src.build -i examples/input.json -o output.pptx

# 여러 파일 병합 (300페이지짜리도 OK)
python -m src.build \
    -i chapters/01_intro.json \
       chapters/02_setup.json \
       chapters/03_implementation.json \
    -o full_deck.pptx
```

## 슬라이드 타입 (11가지)

JSON 변환 시 LLM이 사용할 수 있는 슬라이드 타입은 정확히 11가지로 제한됩니다:

| 타입 | 용도 |
|------|------|
| `title` | 표지/챕터 시작 (다크 배경) |
| `section` | 섹션 구분 (큰 번호 + 제목) |
| `content` | 일반 본문 (글머리/단락) |
| `two_column` | 2단 비교 (Before/After 등) |
| `table` | 마크다운 테이블 (이미지 렌더링) |
| `diagram` | Mermaid 다이어그램 (이미지 렌더링) |
| `code` | 코드 블록 (syntax highlight) |
| `quote` | 강조 인용 |
| `stat_callout` | 큰 숫자 강조 (1~3개 stat) |
| `image_text` | 이미지/스크린샷 + 설명 (좌우 분할) |
| `steps` | 단계별 흐름 (3~5단계) |

이 제약이 디자인 일관성의 근원입니다. 새로운 레이아웃이 필요하면
`src/layouts.py`와 `src/schema.py`에 한 번 정의하면 모든 슬라이드에 적용됩니다.

## 디자인 일관성을 보장하는 4가지 장치

1. **단일 진실 공급원**: 모든 색/폰트/크기는 `src/design.py`의 `Theme`에서만 옴
2. **타입 제한**: 8가지 슬라이드 타입 외에는 빌더가 거부
3. **자동 보정**: primary 컬러 하나에서 secondary/on_primary 자동 생성
4. **렌더러 통합**: Mermaid/Table도 같은 `Theme`을 받아 색·폰트가 슬라이드와 일치

## 캐싱

같은 mermaid/table은 다시 렌더링하지 않습니다 (`.cache/` 디렉토리).
컨텐츠 일부만 수정해서 다시 빌드해도 빠릅니다.

## 디자인 변경

- 컬러만 바꾸기: `config.yaml`의 `primary`/`accent` 수정
- 새 슬라이드 타입 추가: `schema.py`에 모델 추가 + `layouts.py`에 함수 추가
- 폰트 사이즈 일괄 조정: `design.py`의 `Sizes` 클래스 수정
- 페이지 번호 위치/스타일: `layouts.py`의 `_add_footer` 수정

## 트러블슈팅

**한글이 깨진다** → `config.yaml`의 폰트가 시스템에 설치되어 있는지 확인

**Mermaid 렌더링 실패** → `mmdc --version`으로 설치 확인. mermaid 코드 문법 오류일 수 있음

**테이블 잘림** → 행이 너무 많은 경우. JSON 변환 단계에서 슬라이드를 분할하도록 프롬프트에 지시

**디자인을 바꿨는데 적용 안 됨** → `.cache/` 디렉토리 삭제 후 다시 빌드

---

# UV 기반 실행 방법

## 최초 1회 설치

```bash
chmod +x setup.sh run.sh
./setup.sh
```

자동 수행:
- uv 설치 확인
- `.venv` 생성
- Python 패키지 설치
- Playwright Chromium 설치

---

## 실행

```bash
./run.sh
```

또는 직접:

```bash
source .venv/bin/activate
python src/build.py
```
