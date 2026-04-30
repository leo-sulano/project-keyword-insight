"""Generates output/latest.csv and public/data.json with sample data for dashboard preview."""
import json
import os
import random
from datetime import datetime, timezone
import pandas as pd

random.seed(42)

SITES = [
    "https://lucky7evencasino.com",
    "https://fortuneplaycasino.net",
    "https://www.spinjo.io",
    "https://roostersbet.com",
    "https://www.spinsup.io/",
    "https://rollerocasino.com/",
    "https://rocketspincasino.com/",
    "https://www.playmojocasino.com/",
    "https://www.luckyvibecasino.com",
]

KEYWORDS_EN = [
    "online casino", "best online casino", "casino bonus", "free spins",
    "no deposit bonus", "casino slots", "live casino", "slot games",
    "casino games online", "real money casino", "casino welcome bonus",
    "online slots", "best casino bonuses", "casino free spins",
    "mobile casino", "casino jackpot", "poker online", "blackjack online",
    "roulette online", "casino deposit bonus", "casino review",
    "online gambling", "sports betting", "casino app", "crypto casino",
    "fast withdrawal casino", "vip casino", "high roller casino",
    "instant casino", "casino promo code",
]

KEYWORDS_AR = [
    "كازينو اون لاين", "افضل كازينو", "العاب كازينو", "كازينو مجاني",
    "بونص كازينو", "العاب قمار اونلاين", "كازينو عربي", "ربح المال",
    "العاب ربحية", "كازينو بالعربي", "مكافأة ترحيبية", "العاب روليت",
]

rows = []
for site in SITES:
    n_kw = random.randint(15, 40)
    keywords = random.sample(KEYWORDS_EN, min(n_kw, len(KEYWORDS_EN)))
    if random.random() > 0.4:
        keywords += random.sample(KEYWORDS_AR, random.randint(2, 5))

    for kw in keywords:
        for country in ["SAU", "KWT"]:
            impressions = random.randint(20, 3000)
            position = round(random.uniform(1.5, 35.0), 1)
            ctr = round(max(0.1, (35 - position) / 35 * random.uniform(2, 15)), 2)
            clicks = max(1, int(impressions * ctr / 100))
            rows.append({
                "site": site,
                "keyword": kw,
                "country": country,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "avg_position": position,
            })

AR = "؀-ۿݐ-ݿ"
def detect_language(kw):
    import re
    if re.search(f"[{AR}]", kw): return "ar"
    if re.search(r"[a-zA-Z]", kw): return "en"
    return "other"

df = pd.DataFrame(rows).sort_values("clicks", ascending=False).reset_index(drop=True)
df["language"] = df["keyword"].apply(detect_language)

os.makedirs("output", exist_ok=True)
os.makedirs("public", exist_ok=True)

df.to_csv("output/latest.csv", index=False)

payload = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "rows": df.to_dict(orient="records"),
}
with open("public/data.json", "w", encoding="utf-8") as fh:
    json.dump(payload, fh, ensure_ascii=False)

print(f"Written {len(df)} rows to output/latest.csv and public/data.json")
