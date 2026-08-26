/**
 * Accept and reject without a full page reload.
 *
 * Any portal that renders <form class="js-request-action"> in the requests
 * table gets this. The views answer JSON when asked over XHR and keep
 * redirecting otherwise, so with JavaScript off the same forms post normally.
 *
 * On success a "request-action" event is dispatched on document, which is how
 * the usage panel knows to refresh its figures without this file having to
 * know the panel exists.
 */
(function () {
  "use strict";

  var table = document.getElementById("requestsTable");
  if (!table) {
    return;
  }

  // The status the list is filtered to, if any. A request that still matches it
  // belongs on the page after the change and is updated where it sits.
  var statusFilter = table.dataset.filterStatus || "";

  // The form is inside the modal, but its own fields are not always inside the
  // form: a <form> in table context parses with its children detached, so this
  // looks the dismiss control up from the modal rather than from the form.
  function closeModal(form) {
    var modal = form.closest(".modal");
    if (!modal) {
      return;
    }
    if (window.jQuery && window.jQuery(modal).modal) {
      window.jQuery(modal).modal("hide");
      return;
    }
    var dismiss = modal.querySelector('[data-dismiss="modal"]');
    if (dismiss) {
      dismiss.click();
    }
  }

  function updateRow(row, data) {
    var status = row.querySelector(".js-request-status");
    if (status) {
      status.textContent = data.status_display;
    }
    // it has moved on, so it is nobody's to act on from here any more
    var cells = row.querySelectorAll(".js-request-actions");
    if (cells.length === 2) {
      cells[0].innerHTML =
        '<button type="button" class="btn btn-success" disabled>Accept</button>';
      cells[1].innerHTML =
        '<button type="button" class="btn btn-danger" disabled>Reject</button>';
    }
  }

  function notify(message, level) {
    var banner = document.getElementById("requestActionBanner");
    if (!banner) {
      return;
    }
    banner.className = "alert alert-" + level;
    banner.textContent = message;
    banner.classList.remove("d-none");
    window.setTimeout(function () {
      banner.classList.add("d-none");
    }, 4000);
  }

  // Delegated from document: the accept modal is a <div> inside a <tr>, which
  // the HTML parser hoists out of the table altogether.
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!form.classList.contains("js-request-action")) {
      return;
    }
    event.preventDefault();

    var row = document.getElementById("request-row-" + form.dataset.requestId);
    // form.elements covers controls the parser associated with this form even
    // when they did not end up nested inside it.
    var buttons = Array.prototype.slice.call(form.elements).filter(function (node) {
      return node.tagName === "BUTTON";
    });
    buttons.forEach(function (button) {
      button.disabled = true;
    });

    // The form body already carries csrfmiddlewaretoken, so no header needed.
    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin"
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || "Request failed");
          }
          return data;
        });
      })
      .then(function (data) {
        closeModal(form);
        if (row && statusFilter && statusFilter !== data.status) {
          // it no longer belongs in this list, so say where it went
          row.parentNode.removeChild(row);
          notify("Request #" + data.id + " " + data.action + ".", "success");
        } else if (row) {
          updateRow(row, data);
        }
        document.dispatchEvent(new CustomEvent("request-action", { detail: data }));
      })
      .catch(function (error) {
        buttons.forEach(function (button) {
          button.disabled = false;
        });
        notify(error.message || "Something went wrong.", "danger");
      });
  });
})();
