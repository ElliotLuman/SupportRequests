const state = {
  requests: [],
  statusCounts: [],
  priorityCounts: [],
  loading: false,
  updatingIds: new Set(),
};

const rows = document.querySelector("#request-rows");
const pageStatus = document.querySelector("#page-status");
const requestStatus = document.querySelector("#request-status");
const totalCount = document.querySelector("#total-count");
const statusSummary = document.querySelector("#status-summary");
const prioritySummary = document.querySelector("#priority-summary");
const createForm = document.querySelector("#create-request-form");
const formStatus = document.querySelector("#form-status");
const formError = document.querySelector("#form-error");
const createButton = document.querySelector("#create-button");

const STATUS_OPTIONS = ["open", "blocked", "resolved"];
const PRIORITY_OPTIONS = ["low", "medium", "high", "critical"];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setPageMessage(message, isError = false) {
  pageStatus.textContent = message;
  pageStatus.classList.toggle("error", isError);
}

function setRequestMessage(message, isError = false) {
  requestStatus.textContent = message;
  requestStatus.classList.toggle("error", isError);
}

function setFormMessage(message, isError = false) {
  formStatus.textContent = message;
  formStatus.classList.toggle("error", isError);
}

function showFormError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function clearFormError() {
  formError.hidden = true;
  formError.textContent = "";
}

function validateCreatePayload(payload) {
  if (!payload.requester.trim()) {
    return "Requester cannot be blank.";
  }

  if (!payload.category.trim()) {
    return "Category cannot be blank.";
  }

  if (!payload.owner.trim()) {
    return "Owner cannot be blank.";
  }

  return null;
}

function renderSummaryRows(container, counts) {
  container.innerHTML = counts
    .map(
      (item) => `
        <div class="summary-row">
          <span>${escapeHtml(item.label)}</span>
          <strong>${item.count}</strong>
        </div>
      `,
    )
    .join("");
}

function renderSummaries() {
  totalCount.textContent = String(state.requests.length);
  renderSummaryRows(statusSummary, state.statusCounts);
  renderSummaryRows(prioritySummary, state.priorityCounts);
}

function buildSelectOptions(options, selected) {
  return options
    .map((option) => {
      const isSelected = option === selected ? " selected" : "";
      return `<option value="${escapeHtml(option)}"${isSelected}>${escapeHtml(option)}</option>`;
    })
    .join("");
}

function renderRequests() {
  if (!state.requests.length) {
    rows.innerHTML = '<tr><td colspan="8" class="empty-state">No support requests yet.</td></tr>';
    setRequestMessage("No requests found.");
    return;
  }

  rows.innerHTML = state.requests
    .map((request) => {
      const busy = state.updatingIds.has(request.id);
      const disabled = busy ? " disabled" : "";
      const buttonLabel = busy ? "Saving..." : "Save";

      return `
        <tr>
          <td><strong>#${request.id}</strong></td>
          <td>
            <strong>${escapeHtml(request.requester)}</strong>
            <span class="notes">${escapeHtml(request.created_at)}</span>
          </td>
          <td>${escapeHtml(request.category)}</td>
          <td>${escapeHtml(request.priority)}</td>
          <td>${escapeHtml(request.status)}</td>
          <td>${escapeHtml(request.owner)}</td>
          <td class="notes">${escapeHtml(request.notes || "")}</td>
          <td>
            <form class="inline-update" data-request-id="${request.id}">
              <select name="status"${disabled}>
                ${buildSelectOptions(STATUS_OPTIONS, request.status)}
              </select>
              <input name="owner" value="${escapeHtml(request.owner)}"${disabled}>
              <button type="submit"${disabled}>${buttonLabel}</button>
            </form>
          </td>
        </tr>
      `;
    })
    .join("");

  setRequestMessage(`${state.requests.length} request(s) loaded.`);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.error || `Request failed with ${response.status}`;
    throw new Error(message);
  }

  return data;
}

async function loadDashboard() {
  if (state.loading) {
    return;
  }

  state.loading = true;
  setPageMessage("Refreshing dashboard...");
  setRequestMessage("Loading requests...");

  try {
    const [requestData, statusData, priorityData] = await Promise.all([
      requestJson("/api/requests"),
      requestJson("/api/reports/status"),
      requestJson("/api/reports/priority"),
    ]);

    state.requests = requestData.requests ?? [];
    state.statusCounts = statusData.counts ?? [];
    state.priorityCounts = priorityData.counts ?? [];
    renderRequests();
    renderSummaries();
    setPageMessage("Dashboard synced with the API.");
  } catch (error) {
    rows.innerHTML = '<tr><td colspan="8" class="empty-state">Requests could not be loaded.</td></tr>';
    statusSummary.innerHTML = "";
    prioritySummary.innerHTML = "";
    totalCount.textContent = "0";
    setRequestMessage(error.message, true);
    setPageMessage("Dashboard load failed.", true);
  } finally {
    state.loading = false;
  }
}

async function handleCreate(event) {
  event.preventDefault();
  clearFormError();
  createButton.disabled = true;
  setFormMessage("Creating request...");

  const formData = new FormData(createForm);
  const payload = Object.fromEntries(formData.entries());
  const validationError = validateCreatePayload(payload);

  if (validationError) {
    showFormError(validationError);
    setFormMessage("Creation failed.", true);
    createButton.disabled = false;
    return;
  }

  try {
    await requestJson("/api/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    createForm.reset();
    createForm.elements.priority.value = "medium";
    createForm.elements.status.value = "open";
    setFormMessage("Request created.");
    await loadDashboard();
  } catch (error) {
    showFormError(error.message);
    setFormMessage("Creation failed.", true);
  } finally {
    createButton.disabled = false;
  }
}

async function handleInlineUpdate(form) {
  const requestId = Number(form.dataset.requestId);
  const formData = new FormData(form);
  const payload = {
    status: formData.get("status"),
    owner: formData.get("owner"),
  };

  if (!String(payload.owner).trim()) {
    setPageMessage("Owner cannot be blank.", true);
    return;
  }

  state.updatingIds.add(requestId);
  renderRequests();
  setPageMessage(`Saving request #${requestId}...`);

  try {
    await requestJson(`/api/requests/${requestId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    setPageMessage(`Request #${requestId} updated.`);
    await loadDashboard();
  } catch (error) {
    setPageMessage(error.message, true);
    await loadDashboard();
  } finally {
    state.updatingIds.delete(requestId);
    renderRequests();
  }
}

createForm.addEventListener("submit", handleCreate);

rows.addEventListener("submit", async (event) => {
  const form = event.target.closest(".inline-update");
  if (!form) {
    return;
  }

  event.preventDefault();
  await handleInlineUpdate(form);
});

loadDashboard();
