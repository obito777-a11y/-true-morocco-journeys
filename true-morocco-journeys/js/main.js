/* =========================================================================
   TRUE MOROCCO JOURNEYS — main.js
   Vanilla JS only. No external JS deps besides Bootstrap's bundle.
   ========================================================================= */
(function () {
  "use strict";

  // ─── Django backend base URL ─────────────────────────────────────────────
  // Keep this in sync with the port Django is running on (manage.py runserver 8000)
  var API_BASE = "http://localhost:8000/api";

  /* ─── DOM ready ─────────────────────────────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", function () {
    initNavbar();
    initActiveNavLink();
    initRevealOnScroll();
    initCounters();
    initBackToTop();
    initTourFilters();
    initContactForm();
    initNewsletterForms();
    initYear();
  });

  /* ─── Navbar scroll state ────────────────────────────────────────────────── */
  function initNavbar() {
    var nav = document.querySelector(".tmj-navbar");
    if (!nav) return;

    function applyScrollState() {
      if (window.scrollY > 40) {
        nav.classList.add("is-scrolled");
      } else if (!nav.classList.contains("solid")) {
        nav.classList.remove("is-scrolled");
      }
    }
    applyScrollState();
    window.addEventListener("scroll", applyScrollState, { passive: true });

    // Collapse mobile menu after a link is tapped
    var navLinks = document.querySelectorAll(".tmj-navbar .nav-link");
    var collapseEl = document.querySelector(".tmj-navbar .navbar-collapse");
    navLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        if (collapseEl && collapseEl.classList.contains("show") && window.bootstrap) {
          window.bootstrap.Collapse.getOrCreateInstance(collapseEl).hide();
        }
      });
    });
  }

  /* ─── Active nav link ────────────────────────────────────────────────────── */
  function initActiveNavLink() {
    var path = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".tmj-navbar .nav-link[data-page]").forEach(function (link) {
      if (link.getAttribute("data-page") === path) {
        link.classList.add("active");
      }
    });
  }

  /* ─── Scroll-reveal ──────────────────────────────────────────────────────── */
  function initRevealOnScroll() {
    var items = document.querySelectorAll(".reveal");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* ─── Animated counters ──────────────────────────────────────────────────── */
  function initCounters() {
    var counters = document.querySelectorAll("[data-count]");
    if (!counters.length) return;

    function animateCounter(el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var decimals = (el.getAttribute("data-count").split(".")[1] || "").length;
      var duration = 1600;
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = (target * eased).toFixed(decimals);
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target.toFixed(decimals);
      }
      requestAnimationFrame(step);
    }

    if (!("IntersectionObserver" in window)) {
      counters.forEach(animateCounter);
      return;
    }

    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    counters.forEach(function (el) { obs.observe(el); });
  }

  /* ─── Back to top ────────────────────────────────────────────────────────── */
  function initBackToTop() {
    var btn = document.querySelector(".back-to-top");
    if (!btn) return;
    window.addEventListener("scroll", function () {
      btn.classList.toggle("show", window.scrollY > 500);
    }, { passive: true });
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ─── Tour filters ───────────────────────────────────────────────────────── */
  function initTourFilters() {
    var chips = document.querySelectorAll(".filter-chip[data-filter]");
    var cards = document.querySelectorAll("[data-category]");
    var emptyState = document.getElementById("filterEmptyState");
    if (!chips.length || !cards.length) return;

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.classList.remove("active"); });
        chip.classList.add("active");
        var filter = chip.getAttribute("data-filter");
        var visible = 0;

        cards.forEach(function (card) {
          var show = filter === "all" || (card.getAttribute("data-category") || "").split(" ").indexOf(filter) !== -1;
          card.style.display = show ? "" : "none";
          if (show) visible++;
        });

        if (emptyState) emptyState.style.display = visible === 0 ? "block" : "none";
      });
    });

    var searchInput = document.getElementById("tourSearch");
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        var query = searchInput.value.trim().toLowerCase();
        var visible = 0;
        cards.forEach(function (card) {
          var show = (card.getAttribute("data-title") || "").toLowerCase().indexOf(query) !== -1;
          card.style.display = show ? "" : "none";
          if (show) visible++;
        });
        if (emptyState) emptyState.style.display = visible === 0 ? "block" : "none";
        chips.forEach(function (c) { c.classList.remove("active"); });
        var allChip = document.querySelector('.filter-chip[data-filter="all"]');
        if (allChip) allChip.classList.add("active");
      });
    }
  }

  /* ─── Shared API helper ──────────────────────────────────────────────────── */
  function apiPost(endpoint, payload, onSuccess, onError) {
    fetch(API_BASE + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          onSuccess(data.message || "Success");
        } else {
          onError(data.error || "Something went wrong.");
        }
      })
      .catch(function () {
        onError("Network error — make sure the Django backend is running on port 8000.");
      });
  }

  /* ─── Contact form ───────────────────────────────────────────────────────── */
  function initContactForm() {
    var form = document.getElementById("contactForm");
    if (!form) return;
    var successBox = document.getElementById("contactSuccess");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (!form.checkValidity()) {
        form.classList.add("was-validated");
        var firstInvalid = form.querySelector(":invalid");
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      var submitBtn = form.querySelector('button[type="submit"]');
      var originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = "Sending&hellip;";

      // ── BUG FIX: include all 5 fields, including subject ──────────────────
      var payload = {
        name:    (document.getElementById("fName")    || {}).value || "",
        email:   (document.getElementById("fEmail")   || {}).value || "",
        phone:   (document.getElementById("fPhone")   || {}).value || "",
        subject: (document.getElementById("fSubject") || {}).value || "",
        message: (document.getElementById("fMessage") || {}).value || "",
      };

      apiPost(
        "/contact/",
        payload,
        function (msg) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          if (successBox) {
            successBox.classList.add("show");
            successBox.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          form.reset();
          form.classList.remove("was-validated");
        },
        function (errMsg) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          alert("Error: " + errMsg);
        }
      );
    });
  }

  /* ─── Newsletter forms ───────────────────────────────────────────────────── */
  function initNewsletterForms() {
    document.querySelectorAll("form[data-newsletter]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = form.querySelector('input[type="email"]');
        var msgEl = form.querySelector(".newsletter-msg");

        if (!input || !input.checkValidity()) {
          if (msgEl) {
            msgEl.textContent = "Please enter a valid email address.";
            msgEl.className = "newsletter-msg d-block text-rust mt-2";
          }
          return;
        }

        var btn = form.querySelector('button[type="submit"]');
        var originalText = btn ? btn.innerHTML : "";
        if (btn) { btn.disabled = true; btn.innerHTML = "Subscribing&hellip;"; }

        apiPost(
          "/newsletter/",
          { email: input.value.trim() },
          function (msg) {
            if (btn) { btn.disabled = false; btn.innerHTML = originalText; }
            if (msgEl) {
              msgEl.textContent = "✓ " + msg;
              msgEl.className = "newsletter-msg d-block mt-2";
              msgEl.style.color = "#1d9d6a";
            }
            form.reset();
          },
          function (errMsg) {
            if (btn) { btn.disabled = false; btn.innerHTML = originalText; }
            if (msgEl) {
              msgEl.textContent = errMsg;
              msgEl.className = "newsletter-msg d-block text-rust mt-2";
            }
          }
        );
      });
    });
  }

  /* ─── Footer year ────────────────────────────────────────────────────────── */
  function initYear() {
    var el = document.getElementById("currentYear");
    if (el) el.textContent = new Date().getFullYear();
  }

})();
