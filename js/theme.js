/* Colour-scheme toggle — progressive enhancement.
 *
 * The dark stylesheet is linked as media="(prefers-color-scheme: dark)", so the
 * correct scheme is already applied before this file runs, and the site is fully
 * usable with JavaScript disabled. All this adds is a manual override, persisted
 * per reader. The button starts hidden and is revealed here, so a reader without
 * JavaScript never sees a control that does nothing.
 */
(function () {
  "use strict";
  var KEY = "iphs400-color-scheme";
  var link = document.getElementById("dark-scheme");
  var btn = document.getElementById("theme-toggle");
  if (!link || !btn) return;

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function apply(mode) {
    if (mode === "dark") link.media = "all";
    else if (mode === "light") link.media = "not all";
    else link.media = "(prefers-color-scheme: dark)";

    var dark = mode === "dark" || (mode === "system" && systemPrefersDark());
    btn.setAttribute("aria-pressed", String(dark));
    btn.textContent = dark ? "☀ Light mode" : "☾ Dark mode";
  }

  var saved = "system";
  try { saved = localStorage.getItem(KEY) || "system"; } catch (e) { /* private mode */ }

  apply(saved);
  btn.hidden = false;

  btn.addEventListener("click", function () {
    var nowDark = btn.getAttribute("aria-pressed") === "true";
    var next = nowDark ? "light" : "dark";
    try { localStorage.setItem(KEY, next); } catch (e) { /* ignore */ }
    apply(next);
  });
})();
