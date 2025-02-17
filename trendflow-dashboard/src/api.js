import axios from "axios";

// 🔹 기본 API 주소 설정 (FastAPI 서버 URL)
const api = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

export default api;
