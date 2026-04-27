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
2. Momcozy App section first: current-week review count, content analysis, raw reviews translated into Chinese while preserving originals side-by-side.
3. Momcozy attention dimensions: replace generic heatmap wording with “需要关注的几个维度” such as device connection, core logging/session flow, stability/performance, multi-user/account setup.
4. Momcozy App Store and Play Store rating trends are separated by platform and must appear at the top of the Momcozy section, before user comments. If historical ratings are sparse, show only the available collected points and do not fabricate/backfill history.
5. Competitor section: latest App Store / Play Store rating trends separated by platform, competitor review counts and content analysis by business line.
6. Reddit section: categorize posts by theme; for each post include topic view, original post quote, and 1-3 strongly related replies.
7. Data coverage / source gaps can be lower-priority or appendix-level.

Data collection defaults:
- App Store / Play Store countries: US, GB, CA, DE, FR
- Reddit: use public JSON endpoints first, then old.reddit/RSS fallback; avoid rdt as primary source
