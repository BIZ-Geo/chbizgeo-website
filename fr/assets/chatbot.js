/* ==========================================================================
   BIZ Geo – Frage-Bot (Prototyp)
   Beantwortet Fragen ausschliesslich aus den Inhalten dieser Website.
   Läuft vollständig im Browser: lädt assets/search-index.json und sucht den
   passendsten Abschnitt per Stichwort-Überschneidung (TF-Gewichtung).
   Für den Livegang lässt sich answer() gegen einen echten LLM-Endpunkt am
   Server tauschen – die Oberfläche bleibt unverändert.
   ========================================================================== */
(function () {
  "use strict";

  var STOP = new Set(("und oder der die das ein eine einen dem den des ist sind war " +
    "wie was wann wo wer warum wieviel wie viele viel für mit von zu im in an auf " +
    "es sich auch als bei aus nach über um noch nur man kann muss soll wird werden " +
    "haben hat ich du wir ihr sie mein dein unser euer welche welcher welches ob " +
    "gibt es mich mir dir uns bitte danke hallo").split(/\s+/));

  function norm(s) {
    return (s || "").toLowerCase()
      .replace(/[äáà]/g, "a").replace(/[öóò]/g, "o").replace(/[üúù]/g, "u").replace(/ß/g, "ss")
      .replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
  }
  function tokens(s) {
    return norm(s).split(" ").filter(function (w) { return w.length > 2 && !STOP.has(w); });
  }

  var INDEX = [];
  var ready = false;

  // Kuratierte Kurzantworten für die häufigsten Fragen. Sie zeigen zusätzlich
  // auf den passenden Abschnitt; die Freitextsuche greift für alles andere.
  var FAQ = [
    { k: ["kosten", "preis", "gebuhr", "teuer", "bezahlen"],
      a: "Die Kosten richten sich nach den einzelnen Modulen gemäss Preisliste. Für die Vorbereitung auf die eidgenössische Berufsprüfung sind Bundesbeiträge möglich.",
      url: "fachausweis.html#ueberblick" },
    { k: ["dauer", "lange", "wie lang", "jahre", "zeit"],
      a: "Der Lehrgang dauert rund zwei Jahre und ist berufsbegleitend aufgebaut.",
      url: "fachausweis.html#ueberblick" },
    { k: ["voraussetzung", "zulassung", "bedingung", "efz", "anforderung"],
      a: "Vorausgesetzt wird ein EFZ als Geomatiker/in oder eine gleichwertige Qualifikation mit Berufspraxis.",
      url: "fachausweis.html#ueberblick" },
    { k: ["anmelden", "anmeldung", "einschreiben", "buchen"],
      a: "Die Anmeldung läuft online – für den gesamten Lehrgang, für einzelne Module oder für Einzelkurse.",
      url: "anmeldung.html" },
    { k: ["kontakt", "telefon", "email", "mail", "erreichen", "sekretariat"],
      a: "Das Sekretariat (Franziska André) erreichen Sie unter +41 78 674 13 77 oder andre@biz-geo.ch.",
      url: "kontakt.html" },
    { k: ["modul", "module", "basismodul", "wahlmodul"],
      a: "Der Lehrgang umfasst fünf Basismodule (B1–B5) und acht Wahlmodule (S1–S8). Jedes Modul ist auch einzeln als Weiterbildung buchbar.",
      url: "fachausweis.html#basismodule" },
    { k: ["sprache", "franzosisch", "italienisch", "deutsch", "sprachregion"],
      a: "BIZ Geo ist in allen Schweizer Sprachregionen tätig. Angebote und Beratung gibt es auf Deutsch, Französisch und Italienisch.",
      url: "ueber-uns.html#vision" },
    { k: ["kurs", "weiterbildung", "einzelkurs", "kurse"],
      a: "Neben dem Lehrgang gibt es einzeln buchbare Kurse in fünf Fachgebieten – von amtlicher Vermessung über GIS bis Projektmanagement.",
      url: "weiterbildung.html#fachgebiete" },
    { k: ["arbeitgeber", "betrieb", "firma", "mitarbeitende", "berufsbildner", "team"],
      a: "Für Betriebe ist die Weiterbildung berufsbegleitend, eidgenössisch anerkannt, in allen Sprachregionen verfügbar und über Bundesbeiträge gefördert.",
      url: "weiterbildung.html#arbeitgeber" }
  ];

  // Ein Stichwort passt, wenn ein Frage-Wort das Stichwort enthält, umgekehrt,
  // oder beide dieselben ersten fünf Zeichen teilen (fängt Beugungen wie
  // „kostet"/„kosten" oder „dauert"/„dauer").
  function faqHit(keyword, qToks) {
    var kw = norm(keyword);
    return qToks.some(function (t) {
      return t === kw || t.indexOf(kw) === 0 || kw.indexOf(t) === 0 ||
             (kw.length >= 5 && t.length >= 5 && kw.slice(0, 5) === t.slice(0, 5));
    });
  }

  function load() {
    return fetch("assets/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        INDEX = data.map(function (e) {
          return { page: e.page, url: e.url, title: e.title, text: e.text,
                   toks: tokens(e.title + " " + e.title + " " + e.text) };
        });
        ready = true;
      })
      .catch(function () { ready = false; });
  }

  function search(query) {
    var q = tokens(query);
    if (!q.length) return [];
    var scored = INDEX.map(function (e) {
      var score = 0;
      q.forEach(function (w) {
        e.toks.forEach(function (t) {
          if (t === w) score += 2;
          else if (t.indexOf(w) === 0 || w.indexOf(t) === 0) score += 1;
        });
      });
      return { e: e, score: score };
    }).filter(function (s) { return s.score > 0; });
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored;
  }

  function snippet(text, query) {
    var q = tokens(query);
    var sentences = text.split(/(?<=[.!?])\s+/);
    var best = sentences[0] || text, bestScore = -1;
    sentences.forEach(function (s) {
      var t = norm(s), sc = 0;
      q.forEach(function (w) { if (t.indexOf(w) >= 0) sc++; });
      if (sc > bestScore) { bestScore = sc; best = s; }
    });
    if (best.length > 240) best = best.slice(0, 237) + "…";
    return best;
  }

  function answer(query) {
    var qToks = tokens(query);
    // 1) Kuratierte FAQ zuerst
    for (var i = 0; i < FAQ.length; i++) {
      if (FAQ[i].k.some(function (kw) { return faqHit(kw, qToks); })) {
        var f = FAQ[i], hit = INDEX.filter(function (e) { return e.url === f.url; })[0];
        return { text: f.a, link: f.url, linkLabel: hit ? hit.title : "Mehr dazu" };
      }
    }
    // 2) Freitextsuche im Index
    var res = search(query);
    if (!res.length) {
      return { text: "Dazu finde ich auf der Website keine passende Stelle. Für persönliche " +
        "Auskünfte hilft das Sekretariat gern weiter.", link: "kontakt.html", linkLabel: "Kontakt" };
    }
    var top = res[0].e;
    return { text: snippet(top.text, query), link: top.url, linkLabel: top.title,
             more: res.slice(1, 3).map(function (r) { return { url: r.e.url, title: r.e.title }; }) };
  }

  /* ----------------------------------------------------------------- UI ---- */
  var SUGGEST = ["Was kostet der Lehrgang?", "Wie lange dauert die Ausbildung?",
                 "Welche Voraussetzungen brauche ich?", "Wie melde ich mich an?"];

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  function build() {
    var root = el("div", "bot");
    root.innerHTML =
      '<button class="bot__fab" aria-label="Fragen stellen" aria-expanded="false">' +
        '<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">' +
        '<path fill="currentColor" d="M12 3C6.98 3 3 6.58 3 11c0 2.05.86 3.92 2.28 5.35L4 21l4.9-1.3c.98.3 2.03.46 3.1.46 5.02 0 9-3.58 9-8s-3.98-8.16-9-8.16z"/>' +
        '<circle cx="8.5" cy="11" r="1.2" fill="#16202B"/><circle cx="12" cy="11" r="1.2" fill="#16202B"/><circle cx="15.5" cy="11" r="1.2" fill="#16202B"/></svg>' +
      '</button>' +
      '<section class="bot__panel" role="dialog" aria-label="Frage-Bot" aria-hidden="true">' +
        '<header class="bot__head">' +
          '<span><strong>Fragen zu BIZ Geo?</strong><small>Antworten aus den Inhalten dieser Website</small></span>' +
          '<button class="bot__close" aria-label="Schliessen">&times;</button>' +
        '</header>' +
        '<div class="bot__log" aria-live="polite"></div>' +
        '<div class="bot__chips"></div>' +
        '<form class="bot__form">' +
          '<input class="bot__input" type="text" autocomplete="off" placeholder="Frage eingeben …" aria-label="Ihre Frage">' +
          '<button class="bot__send" aria-label="Senden">→</button>' +
        '</form>' +
      '</section>';
    document.body.appendChild(root);

    var fab = root.querySelector(".bot__fab");
    var panel = root.querySelector(".bot__panel");
    var log = root.querySelector(".bot__log");
    var chips = root.querySelector(".bot__chips");
    var form = root.querySelector(".bot__form");
    var input = root.querySelector(".bot__input");
    var opened = false;

    function add(role, node) {
      var row = el("div", "bot__msg bot__msg--" + role);
      if (typeof node === "string") row.textContent = node; else row.appendChild(node);
      log.appendChild(row);
      log.scrollTop = log.scrollHeight;
      return row;
    }

    function respond(text) {
      var r = answer(text);
      var wrap = el("div");
      wrap.appendChild(el("p", "bot__ans", r.text));
      if (r.link) {
        var a = el("a", "bot__link");
        a.href = r.link; a.textContent = r.linkLabel + " →";
        wrap.appendChild(a);
      }
      if (r.more && r.more.length) {
        var more = el("div", "bot__more", "Auch relevant: ");
        r.more.forEach(function (m, i) {
          var a = el("a"); a.href = m.url; a.textContent = m.title;
          more.appendChild(a);
          if (i < r.more.length - 1) more.appendChild(document.createTextNode(" · "));
        });
        wrap.appendChild(more);
      }
      add("bot", wrap);
    }

    function ask(text) {
      add("user", text);
      chips.innerHTML = "";
      if (!ready) { add("bot", "Einen Moment, ich lade noch die Inhalte …"); return; }
      setTimeout(function () { respond(text); }, 250);
    }

    SUGGEST.forEach(function (s) {
      var c = el("button", "bot__chip", s);
      c.addEventListener("click", function () { ask(s); });
      chips.appendChild(c);
    });

    function open() {
      opened = true;
      panel.classList.add("is-open");
      panel.setAttribute("aria-hidden", "false");
      fab.setAttribute("aria-expanded", "true");
      if (!log.dataset.greeted) {
        add("bot", "Grüezi! Ich beantworte Fragen rund um BIZ Geo anhand der Website. Was möchten Sie wissen?");
        log.dataset.greeted = "1";
      }
      setTimeout(function () { input.focus(); }, 60);
    }
    function close() {
      opened = false;
      panel.classList.remove("is-open");
      panel.setAttribute("aria-hidden", "true");
      fab.setAttribute("aria-expanded", "false");
    }

    fab.addEventListener("click", function () { opened ? close() : open(); });
    root.querySelector(".bot__close").addEventListener("click", close);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && opened) close(); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = input.value.trim();
      if (!v) return;
      input.value = "";
      ask(v);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    load();
    build();
  });
})();
