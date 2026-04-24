# Momcozy Weekly Report H5

Purpose: host weekly H5/dashboard reports for Momcozy App + competitor intelligence.

GitHub repo: https://github.com/yishisanren/momcozy-weekly-report
GitHub Pages root: https://yishisanren.github.io/momcozy-weekly-report/
Current report pattern: `reports/YYYY-MM-DD/index.html`

Weekly automation expectations:
- Generate a static H5 page, not a long Feishu document.
- Use `reports/YYYY-MM-DD/index.html` for each weekly report.
- Update root `index.html` to redirect to the latest report.
- Commit and push to `main`.
- Final user delivery should be the GitHub Pages H5 link + <=5 core conclusions.
- Keep local files internal; do not send markdown paths by default.

Content sections expected in H5:
1. Management summary / P0-P2 actions
2. App Store / Play Store rating trend radar
3. Momcozy issue heatmap
4. Competitor observations by business line
5. Reddit community voice with original post/comment quotes
6. Momcozy current-week raw reviews
7. Data coverage / source gaps

Data collection defaults:
- App Store / Play Store countries: US, GB, CA, DE, FR
- Reddit: use public JSON endpoints first, then old.reddit/RSS fallback; avoid rdt as primary source
