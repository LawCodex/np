#!/usr/bin/env python3
"""Convert the archived English translations of Nepali Acts (see np_fetch.py) into Markdown.

Usage: np_convert.py [REPO_DIR]
"""
import datetime, json, os, re, subprocess, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from np_pdfmd import to_markdown, pdf_pages

RAW = os.environ.get("RAW", os.path.join(os.path.dirname(__file__), "..", "..", "_raw", "np"))
REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
RETRIEVED = os.environ.get("RETRIEVED", datetime.date.today().isoformat())
EXCLUDE = re.compile(r"^constitution-of-(?!nepal)|^constitution-of-nepal-2$|convention|protocol")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def slug(s, n=90):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rsplit("-", 1)[0] if len(s) > n else s


def main():
    idx = json.load(open(f"{RAW}/en_index.json"))
    stats = {"written": 0, "scanned": [], "skipped": [], "missing": []}
    seen = {}
    idx.sort(key=lambda r: r.get("ts", ""), reverse=True)
    for r in idx:
        k = r["key"]
        if EXCLUDE.search(k):
            stats["skipped"].append(k)
            continue
        if r.get("status") != "ok" or not os.path.exists(r.get("path", "")):
            stats["missing"].append(r["url"])
            continue
        pages = pdf_pages(r["path"])
        txt = "\n".join(pages)
        if len(re.sub(r"\s", "", txt)) < 150 * max(1, len(pages)) * 0.5:
            stats["scanned"].append(r["url"])
            continue
        lines = [re.sub(r"^[^\w(]+", "", l.strip()) for l in pages[0].split("\n")
                 if l.strip() and not re.search(r"lawcommission|www\.", l, re.I)]
        lines = [re.sub(r"\s{2,}.*$", "", l) for l in lines if len(re.findall(r"[A-Za-z]", l)) >= 4]
        cand = [l for l in lines[:8] if re.search(r"\b(Act|ACT|Code|CODE|Ain|AIN|Constitution|Ordinance)\b", l)]
        title = cand[0] if cand else " ".join(w.capitalize() for w in k.split("-"))
        if k == "constitution-of-nepal":
            title = "Constitution of Nepal"
        flat = " ".join(txt.split())
        m = re.search(r"Date of (?:Authentication|Publication)[^0-9]{0,60}?(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*\(\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*\)", flat)
        date = None
        bs = None
        if m:
            bs = f"{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}"
            try:
                date = datetime.date(int(m.group(4)), int(m.group(5)), int(m.group(6))).isoformat()
            except ValueError:
                date = None
        if not date:
            m3 = re.search(r"Date of[^0-9]{0,80}?(\d{4})[.\-/](\d{1,2})[.\-/]\s?(\d{1,2})\s*\(\s*(\d{1,2})\s*([A-Z][a-z]{2})[a-z]*\.?,?\s*(\d{4})\s*\)", flat)
            if m3:
                bs = f"{m3.group(1)}.{int(m3.group(2)):02d}.{int(m3.group(3)):02d}"
                try:
                    date = datetime.datetime.strptime(f"{m3.group(4)} {m3.group(5)} {m3.group(6)}", "%d %b %Y").date().isoformat()
                except ValueError:
                    pass
        if not date:
            m2 = re.search(r"Date of (?:Authentication|Publication)[^0-9]{0,60}?([A-Z][a-z]+ \d{1,2}, \d{4})", flat)
            if m2:
                try:
                    date = datetime.datetime.strptime(m2.group(1), "%B %d, %Y").date().isoformat()
                except ValueError:
                    pass
        num = re.search(r"Act\s+(?:No\.?|Number)\s*(\d+)\s+of\s+the\s+[Yy]ear\s+(\d{4})(?:\s*\((\d{4})\))?", flat)
        ident = f"Act No. {num.group(1)} of the year {num.group(2)}" if num else None
        # Nepali Acts are named after their Bikram Sambat (B.S.) year, the first year in the title
        ty = re.search(r"(?<!\d)(1[89]\d\d|20\d\d)(?!\d)", title) or re.search(r"(?<!\d)(1[89]\d\d|20\d\d)", k)
        bs_year = (bs or "")[:4] or (ty.group(1) if ty else "undated")
        ys = [int(y) for y in re.findall(r"(?<!\d)(1[89]\d\d|20\d\d)(?!\d)", re.sub(r"(\d{4})(\d{4})", r"\1-\2", k + " " + title))]
        pair = [b for a in ys for b in ys if 56 <= b - a <= 57]
        if not bs and pair:
            bs_year = str(pair[0])
        if k.startswith("constitution-of-nepal"):
            rel = "constitution/constitution-of-nepal.md"
            typ = "constitution"
        else:
            typ = "code" if "code" in k else "act"
            rel = f"acts/{bs_year}/{slug(k)}.md"
        tkey = re.sub(r"\b(the|nepal|of|act)\b|[^a-z0-9]", "", title.lower())
        if tkey in seen:
            stats["skipped"].append(k + " (duplicate of " + seen[tkey] + ")")
            continue
        seen[tkey] = k
        body = to_markdown(r["path"])
        fm = ["---", f"title: {q(title)}"]
        if ident:
            fm.append(f"identifier: {q(ident)}")
        fm += [f"type: {typ}", "jurisdiction: np", "language: en", "translation: true"]
        if date:
            fm.append(f"date: {date}")
        if bs:
            fm.append(f"date_bs: {q(bs)}")
        fm.append("status: unknown")
        fm.append(f"source: {q(r['url'])}")
        fm.append(f"archived: {q(r['archived'])}")
        fm.append(f"retrieved: {RETRIEVED}")
        fm.append("---")
        md = "\n".join(fm) + "\n\n# " + title + "\n\n" + body
        path = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        stats["written"] += 1
    json.dump(stats, open(f"{RAW}/convert-stats.json", "w"), indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in stats.items()}))


if __name__ == "__main__":
    main()
