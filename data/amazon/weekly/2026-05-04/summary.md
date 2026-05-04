# Momcozy Amazon 增量采集｜2026-05-04

- Canopy 请求预算：8
- 实际请求数：2
- 新增评论数：20
- 商品摘要数：0
- Dry run：否

## 新策略
- 固定 ASIN 白名单，不用 Canopy 做搜索。
- P0 每个 ASIN 默认只抓第一页；第一页无新增即停止。
- Baby Sound Machine 多 ASIN 先做商品摘要，不默认全量 reviews。
- M10、BM04M/BM05 暂未上架，不消耗 reviews 配额。

## 错误
- M9 B0CGXMJF8S reviews: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product/reviews?asin=B0CGXMJF8S&domain=US&page=1
- Air 1 B0DBYF4Z6L reviews: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product/reviews?asin=B0DBYF4Z6L&domain=US&page=1
- BM04 B0DR18KGBW reviews: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product/reviews?asin=B0DR18KGBW&domain=US&page=1
- BM08 B0GJ8HDZ29 reviews: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product/reviews?asin=B0GJ8HDZ29&domain=US&page=1
- T31 B0FXGTGQG7 reviews: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product/reviews?asin=B0FXGTGQG7&domain=US&page=1
- Baby Sound Machine B099RSXLGH product: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product?asin=B099RSXLGH&domain=US
- Baby Sound Machine B0D5CY5P9K product: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product?asin=B0D5CY5P9K&domain=US
- Baby Sound Machine B0D5CYDF9T product: 402 Client Error: Payment Required for url: https://rest.canopyapi.co/api/amazon/product?asin=B0D5CYDF9T&domain=US
