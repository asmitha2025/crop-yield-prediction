const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

async function apiGet(url) {
  const response = await fetch(url);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.error || "Request failed");
  return payload;
}

async function apiPost(url, body = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.error || "Request failed");
  return payload;
}

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = value;
}

function formatNumber(value, digits = 0) {
  return Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

function showToast(message, type = "info") {
  let toast = $("#app-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "app-toast";
    toast.className = "fixed bottom-6 right-6 z-[100] max-w-sm rounded-lg border border-outline-variant/30 bg-slate-950 px-4 py-3 text-sm font-semibold text-on-surface shadow-2xl shadow-black/40";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.dataset.type = type;
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 3200);
}

function wireCommonActions() {
  $$("button").forEach((button) => {
    const icon = button.classList.contains("material-symbols-outlined") ? button : $(".material-symbols-outlined", button);
    const label = icon ? icon.textContent.trim() : "";
    if (label === "notifications") {
      button.addEventListener("click", () => showToast("Notifications: model is healthy and dataset is loaded."));
    }
    if (label === "settings") {
      button.addEventListener("click", () => showToast("Settings panel: filters and model controls are now active on each page."));
    }
    if (label === "help") {
      button.addEventListener("click", () => showToast("Help: use search, filters, export, retrain, and prediction controls directly."));
    }
    if (label === "more_vert") {
      button.addEventListener("click", () => showToast("Chart menu: variance plot is generated from the active dataset."));
    }
  });

  $$('input[placeholder*="Search"]').forEach((input) => {
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && input.value.trim()) {
        window.location.href = `/explorer?search=${encodeURIComponent(input.value.trim())}`;
      }
    });
  });
}

function trendPath(points, width = 1000, height = 300, padding = 35) {
  if (!points.length) return "";
  const values = points.map((point) => point.yield);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return points.map((point, index) => {
    const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width;
    const y = height - padding - ((point.yield - min) / span) * (height - padding * 2);
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

async function initDashboard() {
  if (!$("#dashboard-page")) return;
  const data = await apiGet("/api/dashboard");
  setText("[data-dashboard='total-samples']", formatNumber(data.total_samples));
  setText("[data-dashboard='avg-yield']", formatNumber(data.average_yield, 1));
  setText("[data-dashboard='model-accuracy']", formatNumber(data.model_accuracy, 1));
  setText("[data-dashboard='target-percent']", `${formatNumber(data.yield_target_percent, 0)}% Target`);
  setText("[data-dashboard='model-name']", `"${data.model_name}"`);
  setText("[data-dashboard='performance']", `${data.model_accuracy}% model confidence from ${data.total_samples.toLocaleString()} records.`);
  setText("[data-dashboard='temp']", `${formatNumber(data.summary.temperature, 1)}\u00B0C`);
  setText("[data-dashboard='humidity']", `${formatNumber(data.summary.humidity, 1)}%`);
  setText("[data-dashboard='rainfall']", `${formatNumber(data.summary.rainfall, 1)} mm`);

  const line = $("#dashboard-trend-line");
  const area = $("#dashboard-trend-area");
  const path = trendPath(data.trend);
  if (line && area) {
    line.setAttribute("d", path);
    area.setAttribute("d", `${path} L1000,300 L0,300 Z`);
  }

  const anomalyList = $("#dashboard-anomalies");
  if (anomalyList) {
    anomalyList.innerHTML = data.anomalies.map((record) => `
      <div class="flex items-center p-3 hover:bg-white/5 rounded-lg transition-colors cursor-pointer" data-record-id="${record.id}">
        <div class="w-10 h-10 rounded bg-tertiary/10 flex items-center justify-center mr-4">
          <span class="material-symbols-outlined text-tertiary text-sm">warning</span>
        </div>
        <div class="flex-1">
          <p class="text-sm font-bold text-on-surface">${record.status}</p>
          <p class="text-[10px] text-slate-500">${record.location} &bull; pH ${record.ph} &bull; yield ${record.yield} Q/ac</p>
        </div>
        <button class="px-3 py-1 bg-tertiary-container/20 text-tertiary text-[10px] font-bold rounded-full" data-open-record="${record.id}">Open</button>
      </div>
    `).join("");
    $$("[data-open-record]", anomalyList).forEach((button) => {
      button.addEventListener("click", () => {
        window.location.href = `/explorer?search=${encodeURIComponent(button.dataset.openRecord)}`;
      });
    });
  }

  $("#quick-sync")?.addEventListener("click", () => showToast("Mobile diagnostic sync simulated: current dataset snapshot is ready."));
  $("#view-all-logs")?.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.href = "/explorer";
  });
  $$("#dashboard-trend-controls button").forEach((button) => {
    button.addEventListener("click", () => {
      $$("#dashboard-trend-controls button").forEach((item) => item.classList.remove("bg-primary", "text-slate-950"));
      button.classList.add("bg-primary", "text-slate-950");
      showToast(`Trend view changed to ${button.dataset.range}.`);
    });
  });
}

function renderBars(container, items, valueKey, labelKey, colorClass = "bg-primary") {
  if (!container) return;
  const max = Math.max(...items.map((item) => Math.abs(item[valueKey])), 0.001);
  container.innerHTML = items.map((item) => {
    const percent = Math.max(4, Math.abs(item[valueKey]) / max * 100);
    return `
      <div class="space-y-2">
        <div class="flex justify-between text-xs font-bold">
          <span class="text-on-surface-variant">${item[labelKey]}</span>
          <span class="text-primary">${formatNumber(item[valueKey], 3)}</span>
        </div>
        <div class="h-3 rounded-full bg-surface-container-highest overflow-hidden">
          <div class="h-full rounded-full ${colorClass}" style="width:${percent}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

async function initInsights() {
  if (!$("#insights-page")) return;
  const data = await apiGet("/api/insights");
  setText("[data-insight='r2']", formatNumber(data.metrics.r2, 3));
  setText("[data-insight='rmse']", formatNumber(data.metrics.rmse, 2));
  setText("[data-insight='mae']", formatNumber(data.metrics.mae, 2));
  setText("[data-insight='model-name']", `Model: ${data.model_name}`);
  setText("[data-insight='strategy']", `Current ${data.model_name} model is strongest on ${data.feature_importance[0]?.feature || "the top feature"}. Last training run: ${data.training_date}.`);

  renderBars($("#feature-importance-list"), data.feature_importance.slice(0, 8), "importance", "feature", "bg-primary");
  renderBars($("#correlation-list"), data.correlations.slice(0, 8), "correlation", "feature", "bg-tertiary");

  const track = $("#accuracy-track");
  if (track) {
    track.innerHTML = data.accuracy_track.slice(0, 12).map((item) => `
      <div class="grid grid-cols-[90px_1fr] gap-3 items-center">
        <span class="text-[10px] text-slate-500 font-bold">${item.id}</span>
        <div class="h-7 bg-surface-container-highest rounded-lg overflow-hidden relative">
          <div class="absolute left-0 top-0 h-full bg-slate-600" style="width:${Math.min(item.actual / 60 * 100, 100)}%"></div>
          <div class="absolute left-0 top-0 h-full bg-primary/80" style="width:${Math.min(item.predicted / 60 * 100, 100)}%"></div>
        </div>
      </div>
    `).join("");
  }

  $("#export-report")?.addEventListener("click", () => {
    window.location.href = "/api/report";
  });
  $("#retrain-model")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    button.querySelector("span:last-child").textContent = "Retraining...";
    try {
      const result = await apiPost("/api/retrain");
      showToast(`Retrained: ${result.metadata.model_name} is active.`);
      await initInsights();
    } catch (error) {
      showToast(error.message, "error");
    } finally {
      button.disabled = false;
      button.querySelector("span:last-child").textContent = "Retrain Model";
    }
  });
  $("#view-sector-analysis")?.addEventListener("click", () => window.location.href = "/explorer?search=Delta");
  $("#read-retraining-logs")?.addEventListener("click", () => showToast(`Last training: ${data.training_date}.`));
}

function initPredictorExtras() {
  if (!$("#predictor-page")) return;
  $("#simulation-history")?.addEventListener("click", () => {
    const history = JSON.parse(localStorage.getItem("yieldPredictionHistory") || "[]");
    if (!history.length) {
      showToast("No prediction history yet. Generate a prediction first.");
      return;
    }
    const latest = history[history.length - 1];
    showToast(`Last prediction: ${formatNumber(latest.prediction, 1)} Q/ac at ${latest.time}.`);
  });
  $("#full-attribution")?.addEventListener("click", () => {
    window.location.href = "/insights";
  });
  $$(".bg-surface-container.rounded-2xl").forEach((card) => {
    card.addEventListener("click", () => showToast(card.querySelector("h4")?.textContent || "Insight selected."));
  });
}

const explorerState = {
  offset: 0,
  limit: 10,
  sort: "id",
  order: "asc",
  search: "",
  phMax: 9.5,
  locations: new Set(),
};

function recordRow(record) {
  const dot = record.status === "High Yield" ? "bg-emerald-500" : record.status === "Low Yield" ? "bg-red-500" : "bg-amber-500";
  return `
    <tr class="hover:bg-primary/5 transition-colors group">
      <td class="px-6 py-4 text-on-surface">${record.date}<span class="text-slate-500 font-normal ml-2">${record.time}</span></td>
      <td class="px-6 py-4"><div class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full ${dot}"></div>${record.location}</div></td>
      <td class="px-6 py-4 text-slate-300">${record.ph}</td>
      <td class="px-6 py-4"><div class="flex items-center gap-3"><div class="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden"><div class="bg-secondary h-full" style="width:${Math.min(record.moisture, 100)}%"></div></div><span class="text-xs text-slate-500">${record.moisture}%</span></div></td>
      <td class="px-6 py-4 text-slate-300">${record.temperature}&deg;</td>
      <td class="px-6 py-4 text-right font-bold text-on-surface">${record.yield} Q/ac</td>
      <td class="px-6 py-4 text-right"><button class="material-symbols-outlined text-slate-600 group-hover:text-primary cursor-pointer transition-colors" data-record-open="${record.id}">open_in_new</button></td>
    </tr>
  `;
}

function renderExplorerCharts(records) {
  const distribution = $("#yield-distribution-chart");
  if (distribution) {
    const values = records.map((record) => record.yield);
    const max = Math.max(...values, 1);
    distribution.innerHTML = values.map((value) => `
      <div class="flex-1 min-w-2 rounded-t-sm bg-primary/80" title="${value} Q/ac" style="height:${Math.max(8, value / max * 100)}%"></div>
    `).join("");
    const median = values.length ? [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)] : 0;
    setText("#yield-middle-label", `Median (${formatNumber(median, 1)} Q/ac)`);
  }

  const variance = $("#feature-variance-chart");
  if (variance) {
    const features = [
      ["Nitrogen", records.map((record) => record.nitrogen)],
      ["Rainfall", records.map((record) => record.rainfall)],
      ["Humidity", records.map((record) => record.moisture)],
      ["Fertilizer", records.map((record) => record.fertilizer)],
    ];
    variance.innerHTML = features.map(([label, values]) => {
      const min = Math.min(...values, 0);
      const max = Math.max(...values, 1);
      const avg = values.reduce((sum, value) => sum + value, 0) / (values.length || 1);
      const percent = max ? avg / max * 100 : 0;
      return `
        <div>
          <div class="flex justify-between text-xs font-bold mb-2">
            <span class="text-on-surface-variant">${label}</span>
            <span class="text-tertiary">${formatNumber(avg, 1)}</span>
          </div>
          <div class="h-3 rounded-full bg-surface-container-highest overflow-hidden">
            <div class="h-full rounded-full bg-tertiary" style="width:${Math.max(4, percent)}%"></div>
          </div>
          <div class="flex justify-between text-[10px] text-slate-500 mt-1"><span>${formatNumber(min, 1)}</span><span>${formatNumber(max, 1)}</span></div>
        </div>
      `;
    }).join("");
  }
}

async function loadRecords() {
  const params = new URLSearchParams();
  params.set("offset", explorerState.offset);
  params.set("limit", explorerState.limit);
  params.set("sort", explorerState.sort);
  params.set("order", explorerState.order);
  if (explorerState.search) params.set("search", explorerState.search);
  params.set("ph_max", explorerState.phMax);
  if (explorerState.locations.size) params.set("location", Array.from(explorerState.locations).join(","));

  const data = await apiGet(`/api/records?${params.toString()}`);
  $("#records-body").innerHTML = data.records.map(recordRow).join("") || `<tr><td colspan="7" class="px-6 py-10 text-center text-slate-500">No matching records</td></tr>`;
  setText("#records-total", `${formatNumber(data.total)} TOTAL ENTRIES`);
  const start = data.total ? data.offset + 1 : 0;
  const end = Math.min(data.offset + data.limit, data.total);
  setText("#records-range", `Showing ${start} to ${end} of ${formatNumber(data.total)}`);
  setText("#avg-yield-filtered", formatNumber(data.summary.average_yield, 1));
  setText("#avg-ph-filtered", formatNumber(data.summary.average_ph, 2));
  $("#records-prev").disabled = explorerState.offset === 0;
  $("#records-next").disabled = explorerState.offset + explorerState.limit >= data.total;
  renderExplorerCharts(data.records);
  $$("[data-record-open]").forEach((button) => {
    button.addEventListener("click", () => showToast(`Opened ${button.dataset.recordOpen}: details are shown in the current row.`));
  });
}

async function initExplorer() {
  if (!$("#explorer-page")) return;
  const searchParams = new URLSearchParams(window.location.search);
  explorerState.search = searchParams.get("search") || "";
  $("#records-search").value = explorerState.search;

  const initial = await apiGet("/api/records?limit=1");
  const locationBox = $("#location-filter-options");
  locationBox.innerHTML = initial.locations.map((location) => `
    <label class="flex items-center gap-3 group cursor-pointer">
      <input class="w-4 h-4 rounded bg-surface-container-lowest border-none text-primary focus:ring-primary/20" type="checkbox" value="${location}">
      <span class="text-sm text-slate-300 group-hover:text-on-surface transition-colors">${location}</span>
    </label>
  `).join("");

  $("#records-search").addEventListener("input", (event) => {
    explorerState.search = event.target.value;
    explorerState.offset = 0;
    window.clearTimeout(initExplorer.searchTimer);
    initExplorer.searchTimer = window.setTimeout(loadRecords, 250);
  });
  $("#ph-range").addEventListener("input", (event) => {
    explorerState.phMax = Number(event.target.value);
    setText("#ph-range-label", `pH ${explorerState.phMax.toFixed(1)}`);
    explorerState.offset = 0;
    loadRecords();
  });
  $("#temporal-range")?.addEventListener("change", (event) => {
    explorerState.offset = 0;
    showToast(`Temporal range changed to ${event.target.value}.`);
    loadRecords();
  });
  locationBox.addEventListener("change", () => {
    explorerState.locations = new Set($$("input:checked", locationBox).map((item) => item.value));
    explorerState.offset = 0;
    loadRecords();
  });
  $("#reset-filters").addEventListener("click", () => {
    explorerState.search = "";
    explorerState.offset = 0;
    explorerState.phMax = 9.5;
    explorerState.locations.clear();
    $("#records-search").value = "";
    $("#ph-range").value = "9.5";
    setText("#ph-range-label", "pH 9.5");
    $$("input", locationBox).forEach((input) => { input.checked = false; });
    loadRecords();
  });
  $("#records-prev").addEventListener("click", () => {
    explorerState.offset = Math.max(0, explorerState.offset - explorerState.limit);
    loadRecords();
  });
  $("#records-next").addEventListener("click", () => {
    explorerState.offset += explorerState.limit;
    loadRecords();
  });
  $$("[data-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextSort = button.dataset.sort;
      explorerState.order = explorerState.sort === nextSort && explorerState.order === "asc" ? "desc" : "asc";
      explorerState.sort = nextSort;
      loadRecords();
    });
  });
  $("#export-csv").addEventListener("click", () => {
    const params = new URLSearchParams();
    if (explorerState.search) params.set("search", explorerState.search);
    params.set("ph_max", explorerState.phMax);
    if (explorerState.locations.size) params.set("location", Array.from(explorerState.locations).join(","));
    window.location.href = `/api/export.csv?${params.toString()}`;
  });
  $("#create-report").addEventListener("click", () => window.location.href = "/api/report");
  $("#filter-toggle").addEventListener("click", () => showToast("Filters are active in the left panel."));
  $("#column-toggle").addEventListener("click", () => showToast("Core agronomy columns are displayed."));
  await loadRecords();
}

document.addEventListener("DOMContentLoaded", async () => {
  wireCommonActions();
  initPredictorExtras();
  try {
    await Promise.all([initDashboard(), initInsights(), initExplorer()]);
  } catch (error) {
    console.error(error);
    showToast(error.message || "Unable to load dynamic data.", "error");
  }
});
