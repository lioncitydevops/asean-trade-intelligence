// ASEAN Trade, Energy & Supply Chain Intelligence Platform Logic

// API Base Resolution
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has("api")) {
  localStorage.setItem("maritime_api_base", urlParams.get("api"));
}
const API_BASE = (
  window.MARITIME_API_BASE ||
  localStorage.getItem("maritime_api_base") ||
  ""
).replace(/\/$/, "");

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

function getWsUrl() {
  if (API_BASE.startsWith("http://")) {
    return API_BASE.replace("http://", "ws://") + "/ws/telemetry";
  } else if (API_BASE.startsWith("https://")) {
    return API_BASE.replace("https://", "wss://") + "/ws/telemetry";
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host || "127.0.0.1:8000";
  return `${protocol}//${host}/ws/telemetry`;
}

let map;
let vesselMarkers = {};
let vesselTrailHistory = {};
let vesselTrailPolylines = {};
let geofenceLayers = [];
let densityCircles = [];

let showTrails = true;
let showDensity = true;
let showGeofences = true;

let chartEx1, chartEx2, chartEx3, chartEx4;
let wsClient = null;
let currentEngine = "chain";
let pollingTimer = null;

// ASEAN Map Presets
const CHOKEPOINTS = {
  asean: { center: [4.5, 107.0], zoom: 5 },
  malacca: { center: [2.5, 101.8], zoom: 7 },
  sunda: { center: [-6.0, 106.0], zoom: 7 },
  bintulu: { center: [3.5, 112.5], zoom: 6 },
  global: { center: [15.0, 75.0], zoom: 3 },
  hormuz: { center: [26.4, 56.4], zoom: 8 },
};

// Chokepoint Density Rings
const DENSITY_ZONES = [
  { name: "Strait of Malacca", center: [2.5, 101.8], radiusMeters: 85000, color: "#06B6D4" },
  { name: "Singapore Strait", center: [1.25, 103.8], radiusMeters: 35000, color: "#3B82F6" },
  { name: "Sunda Strait", center: [-5.9, 105.8], radiusMeters: 45000, color: "#F59E0B" },
  { name: "Lombok Strait", center: [-8.5, 115.8], radiusMeters: 55000, color: "#10B981" },
  { name: "South China Sea Corridor", center: [12.0, 113.0], radiusMeters: 140000, color: "#8B5CF6" },
  { name: "Fujairah STS Hub", center: [25.2, 56.5], radiusMeters: 45000, color: "#EF4444" },
];

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initToolbarControls();
  initEngineTabs();
  initExhibitTabs();
  initCharts();
  loadInitialTelemetry();
  loadGeofences();
  initReportModal();
  checkAIStatus();
  initWebSocket();
  initPollingFallback();
  startRealtimeClock();
});

let mapTileLayer = null;
let baseLayers = {};
let layerControl = null;

// Initialize Leaflet Map
function initMap() {
  map = L.map("map", {
    center: [4.5, 107.0],
    zoom: 5,
    minZoom: 2,
    maxZoom: 14,
  });

  const urlKey = urlParams.get("carto_key") || localStorage.getItem("CARTO_API_KEY") || "";

  // 1. ESRI World Dark Gray Canvas (Default: High precision, no API key required, zero watermarks)
  const esriBase = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
    attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16,
  });
  const esriRef = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", {
    attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16,
  });
  const esriDarkGroup = L.layerGroup([esriBase, esriRef]);

  // 2. CARTO Dark Matter (Enabled with API key)
  const cartoUrl = urlKey
    ? `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?key=${encodeURIComponent(urlKey)}`
    : "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
  const cartoDark = L.tileLayer(cartoUrl, {
    attribution: '&copy; CartoDB &copy; OpenStreetMap',
    maxZoom: 19,
    subdomains: "abcd",
  });

  // 3. OpenStreetMap Standard (Free global keyless)
  const osmStandard = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  });

  // Select active layer: use CARTO if key is explicitly provided, else ESRI Dark Canvas
  if (urlKey) {
    cartoDark.addTo(map);
    mapTileLayer = cartoDark;
  } else {
    esriDarkGroup.addTo(map);
    mapTileLayer = esriDarkGroup;
  }

  baseLayers = {
    "ESRI Dark Canvas (Recommended)": esriDarkGroup,
    "CARTO Dark Matter": cartoDark,
    "OpenStreetMap Standard": osmStandard,
  };

  layerControl = L.control.layers(baseLayers, null, { position: "topright" }).addTo(map);

  initDensityZones();
}

function initDensityZones() {
  DENSITY_ZONES.forEach(zone => {
    const circle = L.circle(zone.center, {
      color: zone.color,
      fillColor: zone.color,
      fillOpacity: 0.12,
      weight: 1.5,
      radius: zone.radiusMeters,
    }).addTo(map);

    circle.bindTooltip(`<b>${zone.name}</b><br/>Density Radar Active`, {
      permanent: false,
      direction: "top",
      className: "density-tooltip",
    });

    densityCircles.push(circle);
  });
}

function initToolbarControls() {
  // Preset buttons
  document.querySelectorAll("[data-preset]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-preset]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const key = btn.getAttribute("data-preset");
      if (CHOKEPOINTS[key]) {
        map.flyTo(CHOKEPOINTS[key].center, CHOKEPOINTS[key].zoom, { duration: 1.2 });
      }
    });
  });

  // Layer buttons
  const btnTrails = document.getElementById("btn-toggle-trails");
  if (btnTrails) {
    btnTrails.addEventListener("click", () => {
      showTrails = !showTrails;
      btnTrails.classList.toggle("toggle-on", showTrails);
      btnTrails.textContent = `Trails [${showTrails ? "ON" : "OFF"}]`;
      if (!showTrails) {
        Object.values(vesselTrailPolylines).forEach(p => map.removeLayer(p));
      }
    });
  }

  const btnDensity = document.getElementById("btn-toggle-density");
  if (btnDensity) {
    btnDensity.addEventListener("click", () => {
      showDensity = !showDensity;
      btnDensity.classList.toggle("toggle-on", showDensity);
      btnDensity.textContent = `Density [${showDensity ? "ON" : "OFF"}]`;
      densityCircles.forEach(c => {
        if (showDensity) map.addLayer(c); else map.removeLayer(c);
      });
    });
  }

  const btnGeofences = document.getElementById("btn-toggle-geofences");
  if (btnGeofences) {
    btnGeofences.addEventListener("click", () => {
      showGeofences = !showGeofences;
      btnGeofences.classList.toggle("toggle-on", showGeofences);
      btnGeofences.textContent = `Geofences [${showGeofences ? "ON" : "OFF"}]`;
      geofenceLayers.forEach(l => {
        if (showGeofences) map.addLayer(l); else map.removeLayer(l);
      });
    });
  }
}

// Engine Switcher Tabs
function initEngineTabs() {
  document.querySelectorAll("[data-engine]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-engine]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentEngine = btn.getAttribute("data-engine");
      updateEngineView(currentEngine);
    });
  });
}

function updateEngineView(engine) {
  const sectionCascade = document.getElementById("section-chain-cascade");
  if (sectionCascade) {
    sectionCascade.style.display = (engine === "chain") ? "block" : "none";
  }

  if (engine === "maritime") {
    map.flyTo([4.5, 107.0], 5, { duration: 1 });
  } else if (engine === "energy") {
    switchTab("tab-exhibit-1");
  } else if (engine === "risk") {
    switchTab("tab-exhibit-2");
  } else if (engine === "macro") {
    switchTab("tab-exhibit-3");
  } else if (engine === "carbon" || engine === "capital") {
    switchTab("tab-exhibit-4");
  }
}

// Exhibit Tabs
function initExhibitTabs() {
  document.querySelectorAll("[data-tab]").forEach(btn => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll("[data-tab]").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".chart-card").forEach(c => c.style.display = "none");

  const targetBtn = document.querySelector(`[data-tab="${tabId}"]`);
  if (targetBtn) targetBtn.classList.add("active");

  const targetCard = document.getElementById(tabId);
  if (targetCard) targetCard.style.display = "flex";
}

// Charts initialization with Chart.js
function initCharts() {
  fetch(apiUrl("/api/exhibits/data"))
    .then(r => r.json())
    .then(data => {
      renderExhibit1(data.exhibit_1 || []);
      renderExhibit2(data.exhibit_2 || []);
      renderExhibit3(data.exhibit_3 || []);
      renderExhibit4();
    })
    .catch(err => {
      console.warn("Using baseline fallback data for charts", err);
      renderExhibit1([]);
      renderExhibit2([]);
      renderExhibit3([]);
      renderExhibit4();
    });
}

function renderExhibit1(records) {
  const ctx = document.getElementById("chart-exhibit-1");
  if (!ctx) return;

  const labels = records.length ? records.map(r => r.date_str.substring(5)) : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"];
  const maData = records.length ? records.map(r => r.seven_day_ma) : [42, 44, 15, 18, 30, 48, 55, 62, 67, 68];
  const avgData = records.length ? records.map(r => r.historical_avg) : [48, 48, 48, 48, 48, 48, 48, 48, 48, 48];

  if (chartEx1) chartEx1.destroy();
  chartEx1 = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Singapore & Fujairah Presence (7d MA)",
          data: maData,
          borderColor: "#06B6D4",
          backgroundColor: "rgba(6, 182, 212, 0.1)",
          fill: true,
          tension: 0.3,
          borderWidth: 2,
        },
        {
          label: "5-Year Baseline Average",
          data: avgData,
          borderColor: "#64748B",
          borderDash: [5, 5],
          pointRadius: 0,
          borderWidth: 1.5,
        }
      ]
    },
    options: getChartOptions("Tanker Presence (Units)")
  });
}

function renderExhibit2(records) {
  const ctx = document.getElementById("chart-exhibit-2");
  if (!ctx) return;

  const labels = records.length ? records.map(r => r.date_str.substring(5)) : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"];
  const suezData = records.length ? records.map(r => r.suez_7d_ma) : [15, 16, 16, 17, 18, 19, 21, 22, 24, 25];
  const bemData = records.length ? records.map(r => r.bem_7d_ma) : [20, 21, 19, 18, 17, 16, 14, 12, 10, 11];

  if (chartEx2) chartEx2.destroy();
  chartEx2 = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Suez / Cape Diversion Inflow",
          data: suezData,
          borderColor: "#3B82F6",
          borderWidth: 2,
        },
        {
          label: "Bab El-Mandeb Direct Flow",
          data: bemData,
          borderColor: "#EF4444",
          borderWidth: 2,
        }
      ]
    },
    options: getChartOptions("Daily Transit Count")
  });
}

function renderExhibit3(records) {
  const ctx = document.getElementById("chart-exhibit-3");
  if (!ctx) return;

  const labels = records.length ? records.map(r => r.date_str.substring(5)) : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"];
  const amtvi = [100, 102, 104, 107, 109, 111, 112, 113, 114.2, 114.8];
  const india = records.length ? records.map(r => r.india_index) : [100, 100, 110, 122, 134, 138, 140, 141, 142.5, 143.0];
  const china = records.length ? records.map(r => r.china_index) : [100, 100, 85, 70, 60, 59, 60, 59, 59, 58.5];

  if (chartEx3) chartEx3.destroy();
  chartEx3 = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "AMTVI ASEAN Nowcast Index",
          data: amtvi,
          borderColor: "#10B981",
          borderWidth: 2.5,
        },
        {
          label: "India Import Index",
          data: india,
          borderColor: "#F59E0B",
          borderWidth: 2,
        },
        {
          label: "China Seaborne Index",
          data: china,
          borderColor: "#EF4444",
          borderWidth: 2,
        }
      ]
    },
    options: getChartOptions("Rebased Index (Feb 2026 = 100)")
  });
}

function renderExhibit4() {
  const ctx = document.getElementById("chart-exhibit-4");
  if (!ctx) return;

  const labels = ["Baseline", "Cape Reroute (+5d)", "Cape Reroute (+8d)", "Red Sea Diversion (+12.4d)"];
  const cashLockup = [1200, 2400, 3600, 4850];
  const co2Penalties = [0, 12.5, 22.0, 34.2];

  if (chartEx4) chartEx4.destroy();
  chartEx4 = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Transit Inventory Cash Lockup ($M)",
          data: cashLockup,
          backgroundColor: "rgba(225, 29, 72, 0.7)",
          borderColor: "#E11D48",
          borderWidth: 1,
          yAxisID: "y",
        },
        {
          label: "Scope 3 CO2 Emission Penalty (%)",
          data: co2Penalties,
          type: "line",
          borderColor: "#8B5CF6",
          backgroundColor: "transparent",
          borderWidth: 2.5,
          yAxisID: "y1",
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
        y: { type: "linear", position: "left", ticks: { color: "#94A3B8" }, grid: { color: "#1E293B" } },
        y1: { type: "linear", position: "right", ticks: { color: "#8B5CF6" }, grid: { drawOnChartArea: false } }
      },
      plugins: { legend: { labels: { color: "#F1F5F9" } } }
    }
  });
}

function getChartOptions(yTitle) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: "#F1F5F9", font: { family: "Inter", size: 11 } } },
    },
    scales: {
      x: { ticks: { color: "#94A3B8", font: { family: "JetBrains Mono", size: 10 } }, grid: { color: "#1E293B" } },
      y: { title: { display: true, text: yTitle, color: "#94A3B8" }, ticks: { color: "#94A3B8", font: { family: "JetBrains Mono", size: 10 } }, grid: { color: "#1E293B" } }
    }
  };
}

// Real-Time Telemetry Dispatcher - Updates all UI feeds
function handleRealtimeTelemetry(data) {
  if (!data) return;

  // 1. Vessels on Map & Table
  if (data.vessels) {
    updateVesselsOnMap(data.vessels);
    updateTables(data);
  }

  // 2. Top Market Ribbon Ticker
  if (data.market || data.engines) {
    updateMarketRibbon(data.market, data.engines);
  }

  // 3. KPI Cards
  if (data.metrics || data.engines) {
    updateKPICards(data.metrics, data.engines);
  }

  // 4. Chain of Intelligence Cascade Steps
  if (data.chain_cascade) {
    updateChainCascade(data.chain_cascade);
  }

  // 5. Dark Fleet Badge
  if (data.dark_fleet_events) {
    const darkBadge = document.getElementById("dark-count-badge");
    if (darkBadge) {
      darkBadge.textContent = `${data.dark_fleet_events.length} Dark Transits Tracked`;
    }
  }
}

// Update Top Market Ribbon Ticker in real time
function updateMarketRibbon(market, engines) {
  const brentEl = document.getElementById("ticker-brent");
  const tapisEl = document.getElementById("ticker-tapis");
  const gasoilEl = document.getElementById("ticker-gasoil");
  const amtviEl = document.getElementById("ticker-amtvi");
  const co2El = document.getElementById("ticker-co2");
  const cashEl = document.getElementById("ticker-cash");

  const eState = engines && engines.energy && engines.energy.state ? engines.energy.state : null;
  const mnState = engines && engines.macro_nowcast && engines.macro_nowcast.state ? engines.macro_nowcast.state : null;
  const cState = engines && engines.carbon && engines.carbon.state ? engines.carbon.state : null;
  const wcState = engines && engines.working_capital && engines.working_capital.state ? engines.working_capital.state : null;

  if (market && brentEl) {
    brentEl.textContent = `$${market.brent_prompt_price.toFixed(2)}`;
  }
  if (tapisEl) {
    const val = eState ? eState.tapis_asean_usd : (market ? market.brent_prompt_price + 3.7 : 108.20);
    tapisEl.textContent = `$${val.toFixed(2)}`;
  }
  if (gasoilEl) {
    const crack = eState ? eState.singapore_gasoil_crack_usd : 28.50;
    gasoilEl.textContent = `+$${crack.toFixed(2)}/bbl`;
  }
  if (amtviEl) {
    const idx = mnState ? mnState.asean_maritime_trade_volume_index : 114.2;
    const yoy = mnState ? mnState.amtvi_yoy_pct : 3.8;
    amtviEl.textContent = `${idx.toFixed(1)} (+${yoy.toFixed(1)}%)`;
  }
  if (co2El) {
    const co2 = cState ? (cState.daily_regional_freight_co2_tonnes / 1e3).toFixed(1) : "142.5";
    co2El.textContent = `${co2}k t/d`;
  }
  if (cashEl) {
    const cash = wcState ? (wcState.transit_inventory_cash_lockup_usd_millions / 1e3).toFixed(2) : "4.85";
    const ccc = wcState ? wcState.cash_conversion_cycle_expansion_days.toFixed(1) : "8.4";
    cashEl.textContent = `$${cash}B (+${ccc}d CCC)`;
  }
}

// Update KPI Cards in real time
function updateKPICards(metrics, engines) {
  const mIntel = engines && engines.maritime ? engines.maritime : null;
  const eState = engines && engines.energy && engines.energy.state ? engines.energy.state : null;
  const rState = engines && engines.supply_chain && engines.supply_chain.state ? engines.supply_chain.state : null;
  const wcState = engines && engines.working_capital && engines.working_capital.state ? engines.working_capital.state : null;

  // KPI 1: ASEAN Flow
  const kpi1Val = document.getElementById("kpi-1-val");
  const kpi1Sub = document.getElementById("kpi-1-sub");
  if (mIntel && kpi1Val && kpi1Sub) {
    const chk = mIntel.asean_chokepoints || {};
    const transits = (chk.malacca_strait_vessels || 18) + (chk.singapore_strait_vessels || 24);
    kpi1Val.textContent = `${transits} Transits/Day`;
    kpi1Sub.innerHTML = `Active Cargo: <span class="up">${mIntel.total_cargo_in_transit_mbbls}M bbls</span> | Malacca: ${chk.malacca_strait_vessels || 18} | SG: ${chk.singapore_strait_vessels || 24}`;
  }

  // KPI 2: Energy Crack Spread
  const kpi2Val = document.getElementById("kpi-2-val");
  const kpi2Sub = document.getElementById("kpi-2-sub");
  if (eState && kpi2Val && kpi2Sub) {
    kpi2Val.textContent = `+$${eState.singapore_gasoil_crack_usd}/bbl`;
    kpi2Sub.innerHTML = `Tapis Sweet: <span class="warn">$${eState.tapis_asean_usd}</span> | JKM LNG: $${eState.jkm_spot_lng_usd}`;
  }

  // KPI 3: Supply Chain Risk
  const kpi3Val = document.getElementById("kpi-3-val");
  const kpi3Sub = document.getElementById("kpi-3-sub");
  if (rState && kpi3Val && kpi3Sub) {
    kpi3Val.textContent = `${rState.malacca_bottleneck_risk_score} / 100`;
    kpi3Sub.innerHTML = `Cape Diversion: <span class="alert">+${rState.cape_diversion_delay_days} Days</span> | SG Dwell: ${rState.singapore_container_dwell_days}d`;
  }

  // KPI 4: Working Capital Lockup
  const kpi4Val = document.getElementById("kpi-4-val");
  const kpi4Sub = document.getElementById("kpi-4-sub");
  if (wcState && kpi4Val && kpi4Sub) {
    kpi4Val.textContent = `$${wcState.transit_inventory_cash_lockup_usd_millions.toLocaleString()} Million`;
    kpi4Sub.innerHTML = `CCC Expansion: <span class="alert">+${wcState.cash_conversion_cycle_expansion_days} Days</span> | SCF Gap: $${(wcState.scf_liquidity_gap_usd_millions / 1e3).toFixed(1)}B`;
  }
}

// Update Chain of Intelligence Cascade Steps in real time
function updateChainCascade(cascade) {
  if (!cascade || !cascade.steps) return;

  cascade.steps.forEach(step => {
    const num = step.step_number;
    const headEl = document.getElementById(`step-${num}-head`);
    const descEl = document.getElementById(`step-${num}-desc`);

    if (headEl && step.headline) headEl.textContent = step.headline;
    if (descEl && step.data_summary) descEl.textContent = step.data_summary;
  });
}

// Load Geofences
function loadGeofences() {
  fetch(apiUrl("/api/geofences"))
    .then(r => r.json())
    .then(data => {
      if (!data.geofences) return;
      geofenceLayers.forEach(l => map.removeLayer(l));
      geofenceLayers = [];

      data.geofences.forEach(g => {
        const polygon = L.polygon(g.polygon, {
          color: "#06B6D4",
          weight: 1.5,
          fillColor: "#06B6D4",
          fillOpacity: 0.1,
          dashArray: "4, 4"
        }).addTo(map);

        polygon.bindTooltip(`<b>${g.name}</b><br/>${g.description}`, { className: "density-tooltip" });
        geofenceLayers.push(polygon);
      });
    })
    .catch(err => console.warn("Could not load geofences", err));
}

// Load Initial Snapshot
function loadInitialTelemetry() {
  fetch(apiUrl("/api/vessels"))
    .then(r => r.json())
    .then(data => {
      handleRealtimeTelemetry(data);
    })
    .catch(err => console.warn("Failed loading live metrics", err));
}

// Map Vessels Update with Real-Time Trails
function updateVesselsOnMap(vessels) {
  const countLabel = document.getElementById("vessel-count-label");
  if (countLabel) countLabel.textContent = `Tracking ${vessels.length} Vessels (Live AIS)`;

  vessels.forEach(v => {
    const lat = v.latitude;
    const lon = v.longitude;
    const key = v.mmsi;

    let markerColor = "#06B6D4";
    if (v.vessel_type === "LNG Carrier") markerColor = "#10B981";
    if (v.vessel_type === "Container Ship") markerColor = "#3B82F6";
    if (v.vessel_type === "Bulk Carrier") markerColor = "#F59E0B";
    if (!v.is_transponder_on || v.status === "Dark / AIS Disabled") markerColor = "#EF4444";

    // Track trail history (last 5 positions)
    if (!vesselTrailHistory[key]) vesselTrailHistory[key] = [];
    vesselTrailHistory[key].push([lat, lon]);
    if (vesselTrailHistory[key].length > 5) vesselTrailHistory[key].shift();

    // Render trail if enabled
    if (showTrails && vesselTrailHistory[key].length > 1) {
      if (vesselTrailPolylines[key]) {
        vesselTrailPolylines[key].setLatLngs(vesselTrailHistory[key]);
      } else {
        vesselTrailPolylines[key] = L.polyline(vesselTrailHistory[key], {
          color: markerColor,
          weight: 2,
          opacity: 0.6,
        }).addTo(map);
      }
    }

    const svgIcon = L.divIcon({
      className: "vessel-div-icon",
      html: `<div style="width:12px;height:12px;border-radius:50%;background:${markerColor};box-shadow:0 0 8px ${markerColor};border:1px solid #FFF;"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    if (vesselMarkers[key]) {
      vesselMarkers[key].setLatLng([lat, lon]);
    } else {
      const marker = L.marker([lat, lon], { icon: svgIcon }).addTo(map);
      marker.bindPopup(`
        <div style="font-family: Inter, sans-serif; font-size: 11px;">
          <b>${v.vessel_name}</b> (${v.vessel_type})<br/>
          Destination: ${v.destination}<br/>
          Speed: ${v.speed_knots} knots<br/>
          Cargo: ${(v.dwt_tonnes * 7.33 / 1e3).toFixed(0)}k bbls eq.<br/>
          Status: <b>${v.status}</b>
        </div>
      `);
      vesselMarkers[key] = marker;
    }
  });
}

// Update Vessels Table
function updateTables(data) {
  const tbody = document.getElementById("vessels-table-body");
  if (!tbody || !data.vessels) return;

  tbody.innerHTML = "";
  data.vessels.slice(0, 10).forEach(v => {
    const tr = document.createElement("tr");
    const cargoMbbls = ((v.dwt_tonnes * 7.33) / 1e6).toFixed(2);
    tr.innerHTML = `
      <td><b>${v.vessel_name}</b></td>
      <td>${v.vessel_type}</td>
      <td>${cargoMbbls}M bbls</td>
      <td>${v.destination}</td>
      <td><span class="badge-tag ${v.is_transponder_on ? 'badge-live' : 'badge-dark'}">${v.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// WebSocket Real-Time Connection
function initWebSocket() {
  const wsUrl = getWsUrl();
  console.log("Connecting Real-Time Telemetry WebSocket:", wsUrl);

  try {
    wsClient = new WebSocket(wsUrl);

    wsClient.onopen = () => {
      const badgeText = document.getElementById("ws-status-text");
      const pulseDot = document.getElementById("ws-pulse-dot");
      if (badgeText) badgeText.textContent = "TELEMETRY LIVE (WS)";
      if (pulseDot) pulseDot.style.backgroundColor = "#10B981";
    };

    wsClient.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === "TELEMETRY_TICK" || msg.type === "TELEMETRY_SNAPSHOT") {
          handleRealtimeTelemetry(msg.data);
        }
      } catch (e) {
        console.error("Error parsing WS telemetry packet", e);
      }
    };

    wsClient.onclose = () => {
      const badgeText = document.getElementById("ws-status-text");
      const pulseDot = document.getElementById("ws-pulse-dot");
      if (badgeText) badgeText.textContent = "TELEMETRY LIVE (POLL)";
      if (pulseDot) pulseDot.style.backgroundColor = "#F59E0B";
      setTimeout(initWebSocket, 4000);
    };

    wsClient.onerror = () => {
      if (wsClient) wsClient.close();
    };
  } catch (e) {
    console.warn("WebSocket init failed, using HTTP polling", e);
  }
}

// Fallback Polling Loop ensuring 100% continuous real-time feeds even without WebSockets
function initPollingFallback() {
  setInterval(() => {
    if (!wsClient || wsClient.readyState !== WebSocket.OPEN) {
      fetch(apiUrl("/api/vessels"))
        .then(r => r.json())
        .then(data => {
          handleRealtimeTelemetry(data);
          const badgeText = document.getElementById("ws-status-text");
          if (badgeText) badgeText.textContent = "TELEMETRY LIVE (HTTP)";
        })
        .catch(() => {});
    }
  }, 3000);
}

// Real-Time Clock on UI & Modal
function startRealtimeClock() {
  const updateClock = () => {
    const now = new Date();
    const utcStr = now.toUTCString().replace("GMT", "UTC");
    const modalClock = document.getElementById("modal-realtime-timestamp");
    if (modalClock) modalClock.textContent = utcStr;
  };
  updateClock();
  setInterval(updateClock, 1000);
}

// AI Status Check & Report Modal
function checkAIStatus() {
  fetch(apiUrl("/api/ai-status"))
    .then(r => r.json())
    .then(data => {
      const badge = document.getElementById("ai-status-badge");
      if (badge) {
        if (data.ai_enabled) {
          badge.textContent = "GEMINI ACTIVE";
          badge.style.background = "rgba(16, 185, 129, 0.2)";
          badge.style.color = "#6EE7B7";
        } else {
          badge.textContent = "QUANT CASCADE ACTIVE";
          badge.style.background = "rgba(59, 130, 246, 0.2)";
          badge.style.color = "#93C5FD";
        }
      }
      if (data.carto_key && baseLayers["CARTO Dark Matter"] && !urlParams.get("carto_key")) {
        baseLayers["CARTO Dark Matter"].setUrl(`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?key=${encodeURIComponent(data.carto_key)}`);
      }
    }).catch(() => {});
}

function initReportModal() {
  const modal = document.getElementById("report-modal");
  const openBtn = document.getElementById("btn-open-report-modal");
  const closeBtn = document.getElementById("btn-close-modal");
  const cancelBtn = document.getElementById("btn-cancel-modal");
  const generateBtn = document.getElementById("btn-execute-generate");
  const directDownloadBtn = document.getElementById("btn-download-direct");

  document.querySelectorAll("[data-open-report], #btn-open-report-modal, #btn-open-report-modal-2").forEach(btn => {
    btn.addEventListener("click", () => modal.classList.add("show"));
  });
  if (closeBtn) closeBtn.addEventListener("click", () => modal.classList.remove("show"));
  if (cancelBtn) cancelBtn.addEventListener("click", () => modal.classList.remove("show"));

  if (directDownloadBtn) {
    directDownloadBtn.addEventListener("click", () => {
      window.open(apiUrl("/api/download-report"), "_blank");
    });
  }

  if (generateBtn) {
    generateBtn.addEventListener("click", () => {
      const model = document.getElementById("modal-model-select").value;
      const key = document.getElementById("modal-gemini-key").value;
      const progress = document.getElementById("generation-progress");
      const previewPanel = document.getElementById("report-preview-panel");

      if (progress) progress.style.display = "block";
      generateBtn.disabled = true;

      fetch(apiUrl("/api/generate-report"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gemini_api_key: key || null,
          model_name: model,
          force_ai: false
        })
      })
      .then(r => r.json())
      .then(res => {
        if (progress) progress.style.display = "none";
        generateBtn.disabled = false;

        // Render plain colours preview right in modal
        if (res.summary && previewPanel) {
          previewPanel.style.display = "block";
          const titleEl = document.getElementById("preview-report-title");
          const subEl = document.getElementById("preview-report-subtitle");
          const bodyEl = document.getElementById("preview-report-body");

          if (titleEl) titleEl.textContent = res.summary.title || "ASEAN TRADE & ENERGY INTELLIGENCE";
          if (subEl) subEl.textContent = `Generated Real-Time: ${res.as_of_date || new Date().toUTCString()}`;
          if (bodyEl && res.summary.executive_summary_paragraphs) {
            bodyEl.innerHTML = res.summary.executive_summary_paragraphs.map(p => `<p style="margin-bottom: 8px;">${p}</p>`).join("");
          }
        }

        // Open download in background tab
        window.open(apiUrl("/api/download-report"), "_blank");
      })
      .catch(err => {
        if (progress) progress.style.display = "none";
        generateBtn.disabled = false;
        alert("Report generation error: " + err.message);
      });
    });
  }
}
