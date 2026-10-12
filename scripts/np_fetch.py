#!/usr/bin/env python3
"""Fetch English translations of Nepali Acts published by the Nepal Law Commission
(https://lawcommission.gov.np/en/ , WordPress site in use until ~2023) from the Internet Archive.

The current lawcommission.gov.np site only serves Nepali PDFs whose text layer is unusable
(see README). The former English site's PDFs are listed through the Wayback CDX API and fetched
as raw archived files (web.archive.org/web/<timestamp>id_/<url>).

Output: RAW/en_index.json, PDFs in RAW/pdf/.
"""
import json, os, re, sys, time, urllib.parse
import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.environ.get("RAW", os.path.join(os.path.dirname(__file__), "..", "..", "_raw", "np"))
S = requests.Session()
S.headers["User-Agent"] = UA
CDX = "http://web.archive.org/cdx/search/cdx?url=lawcommission.gov.np/en/*&filter=statuscode:200&filter=mimetype:application/pdf&collapse=urlkey&fl=original,timestamp,length"
SKIP = re.compile(r"(^|-)(rules?|regulations?|bye-?laws?|order|policy|policies|strategy|convention|treaty|agreement|protocol|"
                  r"covenant|declaration|charter|guidelines?|directives?|manual|report|plan|notice|procedure|statute-of|"
                  r"standards?|framework|programme|program|code-of-conduct|appeal-for)(-|$)", re.I)
KEEP = re.compile(r"(^|-)(act|ain|code|constitution|sanhita|ordinance)(-|$)", re.I)


def get(url, path=None, binary=True):
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, "rb").read()
    for attempt in range(5):
        try:
            r = S.get(url, timeout=300)
            if r.status_code in (404, 403):
                return None
            r.raise_for_status()
            if path:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path + ".part", "wb") as f:
                    f.write(r.content)
                os.replace(path + ".part", path)
            time.sleep(1.0)
            return r.content
        except Exception as e:
            print("retry", attempt, url, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    return None


def norm_key(name):
    n = urllib.parse.unquote(name).lower()
    n = re.sub(r"\.pdf$", "", n)
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    n = re.sub(r"-(final|eng|english|version|\d)$", "", n)
    n = re.sub(r"^the-", "", n)
    return n


def main():
    os.makedirs(RAW, exist_ok=True)
    cdx = get(CDX, f"{RAW}/cdx_pdf.txt").decode()
    best = {}
    for line in cdx.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        url, ts, length = parts[0], parts[1], parts[2]
        p = urllib.parse.urlsplit(url).path
        if not p.lower().endswith(".pdf") or not ("/wp-content/uploads/" in p or "/documents/" in p):
            continue
        name = p.rsplit("/", 1)[-1]
        key = norm_key(name)
        if SKIP.search(key) or not KEEP.search(key):
            continue
        rank = (1 if "/wp-content/uploads/" in p else 0, ts)
        if key not in best or rank > best[key]["rank"]:
            best[key] = {"key": key, "url": url, "ts": ts, "rank": rank, "name": urllib.parse.unquote(name)}
    print(len(best), "candidate PDFs", file=sys.stderr)
    out = []
    for i, (k, r) in enumerate(sorted(best.items())):
        path = f"{RAW}/pdf/{k[:120]}.pdf"
        b = get(f"http://web.archive.org/web/{r['ts']}id_/{r['url']}", path)
        if not b or not b.startswith(b"%PDF"):
            r["status"] = "missing"
            if b and os.path.exists(path):
                os.remove(path)
        else:
            r["status"] = "ok"
            r["path"] = path
        r["archived"] = f"https://web.archive.org/web/{r['ts']}/{r['url']}"
        del r["rank"]
        out.append(r)
        if i % 25 == 0:
            print(i, len(best), file=sys.stderr)
            json.dump(out, open(f"{RAW}/en_index.json", "w"), indent=1, ensure_ascii=False)
    json.dump(out, open(f"{RAW}/en_index.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
