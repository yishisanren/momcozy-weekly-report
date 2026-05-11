# Momcozy Amazon Collection Status

更新时间：2026-05-04 10:50 CST

## 当前结论

Canopy API key 可用，但月配额只有 100 次。后续策略从“先抓全量”改成“白名单 + 本地状态 + 增量优先 + 严格预算”。

## 已完成

- Canopy `product` endpoint 曾连通成功。
- Canopy `product/reviews` endpoint 曾对 M5 Smart `B0F7XTHCNY` 返回成功，说明评论接口可用但慢。
- 已验证 P0 四个早期核心 ASIN 的公开商品信息：
  - `data/amazon/product_B0F7XTHCNY.json`
  - `data/amazon/product_B0CGXMJF8S.json`
  - `data/amazon/product_B0DBYF4Z6L.json`
  - `data/amazon/product_B0DR18KGBW.json`
  - `data/amazon/p0_product_probe_summary.json`
  - `data/amazon/p0_product_probe_summary.md`

## 用户确认 ASIN 更新

| 产品 | ASIN / 状态 | 当前处理 |
|---|---|---|
| BM08 | B0GJ8HDZ29 | 纳入核心监控，先建 product/评分基线 |
| M10 | 暂时未上架 | 不抓 reviews，每月轻量巡检 |
| BM04M / BM05 | 暂时未上架 | 不抓 reviews，每月轻量巡检 |
| Baby Sound Machine | B099RSXLGH / B0D5CY5P9K / B0D5CYDF9T | 先判断主 ASIN；最多 1 个主 ASIN 抓 reviews |
| T31 | B0FXGTGQG7 | 纳入核心监控候选，先建 product/评分基线 |

## P0 商品概览（已验证旧基线）

| 产品 | ASIN | Amazon 当前评分 | 评分数 | 状态 |
|---|---|---:|---:|---|
| M5 Smart | B0F7XTHCNY | 4.3 | 1765 | product endpoint 成功 |
| M9 | B0CGXMJF8S | 4.2 | 1683 | product endpoint 成功 |
| Air 1 | B0DBYF4Z6L | 4.3 | 1540 | product endpoint 成功 |
| BM04 | B0DR18KGBW | 4.2 | 453 | product endpoint 成功 |

## Reviews endpoint 历史状态

2026-04-27 14:01 CST 复测成功：Canopy `product/reviews` endpoint 已返回评论数据。

- 测试 ASIN：M5 Smart `B0F7XTHCNY`
- domain：US
- HTTP status：200
- 耗时：约 42.7 秒
- 当前页评论数：10
- pageInfo：currentPage=1，totalPages=14，totalResults=134，hasNextPage=true
- 原始响应保存：`data/amazon/reviews_probe_B0F7XTHCNY_20260427_140021.json`
- 规范化保存：`data/amazon/reviews_B0F7XTHCNY_page1_normalized.json`
- 摘要保存：`data/amazon/reviews_B0F7XTHCNY_page1_summary.md`

## 新采集策略：保护 100 次/月配额

默认月度预算：
- 每周 Amazon 增量任务最多 8 次 Canopy 请求。
- 每月 ASIN 巡检最多 10 次 Canopy 请求。
- 保留至少 30 次给临时排查、补采和失败重试。

默认周任务算法：
1. 读取本地 `data/amazon/state.json`（如不存在则创建），包含每个 ASIN 的 last_seen_review_id、last_seen_review_date、last_product_checked_at、last_reviews_checked_at。
2. 先不调用 Canopy，按白名单生成本周计划。
3. 对 P0 ASIN 最多各抓 reviews 第 1 页；如果第一页没有新评论，立刻停止该 ASIN。
4. 只有第一页出现新评论且本周请求预算未用完，才继续抓下一页；遇到已见 review_id/date 立刻停止。
5. product endpoint 只用于新 ASIN、超过 30 天未检查的 ASIN、或需要确认上市状态的 ASIN；不要每周全量查所有 product。
6. 暂未上架款不请求 reviews。
7. 单次运行出现 timeout / HTTP2 framing error 时，对同一 ASIN 最多重试 1 次；仍失败就跳过该 ASIN，保留配额。

## 后续接入报告方式

周报里 Amazon 先作为增强信号：
- 商品评分/评分数/上市状态；
- 新增 verified purchase 差评主题；
- 高信号原文 + 中文翻译；
- 明确标注 ASIN 范围和本周 Canopy 请求次数。

说明：本文件不保存 Canopy API key。
