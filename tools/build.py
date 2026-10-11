#!/usr/bin/env python3
"""데스카페 정적 페이지 생성기

자료실 자료(구글 시트)와 웰다잉 뉴스(news/*.json)를 읽어
글마다 검색엔진이 읽을 수 있는 독립 페이지를 만듭니다.

만드는 것
  library/<id>.html   자료실 자료 1건 = 페이지 1개
  news/<id>.html      웰다잉 뉴스 1호 = 페이지 1개
  sitemap.xml         검색엔진용 전체 페이지 목록
  rss.xml             새 글 알림(네이버 서치어드바이저 RSS 제출용)
  library.html        목록 부분을 미리 채워 둠(자바스크립트 없이도 링크가 보이게)

사용법
  python3 tools/build.py                       # 구글 시트에서 자료를 직접 읽음
  python3 tools/build.py --library-json x.json # 저장해 둔 자료 데이터로 생성

GitHub Actions(.github/workflows/build.yml)가 정기적으로 자동 실행합니다.
"""
import argparse
import datetime as dt
import glob
import html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://deathcafe.co.kr/"
SITE_NAME = "Death Cafe 데스카페"
AUTHOR = "차준택"
FIELDS = ["왜 죽음학인가", "죽음과 죽어감", "생애말기와 연명의료", "죽음준비"]
STATIC_PAGES = [  # (경로, 우선순위)
    ("", "1.0"), ("library.html", "0.9"), ("about.html", "0.8"),
    ("lecture.html", "0.8"), ("thoughts.html", "0.7"),
]
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_if_changed(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and read(path) == text:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def kdate(s):
    """'2026. 10. 3.' -> date. 실패하면 None"""
    m = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", str(s or ""))
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def api_url():
    m = re.search(r'API_URL:\s*"([^"]+)"', read(p("assets", "site.js")))
    return m.group(1) if m else ""


def fetch_library():
    url = api_url()
    if not url:
        return []
    body = json.dumps({"action": "listLibrary"}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "text/plain;charset=utf-8"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError("자료실 데이터를 받지 못했습니다: %r" % data)
    return data.get("items") or []


def paragraphs(text):
    parts = [t.strip() for t in re.split(r"\n", str(text or "")) if t.strip()]
    return "".join("<p>%s</p>" % fmt(t) for t in parts)


def fmt(t):
    """본문 강조 표시: **굵게**, ==강조색== (library.html의 fmt와 같은 규칙)"""
    s = esc(t)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"==(.+?)==", r'<span class="hl">\1</span>', s)
    return s


def page_styles():
    """library.html의 <style> 블록을 그대로 가져와 같은 모양을 유지"""
    m = re.search(r"<style>(.*?)</style>", read(p("library.html")), re.S)
    return m.group(1) if m else ""


def head(title, desc, path, image=None, kind="article", jsonld=None):
    url = SITE + path
    img = image or (SITE + "assets/profile.jpg")
    ld = ('\n<script type="application/ld+json">%s</script>' %
          json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")) if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<base href="/">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(img)}">
<meta property="og:locale" content="ko_KR">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{SITE}rss.xml">{ld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&family=Noto+Sans+KR:wght@400;500;700&family=Cormorant+Garamond:ital,wght@0,500;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<style>{page_styles()}
  a.back{{text-decoration:none;}}
</style>
</head>
<body>
<div id="site-header"></div>
"""


FOOT = """<div id="site-footer"></div>
<script src="assets/site.js"></script>
"""


def is_image(u):
    return bool(u) and re.search(r"\.(png|jpe?g|gif|webp)(\?|$)", u, re.I)


def abs_url(u):
    if not u:
        return ""
    return u if re.match(r"^https?://", u) else SITE + u.lstrip("/")


# ---------------------------------------------------------------- 자료실
def item_page(x):
    f = int(x.get("f") or 0)
    field = FIELDS[f] if 0 <= f < len(FIELDS) else ""
    path = "library/%s.html" % x["id"]
    d = kdate(x.get("date"))
    img = abs_url(x.get("file")) if is_image(x.get("file")) else None
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": x.get("title", ""), "description": x.get("sum", ""),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "about.html"},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "mainEntityOfPage": SITE + path, "inLanguage": "ko", "articleSection": field,
    }
    if d:
        ld["datePublished"] = d.isoformat()
    if img:
        ld["image"] = img
    h = head("%s | 데스카페 웰다잉 자료실" % x.get("title", ""), x.get("sum", ""), path, img, jsonld=ld)
    lec = " lec" if x.get("type") == "강의자료" else ""
    out = [h, '<main class="wrap narrow">',
           '<article class="detail" id="libItem" data-id="%s">' % esc(x["id"]),
           '<a class="back" href="library.html">← 자료실 목록</a>',
           '<div class="meta"><span class="badge%s">%s</span><a href="library.html#f%d" style="text-decoration:none">%s</a><span>%s</span></div>'
           % (lec, esc(x.get("type")), f + 1, esc(field), esc(x.get("date"))),
           "<h1>%s</h1>" % esc(x.get("title"))]
    if is_image(x.get("file")):
        out.append('<figure class="slide"><img src="%s" alt="%s"></figure>' % (esc(x["file"]), esc(x.get("title"))))
    if x.get("body"):
        out.append('<div class="body">%s</div>' % paragraphs(x["body"]))
    if x.get("fileName") and not is_image(x.get("file")):
        dl = ('<a class="btn btn-primary" href="%s" target="_blank" rel="noopener">내려받기</a>' % esc(x["file"])
              if x.get("file") else '<span class="stats">파일 준비 중</span>')
        out.append('<div class="attach card"><div class="fn">%s</div>%s</div>' % (esc(x["fileName"]), dl))
    links = ""
    if x.get("video"):
        links += '<a class="btn btn-primary" href="%s" target="_blank" rel="noopener">영상 보기 ↗</a>' % esc(x["video"])
    if x.get("link"):
        links += '<a class="btn btn-ghost" href="%s" target="_blank" rel="noopener">%s ↗</a>' % (
            esc(x["link"]), esc(x.get("linkLabel") or "원문 보기"))
    if links:
        out.append('<div class="links">%s</div>' % links)
    n_cm = len(x.get("comments") or [])
    out.append('<button type="button" class="heart" id="like" aria-pressed="false" style="width:fit-content">'
               '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.8 4.5c2.1 0 3.6 1.1 4.3 2.3h1.8c.7-1.2 2.2-2.3 4.3-2.3 3.8 0 5.9 3.9 4.4 7.3C19.5 16.4 12 21 12 21z"/></svg>'
               '공감해요 <span>%s</span></button>' % esc(x.get("likes", 0)))
    out.append('<section class="comments" id="comments"><h2>댓글 %d</h2>' % n_cm)
    for c in x.get("comments") or []:
        out.append('<div class="cmt"><span class="who">%s<span>%s</span></span><p>%s</p></div>'
                   % (esc(c.get("name")), esc(c.get("date")), esc(c.get("text"))))
    out.append('</section>')
    out.append('<div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
               '<span>이 주제로 강의를 듣고 싶으신가요?</span><a class="btn btn-ghost btn-small" href="lecture.html">강의 신청</a></div>')
    out.append('</article></main>')
    out.append(FOOT + '<script src="assets/item.js"></script>\n</body>\n</html>\n')
    return path, "\n".join(out)


# ---------------------------------------------------------------- 웰다잉 뉴스
def issue_page(x):
    path = "news/%s.html" % x["id"]
    d = kdate(x.get("date")) or kdate(x["id"])
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": x.get("title", ""), "description": x.get("sum", ""),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "about.html"},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "mainEntityOfPage": SITE + path, "inLanguage": "ko",
    }
    if d:
        ld["datePublished"] = d.isoformat()
    desc = "%s (%s) %s" % (x.get("title", ""), x.get("range", ""), x.get("sum", ""))
    out = [head("%s | 데스카페 웰다잉 뉴스" % x.get("title", ""), desc.strip(), path, jsonld=ld),
           '<main class="wrap narrow"><article class="detail">',
           '<a class="back" href="library.html#news">← 웰다잉 뉴스 목록</a>',
           '<div class="meta"><span class="issue-no">제%s호</span><span>%s</span><span>웰다잉 뉴스</span></div>'
           % (esc(x.get("no")), esc(x.get("range"))),
           "<h1>%s</h1>" % esc(x.get("title"))]
    if x.get("lead"):
        out.append('<p class="lead">%s</p>' % esc(x["lead"]))
    out.append('<ol class="news-items">')
    for n in x.get("items") or []:
        f = n.get("f")
        badge = ('<span class="badge lec">%s</span>' % esc(FIELDS[int(f)])
                 if f is not None and 0 <= int(f) < len(FIELDS) else "")
        src = "출처: " + esc(n.get("source"))
        if n.get("sourceDate"):
            src += " · " + esc(n["sourceDate"])
        if n.get("url"):
            src += ' · <a href="%s" target="_blank" rel="noopener nofollow">원문 보기 ↗</a>' % esc(n["url"])
        view = ('<div class="view"><b>차준택의 시선</b>%s</div>' % esc(n["comment"])) if n.get("comment") else ""
        out.append('<li class="news-item"><div class="meta">%s</div><h2>%s</h2><p class="sm">%s</p><div class="src">%s</div>%s</li>'
                   % (badge, esc(n.get("headline")), esc(n.get("summary")), src, view))
    out.append('</ol>')
    out.append('<p class="note">기사 요약은 원문을 바탕으로 데스카페가 다시 쓴 것입니다. 정확한 내용은 원문을 확인해 주세요.</p>')
    if x.get("care"):
        out.append('<p class="note">마음이 많이 힘드시다면 혼자 견디지 마세요. 자살예방 상담전화 109 (24시간)</p>')
    out.append('<div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
               '<span>이번 주 소식을 보고 떠오른 생각이 있으신가요?</span><a class="btn btn-ghost btn-small" href="thoughts.html">생각 나누기에 남기기</a></div>')
    out.append('</article></main>')
    out.append(FOOT + '<script>DC.chrome("library.html");</script>\n</body>\n</html>\n')
    return path, "\n".join(out)


# ---------------------------------------------------------------- 목록 미리 채우기
def prefill_library_html(items, issues):
    src = read(p("library.html"))
    lib_li = "".join(
        '<li class="item"><a class="open" href="library/%s.html"><span class="meta"><span class="badge%s">%s</span><span>%s</span><span>%s</span></span><span class="ttl">%s</span><span class="sum">%s</span></a></li>'
        % (esc(x["id"]), " lec" if x.get("type") == "강의자료" else "", esc(x.get("type")),
           esc(FIELDS[int(x.get("f") or 0)]), esc(x.get("date")), esc(x.get("title")), esc(x.get("sum")))
        for x in items) or '<li class="empty">불러오는 중입니다.</li>'
    news_li = "".join(
        '<li class="item"><a class="open" href="news/%s.html"><span class="meta"><span class="issue-no">제%s호</span><span>%s</span></span><span class="ttl">%s</span><span class="sum">%s</span></a></li>'
        % (esc(x["id"]), esc(x.get("no")), esc(x.get("range")), esc(x.get("title")), esc(x.get("sum")))
        for x in issues) or '<li class="empty">불러오는 중입니다.</li>'
    src = re.sub(r'(<ul class="list" id="list">).*?(</ul>)', lambda m: m.group(1) + lib_li + m.group(2), src, flags=re.S)
    src = re.sub(r'(<ul class="list" id="newsList">).*?(</ul>)', lambda m: m.group(1) + news_li + m.group(2), src, flags=re.S)
    return write_if_changed(p("library.html"), src)


# ---------------------------------------------------------------- 사이트맵·RSS
def sitemap(entries):
    base = "2026-10-10"  # 고정 페이지를 마지막으로 크게 고친 날
    newest = max([e["date"] for e in entries if e["date"]] + [dt.date(2026, 10, 10)]).isoformat()
    rows = []
    for path, prio in STATIC_PAGES:
        rows.append("  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
                    % (SITE, path, newest if path in ("", "library.html") else base, prio))
    for e in entries:
        lm = e["date"].isoformat() if e["date"] else base
        rows.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>0.8</priority></url>" % (esc(SITE + e["path"]), lm))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")


def rss(entries):
    def rfc(d):
        d = d or dt.date.today()
        return dt.datetime(d.year, d.month, d.day, 9, 0, tzinfo=dt.timezone(dt.timedelta(hours=9))).strftime("%a, %d %b %Y %H:%M:%S +0900")
    items = sorted(entries, key=lambda e: e["date"] or dt.date.min, reverse=True)[:50]
    body = "".join(
        "\n  <item>\n    <title>%s</title>\n    <link>%s</link>\n    <guid isPermaLink=\"true\">%s</guid>\n"
        "    <description>%s</description>\n    <category>%s</category>\n    <pubDate>%s</pubDate>\n  </item>"
        % (esc(e["title"]), esc(SITE + e["path"]), esc(SITE + e["path"]), esc(e["desc"]), esc(e["cat"]), rfc(e["date"]))
        for e in items)
    last = rfc(items[0]["date"]) if items else rfc(None)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
            "  <title>%s</title>\n  <link>%s</link>\n"
            "  <description>웰다잉과 죽음학 자료, 매주 웰다잉 뉴스 — 차준택(Spirit Care)</description>\n"
            "  <language>ko</language>\n  <lastBuildDate>%s</lastBuildDate>%s\n</channel>\n</rss>\n"
            % (SITE_NAME, SITE, last, body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library-json", help="구글 시트 대신 읽을 자료 데이터(JSON) 파일")
    a = ap.parse_args()

    if a.library_json:
        data = json.loads(read(a.library_json))
        items = data.get("items", data) if isinstance(data, dict) else data
    else:
        items = fetch_library()
    items = [x for x in items if SAFE_ID.match(str(x.get("id", "")))]

    issues = json.loads(read(p("news", "index.json"))).get("issues", [])
    issues = [x for x in issues if re.match(r"^\d{4}-\d{2}-\d{2}$", str(x.get("id", "")))]

    changed, entries, keep = [], [], set()
    for x in items:
        path, text = item_page(x)
        keep.add(path)
        if write_if_changed(p(path), text):
            changed.append(path)
        entries.append({"path": path, "date": kdate(x.get("date")), "title": x.get("title", ""),
                        "desc": x.get("sum", ""), "cat": "자료실"})
    for meta in issues:
        full = json.loads(read(p("news", meta["id"] + ".json")))
        path, text = issue_page(full)
        keep.add(path)
        if write_if_changed(p(path), text):
            changed.append(path)
        entries.append({"path": path, "date": kdate(full.get("date")) or kdate(full["id"]),
                        "title": full.get("title", ""), "desc": full.get("sum", ""), "cat": "웰다잉 뉴스"})

    # 시트에서 지워진 자료의 페이지는 정리
    for old in glob.glob(p("library", "*.html")):
        rel = os.path.relpath(old, ROOT).replace(os.sep, "/")
        if rel not in keep:
            os.remove(old)
            changed.append(rel + " (삭제)")

    if prefill_library_html(items, issues):
        changed.append("library.html")
    if write_if_changed(p("sitemap.xml"), sitemap(entries)):
        changed.append("sitemap.xml")
    if write_if_changed(p("rss.xml"), rss(entries)):
        changed.append("rss.xml")

    print("자료 %d건, 뉴스 %d호 처리" % (len(items), len(issues)))
    print("\n".join("  변경: " + c for c in changed) if changed else "  변경 없음")


if __name__ == "__main__":
    sys.exit(main())
