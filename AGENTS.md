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
1. Hero only shows report title/period/source notes and 2-3 key guidance cards; do not show low-value KPI cards like total comments/brand count on the title side.
2. Momcozy rating section must appear first and must use the app's current public store rating, not the average of newly collected weekly reviews. App Store ratings should use live Apple lookup ratings for US/GB/CA/DE/FR, shown by country and optionally weighted by rating count; Play Store ratings should use `google_play_scraper.app(...)[score]` for the verified package.
3. Momcozy user comments follow the rating section: show current-week review count, Chinese translation and original text side-by-side. Keep translations content-comparable to originals, collapse original-review line breaks, keep source/date on one line, and avoid overly narrow original/date columns.
4. Momcozy attention dimensions: replace generic heatmap wording with “需要关注的几个维度” such as device connection, core logging/session flow, stability/performance, multi-user/account setup.
5. Competitor section: latest App Store / Play Store ratings must also use current public store ratings, not weekly review averages; keep weekly new-review content analysis separately.
6. Reddit section: categorize posts by theme; for each post include topic view, original post quote, and 1-3 strongly related replies.
7. Do not include data coverage/source gaps as an H5 report section. Mention meaningful missing data only in the Telegram delivery message.

Data collection defaults:
- App Store / Play Store countries: US, GB, CA, DE, FR
- Reddit: use public JSON endpoints first, then old.reddit/RSS fallback; avoid rdt as primary source
