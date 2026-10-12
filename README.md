# LawCodex — Nepal (`np`)

Laws of Nepal as plain Markdown, one file per text: the **official English translations** of the
Constitution and of Acts published by the **Nepal Law Commission** (नेपाल कानून आयोग), recovered from
Internet Archive copies of the Commission's former English website.

Part of [LawCodex](https://github.com/LawCodex): the laws of every country as Markdown in git.

Retrieved: 2026-10-12. **362 files.** This is a **partial** corpus — read *Gaps* below.

## Contents

| Category | Directory | Files |
|---|---|---:|
| Constitution of Nepal (2015), English translation | `constitution/constitution-of-nepal.md` | 1 |
| Acts (and the old *Muluki Ain*), English translations | `acts/<B.S. year>/` | 361 |
| **Total** | | **362** |

## Gaps

- **No Nepali (original) texts.** The Commission's current site (<https://lawcommission.gov.np>)
  publishes every law as a Nepali PDF (Constitution, ~360 Acts in 17 volumes, ordinances, rules).
  Those PDFs were produced from Microsoft Word with the Kalimati/Kokila fonts and their text layer
  maps glyphs to the wrong Unicode characters (e.g. *नागरिकता* comes out as *नागररकिा*, *कार्य* as
  *कायि*); both `pdftotext` and `pypdf` return the same corrupted text. Publishing it would not be a
  faithful copy of the law, and OCR was out of scope, so the Nepali texts are not included.
- **English translations are those archived between 2015 and 2021** (the Commission's former
  `lawcommission.gov.np/en/` WordPress site, no longer online). They may not reflect later
  amendments, and some Acts listed there may since have been repealed or replaced — notably by the
  2017 codes (Muluki Civil Code, Muluki Criminal Code, etc.), whose English translations were not
  among the archived PDFs. Every file therefore has `status: unknown`.
- Not included: rules/regulations, formation orders, policies, international treaties and the
  constitutions of international organisations that were also on the English site; 1 scanned PDF
  (*Bank and Financial Institution Act, 2073*); 3 PDFs missing from the archive; 9 duplicates (same
  Act archived under two file names — the most recent copy was kept).
- English translations are *not* authoritative: the Nepali text published in the Nepal Gazette
  prevails.

## Structure

```
constitution/constitution-of-nepal.md
acts/<B.S. year>/<slug>.md          e.g. acts/2063/army-act-2063-2006.md
```

Nepali Acts are named after their year in the Bikram Sambat (B.S.) calendar (Gregorian year + 56/57),
which is the directory name; the Gregorian year is usually in the title in brackets.

Front matter: `title`, `identifier` (e.g. `Act No. 7 of the year 2063`, where printed), `type`,
`jurisdiction`, `language` (`en`), `translation: true`, `date` (Gregorian date of authentication /
publication, where printed), `date_bs`, `status` (`unknown`), `source` (original URL on
lawcommission.gov.np), `archived` (the Internet Archive copy actually used), `retrieved`.

Body: text extracted from the PDF (`pdftotext -layout`): running headers, page numbers and the
`www.lawcommission.gov.np` footer are removed; lines are joined into paragraphs; `Part`/`Chapter`
lines become `##`/`###` headings and sections (`12. Heading: text`) become `#### 12. Heading` followed
by their text. Footnotes printed at the foot of a page are kept as `> ` quote lines after the
section where they occur. Tables are kept as fenced blocks where detected.

## Sources

- Nepal Law Commission, former English website — PDFs under
  `https://www.lawcommission.gov.np/en/wp-content/uploads/` and `/en/documents/`, retrieved from the
  Internet Archive (`https://web.archive.org/web/<timestamp>id_/<url>`), listed with the Wayback CDX API.
- Nepal Law Commission, current website — <https://lawcommission.gov.np> (robots.txt
  `Crawl-delay: 10`, respected while surveying it); only Nepali PDFs (see *Gaps*).

## Licence

Laws of Nepal and their official translations are public documents of the Government of Nepal.
This compilation adds no copyrightable content.

## Regenerate

```
pip install -r scripts/requirements.txt
python scripts/np_fetch.py      # lists and downloads archived PDFs to ../_raw/np (1 request/second)
python scripts/np_convert.py .  # writes the Markdown files
```
