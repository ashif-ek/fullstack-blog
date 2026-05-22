import { useState } from "react";
import api, { authService } from "../api";
import { useNavigate, Link } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import Cookies from "js-cookie";
import { useToast } from "../context/ToastContext";
import "../styles/Form.css";

function Form({ method }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [isFocusedEmail, setIsFocusedEmail] = useState(false);
    const [isFocusedPassword, setIsFocusedPassword] = useState(false);

    const navigate = useNavigate();
    const { addToast } = useToast();

    const name = method === "login" ? "Login" : "Register";

    // Password criteria check
    const passwordCriteria = {
        length: password.length >= 8,
        hasUppercase: /[A-Z]/.test(password),
        hasNumber: /[0-9]/.test(password),
        hasSpecial: /[^A-Za-z0-9]/.test(password)
    };
    const strengthScore = Object.values(passwordCriteria).filter(Boolean).length;
    const hasPasswordInput = password.length > 0;

    const getStrengthColor = () => {
        if (strengthScore <= 1) return "bg-red-600";
        if (strengthScore === 2) return "bg-amber-500";
        if (strengthScore === 3) return "bg-emerald-500";
        return "bg-emerald-700";
    };

    const getStrengthText = () => {
        if (strengthScore <= 1) return "Weak";
        if (strengthScore === 2) return "Fair";
        if (strengthScore === 3) return "Good";
        return "Strong";
    };

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        try {
            const res = method === "login"
                ? await authService.login(email, password)
                : await authService.register(email, password);
            if (method === "login") {
                Cookies.set(ACCESS_TOKEN, res.data.access);
                Cookies.set(REFRESH_TOKEN, res.data.refresh);
                addToast("Welcome back! Authentication successful.", "success");
                navigate("/");
            } else {
                addToast("Registration successful! Please log in with your credentials.", "success");
                navigate("/login");
            }
        } catch (error) {
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                let errorMessage = "An error occurred.";
                
                if (typeof errorData === 'object') {
                     const messages = [];
                     for (const key in errorData) {
                         if (Array.isArray(errorData[key])) {
                             messages.push(`${key}: ${errorData[key].join(' ')}`);
                         } else {
                             messages.push(`${key}: ${errorData[key]}`);
                         }
                     }
                     errorMessage = messages.join('\n');
                }
                addToast(errorMessage, "error");
            } else {
                addToast(error.message || "An unexpected error occurred.", "error");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="auth-academic-card p-8 md:p-10 w-full max-w-md rounded-none transition-all duration-300">
            <div className="mb-8 text-center">
                <h1 className="text-3xl font-serif font-bold text-zinc-900 tracking-tight uppercase mb-2">
                    {name}
                </h1>
                <p className="text-zinc-500 text-xs font-sans tracking-wider uppercase">
                    {method === "login" 
                        ? "Enter your academic credentials" 
                        : "Apply for research portal access"}
                </p>
            </div>

            {/* Email Field */}
            <div className="mb-6 relative">
                <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200 ${isFocusedEmail ? "text-red-700" : "text-zinc-400"}`}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                    </svg>
                </div>
                <input
                    className="w-full bg-white border border-zinc-300 pl-12 pr-4 py-3.5 text-zinc-900 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700/20 transition-all rounded-none placeholder-transparent text-sm peer floating-label-input"
                    type="email"
                    id="auth-email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => setIsFocusedEmail(true)}
                    onBlur={() => setIsFocusedEmail(false)}
                    placeholder="Email"
                    required
                />
                <label 
                    htmlFor="auth-email"
                    className="absolute left-12 top-1/2 -translate-y-1/2 text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2 font-sans pointer-events-none transition-all duration-200 origin-left"
                >
                    Email Address
                </label>
            </div>

            {/* Password Field */}
            <div className="mb-6 relative">
                <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200 ${isFocusedPassword ? "text-red-700" : "text-zinc-400"}`}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                    </svg>
                </div>
                <input
                    className="w-full bg-white border border-zinc-300 pl-12 pr-12 py-3.5 text-zinc-900 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700/20 transition-all rounded-none placeholder-transparent text-sm peer floating-label-input"
                    type={showPassword ? "text" : "password"}
                    id="auth-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setIsFocusedPassword(true)}
                    onBlur={() => setIsFocusedPassword(false)}
                    placeholder="Password"
                    required
                />
                <label 
                    htmlFor="auth-password"
                    className="absolute left-12 top-1/2 -translate-y-1/2 text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2 font-sans pointer-events-none transition-all duration-200 origin-left"
                >
                    Password
                </label>
                <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 transition-colors focus:outline-none p-1"
                >
                    {showPassword ? (
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.815 7.815L21 21m-3.95-3.95l-2.5-2.5m0 0a3 3 0 11-4.243-4.243m4.242 4.242L9.88 9.88" />
                        </svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    )}
                </button>
            </div>

            {/* Password Strength Checklist (Register Mode) */}
            {method === "register" && hasPasswordInput && (
                <div className="mb-6 p-4 bg-zinc-50 border border-zinc-200 rounded-none animate-fade-in-down">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-zinc-500 font-sans font-semibold uppercase tracking-wider">Password Strength</span>
                        <span className={`text-xs font-bold font-sans uppercase ${
                            strengthScore <= 1 ? "text-red-700" :
                            strengthScore === 2 ? "text-amber-600" :
                            strengthScore === 3 ? "text-emerald-600" : "text-emerald-700"
                        }`}>{getStrengthText()}</span>
                    </div>
                    {/* Progress Bar */}
                    <div className="h-1.5 w-full bg-zinc-200 rounded-none overflow-hidden mb-3">
                        <div 
                            className={`h-full transition-all duration-300 ${getStrengthColor()}`}
                            style={{ width: `${(strengthScore / 4) * 100}%` }}
                        ></div>
                    </div>
                    {/* Requirements checklist */}
                    <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-zinc-500">
                        <div className="flex items-center gap-1.5 text-[11px]">
                            <svg className={`w-3.5 h-3.5 transition-colors ${passwordCriteria.length ? "text-emerald-600" : "text-zinc-300"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                            <span className={passwordCriteria.length ? "text-zinc-700" : "text-zinc-400"}>8+ characters</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px]">
                            <svg className={`w-3.5 h-3.5 transition-colors ${passwordCriteria.hasUppercase ? "text-emerald-600" : "text-zinc-300"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                            <span className={passwordCriteria.hasUppercase ? "text-zinc-700" : "text-zinc-400"}>1 Uppercase</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px]">
                            <svg className={`w-3.5 h-3.5 transition-colors ${passwordCriteria.hasNumber ? "text-emerald-600" : "text-zinc-300"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                            <span className={passwordCriteria.hasNumber ? "text-zinc-700" : "text-zinc-400"}>1 Number</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[11px]">
                            <svg className={`w-3.5 h-3.5 transition-colors ${passwordCriteria.hasSpecial ? "text-emerald-600" : "text-zinc-300"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                            <span className={passwordCriteria.hasSpecial ? "text-zinc-700" : "text-zinc-400"}>1 Special Char</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Submit Button */}
            <button 
                className="w-full relative overflow-hidden bg-red-700 hover:bg-red-800 text-white font-bold py-3.5 px-4 rounded-none transition duration-300 font-sans uppercase tracking-widest text-xs active:scale-[0.98] disabled:opacity-75 disabled:cursor-not-allowed cursor-pointer shadow-sm"
                type="submit"
                disabled={loading}
            >
                <span className="flex items-center justify-center gap-2">
                    {loading && (
                        <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    )}
                    {loading ? (method === "login" ? "Authenticating..." : "Creating Account...") : name}
                </span>
            </button>

            {/* Redirect Section */}
            <p className="mt-6 text-center text-zinc-600 text-sm">
                {method === "login" ? (
                    <>
                        New Researcher? <Link to="/register" className="text-red-700 hover:text-red-800 font-bold ml-1 transition border-b border-red-700/30 hover:border-red-800">Apply for Access</Link>
                    </>
                ) : (
                    <>
                        Already have credentials? <Link to="/login" className="text-red-700 hover:text-red-800 font-bold ml-1 transition border-b border-red-700/30 hover:border-red-800">Log In</Link>
                    </>
                )}
            </p>

            {/* Administrative Access (Login Page Only) */}
            {method === "login" && (
                <div className="mt-8 pt-6 border-t border-zinc-200 text-center">
                    <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-zinc-50 hover:bg-zinc-100 border border-zinc-200 hover:border-zinc-300 rounded-none text-xs font-sans text-zinc-600 hover:text-red-700 transition-all uppercase tracking-wider">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3.5 h-3.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                        </svg>
                        Administrative Gate
                    </a>
                </div>
            )}
        </form>
    );
}

export default Form;
