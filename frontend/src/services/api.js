import axios from "axios";

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, ""),
  headers: { "Content-Type": "application/json", Accept: "application/json" },
  timeout: 10000,
});

export default api;
