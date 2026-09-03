/**
 * Faculty usage panel.
 *
 * Reads its endpoint and the portal filter's current selection from data
 * attributes on #usagePanel, so the parameter names stay owned by the
 * filterset rather than being re-derived from the URL here.
 */
(function () {
  "use strict";

  var panel = document.getElementById("usagePanel");
  if (!panel) {
    return;
  }

  var endpoint = panel.dataset.usageUrl;
  var filterScope = {
    from: panel.dataset.filterFrom || "",
    to: panel.dataset.filterTo || "",
    instrument: panel.dataset.filterInstrument || "",
    status: panel.dataset.filterStatus || ""
  };
  var hasFilter = Boolean(
    filterScope.from || filterScope.to || filterScope.instrument || filterScope.status
  );

  var el = {};
  [
    "usageRows", "usageScope", "usageHours", "usageCost", "usageHoursCaption",
    "usageBookings", "usageBasis", "usageCustom", "usageFrom", "usageTo",
    "usageApply", "usageFilterChip", "queueAwaiting", "queueAwaitingHours",
    "queueAwaitingCost", "queueCleared", "queueClearedHours", "queueClearedCost",
    "queueDownstream"
  ].forEach(function (id) {
    el[id] = document.getElementById(id);
  });

  var presetButtons = Array.prototype.slice.call(panel.querySelectorAll("[data-preset]"));
  var groupButtons = Array.prototype.slice.call(panel.querySelectorAll("[data-group]"));

  var state = { preset: "this_fy", from: "", to: "", group: "by_instrument" };
  var latest = null;
  var inFlight = null;
  var pendingFlash = [];

  try {
    var saved = JSON.parse(window.localStorage.getItem("cifUsagePanel") || "{}");
    ["preset", "from", "to", "group"].forEach(function (key) {
      if (saved[key]) {
        state[key] = saved[key];
      }
    });
  } catch (error) {
    /* storage unavailable: the defaults are fine */
  }
  // A filter the user just applied wins over whatever the panel last showed.
  state.preset = hasFilter ? "filter" : (state.preset === "filter" ? "this_fy" : state.preset);

  function persist() {
    try {
      window.localStorage.setItem("cifUsagePanel", JSON.stringify(state));
    } catch (error) {
      /* ignore */
    }
  }

  function number(value) {
    return (value || 0).toLocaleString("en-IN", { maximumFractionDigits: 2 });
  }

  function rupees(value) {
    return "₹" + number(value);
  }

  function escapeHtml(value) {
    var holder = document.createElement("div");
    holder.appendChild(document.createTextNode(value == null ? "" : String(value)));
    return holder.innerHTML;
  }

  function setActive(buttons, attribute, value) {
    buttons.forEach(function (button) {
      button.classList.toggle("active", button.dataset[attribute] === value);
    });
  }

  // Figures that changed are highlighted, so an approval is visibly registered
  // rather than silently altering a number nobody was looking at. The classes
  // are applied in one batch to keep this to a single layout flush.
  function setFigure(node, text, quiet) {
    if (node.dataset.ready === "1" && node.textContent !== text) {
      node.classList.remove("usage-flash");
      pendingFlash.push(node);
    }
    node.textContent = text;
    node.classList.toggle("is-quiet", Boolean(quiet));
    node.dataset.ready = "1";
  }

  function flushFlashes() {
    if (!pendingFlash.length) {
      return;
    }
    void panel.offsetWidth;
    pendingFlash.forEach(function (node) {
      node.classList.add("usage-flash");
    });
    pendingFlash = [];
  }

  function requestParams() {
    var params = new URLSearchParams();
    if (state.preset === "filter") {
      if (filterScope.from || filterScope.to) {
        params.set("preset", "custom");
        if (filterScope.from) {
          params.set("from", filterScope.from);
        }
        if (filterScope.to) {
          params.set("to", filterScope.to);
        }
      } else {
        params.set("preset", "all_time");
      }
      if (filterScope.instrument) {
        params.set("instrument", filterScope.instrument);
      }
      if (filterScope.status) {
        params.set("status", filterScope.status);
      }
      return params;
    }

    params.set("preset", state.preset);
    if (state.preset === "custom") {
      if (state.from) {
        params.set("from", state.from);
      }
      if (state.to) {
        params.set("to", state.to);
      }
      if (!state.from && !state.to) {
        return null;
      }
    }
    return params;
  }

  function renderRows() {
    if (!latest) {
      return;
    }
    var rows = latest[state.group] || [];
    if (!rows.length) {
      el.usageRows.innerHTML =
        '<p class="usage-note text-center mb-0">No usage in this range.</p>';
      return;
    }
    var max = rows[0].hours || 1;
    el.usageRows.innerHTML = rows.map(function (row) {
      var children = row.children.map(function (child) {
        return '<div><span class="text-truncate mr-1">' + escapeHtml(child.key) + "</span>" +
          '<span class="text-nowrap"><b>' + number(child.hours) + " h</b> &middot; " +
          '<span class="usage-rowcost">' + rupees(child.cost) + "</span></span></div>";
      }).join("");
      return '<div class="usage-row">' +
        '<div class="d-flex justify-content-between align-items-baseline">' +
        '<span class="text-truncate"><span class="usage-caret">&#9656;</span>' +
        escapeHtml(row.key) + "</span>" +
        '<span class="text-nowrap font-weight-bold ml-1">' + number(row.hours) + " h</span></div>" +
        '<div class="usage-bar"><span style="width:' +
        Math.max(2, (row.hours / max) * 100) + '%"></span></div>' +
        '<div class="d-flex justify-content-between usage-caption">' +
        "<span>" + row.bookings + (row.bookings === 1 ? " booking" : " bookings") + "</span>" +
        '<span class="usage-rowcost">' + rupees(row.cost) + "</span></div>" +
        '<div class="usage-children d-none">' + children + "</div></div>";
    }).join("");
  }

  function renderSummary(data) {
    latest = data;
    var basis = data.basis;
    var totals = data.totals;
    var queue = data.queue;

    setFigure(el.usageHours, number(totals.hours), !totals.hours);
    setFigure(el.usageCost, number(totals.cost), !totals.cost);
    el.usageHoursCaption.textContent = basis.is_approved ? "hours used" : "hours booked";
    el.usageBasis.textContent = basis.label.toLowerCase();
    el.usageBookings.textContent = basis.counts_towards_usage
      ? totals.bookings + (totals.bookings === 1 ? " booking " : " bookings ") +
        (basis.is_approved ? "approved" : basis.label.toLowerCase())
      : basis.label + " bookings never count towards usage";

    var extra = "";
    if (data.range.instrument) {
      extra = escapeHtml(data.range.instrument);
    }
    if (state.preset === "filter") {
      extra += (extra ? " &middot; " : "") + "matching the filter above";
    }
    el.usageScope.innerHTML =
      escapeHtml(data.range.label) + (extra ? "<small>" + extra + "</small>" : "");

    setFigure(el.queueAwaiting, number(queue.awaiting_you.bookings), !queue.awaiting_you.bookings);
    setFigure(el.queueAwaitingHours, number(queue.awaiting_you.hours) + " h", !queue.awaiting_you.hours);
    setFigure(el.queueAwaitingCost, rupees(queue.awaiting_you.cost), !queue.awaiting_you.cost);
    setFigure(el.queueCleared, number(queue.cleared_by_you.bookings), !queue.cleared_by_you.bookings);
    setFigure(el.queueClearedHours, number(queue.cleared_by_you.hours) + " h", !queue.cleared_by_you.hours);
    setFigure(el.queueClearedCost, rupees(queue.cleared_by_you.cost), !queue.cleared_by_you.cost);

    var downstream = [];
    if (queue.with_department.bookings) {
      downstream.push(queue.with_department.bookings + " with department");
    }
    if (queue.with_lab.bookings) {
      downstream.push(queue.with_lab.bookings + " with lab assistant");
    }
    el.queueDownstream.textContent = downstream.join(" · ");

    renderRows();
    flushFlashes();
  }

  function load() {
    var params = requestParams();
    if (!params) {
      return;
    }
    if (!latest) {
      el.usageRows.innerHTML = '<p class="usage-note text-center mb-0">Loading&hellip;</p>';
    }
    // Presets can be clicked faster than the server answers; without this the
    // slowest response would win rather than the last one clicked.
    if (inFlight) {
      inFlight.abort();
    }
    inFlight = new AbortController();

    fetch(endpoint + "?" + params.toString(), {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
      signal: inFlight.signal
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Request failed");
        }
        return response.json();
      })
      .then(renderSummary)
      .catch(function (error) {
        if (error.name === "AbortError") {
          return;
        }
        el.usageRows.innerHTML =
          '<p class="text-danger usage-note text-center mb-0">Could not load usage.</p>';
      });
  }

  presetButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      if (state.preset === button.dataset.preset) {
        return;
      }
      state.preset = button.dataset.preset;
      setActive(presetButtons, "preset", state.preset);
      el.usageCustom.classList.toggle("d-none", state.preset !== "custom");
      persist();
      if (state.preset !== "custom") {
        load();
      }
    });
  });

  groupButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      state.group = button.dataset.group;
      setActive(groupButtons, "group", state.group);
      persist();
      renderRows();
    });
  });

  el.usageApply.addEventListener("click", function () {
    state.from = el.usageFrom.value;
    state.to = el.usageTo.value;
    persist();
    load();
  });

  el.usageRows.addEventListener("click", function (event) {
    var row = event.target.closest(".usage-row");
    if (!row) {
      return;
    }
    var children = row.querySelector(".usage-children");
    var caret = row.querySelector(".usage-caret");
    if (!children || !children.innerHTML.trim()) {
      return;
    }
    caret.innerHTML = children.classList.toggle("d-none") ? "&#9656;" : "&#9662;";
  });

  if (hasFilter) {
    el.usageFilterChip.classList.remove("d-none");
  }
  setActive(presetButtons, "preset", state.preset);
  setActive(groupButtons, "group", state.group);
  el.usageCustom.classList.toggle("d-none", state.preset !== "custom");
  el.usageFrom.value = state.from;
  el.usageTo.value = state.to;
  load();
})();
