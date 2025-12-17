import axios from "axios";
import { jwtDecode } from "jwt-decode"; // Incorrect import fix later if needed, default export usually valid for jwt-decode depending on version. Actually named export is safer in new versions.

export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
