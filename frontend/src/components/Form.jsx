import { useState } from "react";
import api from "../api";
import { useNavigate, Link } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Form.css"

function Form({ route, method }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        try {
            const res = await api.post(route, { email, password })
            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
                navigate("/")
            } else {
                navigate("/login")
            }
        } catch (error) {

            if (error.response) {
                alert(JSON.stringify(error.response.data));
            } else {
                alert(error);
            }

        } finally {
            setLoading(false)
        }
    };

    return (
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">{name}</h1>
            <div className="mb-4">
                <input
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    required
                />
            </div>
            <div className="mb-6">
                <input
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    required
                />
            </div>
            {loading && <div className="text-center mb-4 text-blue-500">Loading...</div>}
            <button 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200" 
                type="submit"
                disabled={loading}
            >
                {name}
            </button>
            <p className="mt-4 text-center text-gray-600">
                {method === "login" ? (
                    <>
                        Don't have an account? <Link to="/register" className="text-blue-500 hover:underline">Register</Link>
                    </>
                ) : (
                    <>
                        Already have an account? <Link to="/login" className="text-blue-500 hover:underline">Login</Link>
                    </>
                )}
            </p>
        </form>
    );
}

export default Form
