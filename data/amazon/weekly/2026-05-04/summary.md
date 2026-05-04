# Momcozy Amazon 增量采集｜2026-05-04

- Canopy 请求预算：8
- 实际请求数：2
- 新增评论数：10
- 商品摘要数：0
- Dry run：否

## 新策略
- 固定 ASIN 白名单，不用 Canopy 做搜索。
- P0 每个 ASIN 默认只抓第一页；第一页无新增即停止。
- Baby Sound Machine 多 ASIN 先做商品摘要，不默认全量 reviews。
- M10、BM04M/BM05 暂未上架，不消耗 reviews 配额。

## 错误
- M9 B0CGXMJF8S reviews: All Canopy keys unavailable: key#1:402, key#2:402
- Air 1 B0DBYF4Z6L reviews: All Canopy keys unavailable: key#1:402, key#2:402
- BM04 B0DR18KGBW reviews: All Canopy keys unavailable: key#1:402, key#2:402
- BM08 B0GJ8HDZ29 reviews: All Canopy keys unavailable: key#1:402, key#2:402
- T31 B0FXGTGQG7 reviews: All Canopy keys unavailable: key#1:402, key#2:402
- Baby Sound Machine B099RSXLGH product: All Canopy keys unavailable: key#1:402, key#2:402
- Baby Sound Machine B0D5CY5P9K product: All Canopy keys unavailable: key#1:402, key#2:402
- Baby Sound Machine B0D5CYDF9T product: All Canopy keys unavailable: key#1:402, key#2:402
