# 蒜串屋 網站風格提案（三選一）

線上預覽：https://nf6124034.github.io/suankushi-sites/

| 版本 | 風格 | 主要客群 | 預覽 |
|---|---|---|---|
| v1 | 招牌點菜單：黃色燈箱、可勾選的點菜單 | 東區上班族、學生、宵夜族 | [/v1/](https://nf6124034.github.io/suankushi-sites/v1/) |
| v2 | 鹹酥雞攤玻璃櫃：日光燈、托盤夾進紅籃子、號碼牌 | 學生、年輕人、朋友聚會 | [/v2/](https://nf6124034.github.io/suankushi-sites/v2/) |
| v3 | 樂燒煙燻：黑陶、冰裂釉、炭火橘，高級串燒套餐 | 約會、上班族、觀光客 | [/v3/](https://nf6124034.github.io/suankushi-sites/v3/) |

每一版都有中文、英文（`/en/`）、日文（`/ja/`）三個頁面。

## 資料夾

```
index.html      選風格首頁（三版的客群、品牌故事、特色）
v1/  v2/  v3/   三個版本的網站
docs/           市場研究、上線與 SEO 操作手冊
previews/       選風格首頁用的截圖
```

## 修改內容

每一版的頁面都是用 `build.py` 產生的，不要直接改 `index.html`：

- 店名、地址、電話、地圖、訂位連結：改 `v1/build.py` 最上面的 `SITE`（三版共用）
- v1、v2 的菜單與價格：改 `v1/build.py` 的 `MENU`
- v3 的套餐與單點：改 `v3/build.py`
- 營業時間：各版 `build.py` 和 `assets/*.js` 最上面的 `HOURS`

改完後在該版的資料夾執行：

```bash
python build.py
```

## 選定之後

這個預覽站設定為不被搜尋引擎收錄（`noindex`）。選定一版後，把那一版部署到餐廳自己的網域，重新執行 `python build.py` 產生正式版的 `robots.txt` 與頁面，SEO 設定才會生效。詳見 `docs/上線與SEO操作手冊.md`。
