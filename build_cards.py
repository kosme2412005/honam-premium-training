# -*- coding: utf-8 -*-
"""
호남연수원 '중기 인재키움 프리미엄 훈련' 과정 카드 생성기.

원본 xlsx(시트 '2. 신청 훈련과정 정보')를 파싱해 index.html의
<!-- COURSES:START --> ~ <!-- COURSES:END --> 사이를 정적 카드 HTML로 교체한다.
과정 정보가 바뀌면: xlsx 갱신 → `python build_cards.py` 재실행.
index.html이 없으면 cards_fragment.html 로만 출력한다.
"""
import zipfile, re, os, html, sys
import xml.etree.ElementTree as ET

XLSX = r"C:\Users\honamedu\Desktop\중기 인재키움 환급 자료\홈페이지 제작\(붙임1) 2026년 중소기업 인재 키움 프리미엄 훈련 운영 과정 목록(호남연수원).xlsx"
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")
FRAGMENT = os.path.join(HERE, "cards_fragment.html")

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"

# 실시 장소 정규화 (원본 시트의 번지 오타/변형 흡수)
ADDR = {
    "광주": ("광주", "광주 북구 동문대로 456번길 40 (호남연수원)"),
    "전주": ("전주", "전북 전주시 덕진구 유상로 67 (전주 스마트공장 배움터)"),
    "제주": ("제주", "제주특별자치도 제주시 첨단로 213-3"),
}


def col_idx(ref):
    m = re.match(r"([A-Z]+)", ref)
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def load_rows(path, sheet_name):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(T)))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets = [(s.get("name"), i + 1) for i, s in enumerate(wb.find("m:sheets", NS))]
    target = None
    for name, idx in sheets:
        if sheet_name in name:
            target = f"xl/worksheets/sheet{idx}.xml"
            break
    if not target:
        raise SystemExit(f"시트 '{sheet_name}' 없음: {[n for n, _ in sheets]}")
    root = ET.fromstring(z.read(target))
    rows = []
    for row in root.find("m:sheetData", NS).findall("m:row", NS):
        cells = {}
        for c in row.findall("m:c", NS):
            v = c.find("m:v", NS)
            if v is None:
                continue
            val = v.text
            if c.get("t") == "s":
                val = shared[int(val)]
            cells[col_idx(c.get("r", "A1"))] = str(val).strip()
        if cells:
            rows.append(cells)
    return rows


def city_of(sido):
    for key in ADDR:
        if key in sido:
            return key
    return "광주"


def fmt_won(n):
    return f"{n:,}"


def parse_courses():
    rows = load_rows(XLSX, "신청 훈련과정")
    courses = []
    for r in rows:
        # 데이터 행: 0=기관명, 1=연번(숫자)
        no = r.get(1, "")
        if not no.isdigit():
            continue
        name = re.sub(r"\s+", " ", r.get(7, "")).strip()
        ctype = r.get(6, "").strip()  # AI융합형 | 일반형
        hours = r.get(9, "")
        days = r.get(10, "")
        schedule = r.get(11, "")
        capacity = r.get(12, "")
        price = int(float(r.get(13, "0")))
        copay = round(price * 0.1)
        city, addr = ADDR[city_of(r.get(16, ""))]
        tel = r.get(18, "").strip()
        courses.append(dict(no=int(no), name=name, ctype=ctype, hours=hours,
                            days=days, schedule=schedule, capacity=capacity,
                            price=price, copay=copay, city=city, addr=addr, tel=tel))
    return courses


def card_html(c):
    badge_cls = "badge-ai" if "AI" in c["ctype"] else "badge-gen"
    esc = html.escape
    return f'''      <article class="course-card reveal" tabindex="0" role="button"
        aria-label="{esc(c['name'])} 상세 보기"
        data-no="{c['no']}" data-type="{esc(c['ctype'])}" data-city="{c['city']}"
        data-name="{esc(c['name'])}" data-hours="{c['hours']}" data-days="{c['days']}"
        data-schedule="{esc(c['schedule'])}" data-capacity="{c['capacity']}"
        data-price="{fmt_won(c['price'])}" data-copay="{fmt_won(c['copay'])}"
        data-addr="{esc(c['addr'])}" data-tel="{esc(c['tel'])}">
        <div class="card-top">
          <span class="badge {badge_cls}">{esc(c['ctype'])}</span>
          <span class="card-city">{c['city']}</span>
        </div>
        <h3 class="card-name">{esc(c['name'])}</h3>
        <p class="card-meta">{c['hours']}시간 · {c['days']}일 과정 · {esc(c['schedule'])} · 정원 {c['capacity']}명</p>
        <div class="card-price">
          <s>{fmt_won(c['price'])}원</s>
          <strong>실부담 {fmt_won(c['copay'])}원</strong>
          <small>90% 환급 적용 시*</small>
        </div>
      </article>'''


def main():
    courses = parse_courses()
    assert len(courses) == 45, f"과정 수 불일치: {len(courses)}개 (기대 45개)"
    # 노출 순서: 광주 → 전주 → 제주, 지역 내에서는 연번순
    city_order = {"광주": 0, "전주": 1, "제주": 2}
    courses.sort(key=lambda c: (city_order[c["city"]], c["no"]))
    ai = sum(1 for c in courses if "AI" in c["ctype"])
    cards = "\n".join(card_html(c) for c in courses)
    block = f"<!-- COURSES:START (build_cards.py 자동 생성 — 직접 수정 가능하나 재실행 시 덮어씀) -->\n{cards}\n      <!-- COURSES:END -->"

    if os.path.exists(INDEX):
        src = open(INDEX, encoding="utf-8").read()
        new, n = re.subn(r"<!-- COURSES:START.*?<!-- COURSES:END -->", block,
                         src, flags=re.S)
        if n != 1:
            raise SystemExit("index.html에서 COURSES 마커를 찾지 못함")
        open(INDEX, "w", encoding="utf-8").write(new)
        print(f"index.html 갱신 완료: 카드 {len(courses)}개 (AI융합형 {ai} / 일반형 {len(courses)-ai})")
    else:
        open(FRAGMENT, "w", encoding="utf-8").write(block)
        print(f"cards_fragment.html 생성: 카드 {len(courses)}개 (AI융합형 {ai} / 일반형 {len(courses)-ai})")


if __name__ == "__main__":
    main()
