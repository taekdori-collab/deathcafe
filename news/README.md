# 웰다잉 뉴스 위클리 데이터

자료실 > 웰다잉 뉴스 탭이 이 폴더의 JSON을 읽어 화면에 보여줍니다.

## 흐름
1. 매주 토요일 아침 예약 작업이 초안을 `news/drafts/YYYY-MM-DD.json`(초안 작성일)으로 올립니다.
   - 미리보기: `https://deathcafe.co.kr/library.html#draft-YYYY-MM-DD` (메뉴에 노출되지 않음)
2. 운영자(차준택)가 검토 후 "게시해줘"라고 요청하면:
   - 수정 사항 반영
   - 파일을 `news/YYYY-MM-DD.json`으로 옮기고 drafts의 파일은 삭제
   - `news/index.json`의 `issues` 배열 **맨 앞**에 요약 항목 추가
   - `python3 tools/build.py` 실행 → `news/YYYY-MM-DD.html` 개별 페이지, `sitemap.xml`, `rss.xml` 갱신
     (실행을 잊어도 GitHub Actions가 push 직후 자동으로 만들어 줍니다)
   - 게시 주소: `https://deathcafe.co.kr/news/YYYY-MM-DD.html`
     (예전 주소 `library.html#news-YYYY-MM-DD`는 새 주소로 자동 이동)

## 호 파일 형식 (`news/YYYY-MM-DD.json`)
```json
{
  "id": "2026-10-10",
  "no": 1,
  "title": "웰다잉 뉴스 위클리 제1호",
  "range": "2026. 10. 3. ~ 10. 9.",
  "date": "2026. 10. 10.",
  "sum": "목록에 보일 한 줄 요약 (이번 주 흐름)",
  "lead": "여는 말 2~3문장",
  "care": false,
  "items": [
    {
      "f": 2,
      "headline": "직접 쓴 제목",
      "summary": "직접 쓴 요약 2~3문장 (원문 문장 복사 금지)",
      "source": "언론사명",
      "sourceDate": "2026. 10. 7.",
      "url": "https://원문주소",
      "comment": "차준택의 시선 1~2문장"
    }
  ]
}
```
- `f`: 강의 분야 번호 — 0 왜 죽음학인가, 1 죽음과 죽어감, 2 생애말기와 연명의료, 3 죽음준비
- `care`: 자살·고독사 등 민감 기사가 포함되면 `true` (109 상담전화 안내가 붙음)
- `no`: 게시된 호 기준 일련번호 (index.json의 가장 큰 no + 1)

## index.json 항목 형식
```json
{ "id": "2026-10-10", "no": 1, "title": "...", "range": "...", "sum": "..." }
```

## 검색 노출 (2026-10-10 추가)
- 자료실 자료 1건 = `library/<id>.html`, 뉴스 1호 = `news/<id>.html` 페이지가 `tools/build.py`로 생성됩니다.
- 생성된 HTML은 직접 고치지 마세요. 원본(구글 시트, news/*.json)을 고친 뒤 다시 생성합니다.
- 홈페이지 `index.html`의 `google-site-verification`, `naver-site-verification` 태그와
  `robots.txt`의 다음(Daum) 인증 줄은 검색엔진 소유확인용이므로 지우지 마세요.
