/* BIZ Geo – Prototyp: Mobile-Navigation + aktiver Navigationszustand */
document.addEventListener('DOMContentLoaded', function () {
  var burger = document.querySelector('.burger');
  var nav = document.querySelector('.nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Header setzt sich beim Scrollen durch einen Schatten ab, statt durch eine
  // dauerhaft sichtbare Trennlinie.
  var header = document.querySelector('.header');
  if (header) {
    var setShadow = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    setShadow();
    window.addEventListener('scroll', setShadow, { passive: true });
  }

  // Dropdown-Untermenüs: per Klick/Tap auf den Pfeil öffnen und schliessen.
  // Der Titel selbst bleibt ein normaler Link zur Übersichtsseite; nur der
  // Pfeil klappt das Menü auf. Auf dem Desktop öffnet zusätzlich Hover (CSS).
  var subs = Array.prototype.slice.call(document.querySelectorAll('.has-sub'));
  function closeAll(except) {
    subs.forEach(function (li) {
      if (li === except) return;
      li.removeAttribute('data-open');
      var t = li.querySelector('.sub-toggle');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  }
  subs.forEach(function (li) {
    var toggle = li.querySelector('.sub-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var open = li.getAttribute('data-open') === 'true';
      closeAll(li);
      li.setAttribute('data-open', open ? 'false' : 'true');
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-sub')) closeAll(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null);
  });

  // Aktive Seite in der Navigation markieren
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').split('#')[0];
    if (href === here) a.setAttribute('aria-current', 'page');
  });

  // Sprachumschalter: im Prototyp nur DE aktiv, FR/IT als Platzhalter
  document.querySelectorAll('.langs a[data-placeholder]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      alert('Sprachversion "' + a.textContent.trim() + '" ist im Prototyp noch nicht hinterlegt.\n' +
            'Vorgesehenes URL-Schema: biz-geo.ch/' + a.textContent.trim().toLowerCase() + '/…');
    });
  });

  /* --------------------------------------------------- Scroll-Bewegung ----
     Nur aktivieren, wenn der Nutzer keine reduzierte Bewegung wünscht.     */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;

  document.documentElement.classList.add('anim');

  // Automatisch Abschnitte und Kachelgruppen zum Einblenden markieren,
  // damit das HTML sauber bleibt und nichts pro Seite gepflegt werden muss.
  document.querySelectorAll('.section .wrap > *').forEach(function (n) {
    if (!n.hasAttribute('data-reveal') && !n.hasAttribute('data-reveal-group')) {
      n.setAttribute('data-reveal', '');
    }
  });
  document.querySelectorAll('.grid, .events, .steps, .facts').forEach(function (g) {
    g.removeAttribute('data-reveal');
    g.setAttribute('data-reveal-group', '');
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('in-view'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

  document.querySelectorAll('[data-reveal], [data-reveal-group]').forEach(function (n) {
    io.observe(n);
  });

  // Hero: Inhalt schwebt beim Scrollen sanft mit und blendet leicht aus.
  var hero = document.querySelector('.hero');
  var heroInner = hero && hero.querySelector('.wrap');
  if (heroInner) {
    heroInner.classList.add('hero__inner');
    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        var h = hero.offsetHeight || 1;
        var p = Math.min(y / h, 1);
        heroInner.style.setProperty('--hero-shift', (y * 0.18).toFixed(1) + 'px');
        heroInner.style.setProperty('--hero-fade', (1 - p * 0.9).toFixed(3));
        ticking = false;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
});
