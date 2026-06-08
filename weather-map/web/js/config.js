(function (global) {
  "use strict";

  const rainPieces = [
    { min: 16, label: "暴雨 >=16 mm/h", color: "#5b1a8e" },
    { min: 8, max: 15.99, label: "大雨 8-15.9", color: "#1f5fbf" },
    { min: 2.5, max: 7.99, label: "中雨 2.5-7.9", color: "#2f9bff" },
    { min: 0.1, max: 2.49, label: "小雨 0.1-2.4", color: "#a8d8ff" },
    { min: 0, max: 0.09, label: "无降水", color: "#edf3f7" },
  ];

  const tempPieces = [
    { min: 35, label: "高温 >=35°C", color: "#8c1d18" },
    { min: 30, max: 34.99, label: "炎热 30-34.9", color: "#d9482b" },
    { min: 20, max: 29.99, label: "温暖 20-29.9", color: "#f2a43a" },
    { min: 10, max: 19.99, label: "舒适 10-19.9", color: "#f6df72" },
    { min: 0, max: 9.99, label: "偏冷 0-9.9", color: "#7bc8a4" },
    { min: -10, max: -0.01, label: "寒冷 -10--0.1", color: "#44a7d8" },
    { min: -20, max: -10.01, label: "严寒 -20--10.1", color: "#276fbf" },
    { max: -20.01, label: "极寒 <-20", color: "#1f3b88" },
  ];

  global.WeatherMapConfig = {
    api: {
      endpoint: "https://api.open-meteo.com/v1/forecast",
      timezone: "Asia/Shanghai",
      currentVariables: ["temperature_2m", "precipitation", "rain"],
      timeoutMs: 12000,
    },
    cache: {
      ttlMs: 10 * 60 * 1000,
      rawPrefix: "mojiLite.raw.",
      datasetPrefix: "mojiLite.dataset.",
    },
    autoUpdateMs: 10 * 60 * 1000,
    metrics: {
      rain: {
        key: "rain",
        label: "降水",
        valueField: "precipitation",
        unit: "mm",
        precision: 1,
        pieces: rainPieces,
        title: "全国省会实时降水",
        subtitle: "以省会当前降水观测/分析值代表所在省级行政区",
      },
      temp: {
        key: "temp",
        label: "气温",
        valueField: "temperature",
        unit: "°C",
        precision: 1,
        pieces: tempPieces,
        title: "全国省会实时气温",
        subtitle: "以省会 2 米气温代表所在省级行政区",
      },
    },
  };
})(window);
