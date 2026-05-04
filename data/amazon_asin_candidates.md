# Momcozy Amazon ASIN 白名单

更新时间：2026-05-04 10:50 CST

采集原则：Canopy API 月配额只有 100 次，请不要把 Canopy 当搜索引擎用。先用用户确认的 ASIN 白名单 + 本地状态表做调度；只有需要确认上市状态或抓新增评论时才消耗 Canopy。

抓取节奏：
- 核心已上市款：首次建立基线时，分批抓评论；之后每周只抓新增评论，遇到已见 review_id/date 就停止翻页。
- 多 ASIN 变体：先抓 product/评分摘要或用已知标题确认主次，不默认全量抓每个变体评论。
- 暂未上架款：不走 Canopy reviews；每月只做一次轻量上市巡检，有明确 ASIN 后再进入白名单。
- Baby Sound Machine 多 ASIN：先按商品评分/评分数确认主 ASIN，再挑 1 个主 ASIN 抓评论；其余只做评分/上市状态监控。

| 产品线 | 型号/关键词 | ASIN 白名单 | 状态判断 | 建议 |
|---|---|---|---|---|
| 吸奶器 | M5 Smart | B0F7XTHCNY | 已上市，强匹配 | 核心监控；已有 Canopy reviews 连通样本；后续增量抓 |
| 吸奶器 | M5 非 Smart | B0CNXDS73F | 已上市，但不是 Smart | 对照款；低频监控 |
| 吸奶器 | M9 | B0CGXMJF8S | 已上市，强匹配 | 核心监控；后续增量抓 |
| 吸奶器 | M9 变体 | B0DTYSLFLX / B0FXMFC4K7 / B0DM4X6BZ9 | 已上市/疑似变体 | 先不全量抓，按评分量决定是否纳入 |
| 吸奶器 | Air 1 | B0DBYF4Z6L | 已上市，强匹配 | 核心监控；后续增量抓 |
| 吸奶器 | M10 | 暂时未上架 | 用户确认暂未上架 | 每月轻量巡检，不抓 reviews |
| 吸奶器 | V3 | 暂未确认 | Amazon US 未确认主 ASIN | 每月轻量巡检 |
| 吸奶器 | V3 Pro | B0CZNR1QCQ | 疑似 V3/V3 Pro，但标题未写明 | 不抓 reviews；待人工/页面确认 |
| 睡眠线 | BM04 | B0DR18KGBW | 已上市，强匹配 | 核心监控；后续增量抓 |
| 睡眠线 | BM04 变体 | B0F4XBCJ8C / B0GJDX7QF2 / B0GJDXC296 | 已上市候选/变体 | 先评分摘要，不默认抓 reviews |
| 睡眠线 | BM08 | B0GJ8HDZ29 | 用户确认 BM08 ASIN | 核心监控；先建 product/评分基线，再按需增量抓评论 |
| 睡眠线 | BM04M / BM05 | 暂时未上架 | 用户确认暂未上架 | 每月轻量巡检，不抓 reviews |
| 睡眠线 | Baby Sound Machine | B099RSXLGH / B0D5CY5P9K / B0D5CYDF9T | 用户确认已上市 ASIN 组 | 先确认主 ASIN；最多选 1 个主 ASIN 抓 reviews，其余只监控评分/状态 |
| 睡眠线 | T31 | B0FXGTGQG7 | 用户确认 T31 ASIN | 核心监控候选；先建 product/评分基线，再按需增量抓评论 |

## Canopy 配额使用方案

月度 100 次上限下，默认预算：
- 每周 Amazon 增量任务最多 8 次 Canopy 请求。
- 每月 ASIN 巡检最多 10 次 Canopy 请求。
- 保留至少 30 次给临时排查/补采。

请求优先级：
1. P0 核心款新增评论：M5 Smart、M9、Air 1、BM04、BM08、T31。
2. 睡眠线声音机：先只选评分/评论量最高的 1 个主 ASIN 抓评论。
3. 变体 ASIN：只在主 ASIN 评论不足或用户明确要求时抓。
4. 暂未上架款：不请求 reviews。

## P0/P1 当前名单

P0（核心监控，增量 reviews）：
- M5 Smart：B0F7XTHCNY
- M9：B0CGXMJF8S
- Air 1：B0DBYF4Z6L
- BM04：B0DR18KGBW
- BM08：B0GJ8HDZ29
- T31：B0FXGTGQG7

P1（先 product/评分摘要，必要时 reviews）：
- Baby Sound Machine：B099RSXLGH、B0D5CY5P9K、B0D5CYDF9T
- M9 变体：B0DTYSLFLX、B0DM4X6BZ9、B0FXMFC4K7
- BM04 变体：B0F4XBCJ8C、B0GJDX7QF2、B0GJDXC296

P2（暂不消耗 Canopy reviews）：
- M10：暂时未上架
- BM04M / BM05：暂时未上架
- V3 / V3 Pro：待确认
