// Lane filter for the question index. Optional: without JavaScript the legend is a plain key and every
// question is listed.
(function () {
  "use strict";
  var legend = document.querySelector("[data-lane-filter]");
  if (!legend) return;
  var rows = Array.prototype.slice.call(document.querySelectorAll(".q-row[data-lane]"));
  var groups = Array.prototype.slice.call(document.querySelectorAll(".q-group"));
  var status = document.querySelector("[data-filter-status]");
  var buttons = [];
  var current = null;

  function apply(lane) {
    current = lane;
    var shown = 0;
    rows.forEach(function (row) {
      var on = !lane || row.getAttribute("data-lane") === lane;
      row.hidden = !on;
      if (on) shown += 1;
    });
    groups.forEach(function (group) {
      if (group.querySelector(".q-row")) group.hidden = !group.querySelector(".q-row:not([hidden])");
    });
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-lane") === lane));
    });
    if (status) {
      status.textContent = lane
        ? "Showing " + shown + " of " + rows.length + " questions, " + lane + " lane. Press the lane again to show all."
        : "Showing all " + rows.length + " questions.";
    }
  }

  Array.prototype.forEach.call(legend.querySelectorAll("li[data-lane]"), function (li) {
    var b = document.createElement("button");
    b.type = "button";
    b.setAttribute("data-lane", li.getAttribute("data-lane"));
    b.setAttribute("aria-pressed", "false");
    b.title = "Show only this lane. " + (li.title || "");
    li.removeAttribute("title");
    while (li.firstChild) b.appendChild(li.firstChild);
    li.appendChild(b);
    buttons.push(b);
    b.addEventListener("click", function () {
      var lane = b.getAttribute("data-lane");
      apply(current === lane ? null : lane);
    });
  });
  legend.setAttribute("aria-label", "Filter questions by lane");
})();

// Chart tooltips. Every mark with a data-tip attribute shows its numbers on hover and on keyboard focus.
// The same numbers are in the page's tables, so nothing depends on this script.
(function () {
  "use strict";
  var marks = document.querySelectorAll(".chart [data-tip]");
  if (!marks.length) return;
  var tip = document.createElement("div");
  tip.className = "chart-tip";
  tip.setAttribute("role", "status");
  tip.hidden = true;
  document.body.appendChild(tip);

  function fill(el) {
    tip.textContent = "";
    el.getAttribute("data-tip").split("|").forEach(function (line, i) {
      var node = document.createElement(i === 0 ? "b" : "div");
      node.textContent = line;
      tip.appendChild(node);
    });
    tip.hidden = false;
  }
  function place(x, y) {
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.min(Math.max(8, x + 14), window.innerWidth - w - 8);
    var top = y + 18 + h > window.innerHeight ? y - h - 12 : y + 18;
    tip.style.left = left + "px";
    tip.style.top = Math.max(8, top) + "px";
  }
  function hide() { tip.hidden = true; }

  Array.prototype.forEach.call(marks, function (el) {
    el.addEventListener("pointerenter", function (e) { fill(el); place(e.clientX, e.clientY); });
    el.addEventListener("pointermove", function (e) { place(e.clientX, e.clientY); });
    el.addEventListener("pointerleave", hide);
    el.addEventListener("focus", function () {
      var r = el.getBoundingClientRect();
      fill(el);
      place(r.left + r.width / 2, r.top + r.height / 2);
    });
    el.addEventListener("blur", hide);
  });
  window.addEventListener("scroll", hide, { passive: true });
})();
