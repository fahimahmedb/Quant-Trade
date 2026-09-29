import re
CLASSES=[
 ("TWEETS", r"tweet|posts? on x\b|# of posts|elon.*post|trump.*post|truth social"),
 ("BOXOFFICE", r"box office|opening weekend|gross"),
 ("MUSIC", r"spotify|billboard|streams|monthly listeners|#1 song|album"),
 ("SCREEN", r"rotten tomatoes|imdb|netflix|top 10|metacritic|episode"),
 ("APP_RANK", r"app store|top app|google trends|downloads"),
 ("MENTIONS", r"\bsay|\bsays?\b|mention|utter|speech|press conference|state of the union|debate"),
 ("ECON_DATA", r"cpi|inflation|jobs report|payroll|unemployment|gdp|fed |fomc|rate cut|interest rate|bps|initial claims|pce"),
 ("CORP_EVENT", r"microstrategy|strategy .*btc|buy.*bitcoin|earnings|ipo|announce|launch|release|acquire|merger|8-k|filing|listed|listing"),
 ("AI_TECH", r"\bai\b|openai|gpt|model|chatbot|lmarena|arena|benchmark|apple|iphone|tesla|spacex|starship|nvidia"),
 ("CRYPTO_PRICE", r"bitcoin|btc|ethereum|\beth\b|solana|\bsol\b|price|above|below|\$\d"),
 ("SPORTS", r"\bvs\.?\b|win the|nfl|nba|mlb|nhl|ufc|f1|grand prix|match|game|champion|premier league|world cup|series"),
 ("POLITICS", r"election|president|senate|house|governor|nominee|poll|approval|impeach|shutdown|bill|congress|prime minister|parliament"),
 ("WEATHER", r"temperature|°|highest temp|lowest temp|rain|snow|hurricane|storm"),
]
def classify(t):
    tl=t.lower()
    for name,rx in CLASSES:
        if re.search(rx, tl): return name
    return "OTHER"
