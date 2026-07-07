/* 호남연수원 · 인재키움 프리미엄 훈련 — 향상 기능 전용 스크립트.
   카드/가격/CTA는 정적 HTML이므로 이 파일이 실패해도 핵심 콘텐츠는 표시된다. */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  /* 진입 시 항상 최상단(히어로)부터 — 브라우저 스크롤 복원/잔여 앵커 차단 */
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  if (location.hash) {
    history.replaceState(null, "", location.pathname + location.search);
  }
  window.scrollTo(0, 0);

  var FORM_URL = document.body.getAttribute("data-form-url");

  /* ── 모바일 네비 ── */
  var burger = document.getElementById("navBurger");
  var menu = document.querySelector(".nav-menu");
  if (burger && menu) {
    burger.addEventListener("click", function () {
      menu.classList.toggle("open");
    });
    menu.addEventListener("click", function (e) {
      if (e.target.tagName === "A") menu.classList.remove("open");
    });
  }

  /* ── 과정 필터/검색 ── */
  var cards = Array.prototype.slice.call(document.querySelectorAll(".course-card"));
  var state = { type: "전체", city: "전체", q: "" };
  var countEl = document.getElementById("filterCount");
  var emptyEl = document.getElementById("courseEmpty");

  function applyFilter() {
    var visible = 0;
    cards.forEach(function (card) {
      var okType = state.type === "전체" || card.dataset.type === state.type;
      var okCity = state.city === "전체" || card.dataset.city === state.city;
      var okQ = !state.q || card.dataset.name.toLowerCase().indexOf(state.q) !== -1;
      var show = okType && okCity && okQ;
      card.style.display = show ? "" : "none";
      if (show) visible++;
    });
    if (countEl) countEl.textContent = "총 " + visible + "개 과정";
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  function bindChips(groupId, key) {
    var group = document.getElementById(groupId);
    if (!group) return;
    group.addEventListener("click", function (e) {
      var btn = e.target.closest(".chip");
      if (!btn) return;
      group.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("active"); });
      btn.classList.add("active");
      state[key] = btn.getAttribute("data-filter-type") || btn.getAttribute("data-filter-city");
      applyFilter();
    });
  }
  bindChips("typeFilter", "type");
  bindChips("cityFilter", "city");

  var search = document.getElementById("courseSearch");
  if (search) {
    search.addEventListener("input", function () {
      state.q = search.value.trim().toLowerCase();
      applyFilter();
    });
  }
  applyFilter();

  /* ── 과정 상세 모달 ── */
  var modal = document.getElementById("courseModal");
  function openModal(card) {
    var d = card.dataset;
    var badge = document.getElementById("modalType");
    badge.textContent = d.type;
    badge.className = "badge " + (d.type.indexOf("AI") !== -1 ? "badge-ai" : "badge-gen");
    document.getElementById("modalName").textContent = d.name;
    document.getElementById("modalHours").textContent = d.hours + "시간";
    document.getElementById("modalDays").textContent = d.days + "일";
    document.getElementById("modalSchedule").textContent = d.schedule + " 중 협의";
    document.getElementById("modalCapacity").textContent = d.capacity + "명";
    document.getElementById("modalAddr").textContent = d.addr;
    var tel = document.getElementById("modalTel");
    tel.innerHTML = '<a href="tel:' + d.tel.replace(/-/g, "") + '">' + d.tel + "</a>";
    document.getElementById("modalPrice").textContent = "정가 " + d.price + "원";
    document.getElementById("modalCopay").textContent = "실부담 " + d.copay + "원";
    document.getElementById("modalApply").href = FORM_URL;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";
  }
  if (modal) {
    cards.forEach(function (card) {
      card.addEventListener("click", function () { openModal(card); });
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openModal(card); }
      });
    });
    modal.addEventListener("click", function (e) {
      if (e.target.hasAttribute("data-close")) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !modal.hidden) closeModal();
    });
  }

  /* ── 모바일 하단 고정 CTA (히어로 지나면 표시) ── */
  var sticky = document.getElementById("stickyCta");
  var hero = document.querySelector(".hero");
  if (sticky && hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      sticky.classList.toggle("show", !entries[0].isIntersecting && modal.hidden);
    }, { threshold: 0.1 }).observe(hero);
  }

  /* ── 등장 애니메이션 ── */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
})();
