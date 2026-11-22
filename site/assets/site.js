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
