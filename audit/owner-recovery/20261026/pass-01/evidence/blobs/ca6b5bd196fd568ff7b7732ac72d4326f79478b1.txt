# Sources et provenance

## Datasets copiés dans ce dossier (récupérés le 2026-09-24 via raw.githubusercontent.com)
- `shiller_sp500_monthly.csv`: https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv (données Shiller, prix mensuels moyens, 1871 à 2026-08). Caveats : ce sont des moyennes mensuelles, d'où le décalage de 2 mois appliqué au signal ; les derniers mois n'ont pas de dividendes et sont exclus ; les séries sont révisées et non vintagées.
- `vix_daily.csv`: https://raw.githubusercontent.com/datasets/finance-vix/main/data/vix-daily.csv (miroir CBOE, 1990-01-02 à 2026-09-22). Caveat : miroir tiers, non vérifié contre le CBOE.
- sha256 : voir `sha256sum *.csv` dans ce dossier.

## Littérature principale
- Bailey & López de Prado, Deflated Sharpe Ratio : https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- Probabilité de sur-apprentissage du backtest : https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- Harvey, Liu & Zhu, seuil t>3 : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314
- McLean & Pontiff, décroissance post-publication : https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365
- Anomalies après coûts : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3073681
- Moskowitz, Ooi & Pedersen, TSMOM : https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf
- AQR, un siècle de trend following : https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing
- Lou, Polk & Skouras, overnight/intraday : https://personal.lse.ac.uk/polk/research/TugOfWar.pdf
- Carry de funding crypto : https://arxiv.org/pdf/2510.14435
- Whelan, économie du marché Kalshi : https://www.karlwhelan.com/Papers/Kalshi.pdf ; https://cepr.org/voxeu/columns/economics-kalshi-prediction-market
- Biais favori-longshot sur Polymarket : https://arxiv.org/pdf/2609.12878
- Frais Kalshi : https://help.kalshi.com/en/articles/13823805-fees
- Arbitrage Polymarket 39,7 M$ : https://www.cryptopolitan.com/research-reveals-40-m-exploit-polymarket/
- Frais dynamiques Polymarket : https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/
- Différences de règles de settlement Kalshi/Polymarket : https://www.oddsshopper.com/articles/prediction-markets/kalshi-vs-polymarket-settlement-rules
- Crash du 10/10/2025 et ADL : https://www.coingecko.com/learn/october-10-crypto-crash-explained
- Volmageddon : https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products

## Praticiens
- pysystemtrade (Carver) : https://github.com/pst-group/pysystemtrade
- Kevin Davey : https://bettersystemtrader.com/005-kevin-davey/
- Robot Wealth : https://robotwealth.com/trade-like-a-quant-bootcamp/
- poly-maker : https://github.com/warproxxx/poly-maker
- Quantpedia, performance in-sample vs out-of-sample : https://quantpedia.com/in-sample-vs-out-of-sample-analysis-of-trading-strategies/
- Revue des projets Jev : https://gist.github.com/drillan/6916b16e8ea31a8ec36c8f59d6483150

Note : certaines pages primaires étaient bloquées par le proxy ; ces chiffres viennent d'abstracts et de résultats de recherche, et doivent être vérifiés avant de servir de preuve de gouvernance.
Le texte exact des 7 posts X n'a pas pu être récupéré (x.com et ses miroirs sont bloqués) ; leur contenu a été reconstitué et n'est pas vérifié.
ed6a0faf1864d60161806b594b45a2642f6149f59b26b3d7b32c2ce38758dc6f  shiller_sp500_monthly.csv
570e05630c9a5e7350d0c3dbe3acc58e793cb5248181ab0e949c121cc082fb83  vix_daily.csv

## Lab v2 : datasets tiers (clonés, non vendorisés ; vérifier la licence de chaque dépôt)
- Futures : github.com/pst-group/pysystemtrade (data/futures, 1980-2024-03)
- Polymarket : shirleyshen0106/polymarket-calibration ; GitHubMagnus/polymarket-calibration ; marketlenstrade/polymarket-historical-data
- Cotes de football : AnishKhetani/premier-league-data
- Crypto : LorenzoBaggi/funding_arb ; guibvieira/freqtrade-hyperliquid-data ; d-glukhovskiy/Erdos_project ; VivekWar/Crypto-Funding-Rate-Arbitrage ; Jroc561/statArb
- Facteurs : scotty-jackson/AQRFactorX (AQR, jusqu'en 2025-09) ; fernando-duarte/ERP (Kenneth French, jusqu'en 2021-11) ; fja05680/sp500 (composition point-in-time du S&P 500)
- Microstructure Kalshi (Becker) : https://www.jbecker.dev/research/prediction-market-microstructure
- Polymarket (Cardozo et al.) : https://arxiv.org/abs/2609.12878 ; arbitrage : https://arxiv.org/abs/2508.03474
- ForecastBench : https://www.forecastbench.org/leaderboards/ ; Lopez-Lira & Tang : https://arxiv.org/abs/2304.07619
- Biais de regard vers le futur des LLM : https://arxiv.org/abs/2309.17322 ; https://arxiv.org/abs/2512.23847
