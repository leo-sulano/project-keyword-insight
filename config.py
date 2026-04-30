SITES = [
    "https://lucky7evencasino.com",
    "https://lucky7evencasino.org",
    "http://lucky7evencasino.io",
    "https://fortuneplaycasino.net",
    "https://fortuneplay.casino/",
    "https://fortuneplay.io",
    "https://www.spinjo.io",
    "https://www.spinjocasino.com",
    "https://www.casinospinjo.com",
    "https://roosters.bet",
    "https://roostersbet.com",
    "https://casinoroosters.com",
    "https://www.spinsup.io/",
    "https://spinsupcasino.com/",
    "https://casinospinsup.com/",
    "https://rollero.io/",
    "https://rollerocasino.com/",
    "https://www.casinorollero.com/",
    "https://rocketspin.io/",
    "https://rocketspincasino.com/",
    "https://www.casinorocketspin.com/",
    "https://www.playmojo.io/",
    "https://www.playmojocasino.com/",
    "https://casinoplaymojo.com/",
    "https://www.luckyvibe.io/",
    "https://www.luckyvibecasino.com",
    "https://www.casinoluckyvibe.com",
]

START_DATE = "2026-02-01"
END_DATE = "2026-04-30"
COUNTRIES = ["SAU", "KWT"]

BRAND_TERMS = [
    # lucky7even (including variant: lucky 7)
    "lucky7even", "lucky7", "lucky 7", "lucky 7 even", "lucky 7even", "lucky seven casino",
    # fortuneplay (including typos: fortunplay)
    "fortuneplay", "fortunplay", "fortune play", "fortuneplay casino", "fortune play casino",
    # spinjo
    "spinjo", "spin jo", "spinjo casino", "spin jo casino",
    # roosters (including common typos: roster/rosterbet)
    "rooster", "roosters", "roster", "roosterbet", "roostersbet", "rosterbet",
    "rooster bet", "roster bet", "roosters bet", "roosters casino", "casinoroosters",
    "روستر", "روستر بت",
    # spinsup (including variant: spin up)
    "spinsup", "spin sup", "spins up", "spin up", "spinsupcasino", "spinsup casino",
    # rollero
    "rollero", "rollero casino", "rollerocasino", "casinorollero",
    # rocketspin
    "rocketspin", "rocket spin", "rocketspin casino", "rocket spin casino", "casinorocketspin",
    # playmojo
    "playmojo", "playmogo", "play mojo", "playmojo casino", "play mojo casino", "casinoplaymojo",
    # luckyvibe
    "luckyvibe", "lucky vibe", "luckyvibe casino", "lucky vibe casino", "casinoluckyvibe",
]

NAVIGATIONAL_TERMS = [
    "login", "log in", "register", "sign up", "signup",
    "homepage", "home page", "official site", "official website",
    "download", "mobile app",
]

MIN_IMPRESSIONS = 5

CREDENTIALS_FILE = "credentials/client_secrets.json"
TOKEN_FILE = "credentials/token.pickle"
OUTPUT_DIR = "output"
LATEST_CSV = "output/latest.csv"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
