(function (global) {
  "use strict";

  const root = global.MojiLiteWeather;
  const config = global.WeatherMapConfig;
  const weatherService = root.weatherService;
  const mapView = root.mapView;

  const state = {
    metric: "rain",
    autoTimer: null,
    lastDataset: null,
  };

  function $(selector) {
    return document.querySelector(selector);
  }

  function setBusy(isBusy) {
    document.body.classList.toggle("is-loading", isBusy);
    const refreshButton = $("#refreshButton");
    if (refreshButton) {
      refreshButton.disabled = isBusy;
    }
  }

  function setMessage(message, tone) {
    const box = $("#message");
    box.textContent = message || "";
    box.dataset.tone = tone || "neutral";
    box.hidden = !message;
  }

  function setStatus(text) {
    $("#statusText").textContent = text;
  }

  function setMetricButtons(metric) {
    document.querySelectorAll("[data-metric]").forEach((button) => {
      const active = button.dataset.metric === metric;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function updateStats(dataset, renderMs) {
    const values = dataset.data
      .map((item) => item.value)
      .filter((value) => value !== null && value !== undefined && Number.isFinite(Number(value)))
      .map(Number);
    const metricConfig = config.metrics[dataset.metric];
    const max = values.length ? Math.max.apply(null, values) : null;
    const min = values.length ? Math.min.apply(null, values) : null;

    $("#providerText").textContent = dataset.provider === "open-meteo" ? "Open-Meteo" : "缓存/基础地图";
    $("#updatedText").textContent = dataset.requestedAt ? mapView.formatDateTime(dataset.requestedAt) : "--";
    $("#renderText").textContent = `${Math.round(renderMs)} ms`;
    $("#coverageText").textContent = `${values.length}/${dataset.data.length}`;
    $("#extremeText").textContent =
      max === null || min === null
        ? "--"
        : `${min.toFixed(metricConfig.precision)} ~ ${max.toFixed(metricConfig.precision)} ${metricConfig.unit}`;
  }

  async function loadMetric(metric, options) {
    state.metric = metric;
    setMetricButtons(metric);
    setBusy(true);
    setMessage("", "neutral");
    setStatus(options && options.force ? "正在刷新实时数据..." : "正在加载数据...");

    try {
      const dataset = await weatherService.getWeatherDataset(metric, options);
      const renderMs = mapView.render(metric, dataset);
      state.lastDataset = dataset;
      updateStats(dataset, renderMs);

      if (dataset.error && !dataset.fromCache) {
        setMessage(`实时数据获取失败：${dataset.error}。已展示基础地图。`, "error");
      } else if (dataset.stale) {
        setMessage(`实时数据获取失败，已展示缓存数据。原因：${dataset.error || "缓存兜底"}`, "warn");
      } else if (dataset.fromCache) {
        setMessage("已使用本地缓存数据，减少重复 API 请求。", "ok");
      }

      setStatus(`${config.metrics[metric].label}图层已更新`);
    } catch (error) {
      setMessage(error.message || String(error), "error");
      setStatus("加载失败");
    } finally {
      setBusy(false);
    }
  }

  function updateAutoRefresh() {
    if (state.autoTimer) {
      global.clearInterval(state.autoTimer);
      state.autoTimer = null;
    }

    const select = $("#refreshInterval");
    const minutes = Number(select.value);
    if (minutes > 0) {
      state.autoTimer = global.setInterval(() => {
        loadMetric(state.metric, { force: true });
      }, minutes * 60 * 1000);
    }
  }

  function initEvents() {
    document.querySelectorAll("[data-metric]").forEach((button) => {
      button.addEventListener("click", () => loadMetric(button.dataset.metric, { force: false }));
    });

    $("#refreshButton").addEventListener("click", () => loadMetric(state.metric, { force: true }));
    $("#refreshInterval").addEventListener("change", updateAutoRefresh);
  }

  function validateGeo() {
    const validation = global.CHINA_GEO_VALIDATION || {};
    $("#geoText").textContent = `${validation.optimizedFeatureCount || "--"} 个省级要素`;
  }

  function init() {
    try {
      mapView.init($("#map"));
      validateGeo();
      initEvents();
      updateAutoRefresh();
      loadMetric(state.metric, { force: false });
    } catch (error) {
      setBusy(false);
      setMessage(error.message || String(error), "error");
      setStatus("初始化失败");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(window);
