const form = document.querySelector("#analysis-form");
const formMessage = document.querySelector("#form-message");
const result = document.querySelector("#result");
const history = document.querySelector("#history");
const refreshButton = document.querySelector("#refreshButton");

const api = {
  analyze: "/api/applications/analyze",
  applications: "/api/applications",
};

const STATUSES = ["saved", "applied", "interview", "rejected", "offer"];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeScore(value) {
  const score = Number(value);
  if (Number.isNaN(score)) return 0;
  return Math.max(0, Math.min(100, Math.round(score)));
}

async function safeJson(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return null;
  }
  return response.json();
}

function pillList(items, missing = false) {
  if (!items || !items.length) {
    return "<p class='empty-state'>No keywords found.</p>";
  }

  return `<ul class="pill-list">${items
    .map(
      (item) =>
        `<li class="pill ${missing ? "missing" : ""}">${escapeHtml(item)}</li>`,
    )
    .join("")}</ul>`;
}

function renderResult(data) {
  const score = safeScore(data.fit_score);

  result.classList.remove("empty-state");
  result.innerHTML = `
    <h2>${escapeHtml(data.job_title)} at ${escapeHtml(data.company)}</h2>

    <div class="score-ring" style="--score: ${score}%">
      <div class="score-inner">${score}%</div>
    </div>

    <p><strong>Text similarity:</strong> ${safeScore(data.similarity_score)}%</p>
    <p><strong>Skill coverage:</strong> ${safeScore(data.skill_coverage)}%</p>

    <h3>Matched keywords</h3>
    ${pillList(data.matched_keywords)}

    <h3>Missing keywords</h3>
    ${pillList(data.missing_keywords, true)}

    <h3>Recommendations</h3>
    <ul class="recommendations">
      ${(data.recommendations || [])
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("")}
    </ul>

    <h3>Personal data processing consent</h3>
    <p class="outreach">${escapeHtml(data.outreach_message)}</p>
  `;
}

async function loadHistory() {
  history.innerHTML = "<p>Loading...</p>";

  try {
    const response = await fetch(api.applications);
    const applications = await safeJson(response);

    if (!response.ok || !applications) {
      history.innerHTML = "<p class='empty-state'>Could not load applications.</p>";
      return;
    }

    if (!applications.length) {
      history.innerHTML = "<p class='empty-state'>No saved applications yet.</p>";
      return;
    }

    history.innerHTML = applications
      .map((item) => {
        const id = Number(item.id);
        const score = safeScore(item.fit_score);
        const date = new Date(item.created_at).toLocaleDateString();

        return `
          <article class="history-item">
            <div class="history-item-header">
              <div>
                <h3>${escapeHtml(item.job_title)}</h3>
                <p>${escapeHtml(item.company)} · ${escapeHtml(date)}</p>
              </div>
              <strong>${score}%</strong>
            </div>

            <div class="status-row">
              <label>
                Status
                <select data-id="${id}">
                  ${STATUSES.map(
                    (status) =>
                      `<option value="${status}" ${
                        status === item.status ? "selected" : ""
                      }>${status}</option>`,
                  ).join("")}
                </select>
              </label>
            </div>
          </article>
        `;
      })
      .join("");

    document.querySelectorAll("select[data-id]").forEach((select) => {
      select.addEventListener("change", async (event) => {
        try {
          const id = Number(event.target.dataset.id);
          const newStatus = event.target.value;

          if (!STATUSES.includes(newStatus)) {
            return;
          }

          const response = await fetch(`${api.applications}/${id}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus }),
          });

          if (!response.ok) {
            alert("Could not update status.");
          }
        } catch {
          alert("Network error while updating status.");
        }
      });
    });
  } catch {
    history.innerHTML = "<p class='empty-state'>Network error.</p>";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "Analyzing...";

  const payload = {
    company: document.querySelector("#company").value.trim(),
    job_title: document.querySelector("#jobTitle").value.trim(),
    cv_text: document.querySelector("#cvText").value.trim(),
    job_description: document.querySelector("#jobDescription").value.trim(),
  };

  if (
    !payload.company ||
    !payload.job_title ||
    !payload.cv_text ||
    !payload.job_description
  ) {
    formMessage.textContent = "Please fill in all fields.";
    return;
  }

  try {
    const response = await fetch(api.analyze, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await safeJson(response);

    if (!response.ok || !data) {
      formMessage.textContent =
        "Something went wrong. Check if texts are long enough.";
      return;
    }

    renderResult(data);
    await loadHistory();
    formMessage.textContent = "Analysis saved.";
  } catch {
    formMessage.textContent = "Network error. Please try again.";
  }
});

refreshButton.addEventListener("click", loadHistory);

loadHistory();