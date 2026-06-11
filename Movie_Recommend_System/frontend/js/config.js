const API_CONFIG = {
  baseUrl: window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : `${window.location.protocol}//${window.location.hostname}:5000`,
};

function apiUrl(path) {
  return `${API_CONFIG.baseUrl}${path}`;
}

function tmdbUrl(endpoint, params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiUrl(`/api/tmdb/${endpoint}${query ? `?${query}` : ""}`);
}
