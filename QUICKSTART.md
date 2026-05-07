# 5분 QUICKSTART

처음 사용하는 분을 위한 단계별 가이드.

## 1. 의존성 설치 (한 번만)

```bash
# Python 패키지
pip install -r requirements.txt
playwright install chromium

# Node.js 패키지 (Mermaid 렌더링용)
npm install -g @mermaid-js/mermaid-cli
```

설치 확인:

```bash
python -c "import pptx, pydantic, playwright; print('OK')"
mmdc --version
```

## 2. 예시 빌드 (먼저 작동 확인)

```bash
python -m src.build -i examples/input.json -c config.yaml -o test.pptx
```

`test.pptx`가 생성되면 OK. 열어보고 디자인이 마음에 드는지 확인합니다.

## 3. 브랜드 컬러 변경

`config.yaml` 열어서 `primary` 컬러만 바꿔보세요:

```yaml
brand:
  name: "내 프로젝트"
  primary: "#2C5F2D"   # 원하는 컬러
  accent: "#F96167"
```

다시 빌드 (캐시 비우고):

```bash
rm -rf .cache
python -m src.build -i examples/input.json -c config.yaml -o test2.pptx
```

전체 슬라이드의 톤이 한 번에 바뀝니다.

## 4. 내 컨텐츠로 만들기

### Step 1. 마크다운으로 컨텐츠 작성

```markdown
# 1교시: 환경 구축

## 학습 목표
- Python과 Node.js의 차이 이해
- VS Code + Cline 설치
- 첫 프로젝트 폴더 구조 만들기

## 핵심 개념
- Python은 백엔드용, Node.js는 도구 실행용
- ...
```

### Step 2. claude.ai에서 JSON으로 변환

1. `prompts/slide_json_prompt.md` 파일 내용 전체 복사
2. claude.ai 새 채팅에 붙여넣기
3. 그 뒤에 위에서 작성한 마크다운 첨부 또는 붙여넣기
4. 받은 JSON을 `chapters/01.json`으로 저장

긴 컨텐츠는 챕터별로 나눠서 진행하세요. 한 번에 30~50 슬라이드가 적정.

### Step 3. PPTX 빌드

```bash
# 단일 파일
python -m src.build -i chapters/01.json -o day1.pptx

# 여러 챕터 병합 (300페이지 OK)
python -m src.build \
    -i chapters/01.json chapters/02.json chapters/03.json \
    -o day1_full.pptx
```

## 5. 자주 막히는 지점

### "한글이 깨져 보여요"

`config.yaml`의 `fonts.heading`/`fonts.body`가 시스템에 설치된 폰트인지 확인.
Windows라면 `맑은 고딕`, Mac이면 `Apple SD Gothic Neo`, Pretendard 추천.

### "Mermaid 슬라이드가 비어 있어요"

```bash
mmdc --version   # 설치 확인
```

설치 안 됐으면 `npm install -g @mermaid-js/mermaid-cli`. mermaid 코드 자체에 문법 오류가 있어도 실패할 수 있으니, 직접 [mermaid live editor](https://mermaid.live)에서 코드를 먼저 검증해보세요.

### "디자인 변경했는데 적용 안 돼요"

```bash
rm -rf .cache
```

mermaid/table은 같은 코드면 캐시에서 재사용됩니다. 디자인 변경 후엔 캐시를 비워야 합니다.

### "테이블 행이 너무 많아 잘려 보여요"

JSON 변환 단계에서 슬라이드를 분할하세요. 7행 넘으면 두 슬라이드로:

```json
{ "type": "table", "title": "전체 비교 (1/2)", ... },
{ "type": "table", "title": "전체 비교 (2/2)", ... }
```

### "image_text 슬라이드의 이미지가 안 보여요"

`image_path`는 빌드 명령을 실행한 디렉토리 기준의 상대경로 또는 절대경로여야 합니다.
`assets/screenshot.png`처럼 적었다면 프로젝트 루트의 `assets/` 폴더에 파일이 있어야 함.

## 6. 디자인 더 손보기

- **레이아웃 좌표 미세 조정**: `src/design.py`의 `Layout` 클래스
- **폰트 크기 일괄 조정**: `src/design.py`의 `Sizes` 클래스
- **새 슬라이드 타입 추가**: `src/schema.py`에 모델 → `src/layouts.py`에 함수 → `render_slide`에 분기
- **mermaid 스타일**: `src/renderers.py`의 `_mermaid_config`
- **테이블 스타일**: `src/renderers.py`의 `_table_html`
