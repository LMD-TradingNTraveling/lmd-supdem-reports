LMD TRADING OPERATIONS CENTER — GITHUB LIVE DATA INTEGRATION

This package is a deployment candidate, not a live deployment.
No changes have been made to your GitHub repository or scheduled downloader.

1. BACK UP the current GitHub index.html.
2. Upload index.html to the repository root, replacing the old index.html.
3. Create the data/ folder in the repository and upload data/live.json.
4. Open https://lmd-tradingntraveling.github.io/lmd-supdem-reports/
   The Overview should show "Trading data last published" and 425 trades.
5. Confirm Reports, Research, Heatmap, and Calendar still function.

IMPORTANT PRIVACY: Your GitHub repository is PUBLIC. The reduced live.json
still reveals transaction-level P&L, trade timestamps, prices, and balances.
Account number has been replaced with the LMDTrading alias. Do not upload
original Tradovate CSVs, credential files, or nt_config.ini to the public repo.
For private performance data, use a private authenticated backend instead.

LOCAL DATA REFRESH:
The included LMD_Publish_Live_Data.py prepares validated data/live.json
from the two full-history master CSVs:

  py LMD_Publish_Live_Data.py --position "C:\path\to\LMD_Position_History_latest.csv" --cash "C:\path\to\LMD_Cash_History_latest.csv" --output "C:\path\to\git-clone\data\live.json"

The script does NOT upload to GitHub. It stops on missing headers, empty data,
trade counts under 425, duplicate conflicting IDs, or a shrinkage versus
an existing published file. Do not feed it weekly-only exports.

Once a local Git clone is configured, a follow-up can connect the validated
publish step to v1.6.5's successful scheduled download and Git push. That
step is not enabled in this package.

Research remains embedded and separate from live performance.
All original dashboard functionality is preserved from v17.
