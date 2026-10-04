# -*- coding: utf-8 -*-
"""
蒜串屋 第二版（鹹酥雞攤玻璃櫃）產生器
====================================
店家資料、菜單、價格、營業時間「共用第一版」：請改 ../v1/build.py 上半部的 SITE / MENU / DRINK_PLANS。
這個檔案只放第二版的文案和玻璃櫃要放哪些照片。改完執行：  python build.py
"""
import html
import json
import runpy
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
V1 = runpy.run_path(str(ROOT.parent / "v1" / "build.py"))
SITE, MENU, DRINK_PLANS, HOURS_SCHEMA, ICONS = V1["SITE"], V1["MENU"], V1["DRINK_PLANS"], V1["HOURS_SCHEMA"], V1["ICONS"]
V1L = V1["LANGS"]  # 第一版的 FAQ、評論文案沿用

U = "https://images.unsplash.com/photo-"
# 玻璃櫃裡的托盤：(品項 id, Unsplash 照片)。示意照，開店後換成自家實拍。
SHELVES = [
    ({"zh": "炭火串燒・台味串", "en": "Charcoal & street skewers", "ja": "炭火串・屋台串"},
     [("leg", "1779358964755-75464e144187"), ("skin", "1789493513908-cb0185caa2fb"), ("pork", "1779474989201-fe2d22ff3f79"),
      ("gongwan", "1788141403899-d6a135658fea"), ("corn", "1533520958595-9ffb2b514373"), ("shiitake", "1755108906864-fdaadb8ab5f1")]),
    ({"zh": "蒜香炸物", "en": "Garlic fried", "ja": "にんにく揚げ物"},
     [("popcorn", "1682264895449-f75b342cbab6"), ("squid", "1763467940825-d067fb3baf22"), ("tempura", "1760047550367-3d72fa3053c5"),
      ("shrimp", "1759823338930-7996c1787c3b"), ("sweetpotato", "1745792714512-77cffdb16020"), ("beefkatsu", "1651328236028-77b585d3f4e5")]),
]
GARLIC = U + "1638521476152-d0a01eaa1207"
BEER = U + "1571613316887-6f8d5cbf7ef7"

LANGS = {
    "zh": {
        "html_lang": "zh-Hant-TW", "og_locale": "zh_TW", "path": "/", "out": "index.html", "a": "",
        "title": "蒜串屋｜忠孝敦化 鹹酥雞・炭火串燒・宵夜（每天到 01:30）",
        "desc": "忠孝敦化站走路 3 分鐘的鹹酥雞攤＋串燒居酒屋。一串 35 元起、招牌蒜香鹹酥雞、生啤暢飲 399，每天開到凌晨 1:30，有冷氣、可外帶外送。",
        "sub": ["鹹酥雞", "炭火串燒", "生啤"],
        "nav": [("case", "夾菜"), ("prices", "價目"), ("ask", "加蒜"), ("drinks", "喝"), ("visit", "到店")],
        "walk": "忠孝敦化站走路 3 分", "go": "導航過來", "call": "打電話", "waitlist": "線上候位",
        "kraft_h": "自己夾", "kraft_p": "夾進籃子，交給老闆。點照片就能夾。",
        "case_h": "玻璃櫃", "photo_note": "示意照片",
        "counter": "捷運忠孝敦化站 3 號出口，走路 3 分鐘",
        "prices_h": "價目表", "prices_p": "櫃子裡放不下的都在這。點一下就丟進籃子，全部都能外帶。",
        "board_note": "價格含稅，不收服務費。菜色依當日進貨調整。",
        "ask_h": "老闆會問你三件事", "ask_p": "鹹酥雞攤的老規矩：起鍋前問你辣度、蒜、九層塔。先選好，號碼牌上會幫你寫。",
        "qs": [
            ("spice", "要辣嗎？", [("0", "不辣"), ("1", "小辣"), ("2", "中辣"), ("3", "大辣")]),
            ("garlic", "蒜要加嗎？", [("yes", "要"), ("more", "多一點"), ("no", "不要")]),
            ("basil", "九層塔？", [("yes", "要"), ("no", "不要")]),
        ],
        "ask_note": "我們的建議：蒜一定要加。",
        "drinks_h": "冰箱自己開", "drinks_p": "鹹香的東西配冰生啤最對。人多就選暢飲，兩小時內隨你續。",
        "per": "/人", "fine": "禁止酒駕・飲酒過量，有害健康。未滿 18 歲請勿飲酒。",
        "visit_h": "到店",
        "f": {"addr": "地址", "mrt": "捷運", "hours": "營業時間", "phone": "電話"},
        "mrt": "板南線忠孝敦化站 3 號出口，走路約 3 分鐘",
        "hours_rows": [("0,1,2,3,4", "週日–週四", "17:30 – 01:30"), ("5,6", "週五–週六", "17:30 – 02:00")],
        "dist_btn": "算算我離多遠", "dist_hint": "用你手機的位置估算走路時間，位置不會傳給我們。",
        "map_title": "蒜串屋在 Google 地圖上的位置",
        "basket": "籃子", "plate_h": "號碼牌", "plate_empty": "籃子還是空的，去櫃子夾幾樣吧。",
        "plate_total": "小計", "plate_clear": "清空籃子", "plate_close": "收起來",
        "plate_hint": "到櫃台把這個畫面給老闆看就好。",
        "strings": {
            "open": "營業中｜今晚到 {t}", "closed": "準備中｜{t} 開燈",
            "basketLabel": "籃子：{n} 樣，{total}，打開號碼牌", "added": "已夾 {name}，共 {n} 份",
            "less": "少一份 {name}", "more": "多一份 {name}",
            "geoWait": "定位中…", "geoFail": "抓不到你的位置，直接按「導航過來」也可以。",
            "geoOk": "你離蒜串屋大約 {d}，走路約 {m} 分鐘。",
            "notes": {"spice": {"0": "不辣", "1": "小辣", "2": "中辣", "3": "大辣"},
                      "garlic": {"yes": "要蒜", "more": "多蒜", "no": "不要蒜"},
                      "basil": {"yes": "要九層塔", "no": "不要九層塔"}},
        },
        "credit": "網站照片為 Unsplash 示意照片。",
        "follow": "追蹤", "delivery": "外送",
    },
    "en": {
        "html_lang": "en", "og_locale": "en_US", "path": "/en/", "out": "en/index.html", "a": "../",
        "title": "Garlic Kushi | Taipei Fried Chicken Stall & Yakitori, Open Late",
        "desc": "A Taiwanese fried chicken stall and charcoal yakitori bar, 3 minutes from MRT Zhongxiao Dunhua. Skewers from NT$35, garlic popcorn chicken, draft beer free-flow NT$399. Open until 1:30am daily.",
        "sub": ["Fried chicken", "Charcoal skewers", "Draft beer"],
        "nav": [("case", "Pick"), ("prices", "Prices"), ("ask", "Garlic"), ("drinks", "Drinks"), ("visit", "Find us")],
        "walk": "3 min from MRT", "go": "Directions", "call": "Call", "waitlist": "Waitlist",
        "kraft_h": "Help yourself", "kraft_p": "Tap a tray to drop it in your basket, then hand it to the boss.",
        "case_h": "The glass case", "photo_note": "Illustrative photos",
        "counter": "3 min walk from MRT Zhongxiao Dunhua, Exit 3",
        "prices_h": "Price board", "prices_p": "Everything that doesn't fit in the case. Tap to add to your basket. All of it travels.",
        "board_note": "Prices include tax. No service charge. Items change with the day's market.",
        "ask_h": "The boss will ask you three things", "ask_p": "The fry-stall ritual: before your order leaves the oil, you're asked about spice, garlic and basil. Answer now and it goes on your number plate.",
        "qs": [
            ("spice", "Spicy?", [("0", "No"), ("1", "A little"), ("2", "Medium"), ("3", "Hot")]),
            ("garlic", "Garlic?", [("yes", "Yes"), ("more", "Extra"), ("no", "None")]),
            ("basil", "Thai basil?", [("yes", "Yes"), ("no", "No")]),
        ],
        "ask_note": "Our advice: always say yes to garlic.",
        "drinks_h": "Open the fridge", "drinks_p": "Salty, garlicky food wants a cold draft beer. Coming as a group? Take the 2-hour free-flow.",
        "per": "/person", "fine": "Never drink and drive. Alcohol served to guests 18 and over.",
        "visit_h": "Find us",
        "f": {"addr": "Address", "mrt": "MRT", "hours": "Hours", "phone": "Phone"},
        "mrt": "Zhongxiao Dunhua Station (Bannan Line), Exit 3, about a 3-minute walk",
        "hours_rows": [("0,1,2,3,4", "Sun–Thu", "17:30 – 01:30"), ("5,6", "Fri–Sat", "17:30 – 02:00")],
        "dist_btn": "How far am I?", "dist_hint": "Uses your phone's location to estimate the walk. Your location is never sent to us.",
        "map_title": "Garlic Kushi on Google Maps",
        "basket": "Basket", "plate_h": "Number", "plate_empty": "Your basket is empty. Pick something from the case.",
        "plate_total": "Subtotal", "plate_clear": "Empty basket", "plate_close": "Close",
        "plate_hint": "Show this screen at the counter. Chinese names are for the staff.",
        "strings": {
            "open": "Open now | until {t} tonight", "closed": "Closed | lights on at {t}",
            "basketLabel": "Basket: {n} items, {total}. Open number plate", "added": "Added {name}, {n} in basket",
            "less": "One less {name}", "more": "One more {name}",
            "geoWait": "Finding you…", "geoFail": "Couldn't get your location. Just tap Directions.",
            "geoOk": "You're about {d} away, roughly a {m}-minute walk.",
            "notes": {"spice": {"0": "不辣 no spice", "1": "小辣 mild", "2": "中辣 medium", "3": "大辣 hot"},
                      "garlic": {"yes": "要蒜 garlic", "more": "多蒜 extra garlic", "no": "不要蒜 no garlic"},
                      "basil": {"yes": "要九層塔 basil", "no": "不要九層塔 no basil"}},
        },
        "credit": "Photos are illustrative, via Unsplash.",
        "follow": "Follow", "delivery": "Delivery",
    },
    "ja": {
        "html_lang": "ja", "og_locale": "ja_JP", "path": "/ja/", "out": "ja/index.html", "a": "../",
        "title": "蒜串屋｜台北・忠孝敦化 台湾からあげ屋台と炭火串焼き 深夜1:30まで",
        "desc": "MRT忠孝敦化駅から徒歩3分、台湾式からあげ屋台と炭火串焼き居酒屋。串1本NT$35から、名物にんにくからあげ、生ビール飲み放題NT$399。毎日深夜1:30まで。",
        "sub": ["台湾からあげ", "炭火串焼き", "生ビール"],
        "nav": [("case", "選ぶ"), ("prices", "価格表"), ("ask", "にんにく"), ("drinks", "お酒"), ("visit", "アクセス")],
        "walk": "駅から徒歩3分", "go": "道順を見る", "call": "電話", "waitlist": "順番待ち",
        "kraft_h": "セルフで選ぶ", "kraft_p": "写真をタップしてカゴへ。カゴをお店の人に渡すだけ。",
        "case_h": "ガラスケース", "photo_note": "イメージ写真",
        "counter": "MRT忠孝敦化駅 3番出口から徒歩3分",
        "prices_h": "価格表", "prices_p": "ケースに入りきらないものはこちら。タップでカゴへ。すべてお持ち帰りできます。",
        "board_note": "税込・サービス料なし。仕入れにより内容が変わります。",
        "ask_h": "お店の人が三つ聞きます", "ask_p": "台湾の唐揚げ屋台の決まりごと。揚げる前に辛さ・にんにく・バジルを聞かれます。ここで選べば番号札に書いておきます。",
        "qs": [
            ("spice", "辛くしますか？", [("0", "辛くない"), ("1", "小辛"), ("2", "中辛"), ("3", "大辛")]),
            ("garlic", "にんにくは？", [("yes", "入れる"), ("more", "多め"), ("no", "なし")]),
            ("basil", "バジルは？", [("yes", "入れる"), ("no", "なし")]),
        ],
        "ask_note": "おすすめは、にんにく入り。",
        "drinks_h": "冷蔵庫は自分で開けて", "drinks_p": "塩気とにんにくには冷えた生ビール。グループなら2時間飲み放題がお得です。",
        "per": "/人", "fine": "飲酒運転は禁止されています。20歳未満の方の飲酒はご遠慮ください。",
        "visit_h": "アクセス",
        "f": {"addr": "住所", "mrt": "MRT", "hours": "営業時間", "phone": "電話"},
        "mrt": "板南線 忠孝敦化駅 3番出口から徒歩約3分",
        "hours_rows": [("0,1,2,3,4", "日〜木", "17:30 – 01:30"), ("5,6", "金・土", "17:30 – 02:00")],
        "dist_btn": "ここから何分？", "dist_hint": "スマホの位置情報で徒歩時間を計算します。位置情報は送信されません。",
        "map_title": "Googleマップで見る蒜串屋",
        "basket": "カゴ", "plate_h": "番号札", "plate_empty": "カゴは空です。ケースから選んでください。",
        "plate_total": "小計", "plate_clear": "カゴを空にする", "plate_close": "閉じる",
        "plate_hint": "この画面をカウンターで見せてください。中国語の品名はお店の人用です。",
        "strings": {
            "open": "営業中｜今夜 {t} まで", "closed": "準備中｜{t} 点灯",
            "basketLabel": "カゴ：{n} 品、{total}。番号札を開く", "added": "{name} をカゴへ（{n}）",
            "less": "{name} を一つ減らす", "more": "{name} を一つ増やす",
            "geoWait": "位置を確認中…", "geoFail": "位置情報が取得できませんでした。「道順を見る」をどうぞ。",
            "geoOk": "蒜串屋まで約 {d}、徒歩約 {m} 分です。",
            "notes": {"spice": {"0": "不辣 辛くない", "1": "小辣 小辛", "2": "中辣 中辛", "3": "大辣 大辛"},
                      "garlic": {"yes": "要蒜 にんにく", "more": "多蒜 にんにく多め", "no": "不要蒜 にんにくなし"},
                      "basil": {"yes": "要九層塔 バジル", "no": "不要九層塔 バジルなし"}},
        },
        "credit": "写真はUnsplashのイメージです。",
        "follow": "フォロー", "delivery": "デリバリー",
    },
}

e = html.escape
ICONS = {**ICONS, "plus": '<path d="M12 5v14M5 12h14"/>', "minus": '<path d="M5 12h14"/>'}


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def items_index():
    out = {}
    for g in MENU:
        for (iid, price, zh, en, ja, nzh, nen, nja, sig) in g["items"]:
            out[iid] = {"price": price, "zh": zh, "en": en, "ja": ja, "sig": sig}
    return out


IDX = items_index()


def nm(iid, lang):
    return IDX[iid][lang]


def maps():
    q = SITE["maps_query"]
    lat, lng = SITE["geo"]
    return (f"https://www.google.com/maps?q={quote(q)}&ll={lat},{lng}&z=17&output=embed",
            f"https://www.google.com/maps/dir/?api=1&destination={quote(q)}")


def tray(iid, photo, lang, L, eager):
    it = IDX[iid]
    name = nm(iid, lang)
    sub = f"<small>{e(it['zh'])}</small>" if lang != "zh" else ""
    sig = f'<span class="sig">{"招牌" if lang == "zh" else ("名物" if lang == "ja" else "Signature")}</span>' if it["sig"] else ""
    if photo:
        src = U + photo
        img = (f'<img src="{src}?w=420&h=315&fit=crop&q=70&auto=format" '
               f'srcset="{src}?w=280&h=210&fit=crop&q=70&auto=format 280w, {src}?w=420&h=315&fit=crop&q=70&auto=format 420w, {src}?w=640&h=480&fit=crop&q=70&auto=format 640w" '
               f'sizes="(max-width: 700px) 46vw, 210px" alt="" loading="{"eager" if eager else "lazy"}" decoding="async">')
    else:
        img = ""
    return (f'<button type="button" class="tray" data-item="{iid}" aria-pressed="false">'
            f'<span class="tray-pan">{img}</span>'
            f'<span class="tag"><span class="clip" aria-hidden="true"></span>{sig}<b>${it["price"]}</b><span>{e(name)}</span>{sub}</span>'
            f'<span class="tally" aria-hidden="true"></span></button>')


def schema(lang, L):
    v1 = V1["schema"](lang, {**V1L[lang], "path": L["path"], "desc": L["desc"], "faq": V1L[lang]["faq"]})
    return v1


def page(lang):
    L = LANGS[lang]
    v1 = V1L[lang]
    a = L["a"]
    name = SITE["name"][lang]
    url = SITE["domain"] + L["path"]
    embed, directions = maps()
    tel = "tel:" + SITE["phone"].replace("-", "")
    alternates = "\n".join(f'<link rel="alternate" hreflang="{LANGS[k]["html_lang"]}" href="{SITE["domain"]}{LANGS[k]["path"]}">' for k in LANGS)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE["domain"]}/">'
    langs = "".join(
        f'<a href="{(a + LANGS[k]["path"].lstrip("/")) or "./"}" hreflang="{LANGS[k]["html_lang"]}" lang="{LANGS[k]["html_lang"]}"'
        f'{" aria-current=" + chr(34) + "true" + chr(34) if k == lang else ""}>{lab}</a>'
        for k, lab in (("zh", "中"), ("en", "EN"), ("ja", "日")))
    fonts = "family=Noto+Sans+TC:wght@400;500;700;900&family=Permanent+Marker"
    if lang == "ja":
        fonts += "&family=Noto+Sans+JP:wght@400;500;700;900"
    nav = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in L["nav"])
    shelves = []
    for si, (title, trays) in enumerate(SHELVES):
        shelves.append(f'<div class="shelf"><h3>{e(title[lang])}</h3><div class="trays">'
                       + "".join(tray(i, p, lang, L, si == 0) for i, p in trays) + "</div></div>")
    board = []
    for g in MENU:
        rows = []
        for (iid, price, zh, en, ja, *_rest) in g["items"]:
            n = {"zh": zh, "en": en, "ja": ja}[lang]
            sub = f"<small>{e(zh)}</small>" if lang != "zh" else ""
            rows.append(f'<li><button type="button" class="row" data-item="{iid}" data-count="0">'
                        f'<span class="n">{e(n)}{sub}</span><span class="p">{price}</span><span class="plus" aria-hidden="true">{icon('plus')}<i></i></span></button></li>')
        note = g["note"][lang]
        board.append(f'<div class="board-group"><h3>{e(g["title"][lang])}{f"<small>{e(note)}</small>" if note else ""}</h3><ul>{"".join(rows)}</ul></div>')
    qs = "".join(
        f'<fieldset class="q"><legend>{e(q)}</legend><div class="chips">'
        + "".join(f'<label><input type="radio" name="{k}" value="{v}"><span>{e(t)}</span></label>' for v, t in opts)
        + "</div></fieldset>"
        for k, q, opts in L["qs"])
    stickers = "".join(
        f'<div class="sticker s{i}"><b>{p}<small>{e(L["per"]) if i < 2 else ""}</small></b><h3>{e(t[lang])}</h3><p>{e(d[lang])}</p></div>'
        for i, (p, t, d) in enumerate(DRINK_PLANS))
    hours = "".join(f'<tr data-day="{d}"><td>{e(lab)}</td><td>{e(t)}</td></tr>' for d, lab, t in L["hours_rows"])
    faq = "".join(f"<details><summary>{e(q)}{icon('plus')}</summary><p>{e(x)}</p></details>" for q, x in v1["faq"])
    data = {
        "strings": L["strings"],
        "geo": list(SITE["geo"]),
        "icons": {"plus": icon("plus"), "minus": icon("minus")},
        "items": {k: {"price": v["price"], "zh": v["zh"], "name": v[lang]} for k, v in IDX.items()},
    }
    h1_cls = ' class="latin"' if lang == "en" else ""
    sub = "".join(f"<span>{e(s)}</span>" for s in L["sub"])
    return f"""<!doctype html>
<html lang="{L['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(L['title'])}</title>
<meta name="description" content="{e(L['desc'])}">
<link rel="canonical" href="{url}">
{alternates}
<meta name="theme-color" content="#c8161d">
<meta property="og:type" content="restaurant.restaurant">
<meta property="og:site_name" content="{e(name)}">
<meta property="og:title" content="{e(L['title'])}">
<meta property="og:description" content="{e(L['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{L['og_locale']}">
<meta property="og:image" content="{U}1682264895449-f75b342cbab6?w=1200&h=630&fit=crop&q=75">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{a}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="{a}assets/stall.css">
{schema(lang, L)}
</head>
<body>
<header class="sign sign-screws">
  <div class="wrap">
    <div class="sign-top"><nav class="lang" aria-label="Language">{langs}</nav></div>
    <div class="sign-main"><h1{h1_cls}>{e(name)}</h1>
    <p class="sign-sub">{sub}</p></div>
  </div>
</header>
<div class="tube-row" data-status data-open="false">
  <div class="wrap" style="display:flex;align-items:center;gap:16px"><span class="tube" aria-hidden="true"></span><p class="status" role="status">…</p></div>
</div>
<nav class="rail" aria-label="{e(L['nav'][0][1])}">
  <div class="wrap">
    <a class="rail-name" href="#top">{e(name)}</a>
    {nav}
    <span class="walk">{e(L['walk'])}</span><a class="rail-go" href="{directions}" rel="noopener">{icon('pin')}{e(L['go'])}</a>
  </div>
</nav>

<main id="top">
<section class="case-wrap" id="case" aria-labelledby="case-h">
  <div class="wrap">
    <div class="case">
      <div class="case-light" aria-hidden="true"></div>
      <div class="kraft"><h2 id="case-h">{e(L['kraft_h'])}</h2><p>{e(L['kraft_p'])}</p><small>{e(L['photo_note'])}</small></div>
      {''.join(shelves)}
    </div>
    <div class="counter">
      <p>{icon('train')}{e(L['counter'])}</p>
      <div class="btns">
        <a class="btn btn-go" href="{directions}" rel="noopener">{icon('pin')}{e(L['go'])}</a>
        <a class="btn btn-plain" href="{SITE['reserve_url']}" rel="noopener">{icon('ticket')}{e(L['waitlist'])}</a>
      </div>
    </div>
  </div>
</section>

<div class="steel" aria-hidden="true"><span></span></div>
<section class="section" id="prices" aria-labelledby="prices-h">
  <div class="wrap">
    <h2 id="prices-h">{e(L['prices_h'])}</h2>
    <p class="lead">{e(L['prices_p'])}</p>
    <div class="board">{''.join(board)}<p class="board-note">{e(L['board_note'])}</p></div>
  </div>
</section>

<div class="steel" aria-hidden="true"><span></span></div>
<section class="section ask" id="ask" aria-labelledby="ask-h">
  <div class="ask-photo"><img src="{GARLIC}?w=1600&q=65&auto=format" alt="" loading="lazy" decoding="async"></div>
  <div class="wrap">
    <div>
      <h2 id="ask-h">{e(L['ask_h'])}</h2>
      <p class="lead">{e(L['ask_p'])}</p>
      <div class="qs">{qs}</div>
      <p class="ask-note">{e(L['ask_note'])}</p>
    </div>
    <div class="ask-big" lang="zh-Hant" aria-hidden="true">蒜</div>
  </div>
</section>

<div class="steel" aria-hidden="true"><span></span></div>
<section class="section drinks" id="drinks" aria-labelledby="drinks-h">
  <div class="wrap fridge-grid">
    <div class="drinks-copy">
      <h2 id="drinks-h">{e(L['drinks_h'])}</h2>
      <p class="lead">{e(L['drinks_p'])}</p>
      <p class="fine">{e(L['fine'])}</p>
    </div>
    <div class="fridge">
      <div class="fridge-crown" lang="zh-Hant" aria-hidden="true">冰</div>
      <div class="fridge-door">
        <img src="{BEER}?w=900&q=70&auto=format" alt="{e(v1['drinks_alt'])}" loading="lazy" decoding="async">
        <div class="stickers">{stickers}</div>
      </div>
      <span class="fridge-handle" aria-hidden="true"></span>
    </div>
  </div>
</section>

<div class="steel" aria-hidden="true"><span></span></div>
<section class="section visit" id="visit" aria-labelledby="visit-h">
  <div class="wrap visit-grid">
    <div>
      <h2 id="visit-h">{e(L['visit_h'])}</h2>
      <div class="facts">
        <div class="fact">{icon('pin')}<div><h3>{e(L['f']['addr'])}</h3><address>{e(SITE['address'][lang])}</address></div></div>
        <div class="fact">{icon('train')}<div><h3>{e(L['f']['mrt'])}</h3><p>{e(L['mrt'])}</p></div></div>
        <div class="fact">{icon('clock')}<div><h3>{e(L['f']['hours'])}</h3><table class="hours"><tbody>{hours}</tbody></table></div></div>
        <div class="fact">{icon('phone')}<div><h3>{e(L['f']['phone'])}</h3><p><a href="{tel}">{e(SITE['phone_display'])}</a></p></div></div>
      </div>
      <div class="distance">
        <button type="button" class="btn btn-line" data-distance>{icon('pin')}{e(L['dist_btn'])}</button>
        <p data-distance-out aria-live="polite">{e(L['dist_hint'])}</p>
      </div>
      <div class="btns" style="display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn-go" href="{directions}" rel="noopener">{icon('pin')}{e(L['go'])}</a>
        <a class="btn btn-line" href="{tel}">{icon('phone')}{e(L['call'])}</a>
      </div>
    </div>
    <div class="map-frame"><iframe src="{embed}" title="{e(L['map_title'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
  </div>
</section>

<section class="section review" aria-labelledby="review-h">
  <div class="wrap">
    <div><h2 id="review-h">{e(v1['review_h'])}</h2><p>{e(v1['review_p'])}</p></div>
    <a class="btn" href="{SITE['review_url']}" rel="noopener">{icon('star')}{e(v1['review_btn'])}</a>
  </div>
</section>

<div class="steel" aria-hidden="true"><span></span></div>
<section class="section faq" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <h2 id="faq-h">{e(v1['faq_h'])}</h2>
    <div class="faq-list">{faq}</div>
  </div>
</section>
</main>

<footer class="foot">
  <div class="wrap">
    <div><strong>{e(name)}</strong><p style="margin:0 0 6px">{e(SITE['name_alt'][lang])}</p><address>{e(SITE['address'][lang])}<br><a href="{tel}">{e(SITE['phone_display'])}</a></address></div>
    <div><h2>{e(L['follow'])}</h2><ul><li><a href="{SITE['instagram']}" rel="noopener">Instagram</a></li><li><a href="{SITE['facebook']}" rel="noopener">Facebook</a></li></ul></div>
    <div><h2>{e(L['delivery'])}</h2><ul><li><a href="{SITE['ubereats']}" rel="noopener">Uber Eats</a></li><li><a href="{SITE['foodpanda']}" rel="noopener">foodpanda</a></li></ul></div>
    <p class="credit">© {e(name)} · {e(L['credit'])}</p>
  </div>
</footer>

<div class="basket-bar">
  <button type="button" class="basket" data-basket><span class="count">0</span><span class="sum"><small>{e(L['basket'])}</small><b>NT$0</b></span></button>
  <a class="btn btn-go go-mini" href="{directions}" rel="noopener">{icon('pin')}{e(L['go'])}</a>
</div>
<p class="sr-only" aria-live="polite" data-live></p>

<dialog class="plate" aria-labelledby="plate-h">
  <div class="plate-head"><h2 id="plate-h">{e(name)}　{e(L['plate_h'])}</h2><span class="plate-num" aria-label="{e(L['plate_h'])}"></span></div>
  <div class="plate-body">
    <p class="plate-empty">{e(L['plate_empty'])}</p>
    <ol></ol>
    <p class="plate-notes"></p>
    <p class="plate-total"><span>{e(L['plate_total'])}</span><b></b></p>
    <p style="margin:0 0 16px;color:var(--ink-soft);font-size:14px">{e(L['plate_hint'])}</p>
    <div class="plate-btns">
      <button type="button" class="btn btn-plain" data-close>{e(L['plate_close'])}</button>
      <button type="button" class="btn btn-line" data-clear>{e(L['plate_clear'])}</button>
    </div>
  </div>
</dialog>

<script type="application/json" id="stall-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{a}assets/stall.js" defer></script>
</body>
</html>
"""


def main():
    for lang, L in LANGS.items():
        out = ROOT / L["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
    # sitemap / robots 與第一版相同
    for f in ("sitemap.xml", "robots.txt"):
        (ROOT / f).write_text((ROOT.parent / "v1" / f).read_text(encoding="utf-8"), encoding="utf-8")
    fav = (ROOT.parent / "v1" / "assets" / "favicon.svg").read_text(encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(fav.replace("#f6c400", "#c8161d").replace('fill="#17130f">蒜', 'fill="#ffd21f">蒜'), encoding="utf-8")
    print("wrote sitemap.xml, robots.txt, favicon.svg")


if __name__ == "__main__":
    main()
