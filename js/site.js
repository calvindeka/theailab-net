/* Page enhancements — progressive only. Every page is complete without this file.
 *
 * 1. "Where we are" (home page). The panel is written at build time, which
 *    freezes "today" at the build date: a site built on Thursday says "Next
 *    session: Today" for the rest of the week. This recomputes the panel, the
 *    highlighted row and the THIS WEEK tag from the schedule data embedded in
 *    the page, using the reader's own date. The logic mirrors current_week()
 *    and next_deadline() in tools/build_site.py; tests/test_unit_live_schedule.py
 *    checks the two agree for every date in the term.
 *
 * 2. Week list on phones. The sidebar's 15 week links sit above the content on
 *    narrow screens, so they are folded into a "Weeks" toggle there. Without
 *    JavaScript the list simply stays open.
 */
(function (root) {
  "use strict";

  // ---- pure logic (also loaded by the test suite under Node) -------------
  function isoToday(d) {
    d = d || new Date();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + m + "-" + day;
  }

  // ISO dates compare correctly as strings, which avoids timezone drift.
  function whereWeAre(data, today) {
    var weeks = data.weeks;
    var week = weeks[weeks.length - 1];
    for (var i = 0; i < weeks.length; i++) {
      var s = weeks[i].sessions;
      if (today <= s[s.length - 1]) { week = weeks[i]; break; }
    }
    var nextSession = null;
    for (var j = 0; j < week.sessions.length; j++) {
      if (week.sessions[j] >= today) { nextSession = week.sessions[j]; break; }
    }
    var deadline = null;
    (data.assignments || []).forEach(function (a) {
      if (a.due >= today && (!deadline || a.due < deadline.due)) deadline = a;
    });
    return { week: week, nextSession: nextSession, deadline: deadline };
  }

  function toDate(iso) {
    var p = iso.split("-");
    return new Date(+p[0], +p[1] - 1, +p[2]);
  }
  function daysBetween(fromIso, toIso) {
    return Math.round((toDate(toIso) - toDate(fromIso)) / 86400000);
  }
  function longDate(iso) {
    return toDate(iso).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var api = { whereWeAre: whereWeAre, daysBetween: daysBetween, isoToday: isoToday };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; }
  if (typeof document === "undefined") { return; }

  // ---- 1. live "where we are" -------------------------------------------
  function renderPanel() {
    var node = document.getElementById("schedule-data");
    var panel = document.querySelector(".this-week");
    if (!node || !panel) return;
    var data;
    try { data = JSON.parse(node.textContent); } catch (e) { return; }

    var today = isoToday();
    var w = whereWeAre(data, today);
    var time = data.course.meets.split(", ").slice(1).join(", ");

    var line;
    if (w.nextSession) {
      var when = w.nextSession === today ? "Today" : longDate(w.nextSession);
      line = "Next session: <strong>" + esc(when) + "</strong> · " + esc(time) + " · " + esc(data.course.location);
    } else {
      line = "Sessions: " + w.week.sessions.map(longDate).map(esc).join(" &amp; ");
    }

    var due = "";
    if (w.deadline) {
      var n = daysBetween(today, w.deadline.due);
      var rel = n === 0 ? "today" : n === 1 ? "tomorrow" : "in " + n + " days";
      due = '<p class="this-week-due">Next deadline: <a href="' + esc(w.deadline.page) + '">' +
            esc(w.deadline.name) + "</a> — <strong>" + esc(longDate(w.deadline.due)) +
            "</strong> (" + rel + ")</p>";
    }

    panel.innerHTML =
      '<p class="this-week-label">Where we are</p>' +
      '<h2><a href="' + esc(w.week.page) + '">Week ' + w.week.number + ": " + esc(w.week.title) + "</a></h2>" +
      "<p>" + line + "</p>" +
      '<p class="this-week-unit">' + esc(w.week.unit) + "</p>" + due;

    // today's row and the THIS WEEK tag
    Array.prototype.forEach.call(document.querySelectorAll("tr[data-date]"), function (tr) {
      tr.classList.toggle("is-today", tr.getAttribute("data-date") === today);
    });
    var tag = document.querySelector(".this-week-tag");
    var heading = document.querySelector('h3[data-week="' + w.week.number + '"]');
    if (tag && heading && tag.parentNode !== heading) heading.appendChild(tag);
  }

  // ---- 2. fold the week list on narrow screens ---------------------------
  function foldWeekNav() {
    var group = document.querySelector(".week-nav-group");
    if (!group || !window.matchMedia) return;
    var narrow = window.matchMedia("(max-width: 50rem)");
    // A page can load before it has a layout (background tab, thumbnail
    // capture): innerWidth is then 0, which also matches max-width. Folding on
    // that reading hid the week list on desktop, so require a real width.
    if (window.innerWidth > 0 && narrow.matches) group.open = false;
    // If the window is widened past the breakpoint, give the list back.
    var reopen = function (e) { if (!e.matches) group.open = true; };
    if (narrow.addEventListener) narrow.addEventListener("change", reopen);
    else if (narrow.addListener) narrow.addListener(reopen);
  }

  renderPanel();
  foldWeekNav();
})(this);
