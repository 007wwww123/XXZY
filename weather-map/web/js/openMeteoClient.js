(function (global) {
  "use strict";

  const root = (global.MojiLiteWeather = global.MojiLiteWeather || {});

  function buildForecastUrl(locations, config) {
    const url = new URL(config.api.endpoint);
    url.searchParams.set("latitude", locations.map((item) => item.latitude).join(","));
    url.searchParams.set("longitude", locations.map((item) => item.longitude).join(","));
    url.searchParams.set("current", config.api.currentVariables.join(","));
    url.searchParams.set("timezone", config.api.timezone);
    url.searchParams.set("forecast_days", "1");
    return url.toString();
  }

  async function fetchJson(url, timeoutMs) {
    const controller = new AbortController();
    const timer = global.setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        method: "GET",
        signal: controller.signal,
        headers: { Accept: "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Open-Meteo returned HTTP ${response.status}`);
      }

      return await response.json();
    } finally {
      global.clearTimeout(timer);
    }
  }

  async function fetchCurrentWeather(locations, config) {
    const requestedAt = new Date().toISOString();
    const requestUrl = buildForecastUrl(locations, config);
    const response = await fetchJson(requestUrl, config.api.timeoutMs);
    const responseList = Array.isArray(response) ? response : [response];

    if (responseList.length !== locations.length) {
      throw new Error(`Open-Meteo response count mismatch: expected ${locations.length}, got ${responseList.length}`);
    }

    return {
      provider: "open-meteo",
      requestedAt,
      requestUrl,
      locations,
      response: responseList,
    };
  }

  root.openMeteoClient = {
    buildForecastUrl,
    fetchCurrentWeather,
  };
})(window);
