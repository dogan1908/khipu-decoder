# 🪢 Khipu Decoder · Quechua Gematria

> An interactive single-file web tool for exploring Andean knot records (khipus) through a phonosemantic gematria lens.

![Status](https://img.shields.io/badge/version-v10-orange) ![License](https://img.shields.io/badge/license-MIT-green) ![Khipus](https://img.shields.io/badge/khipus-629-blue) ![Words](https://img.shields.io/badge/Quechua%20words-557-purple)

## Overview

The Khipu Decoder lets you browse 629 historical khipus from the Open Khipu Repository / Harvard Khipu Database alongside a curated list of 557 Quechua words categorized into 15 semantic fields. The central premise is a phonosemantic gematria mapping of Quechua consonants to digits 0–9 (Dogan Balban, 2026), in which a knot value such as `75` decodes as `P+a · M+a → puma`.

Two coordinated panels make the relationship between knots and words explorable:

- **Khipu values** — every cord value of a selected khipu is clickable; clicking one runs a full gematria decomposition (digits → consonant classes → syllables → matching Quechua words) with category badges.
- **Word browser** — all 557 Quechua words filtered by category and free-text search; each word lists every khipu that contains its gematria value as a clickable chip that jumps directly to the corresponding cord in the value grid.
- **Mindmap** — radial SVG visualization. By default it shows the global word distribution across consonant classes and categories. **As soon as a khipu is selected, the mindmap re-renders to show only the words whose gematria value occurs in that khipu**, with cluster sizes scaled by occurrence frequency.

## Live demo

🌐 **[https://dogan1908.github.io/khipu-decoder/](https://dogan1908.github.io/khipu-decoder/)**

The landing page (`index.html`) lets you choose between the English and German editions. Both are single self-contained HTML files with no runtime dependencies and can also be downloaded and run fully offline.

## Features

| Panel | What it does |
|---|---|
| Khipu list | 629 khipus searchable by ID, provenance, museum or OKR number. Search also matches Quechua words/English meanings — khipus containing the matching value are flagged with ⚡N counters. |
| Gematria system | Three switchable systems: Quechua (Dogan, UR281-verified), Katapayadi (Sanskrit), and an editable custom system. |
| Knot values | All cord values for the selected khipu with structural hints (markers, checksum candidates, repeated values). |
| Decode panel | Per-value digit breakdown, all syllable combinations, exact / nearby (±5) / leading-digit word matches with category badges. |
| Full-text attempt | Whole-khipu narrative, color-coded by structural role: word matches, syllable guesses, repeated markers, Σ-checksums. |
| Word browser | 557 Quechua words, filtered by category + search. Each word shows the khipus it appears in as clickable chips. |
| Mindmap | Khipu-aware radial SVG. Toggle 🎯 Khipu / 🌐 Global. Click any cluster → filters word browser to that category. |

## Data sources

- **Khipu corpus**: [Open Khipu Repository](http://khipukamayuq.fas.harvard.edu/) (Harvard Khipu Database Project, Gary Urton et al.). Cord values were extracted from the public `collca.db` SQLite dump using the precomputed `cord.cord_value` field.
- **Quechua wordlist**: Compiled from standard Cuzco-Collao Quechua reference dictionaries; gematria values computed using the Quechua phonosemantic system from Balban (2026).
- **Categorization**: 15 semantic fields (water, plant, animal, body, human, spirit, tool, place, time, number, action, quality, food, weather, social, other) assigned via keyword heuristics over English glosses with manual refinement.

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
├── index.html                  Landing page (SEO-optimized, language picker)
├── khipu-decoder_v10_en.html   English UI
├── khipu-decoder_v10.html      German UI
├── README.md                   This file
├── LICENSE                     MIT license
├── robots.txt                  Crawler directives (allows AI and search bots)
├── sitemap.xml                 Sitemap with hreflang alternates
├── .gitignore                  Excludes the source SQLite (already embedded in HTML)
└── docs/                       (optional: screenshots, methodology notes)
```

## Methodology notes

- **Cord-value extraction.** The 593 khipus from earlier versions used aggregated knot-cluster values; the 36 newly added khipus from `collca.db` use the precomputed `cord.cord_value` field directly. These two extraction methods may differ in marginal cases (cords with non-standard knot patterns); both sets are otherwise consistent.
- **Word-value matching.** Match counts in the mindmap and word browser count distinct cord positions whose value equals the word's gematria value, regardless of cord ordinal hierarchy.
- **Category assignment.** Heuristic over English glosses with ~60 manual overrides; some assignments are ambiguous (e.g., `tampu` → place vs tool) and reflect the most prominent semantic role.
- **Display caps.** The word browser shows up to 200 cells per filter; each cell expands up to 40 khipu chips. Real-world filters rarely exceed these.

## Technical notes

- Self-contained: ~750 KB single HTML file, ~770 KB English version. Inline CSS, two `<script>` blocks (logic + data).
- No build step, no bundler, no framework. Vanilla JS + SVG.
- Tested in Chrome, Firefox, Safari, Edge (recent versions). The mindmap is responsive SVG and scales to mobile widths.
- The two HTML files are independent — choose your language and use one.

## Citation

If you use this tool in academic work, please cite:

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

## Acknowledgments

- The Open Khipu Repository team (Harvard) for making the khipu corpus publicly accessible.
- Sabine Hyland and the broader khipu studies community for ongoing methodological work.
- The Quechua-speaking communities whose linguistic heritage this tool engages with.

## License

MIT — see [LICENSE](LICENSE).

The code in this repository is MIT-licensed. The khipu data extracted from the Open Khipu Repository remains under its original terms; please consult Harvard's Khipu Database Project for data licensing.
