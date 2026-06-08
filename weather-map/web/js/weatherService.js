(function (global) {
  "use strict";

  const root = (global.MojiLiteWeather = global.MojiLiteWeather || {});
  const config = global.WeatherMapConfig;
  const storage = root.storage;
  const client = root.openMeteoClient;

  function assertRuntimeData() {
    if (!Array.isArray(global.PROVINCE_CAPITALS) || global.PROVINCE_CAPITALS.length === 0) {
      throw new Error("省会坐标资源未加载");
    }
    if (!global.CHINA_PROVINCE_GEOJSON || !Array.isArray(global.CHINA_PROVINCE_GEOJSON.features)) {
      throw new Error("省级 GeoJSON 资源未加载");
    }
  }

  function datasetKey(metric) {
    return `${config.cache.datasetPrefix}${metric}`;
  }

  function rawKey(metric) {
    return `${config.cache.rawPrefix}${metric}`;
  }

  function toNumber(value) {
    if (value === null || value === undefined || value === "") {
      return null;
    }
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue : null;
  }

  function buildProvinceIndex() {
    const byCode = new Map();
    global.CHINA_PROVINCE_GEOJSON.features.forEach((feature) => {
      const props = feature.properties || {};
      byCode.set(String(props.code), {
        geoName: props.name,
        geoFullName: props.fullname,
        geoCenter: props.center,
      });
    });
    return byCode;
  }

  function normalizeRawResponse(rawPayload) {
    const provinceIndex = buildProvinceIndex();

    return rawPayload.locations.map((location, index) => {
      const raw = rawPayload.response[index] || {};
      const current = raw.current || {};
      const currentUnits = raw.current_units || {};
      const geo = provinceIndex.get(String(location.provinceCode)) || {};

      return {
        provinceName: location.provinceName,
        provinceShortName: location.provinceShortName || geo.geoName,
        provinceCode: location.provinceCode,
        region: location.region,
        capitalCity: location.capitalCity,
        latitude: location.latitude,
        longitude: location.longitude,
        geoName: geo.geoName,
        geoFullName: geo.geoFullName || location.provinceName,
        observedAt: current.time || rawPayload.requestedAt,
        temperature: toNumber(current.temperature_2m),
        temperatureUnit: currentUnits.temperature_2m || "°C",
        precipitation: toNumber(current.precipitation),
        precipitationUnit: currentUnits.precipitation || "mm",
        rain: toNumber(current.rain),
        rainUnit: currentUnits.rain || "mm",
        rawIndex: index,
      };
    });
  }

  function buildDataset(metric, rawPayload, options) {
    const metricConfig = config.metrics[metric];
    const observations = normalizeRawResponse(rawPayload);
    const data = observations.map((item) => ({
      name: item.geoFullName || item.provinceName,
      value: item[metricConfig.valueField],
      metric,
      unit: metricConfig.unit,
      provinceCode: item.provinceCode,
      provinceShortName: item.provinceShortName,
      region: item.region,
      capitalCity: item.capitalCity,
      latitude: item.latitude,
      longitude: item.longitude,
      observedAt: item.observedAt,
      temperature: item.temperature,
      precipitation: item.precipitation,
      rain: item.rain,
      rawIndex: item.rawIndex,
    }));

    return {
      metric,
      provider: rawPayload.provider,
      requestedAt: rawPayload.requestedAt,
      savedAt: new Date().toISOString(),
      stale: Boolean(options && options.stale),
      fromCache: Boolean(options && options.fromCache),
      observations,
      data,
    };
  }

  function buildEmptyDataset(metric, message) {
    const data = global.PROVINCE_CAPITALS.map((item) => ({
      name: item.provinceName,
      value: null,
      metric,
      unit: config.metrics[metric].unit,
      provinceCode: item.provinceCode,
      provinceShortName: item.provinceShortName,
      region: item.region,
      capitalCity: item.capitalCity,
      latitude: item.latitude,
      longitude: item.longitude,
    }));

    return {
      metric,
      provider: "none",
      requestedAt: null,
      savedAt: new Date().toISOString(),
      stale: true,
      fromCache: false,
      error: message,
      observations: [],
      data,
    };
  }

  async function getWeatherDataset(metric, options) {
    assertRuntimeData();

    const force = Boolean(options && options.force);
    const cachedDataset = storage.readJson(datasetKey(metric));

    if (!force && storage.isFresh(cachedDataset, config.cache.ttlMs)) {
      return Object.assign({}, cachedDataset, { fromCache: true, stale: false });
    }

    try {
      const rawPayload = await client.fetchCurrentWeather(global.PROVINCE_CAPITALS, config);
      const dataset = buildDataset(metric, rawPayload, { fromCache: false, stale: false });
      storage.writeJson(rawKey(metric), {
        savedAt: dataset.savedAt,
        provider: rawPayload.provider,
        requestUrl: rawPayload.requestUrl,
        requestedAt: rawPayload.requestedAt,
        locations: rawPayload.locations,
        response: rawPayload.response,
      });
      storage.writeJson(datasetKey(metric), dataset);
      return dataset;
    } catch (error) {
      if (cachedDataset) {
        return Object.assign({}, cachedDataset, {
          fromCache: true,
          stale: true,
          error: error.message || String(error),
        });
      }
      return buildEmptyDataset(metric, error.message || String(error));
    }
  }

  root.weatherService = {
    getWeatherDataset,
    normalizeRawResponse,
  };
})(window);
