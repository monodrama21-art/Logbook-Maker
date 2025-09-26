# Logbook Maker

PDF 문서에 페이지 번호와 사본관리 워터마크(Controlled Copy)를 손쉽게 추가할 수 있는 커맨드라인 도구입니다. 입력한 사본관리 번호가 각 페이지 상단에 표시되고, 페이지 하단에는 지정한 총 페이지 수에 맞춰 페이지 번호가 부여됩니다.

## 주요 기능

- 전체 혹은 지정한 페이지 수만큼 페이지 번호 부여
- 각 페이지마다 "Controlled Copy" 워터마크 추가
- 사본관리 번호(Copy No) 텍스트를 사용자 입력으로 표시
- 페이지/복사본 라벨 문구 커스터마이즈 가능

## 설치 방법

```bash
python -m pip install --upgrade pip
python -m pip install .[dev]
```

> 개발 환경이 아닌 경우에는 `.[dev]` 대신 `.` 만 설치하면 됩니다.

## 사용법

기본 사용 예시는 다음과 같습니다.

```bash
logbook-maker input.pdf output.pdf --copy-number "CC-2024-001"
```

### 자주 사용하는 옵션

- `--max-pages`: 처음부터 지정한 수만큼의 페이지만 워터마크 및 페이지 번호를 부여합니다. 나머지 페이지는 원본 그대로 복사됩니다.
- `--total-pages`: 페이지 번호에 표시될 전체 페이지 수를 직접 지정할 수 있습니다.
- `--start-number`: 시작 페이지 번호를 변경할 수 있습니다.
- `--watermark-text`: 워터마크 문구를 바꿀 수 있습니다.
- `--copy-label-template`: 사본관리 번호 라벨 포맷을 지정합니다. 예) `"사본번호: {copy_number}"`
- `--page-label-template`: 페이지 번호 라벨 포맷을 지정합니다. 예) `"{number} / {total} 페이지"`

### 파이썬 모듈에서 사용하기

```python
from logbook_maker import annotate_pdf

annotate_pdf(
    "input.pdf",
    "output.pdf",
    copy_number="CC-2024-001",
    total_pages=10,
)
```

## 개발 및 테스트

테스트 실행:

```bash
python -m pytest
```

## 주의 사항

- 워터마크 및 텍스트는 기본적으로 회색으로 적용되며, PDF 뷰어에 따라 투명도가 다르게 보일 수 있습니다.
- 입력 PDF는 암호화되어 있지 않아야 하며, 읽기 권한이 필요합니다.
