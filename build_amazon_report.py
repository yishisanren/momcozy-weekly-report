#!/usr/bin/env python3
"""Build static H5 page for Momcozy Amazon product review weekly report."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def text_snippet(value: str, limit: int = 620) -> str:
    clean = " ".join((value or "").split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def theme_tags(text: str) -> list[str]:
    t = text.lower()
    tags = []
    checks = [
        ("解放双手 / 多任务", ["hands-free", "multitask", "move around", "go do whatever", "wireless"]),
        ("App 控制", ["app", "control"]),
        ("吸力温和且有效", ["suction", "gentle", "output", "amount of milk"]),
        ("清洁/装配", ["clean", "assemble", "leak"]),
        ("噪音/隐蔽性", ["quiet", "hear", "discreet", "dolly"]),
        ("容量/结构", ["6-7oz", "lid", "upright", "overflow"]),
        ("续航", ["battery", "recharging"]),
    ]
    for label, words in checks:
        if any(w in t for w in words):
            tags.append(label)
    return tags or ["综合正向体验"]


def rating_int(review: dict) -> int:
    try:
        return int(float(review.get("rating") or 0))
    except (TypeError, ValueError):
        return 0


def load_translations(weekly_dir: Path) -> dict[str, dict[str, str]]:
    path = weekly_dir / "review_translations.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(item.get("review_key")): item for item in data if item.get("review_key")}
    if isinstance(data, dict):
        return {str(k): v for k, v in data.items() if isinstance(v, dict)}
    return {}


def zh_for(review: dict, translations: dict[str, dict[str, str]], field: str) -> str:
    item = translations.get(str(review.get("review_key")), {})
    value = item.get(field) or item.get(f"{field}_zh")
    if value:
        return value
    return "（待翻译：cron 需在 build 前写入 review_translations.json）"


def rating_summary(rating: int, items: list[dict]) -> str:
    if not items:
        return f"<article class='rating-card'><h3>{rating} 星</h3><p class='muted'>本周无新增。</p></article>"
    tags = Counter(tag for r in items for tag in theme_tags((r.get("title") or "") + " " + (r.get("body") or "")))
    verified_count = sum(1 for r in items if r.get("verified_purchase"))
    themes = "、".join(f"{tag}（{count}）" for tag, count in tags.most_common(5))
    sample_titles = "；".join(text_snippet(r.get("title") or "无标题", 44) for r in items[:3])
    return f"""
    <article class='rating-card'>
      <h3>{rating} 星｜{len(items)} 条</h3>
      <p>Verified Purchase：{verified_count}/{len(items)}。主要主题：{esc(themes or '综合体验')}。</p>
      <p class='muted'>代表标题：{esc(sample_titles)}</p>
    </article>
    """


def review_detail_rows(items: list[dict], translations: dict[str, dict[str, str]]) -> str:
    if not items:
        return "<p class='muted'>本周无新增。</p>"
    rows = []
    for r in items:
        rows.append(f"""
        <article class="review">
          <div class="review-head"><span>{esc(r.get('model'))}</span><span>{esc(r.get('asin'))}</span><span>{'★' * rating_int(r)}</span><span>{'Verified' if r.get('verified_purchase') else 'Unverified'}</span></div>
          <h3>{esc(r.get('title') or '无标题')}</h3>
          <div class='quote-grid'>
            <div><b>中文翻译</b><p><em>{esc(zh_for(r, translations, 'title'))}</em></p><p>{esc(zh_for(r, translations, 'body'))}</p></div>
            <div><b>英文原文</b><p><em>{esc(r.get('title') or '无标题')}</em></p><p>{esc(text_snippet(r.get('body') or '', 1200))}</p></div>
          </div>
          <div class="meta">来源：{esc(r.get('source'))}｜评论时间：{esc(r.get('date') or '—')}｜Helpful：{esc(r.get('helpful_votes'))}｜采集：{esc(r.get('collected_at'))}</div>
        </article>
        """)
    return "".join(rows)


def build(report_date: str | None = None) -> Path:
    report_date = report_date or date.today().isoformat()
    weekly_dir = ROOT / "data" / "amazon" / "weekly" / report_date
    summary = json.loads((weekly_dir / "summary.json").read_text())
    reviews = json.loads((weekly_dir / "new_reviews.json").read_text()) if (weekly_dir / "new_reviews.json").exists() else []

    by_model = Counter(r.get("model", "未知") for r in reviews)
    by_rating = Counter(r.get("rating") for r in reviews)
    verified = sum(1 for r in reviews if r.get("verified_purchase"))
    tag_counter = Counter(tag for r in reviews for tag in theme_tags((r.get("title") or "") + " " + (r.get("body") or "")))
    grouped = defaultdict(list)
    for r in reviews:
        grouped[r.get("model", "未知")].append(r)

    translations = load_translations(weekly_dir)
    by_star: dict[int, list[dict]] = defaultdict(list)
    for r in reviews:
        by_star[rating_int(r)].append(r)

    positive_count = len(by_star.get(5, [])) + len(by_star.get(4, []))
    low_count = len(by_star.get(1, [])) + len(by_star.get(2, []))
    mid_count = len(by_star.get(3, []))
    conclusion_items = [
        f"本周新增 {len(reviews)} 条 Amazon 评论；评分结构为 {', '.join(f'{k}★×{v}' for k, v in sorted(by_rating.items(), reverse=True)) or '—'}。",
    ]
    if positive_count:
        conclusion_items.append(f"4–5 星共 {positive_count} 条，正向反馈以 {', '.join(tag for tag, _ in tag_counter.most_common(3)) or '综合体验'} 为主。")
    if mid_count:
        conclusion_items.append(f"3 星共 {mid_count} 条，作为中性/混合体验单独观察。")
    if low_count:
        conclusion_items.append(f"1–2 星共 {low_count} 条，已在下方逐条列出英文原文和中文翻译，优先进入问题闭环。")
    else:
        conclusion_items.append("本周没有新增 1–2 星低分评论。")

    rating_summary_rows = "".join(rating_summary(star, by_star.get(star, [])) for star in [5, 4])
    mid_rows = review_detail_rows(by_star.get(3, []), translations) if mid_count else "<p class='muted'>本周无 3 星新增评论。</p>"
    low_rows = "".join(
        f"<h3>{star} 星｜{len(by_star.get(star, []))} 条</h3>" + review_detail_rows(by_star.get(star, []), translations)
        for star in [2, 1]
    )

    errors = summary.get("errors", [])
    unlisted = summary.get("unlisted", [])
    out_dir = ROOT / "amazon-reports" / report_date
    out_dir.mkdir(parents=True, exist_ok=True)

    model_cards = "".join(
        f"<div class='card'><div class='k'>{esc(model)}</div><div class='v'>{count}</div><p>新增评论</p></div>"
        for model, count in by_model.items()
    ) or "<div class='card'><div class='k'>无新增</div><div class='v'>0</div><p>新增评论</p></div>"

    tag_items = "".join(
        f"<li><span>{esc(tag)}</span><b>{count}</b></li>" for tag, count in tag_counter.most_common()
    )

    coverage = "".join(
        f"<li>{esc(e.get('model'))} {esc(e.get('asin'))}：{esc(e.get('stage'))} 返回 {esc((e.get('error') or '').split(' for url:')[0])}</li>"
        for e in errors
    )
    unlisted_html = "".join(f"<li>{esc(x.get('model'))}：{esc(x.get('status'))}</li>" for x in unlisted)

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Momcozy Amazon 产品评论周报｜{esc(report_date)}</title>
  <style>
    :root {{ --bg:#f7f3ee; --ink:#24201c; --muted:#756b60; --card:#fffaf4; --accent:#b85c38; --line:#eadfd2; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Noto Sans CJK SC",Arial,sans-serif; background:var(--bg); color:var(--ink); }}
    main {{ max-width:1120px; margin:0 auto; padding:36px 18px 64px; }}
    .hero {{ padding:34px; border-radius:28px; background:linear-gradient(135deg,#fffaf4,#f0dfcf); box-shadow:0 18px 60px rgba(90,55,30,.12); }}
    .eyebrow {{ color:var(--accent); letter-spacing:.08em; font-weight:700; }}
    h1 {{ margin:10px 0 8px; font-size:clamp(30px,6vw,58px); line-height:1.05; }}
    h2 {{ margin:34px 0 14px; font-size:24px; }}
    p {{ line-height:1.75; }}
    .sub {{ color:var(--muted); max-width:760px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin-top:20px; }}
    .card,.panel,.review {{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:18px; }}
    .k {{ color:var(--muted); font-size:14px; }} .v {{ font-size:34px; font-weight:800; margin:4px 0; }}
    .signals {{ display:grid; grid-template-columns:1.1fr .9fr; gap:16px; }}
    .rating-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; }}
    .rating-card {{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:18px; }}
    .quote-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
    @media (max-width:800px) {{ .signals,.quote-grid {{ grid-template-columns:1fr; }} }}
    ul {{ padding-left:20px; line-height:1.8; }}
    .tag-list {{ list-style:none; padding:0; margin:0; }}
    .tag-list li {{ display:flex; justify-content:space-between; border-bottom:1px solid var(--line); padding:10px 0; gap:16px; }}
    .review {{ margin:12px 0; }}
    .review-head {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }}
    .review-head span {{ background:#f1e2d4; color:#5c3b28; border-radius:999px; padding:5px 10px; font-size:13px; }}
    .review h3 {{ margin:6px 0; font-size:19px; }}
    .meta,.muted {{ color:var(--muted); font-size:13px; line-height:1.6; }}
    .warn {{ background:#fff3e8; border-left:5px solid var(--accent); }}
    footer {{ margin-top:36px; color:var(--muted); font-size:13px; }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div class="eyebrow">AMAZON PRODUCT REVIEW WEEKLY</div>
    <h1>Momcozy Amazon 产品评论周报</h1>
    <p class="sub">周期：{esc(report_date)}｜数据源：Canopy + ASIN 白名单｜本页只展示 Amazon 产品评论，不是 App Store / Play Store / Reddit 周报。</p>
    <div class="grid">
      <div class="card"><div class="k">新增评论</div><div class="v">{len(reviews)}</div><p>本周采集到的 review-level 内容</p></div>
      <div class="card"><div class="k">Verified Purchase</div><div class="v">{verified}</div><p>已验证购买评论</p></div>
      <div class="card"><div class="k">Canopy 请求</div><div class="v">{esc(summary.get('requests_used'))}/{esc(summary.get('max_requests'))}</div><p>触发 402 后停止扩展采集</p></div>
      <div class="card"><div class="k">评分分布</div><div class="v">{', '.join(f'{k}★×{v}' for k,v in sorted(by_rating.items(), reverse=True)) or '—'}</div><p>本周新增评论评分</p></div>
      {model_cards}
    </div>
  </section>

  <section class="signals">
    <div class="panel">
      <h2>01｜本周核心结论</h2>
      <ul>{''.join(f'<li>{esc(item)}</li>' for item in conclusion_items)}</ul>
    </div>
    <div class="panel">
      <h2>02｜主题热度</h2>
      <ul class="tag-list">{tag_items}</ul>
    </div>
  </section>

  <section>
    <h2>03｜新增评论：按打星数分类</h2>
    <p class="sub">4–5 星只做分类总结；1–2 星逐条列出英文原文与中文翻译，便于直接进入产品/客服闭环。</p>
    <div class="rating-grid">{rating_summary_rows}</div>

    <h2>04｜3 星中性/混合评论</h2>
    {mid_rows}

    <h2>05｜1–2 星低分评论逐条列表</h2>
    {low_rows}
  </section>

  <section class="panel warn">
    <h2>06｜覆盖与异常</h2>
    <p>本周已按配额保护策略处理：Canopy 返回 402 Payment Required 后，不继续循环重试、不扩大 ASIN、不翻页烧额度。</p>
    <ul>{coverage or '<li>无异常</li>'}</ul>
    <ul>{unlisted_html}</ul>
  </section>

  <footer>Generated from data/amazon/weekly/{esc(report_date)}. Amazon 页面路径：amazon-reports/{esc(report_date)}/index.html</footer>
</main>
</body>
</html>
"""
    (out_dir / "index.html").write_text(html_text)
    return out_dir / "index.html"


if __name__ == "__main__":
    import sys
    path = build(sys.argv[1] if len(sys.argv) > 1 else None)
    print(path)
