#!/usr/bin/env python3
"""
build_lexicon.py — Build a curated pre-Columbian Quechua lexicon
=================================================================
Downloads Quechua wordlists from Kaikki.org (Wiktionary), filters them
through the pre-Columbian phonological + semantic filter, computes
gematria values, and emits a clean JSON lexicon ready for the
khipu decoder or any other use.

Usage:
    pip install requests
    python build_lexicon.py            # uses default kaikki source
    python build_lexicon.py --output lexicon.json
    python build_lexicon.py --include-suspicious

Pre-existing wordlist can be merged with --merge:
    python build_lexicon.py --merge existing_words.json

Author: Dogan Balban (2026), MIT License
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

# Local module
from prequechua_filter import (
    classify_word, compute_gematria, categorize, is_excluded_pos,
    CAT_LABELS,
)

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


# All 47 page URLs at Kaikki for Quechua
KAIKKI_PAGES = [
    "Alhirya--Ilanda.html", "Inca--Tayiksuyu.html", "Th--allchay.html",
    "alli--amikuy.html", "amu--apaysiy.html", "api--asut%27iy.html",
    "asuy--aymuray.html", "ayni--ch%27iquy.html", "ch%27iri--chahraysiy.html",
    "chaka--chawpichay.html", "chay--chipchi.html", "chiqa--chunta.html",
    "chupa--hamut%27ay.html", "hamuy--hawkay.html", "haya--hunyay.html",
    "huq--imantin.html", "imap--isqun%20chunka.html",
    "i%C3%B1i--juch%27uy%20wasi.html",
    "juk--kawsay.html", "kay--kichkay.html", "kiki--kurku.html",
    "kuru--liyiy.html", "ll--llulmiy.html", "lluna--mati.html",
    "may--mishi.html", "misi--nanay.html", "nin--pampay.html",
    "pana--phu%C3%B1i.html", "pi--pukyuy.html", "puma--qallu.html",
    "qam--qellqay.html", "qh--qipiy.html", "qiru--raphra.html",
    "rapi--rumpiy.html", "runa--shullpinay.html", "sh%CA%BC--siriy.html",
    "sisa--suysuy.html", "suyu--tantay.html", "tapu--traskiy.html",
    "tr%CA%BC--uchpay.html", "uhu--uruya.html", "usa--wantuy.html",
    "wanu--waskha%20p%27itaykachay.html", "wata--wuru.html", "y--yawyay.html",
    "yaya--%C3%B1awsa.html", "%C3%B1a%C3%B1a--%C5%9Fongo.html",
]
KAIKKI_BASE = "https://kaikki.org/dictionary/Quechua/words/"


def fetch_page(url, retries=3, delay=1.0):
    """Fetch one Kaikki HTML page."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; KhipuDecoder/1.0)"}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt+1} after {e}", file=sys.stderr)
            time.sleep(delay * (attempt + 1))


def parse_kaikki_page(html):
    """Extract entries from a Kaikki word-list HTML page."""
    entries = []
    # Each entry is a line like:
    #   * [word (POS)](URL) Definition text...
    #   * [word (N senses)](URL)
    # We match the markdown bullet pattern in HTML (after rendering)
    # Pattern in raw HTML: <li><a href="...">word</a> ...</li>
    # Easier: parse the markdown-ish text representation
    # Look for: [word (PoS)](href) definition
    pattern = re.compile(
        r'\*\s*\[([^\]]+?)\s*\((.+?)\)\]\(([^)]+)\)\s*(.*?)$',
        re.MULTILINE
    )
    # Better: match <li><a href="...">WORD</a> (POS) definition</li> or
    # the simpler markdown that web tools produce
    for line in html.split('\n'):
        m = re.match(r'\s*\*\s*\[(.+?)\s*\((.+?)\)\]\(([^)]+)\)\s*(.*)', line)
        if m:
            word = m.group(1).strip()
            pos = m.group(2).strip()
            url = m.group(3).strip()
            defn = m.group(4).strip()
            # If defn is empty (e.g., "(2 senses)"), keep empty
            entries.append({
                "word": word,
                "pos": pos,
                "url": url,
                "definition": defn,
            })
    return entries


def fetch_all_pages(verbose=True):
    """Fetch all 47 pages and return combined entries."""
    all_entries = []
    for i, page in enumerate(KAIKKI_PAGES, 1):
        url = KAIKKI_BASE + page
        if verbose:
            print(f"[{i:2}/{len(KAIKKI_PAGES)}] fetching {page}", file=sys.stderr)
        try:
            html = fetch_page(url)
            entries = parse_kaikki_page(html)
            for e in entries:
                e["source_page"] = page
            all_entries.extend(entries)
            if verbose:
                print(f"      → {len(entries)} entries", file=sys.stderr)
        except Exception as e:
            print(f"      ✗ failed: {e}", file=sys.stderr)
        time.sleep(0.3)  # be nice to kaikki.org
    return all_entries


def process_entries(entries, include_suspicious=False):
    """Filter, classify, compute gematria, categorize."""
    seen_words = set()
    output = []
    stats = {"total": 0, "native_likely": 0, "loanword": 0, "post_contact": 0,
             "duplicate_or_inflected": 0, "suspicious": 0, "excluded_pos": 0,
             "no_gematria": 0, "deduped": 0}
    
    for entry in entries:
        stats["total"] += 1
        word = entry["word"]
        pos = entry["pos"]
        defn = entry.get("definition", "")
        
        # Skip excluded POS
        if is_excluded_pos(pos):
            stats["excluded_pos"] += 1
            continue
        
        # Dedup by word+POS
        key = f"{word.lower()}|{pos}"
        if key in seen_words:
            stats["deduped"] += 1
            continue
        seen_words.add(key)
        
        # Classify
        result = classify_word(word, defn)
        verdict = result["verdict"]
        stats[verdict] = stats.get(verdict, 0) + 1
        
        # Skip non-native unless asked to include
        if verdict in ("loanword", "post_contact", "duplicate_or_inflected"):
            continue
        if verdict == "suspicious" and not include_suspicious:
            continue
        
        # Compute gematria
        gem = compute_gematria(word)
        if gem is None:
            stats["no_gematria"] += 1
            continue
        
        # Categorize
        cat = categorize(word, defn)
        
        output.append({
            "quechua": word,
            "english": defn,
            "pos": pos,
            "gematria": gem,
            "category": cat,
            "verdict": verdict,
            "flags": result["flags"],
            "source": "kaikki.org/Wiktionary",
            "source_page": entry.get("source_page", ""),
        })
    
    return output, stats


def merge_existing(new_entries, existing_path):
    """Merge with an existing user-curated wordlist (JSON)."""
    if not Path(existing_path).exists():
        print(f"  No existing file at {existing_path}, skipping merge", file=sys.stderr)
        return new_entries
    
    with open(existing_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
    
    # Existing file might be a list of [val, quechua, english, category] tuples
    # or a list of dicts. Normalize.
    existing_words = set()
    if existing and isinstance(existing[0], list):
        # Old format: tuples
        for entry in existing:
            existing_words.add(entry[1].lower() if len(entry) > 1 else "")
    else:
        for entry in existing:
            if isinstance(entry, dict) and "quechua" in entry:
                existing_words.add(entry["quechua"].lower())
    
    # Add new entries that don't overlap
    merged = list(existing) if existing and isinstance(existing[0], dict) else []
    
    # Convert existing tuples to dicts if needed
    if existing and isinstance(existing[0], list):
        for tup in existing:
            if len(tup) >= 3:
                merged.append({
                    "quechua": tup[1],
                    "english": tup[2],
                    "gematria": tup[0],
                    "category": tup[3] if len(tup) > 3 else "other",
                    "verdict": "native_likely",
                    "flags": ["user_curated"],
                    "source": "user_curated_v10",
                })
    
    added = 0
    for entry in new_entries:
        if entry["quechua"].lower() not in existing_words:
            merged.append(entry)
            existing_words.add(entry["quechua"].lower())
            added += 1
    
    print(f"  Merge: {added} new entries added (total: {len(merged)})", file=sys.stderr)
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="lexicon.json", help="Output JSON file")
    ap.add_argument("--cache", default="kaikki_cache.json",
                    help="Cache fetched Kaikki entries here")
    ap.add_argument("--merge", help="Existing JSON to merge with")
    ap.add_argument("--include-suspicious", action="store_true",
                    help="Include words flagged as suspicious")
    ap.add_argument("--no-fetch", action="store_true",
                    help="Skip fetching, use cache only")
    args = ap.parse_args()
    
    cache_path = Path(args.cache)
    if cache_path.exists() and args.no_fetch:
        print(f"Loading cached entries from {args.cache}", file=sys.stderr)
        with open(cache_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    else:
        print(f"Fetching {len(KAIKKI_PAGES)} pages from kaikki.org...", file=sys.stderr)
        entries = fetch_all_pages()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=1)
        print(f"Cached to {args.cache} ({len(entries)} entries)", file=sys.stderr)
    
    print(f"\nProcessing {len(entries)} raw entries...", file=sys.stderr)
    output, stats = process_entries(entries, include_suspicious=args.include_suspicious)
    
    print("\n=== Statistics ===", file=sys.stderr)
    for k, v in stats.items():
        print(f"  {k:<25} {v:>6}", file=sys.stderr)
    print(f"\n  → {len(output)} entries kept", file=sys.stderr)
    
    if args.merge:
        output = merge_existing(output, args.merge)
    
    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=1)
    print(f"\nWritten {args.output} ({len(output)} entries)", file=sys.stderr)
    
    # Summary
    from collections import Counter
    cats = Counter(e["category"] for e in output)
    print("\nCategory distribution:", file=sys.stderr)
    for cat, count in cats.most_common():
        print(f"  {cat:<12} {count:>5}", file=sys.stderr)


if __name__ == "__main__":
    main()
