import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import Cookies from "js-cookie";
import { authService } from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useState, useEffect } from "react";

function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(() => {
        const token = Cookies.get(ACCESS_TOKEN);
        if (!token) return false;
        try {
            const decoded = jwtDecode(token);
            const tokenExpiration = decoded.exp;
            const now = Date.now() / 1000;
            if (tokenExpiration < now) return null; // Needs refresh
            return true;
        } catch {
            return false;
        }
    });

    const refreshToken = async () => {
        const refresh = Cookies.get(REFRESH_TOKEN);
        if (!refresh) {
            setIsAuthorized(false);
            return;
        }
        try {
            const res = await authService.refreshToken(refresh);
            if (res.status === 200) {
                Cookies.set(ACCESS_TOKEN, res.data.access);
                setIsAuthorized(true);
            } else {
                setIsAuthorized(false);
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    };

    useEffect(() => {
        if (isAuthorized === null) {
            refreshToken();
        }
    }, [isAuthorized]);

    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
