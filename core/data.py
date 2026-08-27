import json
from typing import Optional

from config import CONTENT_DIR
from utils.helpers import normalize_text

# Load JSON content datasets
with open(CONTENT_DIR / "talents.json", "r", encoding="utf-8") as jf:
    TALENTS_DATA: dict[str, dict] = json.load(jf)

with open(CONTENT_DIR / "abilities.json", "r", encoding="utf-8") as jf:
    ABILITIES_DATA: dict[str, dict] = json.load(jf)

with open(CONTENT_DIR / "blessings.json", "r", encoding="utf-8") as jf:
    BLESSINGS_DATA: dict[str, dict] = json.load(jf)

BLESSINGS_MAP: dict[str, dict] = BLESSINGS_DATA.get("blessings", {})
CULTS_MAP: dict[str, list[str]] = BLESSINGS_DATA.get("cults", {})
SL_BONUSES: list[dict] = BLESSINGS_DATA.get("sl_bonuses", [])

CULT_DISPLAY_NAMES: dict[str, str] = {
    "manann": "Manann (Bóg Mórz i Oceanów)",
    "morr": "Morr (Bóg Śmierci i Snów)",
    "myrmidia": "Myrmidia (Bogini Sztuki Wojennej i Strategii)",
    "ranald": "Ranald (Bóg Złodziei i Hazardu)",
    "rhya": "Rhya (Bogini Ziemi, Płodności i Wiosny)",
    "shallya": "Shallya (Bogini Miłosierdzia i Uzdrawiania)",
    "sigmar": "Sigmar (Patron Imperium)",
    "taal": "Taal (Bóg Natury, Dziczy i Zwierząt)",
    "ulryk": "Ulryk (Bóg Wojny, Zimy i Wilków)",
    "verena": "Verena (Bogini Mądrości i Sprawiedliwości)",
}

SL_BONUSES_TEXT = (
    "Każde **+2 PS** pozwala wybrać jeden z bonusów:\n"
    "• **Zasięg:** +6 metrów\n"
    "• **Liczba celów:** +1\n"
    "• **Czas trwania:** +6 rund *(niedostępne dla efektów natychmiastowych)*"
)

# ---------------------------
# PRECOMPUTED LOOKUPS & ALIASES
# ---------------------------

CULT_CLEAN_NAMES: dict[str, str] = {
    k: CULT_DISPLAY_NAMES.get(k, k).split(" (")[0] for k in CULTS_MAP
}

BLESSING_SHORT_NAMES: dict[str, str] = {
    k: v.get("name", k).replace("Błogosławieństwo ", "").strip() for k, v in BLESSINGS_MAP.items()
}

PRECOMPUTED_CULTS = [
    {
        "key": k,
        "display_name": disp,
        "clean_name": CULT_CLEAN_NAMES.get(k, k),
        "norm_key": normalize_text(k),
        "norm_display": normalize_text(disp),
        "norm_clean": normalize_text(CULT_CLEAN_NAMES.get(k, k)),
    }
    for k in CULTS_MAP
    for disp in [CULT_DISPLAY_NAMES.get(k, k)]
]

PRECOMPUTED_BLESSINGS = [
    {
        "key": k,
        "name": raw_name,
        "short_name": BLESSING_SHORT_NAMES.get(k, raw_name),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(raw_name),
        "norm_short": normalize_text(BLESSING_SHORT_NAMES.get(k, raw_name)),
    }
    for k, v in BLESSINGS_MAP.items()
    for raw_name in [v.get("name", k)]
]

PRECOMPUTED_TALENTS = [
    {
        "key": k,
        "name": data.get("name", k),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(data.get("name", k)),
    }
    for k, data in TALENTS_DATA.items()
]

PRECOMPUTED_ABILITIES = [
    {
        "key": k,
        "name": data.get("name", k),
        "norm_key": normalize_text(k),
        "norm_name": normalize_text(data.get("name", k)),
    }
    for k, data in ABILITIES_DATA.items()
]


def find_cult(query: str) -> Optional[str]:
    """Find cult key matching query (by key, full display name, deity name, or stem)."""
    q = normalize_text(query)
    for c in PRECOMPUTED_CULTS:
        if q == c["norm_key"] or q == c["norm_display"] or q == c["norm_clean"]:
            return c["key"]
    for c in PRECOMPUTED_CULTS:
        if (q in c["norm_key"] or q in c["norm_display"] or q in c["norm_clean"] or
            c["norm_key"] in q or c["norm_clean"] in q):
            return c["key"]
    for c in PRECOMPUTED_CULTS:
        if len(q) >= 3 and (q[:4] == c["norm_key"][:4] or c["norm_key"][:4] in q):
            return c["key"]
    return None


def find_blessing(query: str) -> Optional[str]:
    """Find blessing key matching query (by key, full name, short name, or stem)."""
    q = normalize_text(query)
    q_clean = q.replace("blogoslawienstwo", "").strip() or q
    for b in PRECOMPUTED_BLESSINGS:
        if (q == b["norm_key"] or 
            q == b["norm_name"] or 
            q == b["norm_short"] or
            q_clean == b["norm_key"] or
            q_clean == b["norm_short"]):
            return b["key"]
    for b in PRECOMPUTED_BLESSINGS:
        if (q in b["norm_key"] or q in b["norm_name"] or q in b["norm_short"] or
            q_clean in b["norm_key"] or q_clean in b["norm_short"] or
            b["norm_key"] in q or b["norm_short"] in q or b["norm_key"] in q_clean or b["norm_short"] in q_clean):
            return b["key"]
    for b in PRECOMPUTED_BLESSINGS:
        if len(q_clean) >= 4 and (q_clean[:4] == b["norm_key"][:4] or q_clean[:4] == b["norm_short"][:4]):
            return b["key"]
    return None
