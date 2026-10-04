// 蒜串屋 v3 — tonight's status, the course fired one by one as you scroll, nav position, distance.
// 營業時間只要改這裡（和 build.py 的 HOURS_SCHEMA 保持一致）。day: 0=週日；分鐘，跨午夜就 >1440。
const HOURS = { 0: [1050, 1530], 1: [1050, 1530], 2: [1050, 1530], 3: [1050, 1530], 4: [1050, 1530], 5: [1050, 1560], 6: [1050, 1560] };

const DATA = JSON.parse(document.getElementById("raku-data").textContent);
const S = DATA.strings;
const fmt = (m) => { m = ((m % 1440) + 1440) % 1440; return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`; };
const fill = (t, o) => t.replace(/\{(\w+)\}/g, (_, k) => o[k]);

// ---------- tonight ----------
function taipeiNow() {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: "Asia/Taipei", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
  const g = (t) => parts.find((p) => p.type === t).value;
  return { day: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(g("weekday")), min: +g("hour") * 60 + +g("minute") };
}
function status() {
  const { day, min } = taipeiNow();
  const prev = (day + 6) % 7;
  if (HOURS[prev] && HOURS[prev][1] > 1440 && min < HOURS[prev][1] - 1440) {
    const [o, c] = HOURS[prev];
    return { open: true, close: c, day: prev, progress: (min + 1440 - o) / (c - o), last: c - (min + 1440) <= 30 };
  }
  const h = HOURS[day];
  if (h && min >= h[0] && min < h[1]) return { open: true, close: h[1], day, progress: (min - h[0]) / (h[1] - h[0]), last: h[1] - min <= 30 };
  return { open: false, next: h && min < h[0] ? h[0] : (HOURS[(day + 1) % 7] || [1050])[0], day, progress: 0 };
}
function paint() {
  const s = status();
  document.querySelectorAll("[data-status]").forEach((el) => { el.dataset.open = String(s.open); });
  document.querySelectorAll("[data-state]").forEach((el) => { el.textContent = s.open ? (s.last ? S.last : S.open) : S.closed; });
  document.querySelectorAll("[data-until]").forEach((el) => { el.textContent = s.open ? fill(S.until, { t: fmt(s.close) }) : fill(S.opens, { t: fmt(s.next) }); });
  document.querySelectorAll(".tonight .bar i").forEach((el) => { el.style.transform = `scaleX(${Math.min(1, s.progress).toFixed(3)})`; });
  document.querySelectorAll(".hours tr[data-day]").forEach((tr) => tr.classList.toggle("today", tr.dataset.day.split(",").map(Number).includes(s.day)));
}
paint();
setInterval(paint, 60_000);

// ---------- the course: the item in view is on the fire ----------
const items = [...document.querySelectorAll(".course-item")];
const front = document.querySelector(".course-front img");
const back = document.querySelector(".course-back");
let current = -1;
function fire(i) {
  if (i === current || !items[i]) return;
  current = i;
  items.forEach((el, k) => {
    el.classList.toggle("fire", k === i);
    el.classList.toggle("fired", k < i);
    if (k === i) el.setAttribute("aria-current", "step"); else el.removeAttribute("aria-current");
  });
  const d = items[i].dataset;
  if (front && d.photo && front.dataset.src !== d.photo) {
    front.style.opacity = "0";
    const next = new Image();
    next.onload = () => { front.src = next.src; front.dataset.src = d.photo; front.style.opacity = "1"; };
    next.src = `${d.photo}?w=900&h=1125&fit=crop&q=70&auto=format`;
  }
  if (back) {
    back.querySelector("h3").textContent = d.name;
    back.querySelector("p").textContent = d.method;
    back.querySelector("[data-heat]").textContent = d.heat;
    back.querySelector("[data-time]").textContent = d.time;
    back.querySelector("[data-season]").textContent = d.season;
  }
}
const hash = decodeURIComponent(location.hash.slice(1));
const hashIndex = items.findIndex((el) => el.id === hash);
fire(hashIndex >= 0 ? hashIndex : 0);

// ---------- firing stages: hover/focus heats one ----------
document.querySelectorAll(".stage").forEach((st) => {
  st.addEventListener("focusin", () => st.classList.add("hot"));
  st.addEventListener("focusout", () => st.classList.remove("hot"));
});

// ---------- on scroll: which course item is at the centre, which section is current ----------
const navLinks = [...document.querySelectorAll(".rail ol a")];
const sections = navLinks.map((a) => document.getElementById(a.getAttribute("href").slice(1)));
let ticking = false;
function onScroll() {
  ticking = false;
  const mid = innerHeight * 0.5;
  if (items.length) {
    const first = items[0].getBoundingClientRect(), last = items[items.length - 1].getBoundingClientRect();
    if (first.top < innerHeight && last.bottom > 0) {
      let best = 0, bestD = Infinity;
      items.forEach((el, k) => { const r = el.getBoundingClientRect(); const d = Math.abs(r.top + r.height / 2 - mid); if (d < bestD) { bestD = d; best = k; } });
      fire(best);
    }
  }
  let cur = -1;
  sections.forEach((sec, k) => { if (sec && sec.getBoundingClientRect().top <= innerHeight * 0.4) cur = k; });
  navLinks.forEach((a, k) => { if (k === cur) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
}
addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
addEventListener("resize", onScroll);
onScroll();

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
        const m = 2 * R * Math.asin(Math.sqrt(h)) * 1.3;
        const mins = Math.max(1, Math.round(m / 80));
        const dist = m < 1000 ? `${Math.round(m / 10) * 10} m` : `${(m / 1000).toFixed(1)} km`;
        out.replaceChildren();
        fill(S.geoOk, { d: "\u0000", m: "\u0001" }).split(/(\u0000|\u0001)/).forEach((p) => {
          if (p === "\u0000" || p === "\u0001") { const b = document.createElement("b"); b.textContent = p === "\u0000" ? dist : String(mins); out.append(b); }
          else out.append(p);
        });
      },
      () => { out.textContent = S.geoFail; },
      { timeout: 10000, maximumAge: 60000 }
    );
  });
}
