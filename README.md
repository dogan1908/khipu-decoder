# 🪢 Khipu Decoder · Quechua Gematria

> An interactive single-file web tool for exploring Andean knot records (khipus) through a phonosemantic gematria lens.

![Status](https://img.shields.io/badge/version-v11-orange) ![License](https://img.shields.io/badge/license-MIT-green) ![Khipus](https://img.shields.io/badge/khipus-629-blue) ![Words](https://img.shields.io/badge/Quechua%20words-1855-purple)

## Overview

The Khipu Decoder lets you browse 629 historical khipus from the Open Khipu Repository / Harvard Khipu Database alongside a curated lexicon of 1,855 Quechua words categorized into 15 semantic fields. The central premise is a phonosemantic gematria mapping of Quechua consonants to digits 0–9 (Balban 2026), in which a knot value such as `75` decodes as `P+a · M+a → puma`.

Three coordinated panels make the relationship between knots and words explorable:

- **Khipu values** — every cord value of a selected khipu is clickable; clicking one runs a full gematria decomposition (digits → consonant classes → syllables → matching Quechua words) with category badges.
- **Word browser** — all 1,855 Quechua words filtered by category and free-text search; each word lists every khipu that contains its gematria value as a clickable chip that jumps directly to the corresponding cord in the value grid.
- **Mindmap** — radial SVG visualization. By default it shows the global word distribution across consonant classes and categories. **As soon as a khipu is selected, the mindmap re-renders to show only the words whose gematria value occurs in that khipu**, with cluster sizes scaled by occurrence frequency.

## Live demo

🌐 **[https://dogan1908.github.io/khipu-decoder/](https://dogan1908.github.io/khipu-decoder/)**

The landing page (`index.html`) lets you choose between the English and German editions. Both are single self-contained HTML files with no runtime dependencies and can also be downloaded and run fully offline.

## What's new in v11

- **Vocabulary tripled**: 557 → 1,855 words (3.3× growth)
- **Pre-Columbian focus**: All entries pass through a phonological + semantic + etymological filter that excludes Spanish loanwords and post-contact concepts
- **Open lexicon**: The full lexicon is exported as `data/quechua_lexicon_v11.json` for reuse in other projects
- **Reproducible pipeline**: `tools/prequechua_filter.py` and `tools/build_lexicon.py` document the methodology and let you rebuild the lexicon from sources

## Pre-Columbian filtering methodology

Pre-Columbian Quechua had specific phonological constraints that distinguish native words from Spanish loanwords introduced after 1532. We use four detection layers:

**Phonological markers (high confidence loanword indicators):**
- `/f/` does not exist in pre-Columbian Quechua → any `f` flags loanword
- `/b/`, `/d/`, `/g/` word-initially → loanword (only allophonic after nasals natively)
- Spanish consonant clusters at word start (`tr-`, `pl-`, `pr-`, `bl-`, `br-`, `cr-`, `dr-`, `fl-`, `fr-`, `gl-`, `gr-`)
- Spanish derivational suffixes (`-ción`, `-sión`, `-mente`, `-dad`, `-tad`)
- Spanish diminutives (`-ito`, `-ita`, `-illo`, `-illa`) in long words

**Semantic markers (post-contact concepts):**
- English glosses referring to: horse, cow, sheep, wheat, apple, computer, alcohol, gun, bible, etc.
- Modern country and place names

**Etymological markers (Wiktionary annotations):**
- Entries marked "Borrowed from Spanish/Castilian/English/Portuguese"

**Whitelist for false positives:**
- Words like `killa` (moon, looks like Spanish `-illa`), `tukrikuq` (overseer, has `kr` across syllables)

This filter is documented in `tools/prequechua_filter.py` and validated against:
- Cerrón-Palomino (1987): *Lingüística Quechua*
- Adelaar & Muysken (2004): *The Languages of the Andes*
- Mannheim (1991): *The Language of the Inka*

## Features

| Panel | What it does |
|---|---|
| Khipu list | 629 khipus searchable by ID, provenance, museum or OKR number. Search also matches Quechua words/English meanings — khipus containing the matching value are flagged with ⚡N counters. |
| Gematria system | Three switchable systems: Quechua (Balban 2026, UR281-verified), Katapayadi (Sanskrit), and an editable custom system. |
| Knot values | All cord values for the selected khipu with structural hints (markers, checksum candidates, repeated values). |
| Decode panel | Per-value digit breakdown, all syllable combinations, exact / nearby (±5) / leading-digit word matches with category badges. |
| Full-text attempt | Whole-khipu narrative, color-coded by structural role: word matches, syllable guesses, repeated markers, Σ-checksums. |
| Word browser | 1,855 Quechua words, filtered by category + search. Each word shows the khipus it appears in as clickable chips. |
| Mindmap | Khipu-aware radial SVG. Toggle 🎯 Khipu / 🌐 Global. Click any cluster → filters word browser to that category. |

## Data sources

- **Khipu corpus**: [Open Khipu Repository](http://khipukamayuq.fas.harvard.edu/) (Harvard Khipu Database Project, Gary Urton et al.). Cord values were extracted from the public `collca.db` SQLite dump using the precomputed `cord.cord_value` field.
- **Quechua wordlist (curated, 557)**: Compiled from standard Cuzco-Collao Quechua reference dictionaries; manually selected for relevance to khipu values.
- **Quechua wordlist (auto-filtered, 1,298)**: Extracted from [Kaikki.org](https://kaikki.org/dictionary/Quechua/) (a structured Wiktionary extract by Tatu Ylonen), filtered through the pre-Columbian methodology above.
- **Categorization**: 15 semantic fields assigned via keyword heuristics over English glosses with manual refinement, plus POS-based fallback.

## Gematria system (quick reference)

```
0  N, Ñ                       Nasal → emptiness, negation
1  K, Q, Y                    Uvular/velar/semivowel
2  R, H                       Liquid + breath
3  L, Ll                      Lateral → flow
4  W                          Labial semivowel → wind
5  M                          Labial nasal → mother/earth
6  T, Ch, S                   Dental/palatal/sibilant
7  P                          Labial plosive
8  Kh, Qh, Ph, Th, Chh        Aspirates
9  K', Q', P', T', Ch'        Ejectives → compressed flow
```

Each digit becomes consonant + `a`. Example: cord value `75` → `P+a · M+a` → `pa-ma` / `pu-ma` → match: **puma** (75) — *puma, mountain lion*.

## Project structure

```
khipu-decoder/
├── index.html                        Landing page (SEO-optimized, language picker)
├── khipu-decoder_v11_en.html         English UI
├── khipu-decoder_v11.html            German UI
├── README.md                         This file
├── LICENSE                           MIT license
├── robots.txt                        Crawler directives (allows AI and search bots)
├── sitemap.xml                       Sitemap with hreflang alternates
├── .gitignore                        Excludes large binary files
│
├── data/
│   └── quechua_lexicon_v11.json      Open lexicon (1,855 entries) — reusable
│
└── tools/
    ├── prequechua_filter.py          Pre-Columbian filter module
    └── build_lexicon.py              Pipeline to rebuild lexicon from Kaikki/Wiktionary
```

## Reproducibility

To rebuild the lexicon from scratch:

```bash
# 1. Download Kaikki.org Quechua dump (~28 MB)
wget https://kaikki.org/dictionary/Quechua/kaikki.org-dictionary-Quechua.jsonl

# 2. Run the filter pipeline (from repo root)
python tools/build_lexicon.py \
  --input kaikki.org-dictionary-Quechua.jsonl \
  --merge data/quechua_lexicon_v11.json \
  --output data/quechua_lexicon_v12.json

# 3. Inspect filter behavior interactively
python tools/prequechua_filter.py
```

## Methodology notes

- **Cord-value extraction.** The 593 khipus from earlier versions used aggregated knot-cluster values; the 36 newly added khipus from `collca.db` use the precomputed `cord.cord_value` field directly. These two extraction methods may differ in marginal cases.
- **Word-value matching.** Match counts in the mindmap and word browser count distinct cord positions whose value equals the word's gematria value, regardless of cord ordinal hierarchy.
- **Filter precision.** Of 2,641 raw Kaikki entries: 51 phonological loanwords + 62 post-contact + 359 inflected forms + 209 excluded POS were rejected; 1,960 candidates passed, of which 1,298 were unique additions to the curated v10 lexicon.
- **Display caps.** The word browser shows up to 200 cells per filter; each cell expands up to 40 khipu chips. Real-world filters rarely exceed these.

## Technical notes

- Self-contained: ~840 KB single HTML file. Inline CSS, two `<script>` blocks (logic + data).
- No build step, no bundler, no framework. Vanilla JS + SVG.
- Tested in Chrome, Firefox, Safari, Edge (recent versions). The mindmap is responsive SVG and scales to mobile widths.
- The two HTML files are independent — choose your language and use one.

## Citation

If you use this tool or the lexicon in academic work, please cite:

```bibtex
@misc{balban2026khipu,
  author       = {Balban, Dogan},
  title        = {Khipu Decoder · Quechua Gematria: An Interactive Phonosemantic Tool for Andean Knot Records},
  year         = {2026},
  howpublished = {\url{https://github.com/dogan1908/khipu-decoder}},
  note         = {ORCID: 0009-0002-5052-6951}
}
```

The underlying khipu dataset is from the Harvard Khipu Database Project — please credit it independently when citing data, e.g.:

> Urton, G. & Brezine, C. J. (2005–2024). *Khipu Database*. Harvard University. http://khipukamayuq.fas.harvard.edu/

The Wiktionary/Kaikki extract:

> Ylonen, T. (2022). *Wiktextract: Wiktionary as Machine-Readable Structured Data*. LREC 2022, pp. 1317–1325.

## Acknowledgments

- The Open Khipu Repository team (Harvard) for making the khipu corpus publicly accessible.
- Tatu Ylonen and the Wiktextract project for structured Wiktionary data.
- Sabine Hyland and the broader khipu studies community for ongoing methodological work.
- The Quechua-speaking communities whose linguistic heritage this tool engages with.

## License

MIT — see [LICENSE](LICENSE).

The code in this repository is MIT-licensed. The khipu data extracted from the Open Khipu Repository remains under its original terms; please consult Harvard's Khipu Database Project for data licensing. Wiktionary-derived entries inherit Wiktionary's CC-BY-SA license; the lexicon JSON marks its sources for compliance.
