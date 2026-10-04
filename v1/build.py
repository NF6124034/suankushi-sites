# -*- coding: utf-8 -*-
"""
蒜串屋 網站產生器
================
改店名、地址、電話、菜單、價格：只要改這個檔案上半部的 SITE 和 MENU，
然後執行：  python build.py
就會重新產生 index.html（中文）、en/index.html、ja/index.html、sitemap.xml、robots.txt。

所有標了 TODO 的地方，開店前都要換成真的資料。
"""
import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent

# ======================================================================
# 1. 店家基本資料（NAP：Name / Address / Phone）
#    這三項要和 Google 商家檔案「一字不差」，SEO 才會加分。
# ======================================================================
SITE = {
    "domain": "https://www.suankushi.tw",          # TODO 你的網域，結尾不要加 /
    "name": {"zh": "蒜串屋", "en": "Garlic Kushi", "ja": "蒜串屋"},
    "name_alt": {"zh": "Garlic Kushi", "en": "蒜串屋", "ja": "にんにく串屋"},
    "phone": "+886-2-0000-0000",                     # TODO
    "phone_display": "(02) 0000-0000",               # TODO
    "postal": "106",
    "address": {                                     # TODO 真實地址
        "zh": "台北市大安區忠孝東路四段000號",
        "en": "No. 000, Sec. 4, Zhongxiao E. Rd., Da'an Dist., Taipei 106",
        "ja": "台北市大安区忠孝東路四段000号",
    },
    "street_schema": "忠孝東路四段000號",            # TODO
    "geo": (25.04149, 121.55095),                     # TODO 店的經緯度（Google Maps 右鍵就能看到）
    # 有了 Google 商家檔案後，把這裡換成「蒜串屋 忠孝東路…」這種店名＋地址的字串，地圖就會直接指到你的店
    "maps_query": "捷運忠孝敦化站",                   # TODO
    "reserve_url": "https://line.me/R/ti/p/@suankushi",   # TODO 線上候位／訂位連結（LINE、inline、EZTABLE…）
    "review_url": "https://search.google.com/local/writereview?placeid=YOUR_PLACE_ID",  # TODO
    "instagram": "https://www.instagram.com/suankushi",   # TODO
    "facebook": "https://www.facebook.com/suankushi",     # TODO
    "ubereats": "https://www.ubereats.com/tw",            # TODO 換成你的店家頁
    "foodpanda": "https://www.foodpanda.com.tw",          # TODO 換成你的店家頁
    "price_range": "NT$300–600",
}

# 營業時間（記得 assets/app.js 最上面的 HOURS 也要一起改）
HOURS_SCHEMA = [
    (["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"], "17:30", "01:30"),
    (["Friday", "Saturday"], "17:30", "02:00"),
]

# ======================================================================
# 2. 菜單：(id, 價格, 中文, 英文, 日文, 說明中, 說明英, 說明日, 標籤)
# ======================================================================
MENU = [
    {
        "title": {"zh": "炭火串燒", "en": "Charcoal skewers", "ja": "炭火串焼き"},
        "note": {"zh": "現點現烤", "en": "grilled to order", "ja": "注文後に焼きます"},
        "items": [
            ("leg", 65, "蒜酥去骨雞腿", "Boneless thigh, garlic crumble", "鶏もも にんにくチップ", "烤好再撒現炸蒜酥", "finished with fresh-fried garlic", "揚げたてにんにくをのせて", True),
            ("negima", 55, "蔥段雞肉", "Chicken & scallion (negima)", "ねぎま", "", "", "", False),
            ("skin", 45, "脆皮雞皮", "Crispy chicken skin", "パリパリ鶏皮", "逼油烤到脆", "rendered until it crackles", "脂を落としてカリッと", False),
            ("tail", 40, "雞屁股", "Chicken tail (bonjiri)", "ぼんじり", "", "", "", False),
            ("heart", 45, "醬燒雞心", "Tare-glazed chicken heart", "ハツ タレ焼き", "", "", "", False),
            ("cart", 50, "雞軟骨", "Chicken cartilage", "なんこつ", "", "", "", False),
            ("pork", 60, "豬五花蔥卷", "Pork belly & scallion roll", "豚バラねぎ巻き", "", "", "", False),
            ("beef", 75, "牛五花金針菇卷", "Beef belly & enoki roll", "牛バラえのき巻き", "", "", "", False),
        ],
    },
    {
        "title": {"zh": "台味串", "en": "Taiwanese street skewers", "ja": "台湾屋台串"},
        "note": {"zh": "夜市的味道", "en": "night-market classics", "ja": "夜市の定番"},
        "items": [
            ("gongwan", 35, "麻辣貢丸", "Spicy pork meatball", "麻辣肉団子", "", "", "", False),
            ("tofuskin", 35, "烤豆皮", "Grilled tofu skin", "湯葉焼き", "", "", "", False),
            ("ricesausage", 40, "糯米腸", "Sticky rice sausage", "もち米腸詰め", "", "", "", False),
            ("bloodcake", 35, "豬血糕", "Pig's blood rice cake", "豚血もち", "花生粉＋香菜", "peanut powder & cilantro", "ピーナッツ粉とパクチー", False),
            ("fishcake", 35, "烤甜不辣", "Grilled fish cake", "さつま揚げ焼き", "", "", "", False),
            ("corn", 40, "奶油玉米", "Buttered corn", "バターコーン", "", "", "", False),
            ("shiitake", 40, "鹽烤香菇", "Salt-grilled shiitake", "椎茸の塩焼き", "", "", "", False),
        ],
    },
    {
        "title": {"zh": "蒜香炸物", "en": "Garlic fried", "ja": "にんにく揚げ物"},
        "note": {"zh": "起鍋前大把蒜仁同炸", "en": "tossed with fried garlic", "ja": "にんにくと一緒に揚げ"},
        "items": [
            ("popcorn", 120, "招牌蒜香鹹酥雞", "Garlic popcorn chicken", "台湾式からあげ にんにく", "", "", "", True),
            ("squid", 150, "胡椒魷魚", "Pepper squid", "イカの胡椒揚げ", "", "", "", False),
            ("cartfried", 100, "炸雞軟骨", "Fried chicken cartilage", "なんこつ揚げ", "", "", "", False),
            ("oyster", 70, "杏鮑菇", "King oyster mushroom", "エリンギ揚げ", "", "", "", False),
            ("beans", 60, "四季豆", "Green beans", "いんげん揚げ", "", "", "", False),
            ("sweetpotato", 60, "梅粉地瓜條", "Sweet potato fries, plum powder", "さつまいも 梅パウダー", "", "", "", False),
            ("tempura", 50, "炸甜不辣", "Fried fish cake", "さつま揚げ", "", "", "", False),
        ],
    },
    {
        "title": {"zh": "日式串炸", "en": "Kushikatsu", "ja": "串カツ"},
        "note": {"zh": "附特製沾醬", "en": "with house dipping sauce", "ja": "特製ソース付き"},
        "items": [
            ("shrimp", 70, "炸蝦串", "Shrimp kushikatsu", "海老串カツ", "", "", "", False),
            ("beefkatsu", 80, "炸牛肉串", "Beef kushikatsu", "牛串カツ", "", "", "", False),
            ("chikuwa", 50, "起司竹輪", "Cheese-stuffed chikuwa", "チーズちくわ", "", "", "", False),
            ("quail", 40, "鵪鶉蛋", "Quail eggs", "うずら", "", "", "", False),
        ],
    },
    {
        "title": {"zh": "收尾", "en": "To finish", "ja": "〆"},
        "note": {"zh": "", "en": "", "ja": ""},
        "items": [
            ("onigiri", 60, "醬油烤飯糰", "Soy-grilled rice ball", "焼きおにぎり", "", "", "", False),
            ("noodles", 90, "蒜油拌麵", "Garlic oil noodles", "にんにく油そば", "", "", "", False),
        ],
    },
]

DRINK_PLANS = [
    # (價格, 標題 zh/en/ja, 說明 zh/en/ja)
    (399, {"zh": "台啤生啤 2 小時暢飲", "en": "Draft Taiwan Beer, 2 hrs", "ja": "台湾ビール生 2時間飲み放題"},
          {"zh": "每人，全桌一起參加", "en": "per person, whole table joins", "ja": "お一人様・全員参加"}),
    (599, {"zh": "生啤＋Highball＋梅酒 2 小時", "en": "Beer + highball + umeshu, 2 hrs", "ja": "生ビール・ハイボール・梅酒 2時間"},
          {"zh": "每人，全桌一起參加", "en": "per person, whole table joins", "ja": "お一人様・全員参加"}),
    (120, {"zh": "台啤生啤 單杯", "en": "Draft Taiwan Beer", "ja": "台湾ビール生 一杯"},
          {"zh": "也有梅酒 Highball 150、熱清酒一合 180", "en": "Umeshu highball 150 · hot sake (1 gō) 180", "ja": "梅酒ハイボール150・熱燗一合180"}),
]

PHOTOS = {
    "hero": "https://images.unsplash.com/photo-1763604048392-18f8383a6542",
    "fried": "https://images.unsplash.com/photo-1633945488458-f8cc1f3a0144",
    "grill": "https://images.unsplash.com/photo-1790006696822-ce7f9e8a761a",
    "table": "https://images.unsplash.com/photo-1766762462673-85a4dbfff363",
}

# ======================================================================
# 3. 各語言文案
# ======================================================================
LANGS = {
    "zh": {
        "html_lang": "zh-Hant-TW", "og_locale": "zh_TW", "path": "/", "out": "index.html", "asset": "",
        "title": "蒜串屋｜忠孝敦化串燒・蒜香炸物・宵夜居酒屋（每天到 01:30）",
        "desc": "台北東區忠孝敦化站旁的串燒炸物居酒屋。炭火串燒一串 35 元起、招牌蒜香鹹酥雞、生啤 2 小時暢飲 399 元，每天營業到凌晨 1:30，有冷氣、可線上候位、外帶外送。",
        "nav": ["菜單", "喝酒", "怎麼來", "常見問題"],
        "tagline": "炸物・串燒・酒場",
        "lede": "台式蒜香炸物，配炭火串燒，開到半夜。",
        "sub": "鹹酥雞的蒜香、居酒屋的炭火，再加上冷氣，一次吃齊。捷運忠孝敦化站走路 3 分鐘。",
        "status_init": "查看營業狀態…",
        "cta_reserve": "線上候位", "cta_go": "導航過來", "cta_menu": "看菜單", "cta_call": "打電話",
        "strip": ["忠孝敦化站 3 分鐘", "有冷氣", "外帶・外送", "一串 35 元起"],
        "hero_alt": "炭火上冒著煙的串燒",
        "hero_cap": "示意照片",
        "why_h": "四個字，講完這家店",
        "why_intro": "我們把台北人最愛的兩種宵夜放在同一張桌上：夜市鹹酥雞攤的蒜香，和居酒屋的炭火串燒。",
        "glyphs": [
            ("蒜", "台式蒜香", "鹹酥雞的靈魂是蒜。炸物起鍋前下大把蒜仁一起爆香，串燒烤好再撒一層現炸蒜酥。"),
            ("炭", "炭火現烤", "串燒全部上炭火，點了才烤。雞皮慢慢逼油，烤到一咬就碎。"),
            ("夜", "開到深夜", "每天開到 01:30，週五、週六到 02:00。加班完、續攤、追劇餓了都來得及。"),
            ("涼", "有冷氣，免路邊排", "不用站在路邊流汗排隊。線上拿號碼，快輪到再過來。"),
        ],
        "fried_alt": "一盤蒜香鹹酥雞", "grill_alt": "師傅在夜裡烤串燒",
        "menu_h": "點菜單",
        "menu_p": "勾選想吃的品項，下面會幫你算好總價。到店後按「放大給店員看」，直接把手機遞給店員就能點餐。",
        "slip_title": "點 菜 單", "slip_table": "桌號", "slip_hand": "＿＿＿",
        "slip_unit": "價格（元）",
        "tag": "招牌",
        "less": "少一份", "more": "多一份",
        "total": "小計", "show": "放大給店員看", "clear": "全部清掉",
        "slip_note": "價格含稅，不收服務費。菜色依當日進貨可能調整，以店內為準。",
        "staff_h": "點 菜 單", "staff_total": "小計", "staff_close": "好，收起來",
        "drinks_h": "喝一杯，再一杯",
        "drinks_p": "炸物和串燒都偏鹹香，最對味的就是冰涼的生啤。人多就選暢飲，兩小時內隨你續。",
        "drinks_alt": "桌上的串燒和啤酒", "drinks_cap": "示意照片",
        "drinks_fine": "禁止酒駕・飲酒過量，有害健康。未滿 18 歲請勿飲酒。",
        "per": "/人",
        "visit_h": "怎麼來",
        "f_addr": "地址", "f_mrt": "捷運", "f_hours": "營業時間", "f_phone": "電話",
        "mrt": "板南線忠孝敦化站 3 號出口，步行約 3 分鐘",
        "hours_rows": [("0,1,2,3,4", "週日–週四", "17:30 – 01:30"), ("5,6", "週五–週六", "17:30 – 02:00")],
        "map_title": "蒜串屋在 Google 地圖上的位置",
        "review_h": "吃得開心，幫我們留一句話",
        "review_p": "你在 Google 上的一句話，會幫下一個找宵夜的人做決定。好吃、不好吃都歡迎直說，我們每則都會看。",
        "review_btn": "寫 Google 評論",
        "faq_h": "常見問題",
        "faq": [
            ("需要先訂位嗎？", "4 人以下可以直接來，現場或線上候位都可以；5 人以上建議先訂位，我們會幫你把桌子併好。"),
            ("可以外帶或外送嗎？", "全部品項都可以外帶。外送可以在 Uber Eats、foodpanda 搜尋「蒜串屋」。"),
            ("營業到幾點？", "週日到週四 17:30–01:30，週五、週六 17:30–02:00。最後點餐時間是打烊前 30 分鐘。"),
            ("有低消或服務費嗎？", "沒有低消，也不收服務費。"),
            ("有素食可以吃嗎？", "香菇、玉米、杏鮑菇、四季豆、地瓜條都是蔬食。炸物和葷食共用炸油，嚴格素食者請斟酌。"),
            ("可以包場或辦聚餐嗎？", "可以，平日 20 人以上可以討論包場，請先打電話或私訊我們。"),
        ],
        "foot_nav": "看看", "foot_follow": "追蹤我們", "foot_order": "外送",
        "credit": "網站示意照片來自 Unsplash。",
        "dock": ["導航", "電話", "線上候位"],
    },
    "en": {
        "html_lang": "en", "og_locale": "en_US", "path": "/en/", "out": "en/index.html", "asset": "../",
        "title": "Garlic Kushi | Late-night Yakitori & Fried Chicken, Taipei",
        "desc": "Late-night izakaya in Taipei's East District, 3 min from MRT Zhongxiao Dunhua. Charcoal yakitori from NT$35, garlic Taiwanese popcorn chicken, 2-hour draft beer from NT$399. Open until 1:30am daily.",
        "nav": ["Menu", "Drinks", "Find us", "FAQ"],
        "tagline": "炸物・串燒・酒場",
        "lede": "Taiwanese garlic fried chicken and charcoal skewers, served until late.",
        "sub": "The garlic of a Taipei night-market fry stall and the charcoal grill of an izakaya, in one air-conditioned room. 3 minutes from MRT Zhongxiao Dunhua.",
        "status_init": "Checking hours…",
        "cta_reserve": "Join the waitlist", "cta_go": "Directions", "cta_menu": "See the menu", "cta_call": "Call",
        "strip": ["3 min from MRT Zhongxiao Dunhua", "Air-conditioned", "Takeaway & delivery", "Skewers from NT$35"],
        "hero_alt": "Skewers smoking over a charcoal grill",
        "hero_cap": "Illustrative photo",
        "why_h": "Four characters say it all",
        "why_intro": "We put Taipei's two favourite late-night foods on one table: the garlic of the night-market fried chicken stall and the charcoal skewers of the izakaya.",
        "glyphs": [
            ("蒜", "Garlic", "Garlic is the soul of Taiwanese fried chicken. A fistful goes into the fryer with every order, and our skewers get a shower of fresh-fried garlic crumble."),
            ("炭", "Charcoal", "Every skewer is grilled over charcoal, only after you order. Chicken skin is rendered slowly until it shatters."),
            ("夜", "Night", "Open until 1:30am every day, 2am on Friday and Saturday. Plenty of time after overtime, after the first bar, or after one more episode."),
            ("涼", "Cool", "No sweating in a sidewalk queue. Grab a number online and come over when your table is nearly ready."),
        ],
        "fried_alt": "A plate of garlic Taiwanese popcorn chicken", "grill_alt": "A cook grilling skewers at night",
        "menu_h": "The order slip",
        "menu_p": "Tick what you want and we'll add it up. At the restaurant, tap “Show the staff” and hand over your phone — that's your order.",
        "slip_title": "ORDER", "slip_table": "Table", "slip_hand": "＿＿＿",
        "slip_unit": "NT$",
        "tag": "Signature",
        "less": "One less", "more": "One more",
        "total": "Subtotal", "show": "Show the staff", "clear": "Clear all",
        "slip_note": "Prices include tax. No service charge. Items may change with the day's market.",
        "staff_h": "ORDER", "staff_total": "Subtotal", "staff_close": "Done",
        "drinks_h": "One drink, then another",
        "drinks_p": "Salty, garlicky, smoky food wants a cold draft beer. Coming in a group? Take the 2-hour free-flow and keep the glasses full.",
        "drinks_alt": "Skewers and beer on a table", "drinks_cap": "Illustrative photo",
        "drinks_fine": "Please drink responsibly. Never drink and drive. Alcohol served to guests 18 and over.",
        "per": "/person",
        "visit_h": "Find us",
        "f_addr": "Address", "f_mrt": "MRT", "f_hours": "Hours", "f_phone": "Phone",
        "mrt": "Zhongxiao Dunhua Station (Bannan Line), Exit 3 — about a 3-minute walk",
        "hours_rows": [("0,1,2,3,4", "Sun–Thu", "17:30 – 01:30"), ("5,6", "Fri–Sat", "17:30 – 02:00")],
        "map_title": "Garlic Kushi on Google Maps",
        "review_h": "Enjoyed it? Leave us a line",
        "review_p": "A sentence on Google helps the next hungry person decide. Good or bad, tell us straight — we read every one.",
        "review_btn": "Write a Google review",
        "faq_h": "FAQ",
        "faq": [
            ("Do I need a reservation?", "Groups of up to 4 can walk in or join the online waitlist. For 5 or more, please book ahead so we can set up your table."),
            ("Do you do takeaway or delivery?", "Everything on the menu is available to take away. For delivery, search “蒜串屋” on Uber Eats or foodpanda."),
            ("How late are you open?", "Sunday to Thursday 17:30–01:30, Friday and Saturday 17:30–02:00. Last orders 30 minutes before closing."),
            ("Is there a minimum spend or service charge?", "No minimum spend and no service charge."),
            ("Do you have vegetarian options?", "Shiitake, corn, king oyster mushroom, green beans and sweet potato fries are meat-free. The fryer oil is shared with meat."),
            ("Can we book the whole place?", "Yes — on weekdays, groups of 20 or more can book the restaurant. Call or message us first."),
        ],
        "foot_nav": "Explore", "foot_follow": "Follow", "foot_order": "Delivery",
        "credit": "Illustrative photos via Unsplash.",
        "dock": ["Directions", "Call", "Waitlist"],
    },
    "ja": {
        "html_lang": "ja", "og_locale": "ja_JP", "path": "/ja/", "out": "ja/index.html", "asset": "../",
        "title": "蒜串屋｜台北・忠孝敦化の焼き鳥と台湾式からあげ 毎日深夜1時半まで",
        "desc": "台北・忠孝敦化駅から徒歩3分の串焼き・揚げ物居酒屋。炭火串焼き1本NT$35から、名物にんにく台湾からあげ、生ビール2時間飲み放題NT$399。毎日深夜1:30まで営業、テイクアウト可。",
        "nav": ["メニュー", "お酒", "アクセス", "よくある質問"],
        "tagline": "炸物・串燒・酒場",
        "lede": "台湾式にんにく揚げ物と炭火串焼き、深夜まで。",
        "sub": "夜市の唐揚げ屋台のにんにくの香りと、居酒屋の炭火。冷房の効いた店内でどちらも楽しめます。MRT忠孝敦化駅から徒歩3分。",
        "status_init": "営業状況を確認中…",
        "cta_reserve": "オンライン順番待ち", "cta_go": "道順を見る", "cta_menu": "メニュー", "cta_call": "電話する",
        "strip": ["忠孝敦化駅 徒歩3分", "冷房完備", "テイクアウト・デリバリー", "串1本 NT$35〜"],
        "hero_alt": "炭火の上で煙を上げる串焼き",
        "hero_cap": "イメージ写真",
        "why_h": "この店を漢字四文字で",
        "why_intro": "台北の人が大好きな二つの夜食を一つのテーブルに。夜市の唐揚げ屋台のにんにくと、居酒屋の炭火串焼きです。",
        "glyphs": [
            ("蒜", "にんにく", "台湾式からあげの決め手はにんにく。揚げ上がり直前にたっぷり加え、串焼きには揚げたてのにんにくチップをのせます。"),
            ("炭", "炭火", "串焼きはすべて注文後に炭火で。鶏皮はじっくり脂を落とし、パリッと仕上げます。"),
            ("夜", "深夜", "毎日深夜1:30まで、金・土は2:00まで。残業帰りにも、二軒目にも。"),
            ("涼", "冷房完備", "歩道で汗をかきながら並ぶ必要はありません。オンラインで順番を取って、近くなったらお越しください。"),
        ],
        "fried_alt": "にんにく台湾からあげ", "grill_alt": "夜に串を焼く職人",
        "menu_h": "注文票",
        "menu_p": "食べたいものにチェックすると合計が出ます。お店で「店員に見せる」を押して、スマホをそのまま見せれば注文完了です。",
        "slip_title": "注 文 票", "slip_table": "卓番", "slip_hand": "＿＿＿",
        "slip_unit": "価格（NT$）",
        "tag": "名物",
        "less": "一つ減らす", "more": "一つ増やす",
        "total": "小計", "show": "店員に見せる", "clear": "すべて消す",
        "slip_note": "税込・サービス料なし。仕入れにより内容が変わる場合があります。",
        "staff_h": "注 文 票", "staff_total": "小計", "staff_close": "閉じる",
        "drinks_h": "もう一杯、もう一杯",
        "drinks_p": "塩気とにんにく、炭の香りには冷えた生ビール。グループなら2時間飲み放題がお得です。",
        "drinks_alt": "テーブルの串焼きとビール", "drinks_cap": "イメージ写真",
        "drinks_fine": "飲酒運転は法律で禁止されています。20歳未満の方の飲酒はご遠慮ください。",
        "per": "/人",
        "visit_h": "アクセス",
        "f_addr": "住所", "f_mrt": "MRT", "f_hours": "営業時間", "f_phone": "電話",
        "mrt": "板南線 忠孝敦化駅 3番出口から徒歩約3分",
        "hours_rows": [("0,1,2,3,4", "日〜木", "17:30 – 01:30"), ("5,6", "金・土", "17:30 – 02:00")],
        "map_title": "Googleマップで見る蒜串屋",
        "review_h": "おいしかったら、ひとことください",
        "review_p": "Googleへのひとことが、次に夜食を探す人の参考になります。良かった点も悪かった点も、遠慮なくどうぞ。",
        "review_btn": "Googleでレビューを書く",
        "faq_h": "よくある質問",
        "faq": [
            ("予約は必要ですか？", "4名様まではそのままご来店いただくか、オンラインで順番待ちができます。5名様以上はご予約をおすすめします。"),
            ("テイクアウトやデリバリーはできますか？", "全メニューお持ち帰りできます。デリバリーはUber Eats・foodpandaで「蒜串屋」と検索してください。"),
            ("何時まで営業していますか？", "日〜木は17:30〜01:30、金・土は17:30〜02:00。ラストオーダーは閉店30分前です。"),
            ("最低料金やサービス料はありますか？", "どちらもありません。"),
            ("ベジタリアン向けメニューはありますか？", "椎茸、とうもろこし、エリンギ、いんげん、さつまいもは肉を使っていません。揚げ油は肉料理と共用です。"),
            ("貸切はできますか？", "平日20名様以上で承ります。まずはお電話かメッセージでご相談ください。"),
        ],
        "foot_nav": "サイト", "foot_follow": "フォロー", "foot_order": "デリバリー",
        "credit": "サイト内の写真はUnsplashのイメージです。",
        "dock": ["道順", "電話", "順番待ち"],
    },
}

# ======================================================================
# 以下是產生網頁的程式，一般不需要修改
# ======================================================================
ICONS = {
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92Z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "ticket": '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2M13 11v2M13 17v2"/>',
    "train": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M12 3v8M8 22l2-4M16 22l-2-4"/><path d="M8 15h.01M16 15h.01"/>',
    "snow": '<path d="M12 2v20M3.3 7l17.4 10M20.7 7 3.3 17"/><path d="m9 4 3 2 3-2M9 20l3-2 3 2"/>',
    "bag": '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/>',
    "skewer": '<path d="M3 21 21 3"/><circle cx="9" cy="15" r="2.4"/><circle cx="13" cy="11" r="2.4"/><circle cx="17" cy="7" r="2.4"/>',
    "star": '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01Z"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
}


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


e = html.escape


def img(src, w, alt, cls="", loading="lazy", sizes="100vw", fetch=""):
    widths = [480, 800, 1200, 1600]
    srcset = ", ".join(f"{src}?w={x}&q=70&auto=format&fit=crop {x}w" for x in widths)
    extra = f' fetchpriority="{fetch}"' if fetch else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src}?w={w}&q=70&auto=format&fit=crop" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{e(alt)}" loading="{loading}" decoding="async"{extra}>')


def maps_links():
    q = SITE["maps_query"]
    lat, lng = SITE["geo"]
    embed = f"https://www.google.com/maps?q={quote(q)}&ll={lat},{lng}&z=17&output=embed"
    directions = f"https://www.google.com/maps/dir/?api=1&destination={quote(q)}"
    return embed, directions


def schema(lang, L):
    url = SITE["domain"] + L["path"]
    menu_sections = []
    for g in MENU:
        menu_sections.append({
            "@type": "MenuSection",
            "name": g["title"][lang],
            "hasMenuItem": [{
                "@type": "MenuItem",
                "name": {"zh": it[2], "en": it[3], "ja": it[4]}[lang],
                "offers": {"@type": "Offer", "price": str(it[1]), "priceCurrency": "TWD"},
            } for it in g["items"]],
        })
    restaurant = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "@id": SITE["domain"] + "/#restaurant",
        "name": SITE["name"][lang],
        "alternateName": SITE["name_alt"][lang],
        "description": L["desc"],
        "url": url,
        "telephone": SITE["phone"],
        "image": [PHOTOS["hero"] + "?w=1200", PHOTOS["fried"] + "?w=1200", PHOTOS["table"] + "?w=1200"],
        "priceRange": SITE["price_range"],
        "servesCuisine": ["Yakitori", "Taiwanese fried chicken", "Kushikatsu", "Izakaya"],
        "acceptsReservations": True,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["street_schema"],
            "addressLocality": "大安區",
            "addressRegion": "台北市",
            "postalCode": SITE["postal"],
            "addressCountry": "TW",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["geo"][0], "longitude": SITE["geo"][1]},
        "hasMap": maps_links()[1],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c}
            for d, o, c in HOURS_SCHEMA
        ],
        "sameAs": [SITE["instagram"], SITE["facebook"]],
        "hasMenu": {"@type": "Menu", "url": url + "#menu", "hasMenuSection": menu_sections},
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in L["faq"]],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return (f'<script type="application/ld+json">\n{dump(restaurant)}\n</script>\n'
            f'<script type="application/ld+json">\n{dump(faq)}\n</script>')


def menu_html(lang, L):
    groups = []
    for g in MENU:
        rows = []
        for (iid, price, zh, en, ja, nzh, nen, nja, sig) in g["items"]:
            name = {"zh": zh, "en": en, "ja": ja}[lang]
            note = {"zh": nzh, "en": nen, "ja": nja}[lang]
            # 外語頁在品名下補中文，方便觀光客直接指給店員看
            if lang != "zh":
                note = f"{zh}" + (f" · {note}" if note else "")
            tag = f'<span class="tag">{e(L["tag"])}</span>' if sig else ""
            em = f"<em>{e(note)}</em>" if note else ""
            rows.append(
                f'<li class="item" data-price="{price}" data-zh="{e(zh)}">'
                f'<input type="checkbox" id="m-{iid}">'
                f'<label for="m-{iid}"><span class="box"><svg viewBox="0 0 34 30" aria-hidden="true"><path d="M4 15c3 2 6 6 8 10C17 15 23 7 32 2"/></svg></span>'
                f'<span class="name">{e(name)}{tag}{em}</span></label>'
                f'<span class="price"><span class="qty">'
                f'<button type="button" data-step="-1" aria-label="{e(L["less"])}：{e(name)}">−</button>'
                f'<output aria-live="polite">1</output>'
                f'<button type="button" data-step="1" aria-label="{e(L["more"])}：{e(name)}">+</button>'
                f'</span>{price}</span></li>'
            )
        note = g["note"][lang]
        small = f"<small>{e(note)}</small>" if note else ""
        groups.append(f'<div class="slip-group"><h3>{e(g["title"][lang])}{small}</h3><ul>{"".join(rows)}</ul></div>')
    return "\n".join(groups)


def page(lang):
    L = LANGS[lang]
    a = L["asset"]
    name = SITE["name"][lang]
    url = SITE["domain"] + L["path"]
    embed, directions = maps_links()
    tel = "tel:" + SITE["phone"].replace("-", "")
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{LANGS[k]["html_lang"]}" href="{SITE["domain"]}{LANGS[k]["path"]}">' for k in LANGS
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE["domain"]}/">'
    lang_switch = "".join(
        f'<a href="{(a + LANGS[k]["path"].lstrip("/")) or "./"}" hreflang="{LANGS[k]["html_lang"]}" '
        f'lang="{LANGS[k]["html_lang"]}"{" aria-current=" + chr(34) + "true" + chr(34) if k == lang else ""}>{lab}</a>'
        for k, lab in (("zh", "中"), ("en", "EN"), ("ja", "日"))
    )
    fonts = ("family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@700;900&family=LXGW+WenKai+TC:wght@400;700")
    if lang == "ja":
        fonts += "&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@700;900"
    nav_ids = ["menu", "drinks", "visit", "faq"]
    nav = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in zip(nav_ids, L["nav"]))
    if lang == "en":
        big = f'<span class="big en-name">{e(name)}</span>'
    else:
        big = f'<span class="big">{e(name)}</span>'
    strip_icons = ["train", "snow", "bag", "skewer"]
    strip = "".join(f"<span>{icon(i)}{e(t)}</span>" for i, t in zip(strip_icons, L["strip"]))
    glyphs = "".join(
        f'<div class="glyph"><b lang="zh-Hant">{g}</b><h3>{e(h)}</h3><p>{e(p)}</p></div>' for g, h, p in L["glyphs"]
    )
    plans = "".join(
        f'<div class="plan"><h3>{e(t[lang])}</h3><p>{e(d[lang])}</p>'
        f'<span class="p">{price}<small>{e(L["per"]) if i < 2 else ""}</small></span></div>'
        for i, (price, t, d) in enumerate(DRINK_PLANS)
    )
    hours = "".join(f'<tr data-day="{d}"><td>{e(lab)}</td><td>{e(t)}</td></tr>' for d, lab, t in L["hours_rows"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(ans)}</p></details>" for q, ans in L["faq"])

    return f"""<!doctype html>
<html lang="{L['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(L['title'])}</title>
<meta name="description" content="{e(L['desc'])}">
<link rel="canonical" href="{url}">
{alternates}
<meta name="theme-color" content="#f6c400">
<meta property="og:type" content="restaurant.restaurant">
<meta property="og:site_name" content="{e(name)}">
<meta property="og:title" content="{e(L['title'])}">
<meta property="og:description" content="{e(L['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{L['og_locale']}">
<meta property="og:image" content="{PHOTOS['table']}?w=1200&h=630&fit=crop&q=75">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{a}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="{a}assets/style.css">
{schema(lang, L)}
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="#top">{e(name)}<small>{e(SITE['name_alt'][lang])}</small></a>
    <nav class="nav" aria-label="{e(L['nav'][0])}">{nav}</nav>
    <div class="lang">{lang_switch}</div>
  </div>
</header>

<main id="top">
<section class="sign" aria-labelledby="store-name">
  <div class="wrap">
    <div class="sign-frame">
      <div class="sign-copy">
        <h1 class="sign-name" id="store-name">{big}<span class="vert" lang="zh-Hant">{e(L['tagline'])}</span></h1>
        <p class="sign-lede">{e(L['lede'])}</p>
        <p class="sign-sub">{e(L['sub'])}</p>
        <p class="status" data-status data-open="false" role="status"><span class="dot" aria-hidden="true"></span><span data-status-text>{e(L['status_init'])}</span></p>
        <div class="actions">
          <a class="btn btn-primary" href="{SITE['reserve_url']}" rel="noopener">{icon('ticket')}{e(L['cta_reserve'])}</a>
          <a class="btn btn-ghost" href="{directions}" rel="noopener">{icon('pin')}{e(L['cta_go'])}</a>
          <a class="btn btn-ghost" href="#menu">{icon('list')}{e(L['cta_menu'])}</a>
        </div>
      </div>
      <figure class="sign-photo" style="margin:0">
        {img(PHOTOS['hero'], 900, L['hero_alt'], loading='eager', sizes='(max-width: 860px) 100vw, 45vw', fetch='high')}
        <figcaption>{e(L['hero_cap'])}</figcaption>
      </figure>
    </div>
    <div class="sign-strip">{strip}</div>
  </div>
</section>

<section class="why" aria-labelledby="why-h">
  <div class="wrap">
    <h2 id="why-h">{e(L['why_h'])}</h2>
    <p class="why-intro">{e(L['why_intro'])}</p>
    <div class="glyphs">{glyphs}</div>
    <div class="why-photo">
      {img(PHOTOS['fried'], 1000, L['fried_alt'], sizes='(max-width: 760px) 100vw, 58vw')}
      {img(PHOTOS['grill'], 700, L['grill_alt'], sizes='(max-width: 760px) 100vw, 40vw')}
    </div>
  </div>
</section>

<section class="menu" id="menu" aria-labelledby="menu-h">
  <div class="wrap">
    <div class="menu-head">
      <h2 id="menu-h">{e(L['menu_h'])}</h2>
      <p>{e(L['menu_p'])}</p>
    </div>
    <form class="slip" data-slip onsubmit="return false">
      <div class="slip-title">
        <strong>{e(L['slip_title'])}</strong>
        <span>{e(name)}　{e(L['slip_table'])} <span class="hand">{e(L['slip_hand'])}</span></span>
        <span>{e(L['slip_unit'])}</span>
      </div>
      <div class="slip-cols">
{menu_html(lang, L)}
      </div>
      <div class="slip-foot">
        <p class="total" style="margin:0"><span>{e(L['total'])}</span><output data-total>NT$0</output><span class="count" data-count></span></p>
        <div class="slip-btns">
          <button type="button" class="btn btn-primary" data-show disabled>{e(L['show'])}</button>
          <button type="button" class="btn btn-ghost" data-clear disabled>{e(L['clear'])}</button>
        </div>
      </div>
      <p class="slip-note">{e(L['slip_note'])}</p>
    </form>
  </div>
</section>

<dialog class="show-staff" aria-labelledby="staff-h">
  <div class="staff-inner">
    <h2 id="staff-h">{e(L['staff_h'])}</h2>
    <ol></ol>
    <p class="staff-total"><span>{e(L['staff_total'])}</span><b data-staff-total></b></p>
    <button type="button" class="btn" data-close>{e(L['staff_close'])}</button>
  </div>
</dialog>

<section class="drinks" id="drinks" aria-labelledby="drinks-h">
  <div class="wrap drinks-grid">
    <div>
      <h2 id="drinks-h">{e(L['drinks_h'])}</h2>
      <p class="lead">{e(L['drinks_p'])}</p>
      <div class="plans">{plans}</div>
      <p class="fine">{e(L['drinks_fine'])}</p>
    </div>
    <figure>
      {img(PHOTOS['table'], 900, L['drinks_alt'], sizes='(max-width: 860px) 100vw, 45vw')}
      <figcaption>{e(L['drinks_cap'])}</figcaption>
    </figure>
  </div>
</section>

<section class="visit" id="visit" aria-labelledby="visit-h">
  <div class="wrap visit-grid">
    <div>
      <h2 id="visit-h">{e(L['visit_h'])}</h2>
      <div class="facts">
        <div class="fact">{icon('pin')}<div><h3>{e(L['f_addr'])}</h3><address>{e(SITE['address'][lang])}</address></div></div>
        <div class="fact">{icon('train')}<div><h3>{e(L['f_mrt'])}</h3><p>{e(L['mrt'])}</p></div></div>
        <div class="fact">{icon('clock')}<div><h3>{e(L['f_hours'])}</h3><table class="hours"><tbody>{hours}</tbody></table></div></div>
        <div class="fact">{icon('phone')}<div><h3>{e(L['f_phone'])}</h3><p><a href="{tel}">{e(SITE['phone_display'])}</a></p></div></div>
      </div>
      <div class="actions">
        <a class="btn btn-primary" href="{directions}" rel="noopener">{icon('pin')}{e(L['cta_go'])}</a>
        <a class="btn btn-ghost" href="{tel}">{icon('phone')}{e(L['cta_call'])}</a>
      </div>
    </div>
    <div class="map">
      <iframe src="{embed}" title="{e(L['map_title'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    </div>
  </div>
</section>

<section class="review" aria-labelledby="review-h">
  <div class="wrap">
    <div>
      <h2 id="review-h">{e(L['review_h'])}</h2>
      <p>{e(L['review_p'])}</p>
    </div>
    <div class="actions">
      <a class="btn btn-primary" href="{SITE['review_url']}" rel="noopener">{icon('star')}{e(L['review_btn'])}</a>
    </div>
  </div>
</section>

<section class="faq" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <h2 id="faq-h">{e(L['faq_h'])}</h2>
    <div class="faq-list">{faq}</div>
  </div>
</section>
</main>

<footer class="foot">
  <div class="wrap">
    <div>
      <strong>{e(name)}</strong>
      <address>{e(SITE['address'][lang])}<br><a href="{tel}">{e(SITE['phone_display'])}</a></address>
    </div>
    <div>
      <h2>{e(L['foot_follow'])}</h2>
      <ul><li><a href="{SITE['instagram']}" rel="noopener">Instagram</a></li><li><a href="{SITE['facebook']}" rel="noopener">Facebook</a></li></ul>
    </div>
    <div>
      <h2>{e(L['foot_order'])}</h2>
      <ul><li><a href="{SITE['ubereats']}" rel="noopener">Uber Eats</a></li><li><a href="{SITE['foodpanda']}" rel="noopener">foodpanda</a></li></ul>
    </div>
    <p class="credit">© {e(name)} · {e(L['credit'])}</p>
  </div>
</footer>

<nav class="dock" aria-label="{e(L['cta_go'])}">
  <a href="{directions}" rel="noopener">{icon('pin')}{e(L['dock'][0])}</a>
  <a href="{tel}">{icon('phone')}{e(L['dock'][1])}</a>
  <a class="main" href="{SITE['reserve_url']}" rel="noopener">{icon('ticket')}{e(L['dock'][2])}</a>
</nav>

<script src="{a}assets/app.js" defer></script>
</body>
</html>
"""


def main():
    for lang, L in LANGS.items():
        out = ROOT / L["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
    urls = "\n".join(
        f"  <url><loc>{SITE['domain']}{L['path']}</loc>"
        + "".join(f'<xhtml:link rel="alternate" hreflang="{LANGS[k]["html_lang"]}" href="{SITE["domain"]}{LANGS[k]["path"]}"/>' for k in LANGS)
        + "</url>"
        for L in LANGS.values()
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
