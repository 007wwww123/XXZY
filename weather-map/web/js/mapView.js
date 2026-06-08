(function (global) {
  "use strict";

  const root = (global.MojiLiteWeather = global.MojiLiteWeather || {});
  const config = global.WeatherMapConfig;

  let chart = null;
  let initialized = false;

  function formatValue(value, metricConfig) {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return "--";
    }
    return `${Number(value).toFixed(metricConfig.precision)} ${metricConfig.unit}`;
  }

  function formatDateTime(value) {
    if (!value) {
      return "--";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function init(container) {
    if (!global.echarts) {
      throw new Error("ECharts 未加载");
    }
    if (!global.CHINA_PROVINCE_GEOJSON) {
      throw new Error("中国省级 GeoJSON 未加载");
    }

    global.echarts.registerMap("china-provinces", global.CHINA_PROVINCE_GEOJSON);
    chart = global.echarts.init(container, null, { renderer: "canvas" });
    initialized = true;
    global.addEventListener("resize", () => chart && chart.resize());
    return chart;
  }

  function render(metric, dataset) {
    if (!initialized || !chart) {
      throw new Error("地图尚未初始化");
    }

    const metricConfig = config.metrics[metric];
    const renderStart = performance.now();

    chart.setOption(
      {
        backgroundColor: "transparent",
        title: {
          text: metricConfig.title,
          subtext: metricConfig.subtitle,
          left: 18,
          top: 14,
          textStyle: {
            color: "#1f2937",
            fontSize: 18,
            fontWeight: 700,
          },
          subtextStyle: {
            color: "#64748b",
            fontSize: 12,
          },
        },
        tooltip: {
          trigger: "item",
          borderWidth: 0,
          padding: 0,
          backgroundColor: "transparent",
          formatter(params) {
            const data = params.data || {};
            const metricValue = formatValue(data.value, metricConfig);
            const temp = formatValue(data.temperature, config.metrics.temp);
            const rain = formatValue(data.precipitation, config.metrics.rain);
            return [
              '<div class="map-tooltip">',
              `<div class="tooltip-title">${params.name || data.name || "--"}</div>`,
              `<div class="tooltip-row"><span>省会</span><strong>${data.capitalCity || "--"}</strong></div>`,
              `<div class="tooltip-row"><span>${metricConfig.label}</span><strong>${metricValue}</strong></div>`,
              `<div class="tooltip-row"><span>气温</span><strong>${temp}</strong></div>`,
              `<div class="tooltip-row"><span>降水</span><strong>${rain}</strong></div>`,
              `<div class="tooltip-row"><span>观测时间</span><strong>${formatDateTime(data.observedAt)}</strong></div>`,
              "</div>",
            ].join("");
          },
        },
        visualMap: {
          type: "piecewise",
          pieces: metricConfig.pieces,
          left: 18,
          bottom: 22,
          itemWidth: 18,
          itemHeight: 12,
          itemGap: 7,
          textStyle: {
            color: "#334155",
            fontSize: 11,
          },
          backgroundColor: "rgba(255,255,255,0.88)",
          borderColor: "#d9e2ec",
          borderWidth: 1,
          padding: [10, 12],
          outOfRange: {
            color: "#d8dee6",
          },
        },
        series: [
          {
            name: metricConfig.label,
            type: "map",
            map: "china-provinces",
            nameProperty: "fullname",
            roam: true,
            zoom: 1.12,
            scaleLimit: {
              min: 0.8,
              max: 4,
            },
            data: dataset.data,
            selectedMode: false,
            label: {
              show: false,
            },
            emphasis: {
              label: {
                show: true,
                color: "#0f172a",
                fontSize: 12,
                fontWeight: 700,
              },
              itemStyle: {
                areaColor: "#f8fafc",
                borderColor: "#0f172a",
                borderWidth: 1.1,
              },
            },
            itemStyle: {
              borderColor: "#94a3b8",
              borderWidth: 2,
              areaColor: "#d8dee6",
            },
          },
        ],
      },
      true
    );

    return performance.now() - renderStart;
  }

  root.mapView = {
    init,
    render,
    formatDateTime,
    formatValue,
  };
})(window);
