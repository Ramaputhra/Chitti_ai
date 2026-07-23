# CHITTI V2 — PERFORMANCE & OPTIMIZATION GUIDE

## 1. Zero Polling & Event-Driven Redraws
- Continuous polling and busy waiting loops are strictly prohibited.
- Windows redraw only on event dispatch or active animation ticks.

## 2. Texture & Asset Caching
- SVG vector parsing and texture decoding are cached in `TextureCache` and `AssetCache`.
- Lazy asset loading prevents unnecessary memory consumption.
