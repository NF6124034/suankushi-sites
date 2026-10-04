// 蒜串屋 — live open status + the order slip.
// 營業時間只要改這裡（和 HTML / JSON-LD 裡的時間保持一致）。
// day: 0=週日 … 6=週六；時間用分鐘，超過午夜就 >1440（01:30 = 1530）。
const HOURS = {
  0: [1050, 1530],
  1: [1050, 1530],
  2: [1050, 1530],
  3: [1050, 1530],
  4: [1050, 1530],
  5: [1050, 1560],
  6: [1050, 1560],
};

const T = {
  "zh-Hant-TW": {
    open: (c) => `營業中 · 今晚到 ${c}`,
    closed: (o) => `準備中 · ${o} 開門`,
    items: (n) => `${n} 樣`,
    currency: "NT$",
  },
  en: {
    open: (c) => `Open now · until ${c} tonight`,
    closed: (o) => `Closed · opens ${o}`,
    items: (n) => `${n} item${n === 1 ? "" : "s"}`,
    currency: "NT$",
  },
  ja: {
    open: (c) => `営業中 · 今夜 ${c} まで`,
    closed: (o) => `準備中 · ${o} 開店`,
    items: (n) => `${n} 品`,
    currency: "NT$",
  },
};
const L = T[document.documentElement.lang] || T["zh-Hant-TW"];

const fmt = (m) => {
  m = ((m % 1440) + 1440) % 1440;
  return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
};

// Current day/minute in Taipei regardless of the visitor's timezone.
function taipeiNow() {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Taipei", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(new Date());
  const get = (t) => parts.find((p) => p.type === t).value;
  const day = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(get("weekday"));
  return { day, min: Number(get("hour")) * 60 + Number(get("minute")) };
}

function status() {
  const { day, min } = taipeiNow();
  const prev = (day + 6) % 7;
  // still inside last night's service (after midnight)?
  const [po, pc] = HOURS[prev] || [];
  if (pc && pc > 1440 && min < pc - 1440) return { open: true, close: pc, serviceDay: prev };
  const [o, c] = HOURS[day] || [];
  if (o != null && min >= o && min < c) return { open: true, close: c, serviceDay: day };
  // next opening
  if (o != null && min < o) return { open: false, next: o, serviceDay: day };
  for (let i = 1; i <= 7; i++) {
    const d = (day + i) % 7;
    if (HOURS[d]) return { open: false, next: HOURS[d][0], serviceDay: day };
  }
  return { open: false, serviceDay: day };
}

function paintStatus() {
  const s = status();
  document.querySelectorAll("[data-status]").forEach((el) => {
    el.dataset.open = String(s.open);
    el.querySelector("[data-status-text]").textContent = s.open ? L.open(fmt(s.close)) : L.closed(fmt(s.next ?? 1050));
  });
  document.querySelectorAll(".hours tr[data-day]").forEach((tr) => {
    tr.classList.toggle("today", tr.dataset.day.split(",").map(Number).includes(s.serviceDay));
  });
}
paintStatus();
setInterval(paintStatus, 60_000);

// ---------- order slip ----------
const slip = document.querySelector("[data-slip]");
if (slip) {
  const totalEl = slip.querySelector("[data-total]");
  const countEl = slip.querySelector("[data-count]");
  const showBtn = slip.querySelector("[data-show]");
  const clearBtn = slip.querySelector("[data-clear]");
  const dialog = document.querySelector("dialog.show-staff");
  const items = [...slip.querySelectorAll(".item")];

  const state = () =>
    items
      .filter((li) => li.querySelector("input").checked)
      .map((li) => ({
        name: li.querySelector(".name").firstChild.textContent.trim(),
        zh: li.dataset.zh,
        price: Number(li.dataset.price),
        qty: Number(li.querySelector("output").value),
      }));

  function update() {
    const picked = state();
    const total = picked.reduce((s, i) => s + i.price * i.qty, 0);
    const count = picked.reduce((s, i) => s + i.qty, 0);
    totalEl.value = `${L.currency}${total.toLocaleString()}`;
    countEl.textContent = L.items(count);
    showBtn.disabled = clearBtn.disabled = picked.length === 0;
  }

  items.forEach((li) => {
    const box = li.querySelector("input");
    const out = li.querySelector("output");
    box.addEventListener("change", () => {
      li.classList.toggle("on", box.checked);
      if (!box.checked) out.value = 1;
      update();
    });
    li.querySelectorAll(".qty button").forEach((b) =>
      b.addEventListener("click", () => {
        const n = Number(out.value) + Number(b.dataset.step);
        if (n < 1) { box.checked = false; li.classList.remove("on"); out.value = 1; }
        else out.value = Math.min(n, 99);
        update();
      })
    );
  });

  clearBtn.addEventListener("click", () => {
    items.forEach((li) => { li.querySelector("input").checked = false; li.classList.remove("on"); li.querySelector("output").value = 1; });
    update();
  });

  showBtn.addEventListener("click", () => {
    const picked = state();
    const list = dialog.querySelector("ol");
    list.replaceChildren(
      ...picked.map((i) => {
        const row = document.createElement("li");
        // 店員看中文：外語頁面也以中文品名為主，原文放在下面
        const n = document.createElement("span");
        n.textContent = i.zh || i.name;
        if (i.zh && i.zh !== i.name) {
          const s = document.createElement("small");
          s.textContent = i.name;
          n.append(s);
        }
        const q = document.createElement("b");
        q.textContent = `× ${i.qty}`;
        row.append(n, q);
        return row;
      })
    );
    dialog.querySelector("[data-staff-total]").textContent = totalEl.value;
    dialog.showModal();
  });
  dialog.querySelector("[data-close]").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });

  update();
}
