# 샤인영어 · 일간 학습 리포트

대구 수성구 **샤인영어**의 학생 일간 학습 리포트를 학부모님께 **앱 설치 없이 링크 하나로** 보내기 위한 정적 웹사이트입니다. GitHub Pages로 서비스됩니다.

- 사이트 주소: <https://loveinny7.github.io/shine-report/>
- 샘플 리포트: <https://loveinny7.github.io/shine-report/sample.html>

## 구성

```
index.html                     최근 리포트 목록 (build.py가 자동 생성)
sample.html                    샘플 리포트 — 김서준 · 동도중 · 중2 (가상 인물)
reports/                       학생별 리포트 페이지 (build.py가 생성)
assets/style.css               공용 디자인 (네이비 #1B2A4A · 골드 #C8A252)
templates/report.html          리포트 1장 템플릿
templates/index.html           목록 페이지 템플릿
data/*.json                    리포트 원본 데이터 — 여기만 고치면 됩니다
build.py                       JSON → HTML 빌드 스크립트 (파이썬 표준 라이브러리만 사용)
```

## 새 리포트 만드는 방법 (3단계)

1. `data/sample.json`을 복사해 이름을 바꿉니다.
   ```
   cp data/sample.json data/2026-11-28-kimseojun.json
   ```
2. 파일 안의 값을 고칩니다.

   | 항목 | 설명 |
   | --- | --- |
   | `id` | 파일 식별자 (영문·숫자·하이픈) |
   | `output` | 생성될 페이지 경로. 생략하면 `reports/{id}.html` |
   | `date` | `2026-11-28` 형식 |
   | `badge` | 상단 상태 배지. `tone`: `gold` / `soft` / `mint` |
   | `student` | `name`, `school`, `grade`, `initial`(동그라미 안 글자) |
   | `summary` | 목록에 보이는 한 줄 요약 |
   | `lessons` | 오늘 수업 (`book`, `detail`, `tags`) |
   | `next_class` | 다음 시간 예고 (없으면 생략) |
   | `homework` | 숙제 체크리스트 (`task`, `done`, `note`) |
   | `tests` | 테스트 타일 (`value`, `unit`, `label`, `note`) |
   | `note` | 선생님 한마디 (`lead`, `body`, `name`, `sub`) |
   | `listed` | `false`면 목록(index)에 노출하지 않음 |

3. 빌드하고 확인한 뒤 올립니다.
   ```
   python3 build.py
   git add -A && git commit -m "2026-11-28 김서준 리포트" && git push
   ```

`index.html`은 `data/*.json` 전체를 읽어 날짜 최신순으로 자동 갱신되므로, 목록은 따로 손대지 않아도 됩니다.

특정 리포트만 다시 만들 때:

```
python3 build.py data/2026-11-28-kimseojun.json   # 해당 페이지만 재생성 (index는 항상 갱신)
```

## 디자인 규칙

- 모바일 우선: 최대 폭 480px, 카드 레이아웃. 학부모님이 카카오톡으로 받은 링크를 폰에서 바로 여는 상황을 기준으로 만들었습니다.
- 색: 네이비 `#1B2A4A` / 골드 `#C8A252` / 크림 `#F7F4EE`
- 글꼴: Pretendard (CDN) → Noto Sans KR → 시스템 한글 글꼴 순서로 대체
- 인쇄(PDF 저장)용 스타일 포함: 브라우저에서 `Ctrl+P` → PDF로 저장하면 A4 한 장으로 정리됩니다.

## 주의

- 이 저장소는 **공개(public)** 입니다. 링크를 아는 사람은 누구나 볼 수 있습니다.
- 학생 실명·학교가 인터넷에 노출되므로, 실제 리포트를 올릴 때는 다음을 권합니다.
  - 이름은 `김OO`처럼 일부 가림, 또는 학생별 임의 ID 사용
  - 전화번호·집주소·상담 내용 등 민감정보는 페이지에 넣지 않기
  - 필요하면 저장소를 Private으로 전환하고 GitHub Pages 접근 제한을 검토

## 배포

`main` 브랜치 루트를 그대로 GitHub Pages로 서비스합니다. `.nojekyll` 파일이 있어 Jekyll 처리를 거치지 않습니다.
