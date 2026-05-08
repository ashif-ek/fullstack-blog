import axios from "axios";
import Cookies from "js-cookie";
import { v4 as uuidv4 } from 'uuid';

export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "/",
    timeout: 8000, // 8 seconds timeout
});

// Error Message Mapping
const ERROR_MESSAGES = {
    400: "Bad Request: Please check your input.",
    401: "Unauthorized: Please log in again.",
    403: "Forbidden: You do not have permission.",
    404: "Not Found: The requested resource was not found.",
    408: "Request Timeout: The server took too long to respond.",
    500: "Server Error: Something went wrong on our end.",
    502: "Bad Gateway: Invalid response from upstream server.",
    503: "Service Unavailable: Please try again later.",
    504: "Gateway Timeout: Upstream server timed out.",
};

api.interceptors.request.use(
    (config) => {
        const token = Cookies.get(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Automatically add an Idempotency-Key for write operations
        const writeMethods = ['post', 'put', 'patch', 'delete'];
        if (writeMethods.includes(config.method.toLowerCase())) {
            config.headers['Idempotency-Key'] = uuidv4();
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Retry Logic (GET only, max 2 retries)
        if (
            error.code === "ECONNABORTED" ||
            (error.response && error.response.status >= 500)
        ) {
            if (
                originalRequest.method === "get" &&
                !originalRequest._retryCount
            ) {
                originalRequest._retryCount = 0;
            }

            if (
                originalRequest.method === "get" &&
                originalRequest._retryCount < 2
            ) {
                originalRequest._retryCount += 1;
                console.warn(
                    `Retrying request... Attempt ${originalRequest._retryCount}`
                );
                return api(originalRequest);
            }
        }

        // Error Normalization & Mapping
        let message = "An unexpected error occurred.";
        if (error.response) {
            const status = error.response.status;
            message = ERROR_MESSAGES[status] || `Error ${status}: ${error.response.statusText}`;

            // Normalize error object
            error.readable_message = message;
        } else if (error.request) {
            message = "Network Error: No response received.";
            error.readable_message = message;
        } else {
            message = error.message;
            error.readable_message = message;
        }

        console.error("API Error:", message);
        return Promise.reject(error);
    }
);

export default api;
