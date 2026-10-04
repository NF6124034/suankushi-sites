# -*- coding: utf-8 -*-
"""
蒜串屋 第三版（樂燒煙燻・高級串燒）產生器
========================================
店名、地址、電話、地圖、訂位連結共用第一版：請改 ../v1/build.py 的 SITE。
第三版的套餐、單點價格、文案都在這個檔案。改完執行：  python build.py
套餐的火候、秒數與做法是「示意」，請師傅確認後再上線。
"""
import html
import json
import runpy
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
V1 = runpy.run_path(str(ROOT.parent / "v1" / "build.py"))
SITE, HOURS_SCHEMA = V1["SITE"], V1["HOURS_SCHEMA"]
ICONS = {**V1["ICONS"], "plus": '<path d="M12 5v14M5 12h14"/>', "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>'}

U = "https://images.unsplash.com/photo-"
P = {
    "hero": U + "1763604048392-18f8383a6542",
    "table": U + "1766762462673-85a4dbfff363",
    "crackle": U + "1475965894430-b05c9d13568a",
    "embers": U + "1777150931512-ff3b5eac3144",
}

COURSE_PRICE = 980
# (id, 照片, 中, 英, 日, 火 key, 秒數(None=特殊), 調味 key, 做法 zh/en/ja, 驚喜)
COURSE = [
    ("sasami", "1727281970228-a5ae69599fd8", "雞柳・山葵", "Breast tender, wasabi", "ささみ わさび", "mid", 60, "wasabi",
     ("只烤到外層變白，中心保持粉嫩，配現磨山葵。", "Seared just until the outside turns white, pink at the heart, with fresh wasabi.", "表面が白くなるまでさっと焼き、中はほんのり桃色。生わさびで。"), False),
    ("negima", "1727281970348-c3c3b253c662", "雞腿蔥段", "Thigh & scallion", "ねぎま", "high", 90, "salt",
     ("雞腿肉夾三星蔥，大火鎖住肉汁，只撒鹽。", "Thigh and Sanxing scallion over high heat to hold the juices. Salt only.", "鶏ももと三星ねぎ。強火で肉汁を閉じ込め、塩だけで。"), False),
    ("kawa", "1778327564625-abda522078de", "雞皮", "Chicken skin", "皮", "far", 600, "tare",
     ("遠火慢慢逼油，刷三次醬，烤到一咬就碎。", "Rendered slowly far from the coals, glazed three times until it shatters.", "遠火でじっくり脂を落とし、タレを三度重ねてパリッと。"), False),
    ("hatsu", "1767974968707-db3d448d4ef3", "雞心", "Heart", "ハツ", "high", 70, "salt",
     ("切開去血管，強火快烤，保持彈脆。", "Opened and cleaned, seared fast to keep the snap.", "開いて下処理し、強火で手早く。歯ごたえを残して。"), False),
    ("nankotsu", "1775379995350-43098b52d8ed", "雞軟骨", "Cartilage", "なんこつ", "high", 80, "lemon",
     ("強火烤出焦香，擠一點檸檬。", "Charred at high heat, finished with a squeeze of lemon.", "強火で香ばしく、レモンを少し。"), False),
    ("bonjiri", "1639716553235-a8275d845fd7", "雞屁股", "Tail (bonjiri)", "ぼんじり", "mid", 150, "salt",
     ("中火讓油脂滴到炭上，再用那陣煙燻回肉裡。", "Medium heat lets the fat drip onto the coals and smoke back into the meat.", "中火で脂を炭に落とし、立ちのぼる煙で燻す。"), False),
    ("garlic", "1682264895449-f75b342cbab6", "台式蒜香酥炸雞", "Taiwanese garlic fried chicken", "台湾式にんにく唐揚げ", "fry", None, "garlic",
     ("燒鳥套餐中間的台灣驚喜：炸兩次，起鍋前下現剁台灣蒜和九層塔。", "The Taiwanese surprise in the middle of a yakitori course: double-fried, finished with fresh-chopped Taiwanese garlic and Thai basil.", "焼き鳥コースの途中に台湾のサプライズ。二度揚げし、刻みたての台湾にんにくとバジルで。"), True),
    ("tebasaki", "1763604048392-18f8383a6542", "雞翅", "Wing", "手羽先", "far", 480, "salt",
     ("遠火烤八分鐘，皮脆、肉一拉就離骨。", "Eight minutes far from the coals: crisp skin, meat that pulls from the bone.", "遠火で八分。皮はパリッと、骨離れよく。"), False),
    ("reba", "1708597525178-6c302364f37c", "雞肝", "Liver", "レバー", "mid", 60, "tare",
     ("中火烤到剛好凝固，醬汁收到發亮。", "Medium heat until just set, the glaze reduced to a shine.", "中火で半生に、タレを照りよく。"), False),
    ("season", "1755108906864-fdaadb8ab5f1", "季節時蔬", "Seasonal vegetable", "季節の野菜", "mid", 90, "soy",
     ("依季節更換，例如香菇或玉米筍。", "Changes with the season, for example shiitake or baby corn.", "季節で替わります。たとえば椎茸やヤングコーン。"), False),
    ("tsukune", "1783788357923-649e29b7b006", "月見雞肉丸", "Tsukune with yolk", "月見つくね", "mid", 180, "yolk",
     ("手打雞肉丸拌入軟骨，沾生蛋黃與醬。", "Hand-made chicken meatball with cartilage, dipped in raw yolk and tare.", "軟骨入りの手ごねつくね、卵黄とタレで。"), False),
    ("chazuke", "1727281970324-4bda7bab3073", "雞湯泡飯", "Chicken broth rice", "鶏スープ茶漬け", "none", None, "broth",
     ("用雞骨湯收尾。", "A bowl of chicken-bone broth over rice to close.", "鶏ガラスープで〆。"), False),
]
HEAT = {"high": ("強火", "High heat", "強火"), "mid": ("中火", "Medium heat", "中火"), "far": ("遠火", "Far from coals", "遠火"),
        "fry": ("油炸兩次", "Double-fried", "二度揚げ"), "none": ("不上火", "Off the fire", "火入れなし")}
SEASON = {"wasabi": ("山葵", "Wasabi", "わさび"), "salt": ("鹽", "Salt", "塩"), "tare": ("醬", "Tare", "タレ"), "lemon": ("鹽・檸檬", "Salt, lemon", "塩・レモン"),
          "garlic": ("蒜・九層塔", "Garlic, Thai basil", "にんにく・バジル"), "soy": ("醬油", "Soy", "醤油"), "yolk": ("蛋黃・醬", "Yolk, tare", "卵黄・タレ"),
          "broth": ("雞湯", "Broth", "鶏スープ")}

# 單點：(群組 zh/en/ja, [(中, 英, 日, 價格)])
CARTE = [
    (("串", "Skewers", "串"), [("雞腿蔥段", "Thigh & scallion", "ねぎま", 120), ("雞皮", "Chicken skin", "皮", 90), ("雞心", "Heart", "ハツ", 100),
                              ("雞屁股", "Tail", "ぼんじり", 100), ("雞翅", "Wing", "手羽先", 140), ("月見雞肉丸", "Tsukune with yolk", "月見つくね", 160),
                              ("雞肝", "Liver", "レバー", 100), ("和牛五花", "Wagyu belly", "和牛バラ", 280)]),
    (("蒜香炸物", "Garlic fried", "にんにく揚げ", ), [("台式蒜香酥炸雞", "Taiwanese garlic fried chicken", "台湾式にんにく唐揚げ", 320),
                                               ("胡椒鹽酥透抽", "Salt & pepper squid", "ヤリイカの塩胡椒揚げ", 360),
                                               ("蒜香炸雞軟骨", "Garlic fried cartilage", "なんこつのにんにく揚げ", 260),
                                               ("九層塔炸杏鮑菇", "King oyster mushroom, Thai basil", "エリンギとバジルの揚げ物", 220)]),
    (("時蔬・收尾", "Vegetables & to finish", "野菜・〆"), [("香菇", "Shiitake", "椎茸", 90), ("銀杏", "Ginkgo nuts", "銀杏", 100),
                                                    ("獅子唐", "Shishito pepper", "ししとう", 90), ("雞湯泡飯", "Chicken broth rice", "鶏スープ茶漬け", 180),
                                                    ("醬油烤飯糰", "Soy-grilled rice ball", "焼きおにぎり", 120)]),
    (("酒", "Drinks", "酒"), [("生啤酒", "Draft beer", "生ビール", 180), ("柚子 Highball", "Yuzu highball", "柚子ハイボール", 220),
                             ("冷酒 一合", "Chilled sake, 180 ml", "冷酒 一合", 380), ("師傅搭酒 三杯", "Three-glass pairing", "ペアリング 三杯", 680)]),
]
GARLIC_DISHES = [CARTE[1][1][0], CARTE[1][1][1], CARTE[1][1][2], CARTE[1][1][3]]

LANGS = {
    "zh": {
        "html_lang": "zh-Hant-TW", "og_locale": "zh_TW", "path": "/", "out": "index.html", "a": "",
        "title": "蒜串屋｜忠孝敦化 炭火串燒套餐・台式蒜香炸物（線上訂位）",
        "desc": "忠孝敦化站旁的炭火串燒店。師傅串燒套餐 12 品 NT$980，套餐中間藏一道台式蒜香酥炸雞。適合約會、慶祝與下班後的一頓好飯，每天營業到凌晨 1:30，可線上訂位。",
        "sub": "炭火串燒・台式蒜香",
        "lede": "炭火串燒，加一道台式蒜香。|火候，是師傅一串一串顧出來的。",
        "reserve": "線上訂位", "go": "怎麼過來", "call": "打電話",
        "nav": [("stages", "火候"), ("course", "套餐"), ("garlic", "蒜"), ("carte", "單點"), ("reserve", "訂位"), ("faq", "問答")],
        "tonight": "今晚", "card": [("套餐", "師傅串燒 12 品"), ("價格", f"NT${COURSE_PRICE}"), ("營業", None), ("位置", "忠孝敦化站 3 分")],
        "photo_note": "示意照片",
        "stages_h": "火候四段",
        "stages": [("上火", "HEAT", "炭燒到表面發白才開始烤，那是火最穩的時候。", "1639716553235-a8275d845fd7"),
                   ("翻面", "TURN", "什麼時候翻，看的是油滴下去的聲音和肉的顏色。", "1778327564625-abda522078de"),
                   ("離火", "REST", "離火靜置幾秒，讓肉汁回到中心。", "1775379995350-43098b52d8ed"),
                   ("上桌", "SERVE", "烤好就上，一串一串，不讓它在盤子上等。", "1783788357923-649e29b7b006")],
        "course_brush": "串", "course_h": f"今晚的套餐：師傅串燒 12 品",
        "course_p": "往下捲，正在你眼前的那一串，就是此刻火上的那一串。",
        "price_label": "套餐 12 品・每位", "surprise": "台灣驚喜",
        "heat_l": "火", "time_l": "時間", "season_l": "調味",
        "course_note": "火候、時間與做法為示意，實際依師傅當天判斷；菜色依季節調整。",
        "garlic_h": "燒鳥吃到一半，來一道台灣的蒜香。",
        "garlic_p": "套餐第七品是我們的驚喜：鹹酥雞的蒜香與九層塔，用燒鳥的精細度重新做一次。也可以單點。",
        "night_h": "兩個人，一壺冷酒，炭火的光。", "night_p": "適合約會，也適合慶祝。訂位時在備註寫下來，我們會盡量安排。", "night_alt": "桌上的串燒與酒",
        "carte_h": "單點", "carte_p": "套餐之外想再加的，或只想喝一杯配幾串，都可以。", "carte_note": "價格含稅。菜色依季節與進貨調整。",
        "reserve_brush": "夜", "reserve_h": "訂位・到店", "reserve_p": "建議先線上訂位；當天有空位，也歡迎直接過來。",
        "facts": {"addr": "地址", "mrt": "捷運", "hours": "營業", "phone": "電話"},
        "mrt": "板南線忠孝敦化站 3 號出口，走路約 3 分鐘",
        "hours_rows": [("0,1,2,3,4", "週日–週四", "17:30 – 01:30"), ("5,6", "週五–週六", "17:30 – 02:00")],
        "dist_btn": "算算我走過去要多久", "dist_hint": "（用手機定位估算，位置不會傳給我們）",
        "map_title": "蒜串屋在 Google 地圖上的位置",
        "review_h": "吃完覺得值得，幫我們在 Google 留一句話。",
        "review_p": "好與不好都歡迎直說，每一則我們都會看。",
        "review_btn": "寫 Google 評論",
        "faq_h": "問答",
        "faq": [
            ("需要先訂位嗎？", "建議先線上訂位，尤其是週五、週六晚上；當天有空位也歡迎直接過來。"),
            ("套餐和單點可以一起點嗎？", "可以。套餐是 12 品，吃完還想加的串或炸物都可以再單點。"),
            ("營業到幾點？", "週日到週四 17:30–01:30，週五、週六 17:30–02:00。最後點餐是打烊前 30 分鐘。"),
            ("有素食或過敏的選項嗎？", "時蔬可以做成蔬食；有過敏請在訂位時告訴我們。炸物和其他食材共用炸油。"),
            ("適合約會或慶生嗎？", "適合。訂位時在備註寫下來，我們會盡量幫你安排。"),
            ("可以包場嗎？", "平日可以討論包場，請先打電話給我們。"),
        ],
        "credit": "網站照片為 Unsplash 示意照片，開幕後會換成店內實拍。",
        "follow": "追蹤", "delivery": "外送",
        "strings": {"open": "營業中", "last": "最後點餐", "closed": "準備中", "until": "到 {t}", "opens": "{t} 開門",
                    "geoWait": "定位中…", "geoFail": "抓不到你的位置，直接按「怎麼過來」也可以。", "geoOk": "你離我們大約 {d}，走路約 {m} 分鐘。"},
    },
    "en": {
        "html_lang": "en", "og_locale": "en_US", "path": "/en/", "out": "en/index.html", "a": "../",
        "title": "Garlic Kushi | Charcoal Yakitori Course in Taipei, Book Online",
        "desc": "Charcoal yakitori near MRT Zhongxiao Dunhua, Taipei. The grill master's 12-course skewer set at NT$980, with a Taiwanese garlic fried chicken surprise in the middle. Open until 1:30am. Book online.",
        "sub": "Charcoal yakitori · Taiwanese garlic",
        "lede": "Charcoal yakitori with one Taiwanese garlic surprise.|The heat is watched one skewer at a time.",
        "reserve": "Book a table", "go": "Directions", "call": "Call",
        "nav": [("stages", "Fire"), ("course", "Course"), ("garlic", "Garlic"), ("carte", "À la carte"), ("reserve", "Book"), ("faq", "FAQ")],
        "tonight": "TONIGHT", "card": [("Course", "12 skewers"), ("Price", f"NT${COURSE_PRICE}"), ("Open", None), ("Where", "3 min from MRT")],
        "photo_note": "Illustrative photo",
        "stages_h": "Four stages of fire",
        "stages": [("上火", "HEAT", "We start only when the charcoal turns white. That is when the heat is steadiest.", "1639716553235-a8275d845fd7"),
                   ("翻面", "TURN", "When to turn is read from the sound of the dripping fat and the colour of the meat.", "1778327564625-abda522078de"),
                   ("離火", "REST", "Off the fire for a few seconds so the juices return to the centre.", "1775379995350-43098b52d8ed"),
                   ("上桌", "SERVE", "Served the moment it is ready, one skewer at a time. Nothing waits on the plate.", "1783788357923-649e29b7b006")],
        "course_brush": "串", "course_h": "Tonight's course: the grill master's 12",
        "course_p": "Scroll down. The skewer in front of you is the one on the fire right now.",
        "price_label": "12-item course, per person", "surprise": "TAIWAN SURPRISE",
        "heat_l": "Fire", "time_l": "Time", "season_l": "Seasoning",
        "course_note": "Heat, timing and method are illustrative; the grill master decides on the night. The course changes with the season.",
        "garlic_h": "Halfway through the yakitori, a taste of Taiwanese garlic.",
        "garlic_p": "Course seven is our surprise: the garlic and Thai basil of Taiwan's popcorn-chicken stalls, remade with yakitori precision. Also à la carte.",
        "night_h": "Two people, a carafe of cold sake, the glow of the coals.", "night_p": "Made for a date, or a celebration. Add a note when you book and we'll do what we can.", "night_alt": "Skewers and drinks on a table",
        "carte_h": "À la carte", "carte_p": "Add more after the course, or just come for a drink and a few skewers.", "carte_note": "Prices include tax. Items change with the season and the market.",
        "reserve_brush": "夜", "reserve_h": "Book & find us", "reserve_p": "Booking ahead is best; if there's a free table on the night, walk right in.",
        "facts": {"addr": "ADDRESS", "mrt": "MRT", "hours": "HOURS", "phone": "PHONE"},
        "mrt": "Zhongxiao Dunhua Station (Bannan Line), Exit 3, about 3 minutes on foot",
        "hours_rows": [("0,1,2,3,4", "Sun–Thu", "17:30 – 01:30"), ("5,6", "Fri–Sat", "17:30 – 02:00")],
        "dist_btn": "How long is the walk from here?", "dist_hint": "(estimated from your phone's location, never sent to us)",
        "map_title": "Garlic Kushi on Google Maps",
        "review_h": "If it was worth it, leave us a line on Google.",
        "review_p": "Good or bad, tell us straight. We read every one.",
        "review_btn": "Write a Google review",
        "faq_h": "FAQ",
        "faq": [
            ("Do I need to book?", "Booking online is best, especially on Friday and Saturday nights. Walk-ins are welcome when there's a free table."),
            ("Can I order the course and à la carte together?", "Yes. The course is 12 items; add any skewers or fried dishes after."),
            ("How late are you open?", "Sunday to Thursday 17:30–01:30, Friday and Saturday 17:30–02:00. Last orders 30 minutes before closing."),
            ("Vegetarian or allergy options?", "The seasonal vegetables can be made meat-free. Tell us about allergies when you book. The fryer oil is shared."),
            ("Good for a date or a birthday?", "Yes. Add a note to your booking and we'll do what we can."),
            ("Can we book the whole place?", "On weekdays, yes. Call us first."),
        ],
        "credit": "Photos are illustrative, via Unsplash, until the restaurant opens.",
        "follow": "FOLLOW", "delivery": "DELIVERY",
        "strings": {"open": "Open now", "last": "Last orders", "closed": "Closed", "until": "until {t}", "opens": "opens {t}",
                    "geoWait": "Finding you…", "geoFail": "Couldn't get your location. Just tap Directions.", "geoOk": "You're about {d} away, roughly a {m}-minute walk."},
    },
    "ja": {
        "html_lang": "ja", "og_locale": "ja_JP", "path": "/ja/", "out": "ja/index.html", "a": "../",
        "title": "蒜串屋｜台北・忠孝敦化 炭火焼き鳥コースと台湾式にんにく唐揚げ（ネット予約）",
        "desc": "MRT忠孝敦化駅すぐの炭火焼き鳥。職人の串焼きコース12品NT$980、途中に台湾式にんにく唐揚げのサプライズ。深夜1:30まで営業、ネット予約可。",
        "sub": "炭火焼き鳥・台湾にんにく",
        "lede": "炭火の焼き鳥に、台湾にんにくの一皿を。|火加減は、職人が一本ずつ見ています。",
        "reserve": "ネット予約", "go": "アクセス", "call": "電話",
        "nav": [("stages", "火入れ"), ("course", "コース"), ("garlic", "にんにく"), ("carte", "単品"), ("reserve", "予約"), ("faq", "Q&A")],
        "tonight": "今夜", "card": [("コース", "職人の串 12品"), ("料金", f"NT${COURSE_PRICE}"), ("営業", None), ("場所", "忠孝敦化駅 3分")],
        "photo_note": "イメージ写真",
        "stages_h": "火入れの四段",
        "stages": [("上火", "HEAT", "炭の表面が白くなってから焼き始めます。火がいちばん安定する時です。", "1639716553235-a8275d845fd7"),
                   ("翻面", "TURN", "返す時は、脂が落ちる音と肉の色で決めます。", "1778327564625-abda522078de"),
                   ("離火", "REST", "火から外して数秒休ませ、肉汁を中心に戻します。", "1775379995350-43098b52d8ed"),
                   ("上桌", "SERVE", "焼き上がったらすぐに一本ずつ。皿の上で待たせません。", "1783788357923-649e29b7b006")],
        "course_brush": "串", "course_h": "今夜のコース：職人の串 12品",
        "course_p": "スクロールしてください。目の前の一本が、いま火の上にある一本です。",
        "price_label": "コース 12品・お一人様", "surprise": "台湾サプライズ",
        "heat_l": "火", "time_l": "時間", "season_l": "味付け",
        "course_note": "火加減・時間・調理法はイメージです。当日は職人が判断します。内容は季節で替わります。",
        "garlic_h": "焼き鳥の途中で、台湾のにんにくを一皿。",
        "garlic_p": "コース七品目はサプライズ。台湾の唐揚げ屋台のにんにくとバジルを、焼き鳥の精度で作り直しました。単品でもどうぞ。",
        "night_h": "ふたりで、冷酒を一合、炭火のあかり。", "night_p": "デートにも、お祝いにも。ご予約の備考に書いていただければ、できる限りご用意します。", "night_alt": "テーブルの串焼きとお酒",
        "carte_h": "単品", "carte_p": "コースのあとに追加しても、一杯と数本だけでも。", "carte_note": "税込。季節と仕入れにより内容が変わります。",
        "reserve_brush": "夜", "reserve_h": "ご予約・アクセス", "reserve_p": "ネット予約がおすすめです。当日空席があれば、そのままお越しください。",
        "facts": {"addr": "住所", "mrt": "MRT", "hours": "営業", "phone": "電話"},
        "mrt": "板南線 忠孝敦化駅 3番出口から徒歩約3分",
        "hours_rows": [("0,1,2,3,4", "日〜木", "17:30 – 01:30"), ("5,6", "金・土", "17:30 – 02:00")],
        "dist_btn": "ここから歩いて何分？", "dist_hint": "（スマホの位置情報で計算。送信はされません）",
        "map_title": "Googleマップで見る蒜串屋",
        "review_h": "よかったら、Googleにひとことください。",
        "review_p": "良い点も悪い点も、遠慮なく。すべて読んでいます。",
        "review_btn": "Googleでレビューを書く",
        "faq_h": "Q&A",
        "faq": [
            ("予約は必要ですか？", "ネット予約がおすすめです。特に金・土の夜は。空席があれば当日のご来店も歓迎です。"),
            ("コースと単品は一緒に頼めますか？", "はい。コースは12品、そのあと串や揚げ物を追加できます。"),
            ("何時まで営業していますか？", "日〜木は17:30〜01:30、金・土は17:30〜02:00。ラストオーダーは閉店30分前です。"),
            ("ベジタリアンやアレルギー対応は？", "季節の野菜は肉なしにできます。アレルギーはご予約時にお知らせください。揚げ油は共用です。"),
            ("デートや誕生日に向いていますか？", "はい。ご予約の備考に書いていただければ、できる限りご用意します。"),
            ("貸切はできますか？", "平日はご相談ください。まずはお電話を。"),
        ],
        "credit": "写真は開店までUnsplashのイメージを使用しています。",
        "follow": "フォロー", "delivery": "デリバリー",
        "strings": {"open": "営業中", "last": "ラストオーダー", "closed": "準備中", "until": "{t} まで", "opens": "{t} 開店",
                    "geoWait": "位置を確認中…", "geoFail": "位置情報が取得できませんでした。「アクセス」をどうぞ。", "geoOk": "ここから約 {d}、徒歩約 {m} 分です。"},
    },
}
LI = {"zh": 0, "en": 1, "ja": 2}
e = html.escape


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def secs(n, lang):
    if n is None:
        return "170°C → 190°C" if lang else "170°C → 190°C"
    if n < 120:
        return {"zh": f"約 {n} 秒", "en": f"~{n} s", "ja": f"約{n}秒"}[lang]
    m = round(n / 60)
    return {"zh": f"約 {m} 分", "en": f"~{m} min", "ja": f"約{m}分"}[lang]


def img(src, w, h, alt, sizes, eager=False):
    ws = [480, 800, 1200, 1600]
    srcset = ", ".join(f"{src}?w={x}&h={round(x * h / w)}&fit=crop&q=70&auto=format {x}w" for x in ws)
    return (f'<img src="{src}?w={w}&h={h}&fit=crop&q=70&auto=format" srcset="{srcset}" sizes="{sizes}" alt="{e(alt)}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async"{" fetchpriority=" + chr(34) + "high" + chr(34) if eager else ""}>')


def maps():
    q = SITE["maps_query"]
    lat, lng = SITE["geo"]
    return (f"https://www.google.com/maps?q={quote(q)}&ll={lat},{lng}&z=17&output=embed",
            f"https://www.google.com/maps/dir/?api=1&destination={quote(q)}")


def schema(lang, L):
    i = LI[lang]
    url = SITE["domain"] + L["path"]
    sections = [{"@type": "MenuSection", "name": L["course_h"],
                 "offers": {"@type": "Offer", "price": str(COURSE_PRICE), "priceCurrency": "TWD"},
                 "hasMenuItem": [{"@type": "MenuItem", "name": c[2 + i]} for c in COURSE]}]
    for g, rows in CARTE:
        sections.append({"@type": "MenuSection", "name": g[i], "hasMenuItem": [
            {"@type": "MenuItem", "name": r[i], "offers": {"@type": "Offer", "price": str(r[3]), "priceCurrency": "TWD"}} for r in rows]})
    restaurant = {
        "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE["domain"] + "/#restaurant",
        "name": SITE["name"][lang], "alternateName": SITE["name_alt"][lang], "description": L["desc"], "url": url,
        "telephone": SITE["phone"], "image": [P["hero"] + "?w=1200"], "priceRange": "NT$600–1000",
        "servesCuisine": ["Yakitori", "Japanese", "Taiwanese"], "acceptsReservations": True,
        "address": {"@type": "PostalAddress", "streetAddress": SITE["street_schema"], "addressLocality": "大安區",
                    "addressRegion": "台北市", "postalCode": SITE["postal"], "addressCountry": "TW"},
        "geo": {"@type": "GeoCoordinates", "latitude": SITE["geo"][0], "longitude": SITE["geo"][1]},
        "hasMap": maps()[1],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c} for d, o, c in HOURS_SCHEMA],
        "sameAs": [SITE["instagram"], SITE["facebook"]],
        "potentialAction": {"@type": "ReserveAction", "target": SITE["reserve_url"]},
        "hasMenu": {"@type": "Menu", "url": url + "#course", "hasMenuSection": sections},
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in L["faq"]]}
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{dump(restaurant)}\n</script>\n<script type="application/ld+json">\n{dump(faq)}\n</script>'


BRUSH_GLYPHS = "".join(sorted(set("蒜串屋" + "上火翻面離火上桌" + "串蒜夜")))


def page(lang):
    L = LANGS[lang]
    i = LI[lang]
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
    fonts = (f"family=Chiron+Hei+HK:wght@400;500;700;900&family=Azeret+Mono:wght@400;500"
             f"&family=Ma+Shan+Zheng&text={quote(BRUSH_GLYPHS)}")
    # Ma Shan Zheng 只載入用到的字；其他字型分開載入完整字集
    font_links = (f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&text={quote(BRUSH_GLYPHS)}&display=swap">\n'
                  f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chiron+Hei+HK:wght@400;500;700;900&family=Azeret+Mono:wght@400;500'
                  f'{"&family=Noto+Sans+JP:wght@400;500;700;900" if lang == "ja" else ""}&display=swap">')
    nav = "".join(f'<li><a href="#{sid}">{e(t)}</a></li>' for sid, t in L["nav"])
    card = "".join(
        f'<dt>{e(k)}</dt><dd{" class=" + chr(34) + "mono" + chr(34) if (v or "").startswith("NT$") else ""}>'
        + (f'<span data-until></span>' if v is None else e(v)) + "</dd>"
        for k, v in L["card"])
    stages = "".join(
        f'<article class="stage" tabindex="0"><img src="{U}{ph}?w=200&h=200&fit=crop&q=65&auto=format" alt="" loading="lazy" decoding="async">'
        f'<h3><span class="brush" lang="zh-Hant">{e(w)}</span>{"" if lang == "zh" else f"<small>{e(en.title())}</small>"}</h3><p>{e(t)}</p></article>'
        for n, (w, en, t, ph) in enumerate(L["stages"]))
    course = []
    for n, (cid, ph, zh, en, ja, heat, sec, season, method, surprise) in enumerate(COURSE):
        nm = (zh, en, ja)[i]
        sub = f"<small>{e(zh)}</small>" if lang != "zh" else ""
        tag = f'<span class="surprise">{e(L["surprise"])}</span>' if surprise else ""
        h, t, s = HEAT[heat][i], secs(sec, lang) if heat != "none" else {"zh": "收尾", "en": "To close", "ja": "〆"}[lang], SEASON[season][i]
        course.append(
            f'<li><a class="course-item" id="c-{cid}" href="#c-{cid}" data-photo="{U}{ph}" data-name="{e(nm)}" data-method="{e(method[i])}" '
            f'data-heat="{e(h)}" data-time="{e(t)}" data-season="{e(s)}">'
            f'<span class="n">{n + 1:02d}</span><span class="name">{e(nm)}{tag}{sub}</span>'
            f'<span class="data">{e(h)} · {e(t)}<br>{e(s)}</span></a></li>')
    first = COURSE[0]
    garlic = "".join(f'<li><b>{e(d[i])}</b><small>{e(d[0]) if lang != "zh" else ""}</small><span class="mono">{d[3]}</span></li>' for d in GARLIC_DISHES)
    carte = "".join(
        f'<div><h3>{e(g[i])}</h3><ul>' + "".join(
            f'<li><span>{e(r[i])}{f"<small>{e(r[0])}</small>" if lang != "zh" else ""}</span><span class="mono">{r[3]}</span></li>' for r in rows)
        + "</ul></div>" for g, rows in CARTE)
    hours = "".join(f'<tr data-day="{d}"><td>{e(lab)}</td><td class="mono">{e(t)}</td></tr>' for d, lab, t in L["hours_rows"])
    faq = "".join(f"<details><summary>{e(q)}{icon('plus')}</summary><p>{e(x)}</p></details>" for q, x in L["faq"])
    data = {"strings": L["strings"], "geo": list(SITE["geo"])}
    crackle = f"url('{P['crackle']}?w=900&q=60&auto=format')"
    return f"""<!doctype html>
<html lang="{L['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(L['title'])}</title>
<meta name="description" content="{e(L['desc'])}">
<link rel="canonical" href="{url}">
{alternates}
<meta name="theme-color" content="#0f0d0c">
<meta property="og:type" content="restaurant.restaurant">
<meta property="og:site_name" content="{e(name)}">
<meta property="og:title" content="{e(L['title'])}">
<meta property="og:description" content="{e(L['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{L['og_locale']}">
<meta property="og:image" content="{P['hero']}?w=1200&h=630&fit=crop&q=75">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{a}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
{font_links}
<link rel="stylesheet" href="{a}assets/raku.css">
<style>:root{{--crackle:{crackle};}}</style>
{schema(lang, L)}
</head>
<body>
<aside class="rail" data-status data-open="false">
  <a class="mark" href="#top" aria-label="{e(name)}"><b lang="zh-Hant">{e(SITE['name']['zh'])}</b><span>{e(L['sub'])}</span></a>
  <nav aria-label="{e(L['nav'][0][1])}"><ol>{nav}</ol></nav>
  <section class="tonight" aria-label="{e(L['tonight'])}">
    <h2>{e(L['tonight'])}</h2>
    <p class="state" data-state>…</p>
    <p data-until></p>
    <div class="bar" aria-hidden="true"><i></i></div>
  </section>
  <nav class="langs" aria-label="Language">{langs}</nav>
</aside>
<header class="topbar" data-status data-open="false">
  <b lang="zh-Hant">{e(SITE['name']['zh'])}</b>
  <span class="state-mini"><span data-state>…</span><span data-until></span></span>
  <nav class="langs" aria-label="Language">{langs}</nav>
</header>

<main id="top">
<section class="kiln" aria-labelledby="h1">
  <div class="kiln-copy">
    <h1 id="h1"><span class="brush" lang="zh-Hant">{e(SITE['name']['zh'])}</span><span class="stroke" aria-hidden="true"></span><span class="sub">{e(name if lang == 'en' else L['sub'])}</span></h1>
    <p class="lede">{''.join(f'<span>{e(x)}</span>' for x in L['lede'].split('|'))}</p>
    <div class="actions">
      <a class="btn btn-fire" href="{SITE['reserve_url']}" rel="noopener">{e(L['reserve'])}{icon('arrow')}</a>
      <a class="btn btn-line" href="{directions}" rel="noopener">{e(L['go'])}</a>
    </div>
  </div>
  <figure class="kiln-photo">
    {img(P['hero'], 1200, 1500, '', '(max-width: 1000px) 100vw, 45vw', eager=True)}
    <figcaption>{e(L['photo_note'])}</figcaption>
    <div class="vessel-card" data-status data-open="false" role="group" aria-label="{e(L['tonight'])}"><dl>{card}</dl></div>
  </figure>
</section>

<section class="stages" id="stages" aria-labelledby="stages-h">
  <h2 id="stages-h">{e(L['stages_h'])}</h2>
  {stages}
</section>

<section class="section" id="course" aria-labelledby="course-h">
  <div class="head"><span class="brush" lang="zh-Hant" aria-hidden="true">{L['course_brush']}</span><h2 id="course-h">{e(L['course_h'])}</h2><p>{e(L['course_p'])}</p></div>
  <div class="course-grid">
    <div class="course-side">
      <figure class="course-front" style="margin:0"><img src="{U}{first[1]}?w=900&h=1125&fit=crop&q=70&auto=format" data-src="{U}{first[1]}" alt="" loading="lazy" decoding="async"><figcaption>{e(L['photo_note'])}</figcaption></figure>
      <div class="course-back" aria-live="polite">
        <h3>{e(first[2 + i])}</h3>
        <p>{e(first[8][i])}</p>
        <div class="meta mono"><span>{e(L['heat_l'])} <b data-heat>{e(HEAT[first[5]][i])}</b></span><span>{e(L['time_l'])} <b data-time>{e(secs(first[6], lang))}</b></span><span>{e(L['season_l'])} <b data-season>{e(SEASON[first[7]][i])}</b></span></div>
      </div>
      <p class="price-line"><span>{e(L['price_label'])}</span><b>NT${COURSE_PRICE}</b></p>
    </div>
    <div>
      <ol class="course-list">{''.join(course)}</ol>
      <p class="course-note">{e(L['course_note'])}</p>
    </div>
  </div>
</section>

<section class="garlic" id="garlic" aria-labelledby="garlic-h">
  <div class="garlic-fire"><img src="{P['embers']}?w=1400&q=65&auto=format" alt="" loading="lazy" decoding="async"><span class="brush" lang="zh-Hant" aria-hidden="true">蒜</span></div>
  <div class="garlic-copy">
    <h2 id="garlic-h">{e(L['garlic_h'])}</h2>
    <p>{e(L['garlic_p'])}</p>
    <ul class="dishes">{garlic}</ul>
  </div>
</section>

<section class="night" aria-labelledby="night-h">
  <img src="{P['table']}?w=1800&q=70&auto=format" alt="{e(L['night_alt'])}" loading="lazy" decoding="async">
  <div class="night-copy"><h2 id="night-h">{e(L['night_h'])}</h2><p>{e(L['night_p'])}</p></div>
  <span class="night-note">{e(L['photo_note'])}</span>
</section>

<section class="section" id="carte" aria-labelledby="carte-h">
  <div class="head" style="grid-template-columns:1fr"><h2 id="carte-h">{e(L['carte_h'])}</h2><p>{e(L['carte_p'])}</p></div>
  <div class="glaze-panel"><div class="carte">{carte}</div><p class="carte-note">{e(L['carte_note'])}</p></div>
</section>

<section class="section" id="reserve" aria-labelledby="reserve-h">
  <div class="head"><span class="brush" lang="zh-Hant" aria-hidden="true">{L['reserve_brush']}</span><h2 id="reserve-h">{e(L['reserve_h'])}</h2><p>{e(L['reserve_p'])}</p></div>
  <div class="visit-grid">
    <div>
      <div class="actions" style="margin-bottom:32px">
        <a class="btn btn-fire" href="{SITE['reserve_url']}" rel="noopener">{e(L['reserve'])}{icon('arrow')}</a>
        <a class="btn btn-line" href="{directions}" rel="noopener">{e(L['go'])}</a>
        <a class="btn btn-line" href="{tel}">{e(L['call'])}</a>
      </div>
      <dl class="facts">
        <div class="fact"><dt>{e(L['facts']['addr'])}</dt><dd><address style="font-style:normal">{e(SITE['address'][lang])}</address></dd></div>
        <div class="fact"><dt>{e(L['facts']['mrt'])}</dt><dd>{e(L['mrt'])}</dd></div>
        <div class="fact"><dt>{e(L['facts']['hours'])}</dt><dd><table class="hours"><tbody>{hours}</tbody></table></dd></div>
        <div class="fact"><dt>{e(L['facts']['phone'])}</dt><dd><a href="{tel}">{e(SITE['phone_display'])}</a></dd></div>
      </dl>
      <p class="distance"><button type="button" data-distance>{e(L['dist_btn'])}</button> <span data-distance-out aria-live="polite">{e(L['dist_hint'])}</span></p>
    </div>
    <div class="map"><iframe src="{embed}" title="{e(L['map_title'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
  </div>
</section>

<section class="section faq" id="faq" aria-labelledby="faq-h" style="padding-top:0">
  <div class="head" style="grid-template-columns:1fr"><h2 id="faq-h">{e(L['faq_h'])}</h2></div>
  <div class="faq-list">{faq}</div>
</section>
</main>

<footer class="foot">
  <div><strong lang="zh-Hant">{e(SITE['name']['zh'])}</strong><p style="margin:0 0 6px">{e(SITE['name_alt']['zh'] if lang == 'zh' else (SITE['name']['en'] if lang == 'en' else SITE['name_alt']['ja']))}</p><address>{e(SITE['address'][lang])}<br><a href="{tel}">{e(SITE['phone_display'])}</a></address></div>
  <ul><li><a href="{SITE['instagram']}" rel="noopener">Instagram</a></li><li><a href="{SITE['facebook']}" rel="noopener">Facebook</a></li><li><a href="{SITE['ubereats']}" rel="noopener">Uber Eats</a></li><li><a href="{SITE['foodpanda']}" rel="noopener">foodpanda</a></li></ul>
  <p class="foot-review">{e(L['review_h'])} <a href="{SITE['review_url']}" rel="noopener">{e(L['review_btn'])}</a></p>
  <p class="credit">© {e(name)} · {e(L['credit'])}</p>
</footer>

<nav class="dock" aria-label="{e(L['reserve'])}">
  <a class="btn btn-fire" href="{SITE['reserve_url']}" rel="noopener">{e(L['reserve'])}</a>
  <a class="btn btn-line" href="{directions}" rel="noopener">{e(L['go'])}</a>
</nav>

<script type="application/json" id="raku-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="{a}assets/raku.js" defer></script>
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
        + "</url>" for L in LANGS.values())
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                                      f"{urls}\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "assets" / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#0f0d0c"/>'
        '<rect x="14" y="50" width="36" height="4" rx="2" fill="#ea5b1d"/>'
        '<text x="32" y="44" text-anchor="middle" font-family="serif" font-size="38" fill="#e6e1d8">蒜</text></svg>', encoding="utf-8")
    print("wrote sitemap.xml, robots.txt, favicon.svg")


if __name__ == "__main__":
    main()
