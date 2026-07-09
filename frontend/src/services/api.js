import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const sendChatMessage = (sessionId, message) =>
  api.post("/chat", { session_id: sessionId, message }).then((res) => res.data);

export const fetchInteraction = (sessionId) =>
  api.get("/interaction", { params: { session_id: sessionId } }).then((res) => res.data);

export const saveInteraction = (sessionId) =>
  api.post("/interaction/save", null, { params: { session_id: sessionId } }).then((res) => res.data);

export const fetchHCPs = () => api.get("/hcps").then((res) => res.data);

export const fetchProducts = () => api.get("/products").then((res) => res.data);

export default api;
