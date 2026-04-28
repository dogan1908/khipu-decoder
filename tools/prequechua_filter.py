#!/usr/bin/env python3
"""
PRE-COLUMBIAN QUECHUA WORD FILTER & GEMATRIA TOOLKIT
=====================================================
Filters Quechua wordlists for words likely of pre-Columbian origin
(i.e., not loanwords from Spanish post-1532 contact).

Phonological markers used:
  - /f/ does not exist in pre-Columbian Quechua
  - /b/, /d/, /g/ word-initially = loanword
  - Spanish consonant clusters at word start (tr, pl, pr, bl, br, etc.)
  - Spanish derivational suffixes (-ción, -mente, -dad, -tad)
  - Diminutives (-ito, -ita, -illo, -illa) in long words

Semantic markers (post-contact concepts):
  - English glosses referring to post-contact items: alcohol, apricot,
    horse, cow, sheep, gun, book, pope, etc.

Scientific basis:
  - Cerrón-Palomino (1987): "Lingüística Quechua"
  - Adelaar & Muysken (2004): "The Languages of the Andes"
  - Mannheim (1991): "The Language of the Inka"

Author: Dogan Balban (2026), MIT License
"""
import re

NATIVE_OK = {
    "killa", "lliklla", "wachilla", "kasilla",
    "tucricuc", "tukrikuq", "qillqa", "killka",
    "mama killa", "tayta inti", "pacha mama",
}

SPANISH_CLUSTERS = ["tr", "pl", "pr", "bl", "br", "cr", "dr",
                    "fl", "fr", "gl", "gr"]

SPANISH_SUFFIXES_HARD = ["cion", "sion", "mente", "idad", "dad", "tad"]
SPANISH_DIMINUTIVES = ["ito", "ita", "illo", "illa"]

POST_CONTACT_GLOSSES = {
    "horse", "cow", "cattle", "sheep", "goat", "pig", "donkey", "mule",
    "chicken", "rooster", "hen", "pigeon",
    "wheat", "barley", "rice", "olive", "grape", "wine",
    "apple", "peach", "pear", "plum", "apricot", "cherry", "lemon", "orange",
    "banana", "mango", "papaya", "pineapple", "almond", "walnut",
    "onion", "garlic", "lettuce", "cabbage", "carrot",
    "computer", "robot", "telephone", "television", "radio", "internet",
    "wikipedia", "wiktionary", "car", "bicycle", "airplane", "train",
    "battery", "electricity",
    "alcohol", "petroleum", "plastic",
    "bible", "church", "priest", "pope", "bishop", "monk", "saint",
    "angel", "devil", "christmas", "easter",
    "gun", "rifle", "pistol", "cannon", "bomb",
    "doctor", "engineer", "lawyer", "professor", "president",
    "school", "university", "library", "hospital", "bank",
    "money", "dollar", "peso",
    "europe", "africa", "asia", "australia",
    "germany", "france", "spain", "italy", "england", "russia", "china",
    "japan", "egypt", "greece", "rome",
    "bee",  # native bees use "wayrunqu", "abiha" is loan from abeja
}


def classify_word(quechua, english=""):
    """Return {'verdict', 'flags', 'confidence'}."""
    q = quechua.lower().strip()
    eng = (english or "").lower().strip()
    flags = []

    if q in NATIVE_OK:
        return {"verdict": "native_likely",
                "flags": ["whitelisted"],
                "confidence": "high"}

    # Layer A: phonemic markers
    if "f" in q:
        flags.append("has_f")
    if re.search(r"^b", q):
        flags.append("initial_b")
    if re.search(r"^d", q):
        flags.append("initial_d")
    if re.search(r"^g[aeiou]", q):
        flags.append("initial_g")
    if re.search(r"(?<![mn])[aeiouaeiou][bdg][aeiouaeiou]", q):
        flags.append("intervocalic_voiced")

    for c in SPANISH_CLUSTERS:
        if q.startswith(c):
            flags.append(f"initial_cluster_{c}")
            break

    if len(q) >= 6:
        for suffix in SPANISH_SUFFIXES_HARD:
            if q.endswith(suffix):
                flags.append(f"suffix_{suffix}")
                break
        for suffix in SPANISH_DIMINUTIVES:
            if q.endswith(suffix) and len(q) > 6:
                flags.append("possible_diminutive")
                break

    # Layer D: semantic markers
    if eng:
        eng_words = set(re.findall(r"[a-z]+", eng))
        for marker in POST_CONTACT_GLOSSES:
            if marker in eng_words:
                flags.append(f"post_contact_gloss_{marker}")
                break
        if "alternative spelling of" in eng or "alternative form of" in eng:
            flags.append("alt_spelling")
        if any(p in eng for p in ("first-person", "second-person", "third-person")):
            flags.append("inflected_form")
        if any(p in eng for p in ("future participle", "present perfect", "genitive of",
                                   "past participle", "imperative of")):
            flags.append("inflected_form")

    HARD = {"has_f", "initial_b", "initial_d", "initial_g", "intervocalic_voiced"}
    HARD.update(f"initial_cluster_{c}" for c in SPANISH_CLUSTERS)
    HARD.update(f"suffix_{s}" for s in SPANISH_SUFFIXES_HARD)

    is_loan_phon = any(f in HARD for f in flags)
    is_loan_sem = any(f.startswith("post_contact_gloss_") for f in flags)
    is_inflected = any(f in ("alt_spelling", "inflected_form") for f in flags)

    if is_loan_phon:
        return {"verdict": "loanword", "flags": flags, "confidence": "high"}
    if is_loan_sem:
        return {"verdict": "post_contact", "flags": flags, "confidence": "medium"}
    if is_inflected:
        return {"verdict": "duplicate_or_inflected", "flags": flags, "confidence": "high"}
    if "possible_diminutive" in flags:
        return {"verdict": "suspicious", "flags": flags, "confidence": "low"}
    return {"verdict": "native_likely", "flags": flags, "confidence": "high"}


def is_excluded_pos(pos):
    EXCLUDED = ["Proper name", "Suffix", "Character", "Determiner",
                "Conjunction", "Particle", "Postposition", "Preposition"]
    return any(pos.startswith(x) for x in EXCLUDED)


# ─── Quechua Phonosemantic Gematria (Balban 2026) ──────────────────────────
GEMATRIA_MAP = {
    "n": 0, "n~": 0, "ñ": 0,
    "k": 1, "q": 1, "y": 1,
    "r": 2, "h": 2,
    "l": 3,
    "w": 4,
    "m": 5,
    "t": 6, "s": 6,
    "p": 7,
}


def compute_gematria(word):
    """Compute gematria value using Balban 2026 system. Returns int or None."""
    w = word.lower().strip().replace(" ", "")
    digits = []
    i = 0
    while i < len(w):
        three = w[i:i+3]
        two = w[i:i+2]
        if three == "chh":
            digits.append(8); i += 3; continue
        if two in ("kh", "qh", "ph", "th"):
            digits.append(8); i += 2; continue
        if three == "ch'":
            digits.append(9); i += 3; continue
        if i+1 < len(w) and w[i+1] == "'" and w[i] in "kqpt":
            digits.append(9); i += 2; continue
        if two == "ll":
            digits.append(3); i += 2; continue
        if two == "ch":
            digits.append(6); i += 2; continue
        if two == "sh":
            digits.append(6); i += 2; continue
        c = w[i]
        if c in GEMATRIA_MAP:
            digits.append(GEMATRIA_MAP[c])
        i += 1
    if not digits:
        return None
    return int("".join(str(d) for d in digits))


# ─── Auto-categorization ────────────────────────────────────────────────────
CAT_KEYWORDS = {
    "water":   ["water", "rain", "river", "lake", "sea", "wet", "drink", "thirst"],
    "plant":   ["plant", "tree", "flower", "leaf", "grass", "seed", "fruit", "root",
                "wood", "forest", "harvest", "grain", "quinoa", "coca", "potato",
                "corn", "maize", "tuber", "branch", "stem", "achira", "begonia"],
    "animal":  ["animal", "bird", "fish", "snake", "frog", "puma", "fox", "deer",
                "rabbit", "condor", "eagle", "duck", "guinea pig", "llama", "alpaca",
                "vicuna", "spider", "insect", "feather", "wing", "tail", "wool",
                "weasel", "opossum", "turkey", "hummingbird", "mountain lion"],
    "body":    ["head", "hand", "foot", "eye", "ear", "nose", "mouth", "tongue",
                "tooth", "heart", "blood", "bone", "skin", "hair", "face", "arm",
                "leg", "finger", "belly", "back", "chest", "navel"],
    "human":   ["man ", "woman", "child", "boy", "girl", "father", "mother", "son ",
                "daughter", "brother", "sister", "friend", "people", "family",
                "uncle", "aunt", "old man", "old woman", "lord", "chief"],
    "spirit":  ["god", "spirit", "soul", "sacred", "holy", "temple", "sun", "moon",
                "star", "sky", "huaca", "ancestor", "deity", "goddess"],
    "tool":    ["tool", "pot", "jar", "cup", "knife", "rope", "thread", "cloth",
                "weave", "khipu", "quipu", "house", "door", "wall", "roof", "bridge",
                "spindle", "needle", "loom", "bed", "bundle", "yarn"],
    "place":   ["mountain", "hill", "valley", "plain", "rock", "stone", "cave",
                "land", "place", "town", "village", "puna", "altiplano", "wilderness"],
    "time":    ["day", "night", "morning", "evening", "dawn", "year", "season", "time"],
    "number":  ["one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten", "hundred", "thousand", "many", "much", "eighty"],
    "action":  ["to walk", "to go", "to come", "to eat", "to drink", "to sleep",
                "to die", "to live", "to make", "to work", "to give", "to take",
                "to see", "to hear", "to begin", "to start", "to lead", "to twist",
                "to chew", "to laugh", "to dawn", "to sneeze", "to choose",
                "to ripen", "to swell", "to harvest", "to support", "to share",
                "to disrobe", "to grasp", "to smell", "to carry", "to adorn"],
    "quality": ["good", "bad", "big", "small", "tall", "short", "long", "wide",
                "thick", "hot", "cold", "dry", "wet", "strong", "weak", "old",
                "new", "red", "green", "blue", "yellow", "black", "white",
                "naked", "bare", "ripe", "twisted", "sad"],
    "food":    ["food", "meal", "bread", "meat", "soup", "chicha", "cook", "salt",
                "honey", "flour"],
    "weather": ["cloud", "wind", "storm", "snow", "ice", "rainbow"],
    "social":  ["law", "rule", "tribute", "work", "labor", "duty", "trade", "feast",
                "song", "story", "language", "share"],
}

CAT_LABELS = {
    "water":   ["water", "#3b82c4"],
    "plant":   ["plant", "#56a35a"],
    "animal":  ["animal", "#a06030"],
    "body":    ["body", "#c44470"],
    "human":   ["human", "#9060c0"],
    "spirit":  ["spirit", "#d0a020"],
    "tool":    ["tool", "#808080"],
    "place":   ["place", "#8b5e3c"],
    "time":    ["time", "#5070a0"],
    "number":  ["number", "#404040"],
    "action":  ["action", "#7050b0"],
    "quality": ["quality", "#c08020"],
    "food":    ["food", "#d06030"],
    "weather": ["weather", "#7090a0"],
    "social":  ["social", "#205050"],
    "other":   ["other", "#606060"],
}


def categorize(quechua, english):
    eng = (english or "").lower()
    if not eng:
        return "other"
    scores = {}
    for cat, kw_list in CAT_KEYWORDS.items():
        score = 0
        for kw in kw_list:
            if kw in eng:
                score += len(kw)
        if score > 0:
            scores[cat] = score
    if not scores:
        return "other"
    return max(scores.items(), key=lambda x: x[1])[0]


if __name__ == "__main__":
    test = [
        ("puma", "puma, mountain lion"),
        ("inti", "sun"),
        ("killa", "moon"),
        ("plasa", "plaza"),
        ("alkul", "alcohol"),
        ("abiha", "bee"),
        ("albarikuki", "apricot"),
        ("achira", "achira plant, purple arrowroot"),
        ("q'illu", "yellow"),
        ("puriy", "to walk"),
        ("hatun", "big"),
        ("akan", "third-person singular present indicative of akay"),
        ("antaniqiq", "Computer"),
        ("dyus", "God"),
        ("aklla", "virgin selected for religious service in the Inca Empire"),
    ]
    print(f"{'Word':<15} {'Verdict':<25} {'Cat':<10} {'Gem':<8} Flags")
    print("─" * 100)
    for q, eng in test:
        r = classify_word(q, eng)
        cat = categorize(q, eng)
        g = compute_gematria(q)
        flagstr = ",".join(r["flags"][:3]) if r["flags"] else ""
        print(f"{q:<15} {r['verdict']:<25} {cat:<10} {g!s:<8} {flagstr}")
