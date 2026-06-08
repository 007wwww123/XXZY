(function (global) {
  "use strict";

  const root = (global.MojiLiteWeather = global.MojiLiteWeather || {});

  function readJson(key) {
    try {
      const value = global.localStorage.getItem(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.warn("Local cache read failed:", error);
      return null;
    }
  }

  function writeJson(key, value) {
    try {
      global.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.warn("Local cache write failed:", error);
      return false;
    }
  }

  function remove(key) {
    try {
      global.localStorage.removeItem(key);
    } catch (error) {
      console.warn("Local cache remove failed:", error);
    }
  }

  function isFresh(entry, ttlMs) {
    if (!entry || !entry.savedAt) {
      return false;
    }
    return Date.now() - Date.parse(entry.savedAt) < ttlMs;
  }

  root.storage = {
    readJson,
    writeJson,
    remove,
    isFresh,
  };
})(window);
