/* Clube Natação de Olhão — interações e animações (escrito à mão). */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const hasGsap = () => window.gsap && window.ScrollTrigger;

  const yr = $(".js-year"); if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- inscription form: confirmation after Netlify redirect */
  if (new URLSearchParams(location.search).has("enviado")) {
    const done = $(".form__done"); if (done) done.hidden = false;
  }

  /* ---------- hero video: portrait file on tall screens */
  const video = $(".hero__video");
  if (video) {
    const tall = innerHeight > innerWidth * 1.1;
    if (tall && video.dataset.posterTall) video.poster = video.dataset.posterTall;
    if (!reduce) {
      video.src = tall ? video.dataset.srcTall : video.dataset.srcWide;
      video.play().catch(() => {});
    }
  }

  /* ---------- nav state: solid once scrolled, brand after the hero lockup, hidden going down.
     Plain scroll listener so it also works without GSAP or with reduced motion. */
  const nav = $(".nav");
  if (nav) {
    let lastY = scrollY;
    const onScroll = () => {
      const y = scrollY;
      nav.classList.toggle("is-scrolled", y > 60);
      nav.classList.toggle("is-branded", y > 150);
      if (Math.abs(y - lastY) < 6) return;
      nav.classList.toggle("is-hidden", y > 400 && y > lastY && !document.body.classList.contains("menu-open"));
      lastY = y;
    };
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- menu */
  const burger = $(".nav__burger");
  const setMenu = open => {
    document.body.classList.toggle("menu-open", open);
    burger?.setAttribute("aria-expanded", String(open));
    burger?.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    $(".menu")?.setAttribute("aria-hidden", String(!open));
    if (open) nav?.classList.remove("is-hidden");          // keep the close button reachable
    document.dispatchEvent(new CustomEvent("cno:menu", { detail: open }));
  };
  burger?.addEventListener("click", () => setMenu(!document.body.classList.contains("menu-open")));
  $$(".menu a").forEach(a => a.addEventListener("click", () => setMenu(false)));
  addEventListener("keydown", e => { if (e.key === "Escape" && document.body.classList.contains("menu-open")) { setMenu(false); burger?.focus(); } });

  /* ---------- manifesto: wrap words */
  $$(".js-words").forEach(el => {
    // keeps the <br> line breaks of the source: each line is wrapped word by word
    el.innerHTML = el.innerHTML.split(/(<br[^>]*>)/i)
      .map((part, i) => i % 2 ? " " + part : part.replace(/<[^>]*>/g, "").trim().split(/\s+/).filter(Boolean).map(w => `<span class="w">${w}</span>`).join(" "))
      .join("");
  });

  /* ---------- custom cursor */
  const cursor = $(".cursor");
  if (fine && cursor && !reduce) {
    let x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y;
    addEventListener("mousemove", e => { x = e.clientX; y = e.clientY; }, { passive: true });
    const label = $(".cursor__label", cursor);
    (function loop() {
      cx += (x - cx) * .2; cy += (y - cy) * .2;
      cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0)`;
      requestAnimationFrame(loop);
    })();
    document.addEventListener("mouseover", e => {
      const t = e.target.closest("[data-cursor], a, button");
      if (!t) { cursor.className = "cursor"; return; }
      if (t.dataset.cursor) { label.textContent = t.dataset.cursor; cursor.className = "cursor is-label"; }
      else cursor.className = "cursor is-hover";
    });
  }

  /* ---------- magnetic buttons */
  if (fine && !reduce) $$(".magnetic").forEach(b => {
    b.addEventListener("mousemove", e => {
      const r = b.getBoundingClientRect();
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .25}px, ${(e.clientY - r.top - r.height / 2) * .35}px)`;
    });
    b.addEventListener("mouseleave", () => { b.style.transition = "transform .6s cubic-bezier(.22,1,.36,1)"; b.style.transform = ""; setTimeout(() => b.style.transition = "", 600); });
  });

  /* ---------- tilt cards */
  if (fine && !reduce) $$(".tilt").forEach(t => {
    t.addEventListener("mousemove", e => {
      const r = t.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
      t.style.transform = `perspective(900px) rotateX(${-py * 6}deg) rotateY(${px * 8}deg)`;
    });
    t.addEventListener("mouseleave", () => { t.style.transition = "transform .8s cubic-bezier(.22,1,.36,1)"; t.style.transform = ""; setTimeout(() => t.style.transition = "", 800); });
  });

  /* ---------- the cap: follows the mouse in 3D and floats */
  const cap = $(".js-cap picture");
  if (cap && !reduce) {
    let rx = 0, ry = 0, tx = 0, ty = 0, t0 = performance.now();
    const stage = $(".js-cap").closest("section");
    if (fine) stage.addEventListener("mousemove", e => {
      const r = stage.getBoundingClientRect();
      ty = ((e.clientX - r.left) / r.width - .5) * 22; tx = -((e.clientY - r.top) / r.height - .5) * 16;
    });
    stage.addEventListener("mouseleave", () => { tx = ty = 0; });
    (function float(now) {
      rx += (tx - rx) * .06; ry += (ty - ry) * .06;
      const f = Math.sin((now - t0) / 1400) * 10;
      cap.style.transform = `translateY(${f}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${ry * -.15}deg)`;
      requestAnimationFrame(float);
    })(t0);
  }

  /* ---------- record time: scramble like a timing board */
  function scramble(el) {
    const final = el.dataset.final, digits = "0123456789";
    let frame = 0; const total = 44;
    (function tick() {
      frame++;
      el.textContent = final.split("").map((ch, i) => {
        if (!/\d/.test(ch)) return ch;
        return frame > total * (i + 1) / final.length ? ch : digits[(Math.random() * 10) | 0];
      }).join("");
      if (frame < total + 4) requestAnimationFrame(tick); else el.textContent = final;
    })();
  }

  /* ---------- counters */
  function count(el) {
    const end = +el.dataset.count, start = end > 1000 ? end - 60 : 0, dur = 1600, t0 = performance.now();
    (function step(now) {
      const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(start + (end - start) * e);
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }

  /* ---------- no animation fallback */
  function staticMode() {
    document.body.classList.remove("is-loading");
    document.documentElement.classList.add("no-motion");   // CSS lets the horizontal pieces scroll by hand
    $$(".reveal").forEach(el => { el.style.opacity = 1; el.style.transform = "none"; });
    $(".loader")?.remove();
    $$(".manifesto__text .w").forEach(w => w.classList.add("on"));
    $$(".js-scramble").forEach(el => el.textContent = el.dataset.final);
  }

  function start() {
    if (reduce || !hasGsap()) { staticMode(); return; }
    const { gsap, ScrollTrigger } = window;
    gsap.registerPlugin(ScrollTrigger);
    gsap.config({ nullTargetWarn: false });

    /* smooth scroll */
    let lenis = null;
    if (window.Lenis) {
      lenis = new Lenis({ duration: 1.15, smoothWheel: true });
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(t => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
      $$('a[href^="#"]').forEach(a => a.addEventListener("click", e => {
        const id = a.getAttribute("href"); if (id.length < 2) return;
        const target = $(id); if (!target) return;
        e.preventDefault(); lenis.scrollTo(target, { offset: +(a.dataset.offset || -20) });
      }));
    }
    document.addEventListener("cno:menu", e => e.detail ? lenis?.stop() : lenis?.start());
    const hasLoader = !!$(".loader");
    if (!hasLoader) {
      /* inner pages: short entrance, no preloader */
      document.body.classList.remove("is-loading");
      gsap.from(".page-hero .split", { yPercent: 110, duration: 1.4, stagger: .08, ease: "expo.out", delay: .1 });
      gsap.from([".page-hero .eyebrow", ".page-hero__lead", ".page-hero__actions", ".page-hero__media"], { opacity: 0, y: 30, duration: 1.2, stagger: .08, ease: "expo.out", delay: .3 });
    }
    if (hasLoader) lenis?.stop();

    /* ---------- preloader */
    const counter = $(".js-load-count");
    if (hasLoader) {
    /* The crest, the club name and "Aos seus lugares" come in with CSS (see .loader__*),
       so they show from the very first paint; GSAP drives the rope, the count and the exit. */
    const prog = { v: 0 };
    const FILL = 7;           // seconds the rope and the count take to fill the lane
    const X = FILL - 2;       // everything after the fill moves with it
    const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
    tl.to(".loader__rope", { scaleX: 1, duration: FILL, ease: "power3.inOut" }, 0)
      .to(prog, { v: 100, duration: FILL, ease: "power2.inOut", onUpdate: () => counter.textContent = String(Math.round(prog.v)).padStart(2, "0") }, 0)
      .to(".loader__water", { height: "125%", duration: 1.1, ease: "power3.in" }, X + 1.95)
      .to(".loader", { yPercent: -100, duration: 1, ease: "expo.inOut" }, X + 2.85)
      .add(() => { document.body.classList.remove("is-loading"); lenis?.start(); $(".loader")?.remove(); }, X + 3.7);

    /* hero intro */
    gsap.set(".hero__title .split", { yPercent: 110 });
    tl.to(".hero__title .split", { yPercent: 0, duration: 1.5, stagger: .1 }, X + 3.15)
      .from(".hero__video", { scale: 1.35, duration: 2.6, ease: "expo.out" }, X + 2.9)
      .from([".hero__brand", ".hero__lead", ".hero__actions", ".hero__marquee", ".hero__scroll"], { opacity: 0, y: 24, duration: 1.2, stagger: .08 }, X + 3.3)
      .from(".nav", { opacity: 0, duration: 1.2, clearProps: "opacity" }, X + 3.5);  // opacity only: the nav hides with a CSS transform

    /* returning in the same session: same entrance, faster */
    let seen = false;
    try { seen = sessionStorage.getItem("cno-visto") === "1"; sessionStorage.setItem("cno-visto", "1"); } catch (e) {}
    if (seen) tl.timeScale(1.7);
    }

    /* hero parallax out */
    gsap.to(".hero__inner", { yPercent: 18, opacity: .2, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } });
    gsap.to(".hero__video", { yPercent: 12, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } });

    /* progress lane rope */
    gsap.to(".progress__rope", { scaleX: 1, ease: "none", scrollTrigger: { start: 0, end: "max", scrub: .3 } });

    /* manifesto words light up */
    const words = $$(".manifesto__text .w");
    ScrollTrigger.create({ trigger: ".manifesto__text", start: "top 78%", end: "bottom 45%", scrub: true,
      onUpdate: s => { const n = Math.round(s.progress * words.length); words.forEach((w, i) => w.classList.toggle("on", i < n)); } });
    $$("[data-speed]").forEach(el => gsap.to(el, { yPercent: +el.dataset.speed * 100, ease: "none", scrollTrigger: { trigger: ".manifesto", start: "top bottom", end: "bottom top", scrub: true } }));

    /* counters */
    $$("[data-count]").forEach(el => ScrollTrigger.create({ trigger: el, start: "top 85%", once: true, onEnter: () => count(el) }));
    gsap.from(".stat", { y: 50, opacity: 0, duration: 1.2, ease: "expo.out", stagger: .1, scrollTrigger: { trigger: ".stats", start: "top 75%" } });

    /* journey: horizontal on desktop */
    const mm = gsap.matchMedia();
    mm.add("(min-width: 901px)", () => {
      const track = $(".journey__track");
      if (!track) return;
      const dist = () => track.scrollWidth - innerWidth;
      gsap.to(track, { x: () => -dist(), ease: "none", scrollTrigger: { trigger: ".journey", pin: ".journey__pin", start: "top top", end: () => "+=" + dist(), scrub: .8, invalidateOnRefresh: true, anticipatePin: 1 } });
    });
    mm.add("(max-width: 900px)", () => {
      $$(".lap").forEach(l => gsap.from(l, { y: 40, opacity: 0, duration: 1, ease: "expo.out", scrollTrigger: { trigger: l, start: "top 85%" } }));
    });

    /* headings rise */
    $$(".reveal").forEach(el => gsap.to(el, { opacity: 1, y: 0, duration: 1.1, ease: "expo.out", scrollTrigger: { trigger: el, start: "top 88%" } }));
    $$(".h2:not(.reveal)").forEach(h => gsap.from(h, { y: 60, opacity: 0, duration: 1.3, ease: "expo.out", scrollTrigger: { trigger: h, start: "top 85%" } }));
    $$(".eyebrow").forEach(h => gsap.from(h, { x: -20, opacity: 0, duration: 1, ease: "expo.out", scrollTrigger: { trigger: h, start: "top 90%" } }));

    /* coaches */
    gsap.from(".olympian__board .board__row", { x: 40, opacity: 0, duration: 1, stagger: .12, ease: "expo.out", scrollTrigger: { trigger: ".olympian__board", start: "top 75%" } });
    gsap.from(".olympian__title", { y: 60, opacity: 0, duration: 1.3, ease: "expo.out", scrollTrigger: { trigger: ".olympian", start: "top 75%" } });
    $$(".js-scramble").forEach(el => ScrollTrigger.create({ trigger: el, start: "top 80%", once: true, onEnter: () => scramble(el) }));
    $$(".coach").forEach(c => {
      gsap.from(c.querySelector(".coach__title"), { y: 60, opacity: 0, duration: 1.3, ease: "expo.out", scrollTrigger: { trigger: c, start: "top 75%" } });
      gsap.from(c.querySelectorAll(".facts__row"), { x: c.classList.contains("coach--flip") ? -40 : 40, opacity: 0, duration: 1, stagger: .12, ease: "expo.out", scrollTrigger: { trigger: c, start: "top 75%" } });
    });

    /* bento */
    gsap.from(".tile", { y: 80, opacity: 0, duration: 1.2, stagger: .08, ease: "expo.out", scrollTrigger: { trigger: ".bento", start: "top 80%" } });

    /* cap entrance */
    gsap.from(".cap__stage", { y: 120, rotate: -8, opacity: 0, duration: 1.6, ease: "expo.out", scrollTrigger: { trigger: ".cap", start: "top 70%" } });

    /* reels: drift + follow scroll velocity */
    $$(".reel").forEach(reel => {
      const track = $(".reel__track", reel); track.innerHTML += track.innerHTML; // loop
      const dir = +reel.dataset.dir; let x = dir > 0 ? 0 : -track.scrollWidth / 2, boost = 0;
      ScrollTrigger.create({ trigger: reel, start: "top bottom", end: "bottom top", onUpdate: s => { boost = Math.min(18, Math.abs(s.getVelocity()) / 120); } });
      gsap.ticker.add(() => {
        const half = track.scrollWidth / 2;
        x -= dir * (0.6 + boost); boost *= .92;
        if (x <= -half) x += half; if (x > 0) x -= half;
        track.style.transform = `translate3d(${x}px,0,0)`;
      });
    });

    /* quotes + join */
    gsap.from(".quotes blockquote", { y: 50, opacity: 0, duration: 1.2, stagger: .15, ease: "expo.out", scrollTrigger: { trigger: ".quotes", start: "top 85%" } });
    gsap.from(".schedule li", { x: 60, opacity: 0, duration: 1, stagger: .1, ease: "expo.out", scrollTrigger: { trigger: ".schedule", start: "top 80%" } });
    gsap.to(".join__img img", { yPercent: 10, scale: 1.1, ease: "none", scrollTrigger: { trigger: ".join", start: "top bottom", end: "bottom top", scrub: true } });

    /* footer mark */
    gsap.from(".foot__mark", { yPercent: 40, opacity: 0, duration: 1.6, ease: "expo.out", scrollTrigger: { trigger: ".foot__mark", start: "top 95%" } });

    addEventListener("load", () => ScrollTrigger.refresh());
  }

  /* gsap is deferred: wait for it, but never leave the loader up */
  let tries = 0;
  (function wait() {
    if (hasGsap() || reduce || tries > 40) return start();
    tries++; setTimeout(wait, 50);
  })();
})();
