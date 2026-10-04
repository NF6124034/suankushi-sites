// 蒜串屋 v2 — tube status, tongs → basket, the boss's questions, number plate, distance.
// 營業時間只要改這裡（和 build.py 的 HOURS_SCHEMA 保持一致）。day: 0=週日；分鐘，跨午夜就 >1440。
const HOURS = { 0: [1050, 1530], 1: [1050, 1530], 2: [1050, 1530], 3: [1050, 1530], 4: [1050, 1530], 5: [1050, 1560], 6: [1050, 1560] };

const DATA = JSON.parse(document.getElementById("stall-data").textContent);
const S = DATA.strings;
const ITEMS = DATA.items;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

const fmt = (m) => { m = ((m % 1440) + 1440) % 1440; return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`; };
const money = (n) => `NT$${n.toLocaleString()}`;
const fill = (t, o) => t.replace(/\{(\w+)\}/g, (_, k) => o[k]);

// ---------- live status ----------
function taipeiNow() {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: "Asia/Taipei", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
  const g = (t) => parts.find((p) => p.type === t).value;
  return { day: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(g("weekday")), min: +g("hour") * 60 + +g("minute") };
}
function status() {
  const { day, min } = taipeiNow();
  const prev = (day + 6) % 7;
  if (HOURS[prev] && HOURS[prev][1] > 1440 && min < HOURS[prev][1] - 1440) return { open: true, close: HOURS[prev][1], day: prev };
  const h = HOURS[day];
  if (h && min >= h[0] && min < h[1]) return { open: true, close: h[1], day };
  return { open: false, next: h && min < h[0] ? h[0] : (HOURS[(day + 1) % 7] || [1050])[0], day };
}
function paintStatus() {
  const s = status();
  document.querySelectorAll("[data-status]").forEach((el) => {
    el.dataset.open = String(s.open);
    el.querySelector(".status").textContent = s.open ? fill(S.open, { t: fmt(s.close) }) : fill(S.closed, { t: fmt(s.next) });
  });
  document.querySelectorAll(".hours tr[data-day]").forEach((tr) => tr.classList.toggle("today", tr.dataset.day.split(",").map(Number).includes(s.day)));
}
paintStatus();
setInterval(paintStatus, 60_000);

// ---------- basket ----------
const basket = new Map();
const notes = { spice: null, garlic: null, basil: null };
try {
  const saved = JSON.parse(localStorage.getItem("suankushi-basket") || "{}");
  Object.entries(saved.items || {}).forEach(([id, q]) => ITEMS[id] && q > 0 && basket.set(id, Math.min(q, 99)));
  Object.assign(notes, saved.notes || {});
} catch {}
const save = () => { try { localStorage.setItem("suankushi-basket", JSON.stringify({ items: Object.fromEntries(basket), notes })); } catch {} };

const basketBtn = document.querySelector("[data-basket]");
const countEl = basketBtn.querySelector(".count");
const sumEl = basketBtn.querySelector(".sum b");
const live = document.querySelector("[data-live]");

function paintBasket() {
  let n = 0, total = 0;
  basket.forEach((q, id) => { n += q; total += q * ITEMS[id].price; });
  countEl.textContent = n;
  sumEl.textContent = money(total);
  basketBtn.setAttribute("aria-label", fill(S.basketLabel, { n, total: money(total) }));
  document.querySelectorAll("[data-item]").forEach((el) => {
    const q = basket.get(el.dataset.item) || 0;
    if (el.classList.contains("tray")) {
      el.setAttribute("aria-pressed", String(q > 0));
      el.querySelector(".tally").textContent = q ? `×${q}` : "";
    } else {
      el.dataset.count = q;
      el.querySelector(".plus i").textContent = q || "";
    }
  });
  save();
}

function fly(fromEl) {
  if (reduceMotion || !fromEl) return;
  const img = fromEl.querySelector("img");
  const a = (img || fromEl).getBoundingClientRect();
  const b = basketBtn.getBoundingClientRect();
  const f = document.createElement("div");
  f.className = "flyer";
  Object.assign(f.style, { left: `${a.left}px`, top: `${a.top}px`, width: `${a.width}px`, height: `${a.height}px` });
  if (img) f.append(img.cloneNode());
  else f.style.background = "var(--marker)";
  document.body.append(f);
  const dx = b.left + b.width / 2 - (a.left + a.width / 2);
  const dy = b.top + b.height / 2 - (a.top + a.height / 2);
  f.animate(
    [
      { transform: "translate(0,0) scale(1) rotate(0)", opacity: 1 },
      { transform: `translate(${dx * 0.45}px, ${dy * 0.45 - 140}px) scale(0.55) rotate(-12deg)`, opacity: 1, offset: 0.45 },
      { transform: `translate(${dx}px, ${dy}px) scale(0.12) rotate(-24deg)`, opacity: 0.6 },
    ],
    { duration: 640, easing: "cubic-bezier(0.16, 1, 0.3, 1)" }
  ).onfinish = () => { f.remove(); basketBtn.classList.remove("bump"); void basketBtn.offsetWidth; basketBtn.classList.add("bump"); };
}

function add(id, el) {
  basket.set(id, Math.min((basket.get(id) || 0) + 1, 99));
  paintBasket();
  fly(el);
  live.textContent = fill(S.added, { name: ITEMS[id].name, n: basket.get(id) });
}
document.querySelectorAll("[data-item]").forEach((el) => el.addEventListener("click", () => add(el.dataset.item, el)));

// ---------- the boss's questions ----------
document.querySelectorAll(".q input").forEach((r) => {
  if (notes[r.name] === r.value) r.checked = true;
  r.addEventListener("change", () => { notes[r.name] = r.value; save(); });
});

// ---------- number plate ----------
const plate = document.querySelector("dialog.plate");
const plateList = plate.querySelector("ol");
const plateNum = plate.querySelector(".plate-num");
let num = null;

function paintPlate() {
  plateList.replaceChildren();
  let total = 0;
  basket.forEach((q, id) => {
    const it = ITEMS[id];
    total += q * it.price;
    const li = document.createElement("li");
    const name = document.createElement("span");
    name.textContent = it.zh;
    if (it.name !== it.zh) { const s = document.createElement("small"); s.textContent = it.name; name.append(s); }
    const right = document.createElement("b");
    const minus = Object.assign(document.createElement("button"), { type: "button", className: "step", innerHTML: DATA.icons.minus });
    minus.setAttribute("aria-label", fill(S.less, { name: it.name }));
    const plus = Object.assign(document.createElement("button"), { type: "button", className: "step", innerHTML: DATA.icons.plus });
    plus.setAttribute("aria-label", fill(S.more, { name: it.name }));
    minus.onclick = () => { q - 1 > 0 ? basket.set(id, q - 1) : basket.delete(id); paintBasket(); paintPlate(); };
    plus.onclick = () => { basket.set(id, Math.min(q + 1, 99)); paintBasket(); paintPlate(); };
    right.append(minus, `×${q}`, plus);
    li.append(name, right);
    plateList.append(li);
  });
  const empty = basket.size === 0;
  plate.querySelector(".plate-empty").hidden = !empty;
  plate.querySelector(".plate-total").hidden = empty;
  plate.querySelector("[data-clear]").disabled = empty;
  plate.querySelector(".plate-total b").textContent = money(total);
  const picked = ["spice", "garlic", "basil"].map((k) => notes[k] && S.notes[k][notes[k]]).filter(Boolean);
  const n = plate.querySelector(".plate-notes");
  n.textContent = picked.join("・");
  n.hidden = empty || !picked.length;
}
basketBtn.addEventListener("click", () => {
  if (num == null) num = 10 + Math.floor(Math.random() * 89);
  plateNum.textContent = num;
  paintPlate();
  plate.showModal();
});
plate.querySelector("[data-close]").addEventListener("click", () => plate.close());
plate.querySelector("[data-clear]").addEventListener("click", () => { basket.clear(); paintBasket(); paintPlate(); });
plate.addEventListener("click", (e) => { if (e.target === plate) plate.close(); });

paintBasket();

// ---------- how far am I ----------
const distBtn = document.querySelector("[data-distance]");
if (distBtn) {
  const out = document.querySelector("[data-distance-out]");
  const [lat0, lng0] = DATA.geo;
  distBtn.addEventListener("click", () => {
    if (!navigator.geolocation) { out.textContent = S.geoFail; return; }
    out.textContent = S.geoWait;
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const R = 6371000, rad = (d) => (d * Math.PI) / 180;
        const dLat = rad(coords.latitude - lat0), dLng = rad(coords.longitude - lng0);
        const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(lat0)) * Math.cos(rad(coords.latitude)) * Math.sin(dLng / 2) ** 2;
        const m = 2 * R * Math.asin(Math.sqrt(h)) * 1.3; // 街道繞路係數
        const mins = Math.max(1, Math.round(m / 80));
        const dist = m < 1000 ? `${Math.round(m / 10) * 10} m` : `${(m / 1000).toFixed(1)} km`;
        out.innerHTML = "";
        out.append(...fill(S.geoOk, { d: "\u0000", m: "\u0001" }).split(/(\u0000|\u0001)/).map((p) => {
          if (p === "\u0000" || p === "\u0001") { const b = document.createElement("b"); b.textContent = p === "\u0000" ? dist : String(mins); return b; }
          return document.createTextNode(p);
        }));
      },
      () => { out.textContent = S.geoFail; },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
    );
  });
}
