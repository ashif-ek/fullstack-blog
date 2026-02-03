import { useState } from "react";
import api from "../api";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useToast } from "../context/ToastContext";

function ChangePassword() {
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const { addToast } = useToast();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (newPassword !== confirmPassword) {
            addToast("New passwords do not match.", "error");
            return;
        }

        setLoading(true);
        try {
            await api.put("/api/change-password/", {
                old_password: oldPassword,
                new_password: newPassword
            });
            addToast("Password changed successfully! Please log in again.", "success");
            navigate("/logout"); // Force logout to clear old tokens
        } catch (error) {
            const msg = error.response?.data?.old_password?.[0] || 
                        error.response?.data?.new_password?.[0] || 
                        error.readable_message || 
                        "Failed to change password.";
            addToast(msg, "error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="max-w-md mx-auto bg-white border border-gray-200 p-10 shadow-sm animate-fade-in-down">
                <h2 className="text-3xl font-serif font-bold mb-6 text-slate-900 tracking-tight">Change Password</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-6">
                        <label className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">Current Password</label>
                        <input
                            type="password"
                            value={oldPassword}
                            onChange={(e) => setOldPassword(e.target.value)}
                            className="bg-white border border-gray-300 w-full py-4 px-5 text-slate-900 leading-tight focus:outline-none focus:border-slate-900 focus:ring-0 transition font-sans rounded-none"
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">New Password</label>
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className="bg-white border border-gray-300 w-full py-4 px-5 text-slate-900 leading-tight focus:outline-none focus:border-slate-900 focus:ring-0 transition font-sans rounded-none"
                            required
                        />
                    </div>
                    <div className="mb-8">
                        <label className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">Confirm New Password</label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="bg-white border border-gray-300 w-full py-4 px-5 text-slate-900 leading-tight focus:outline-none focus:border-slate-900 focus:ring-0 transition font-sans rounded-none"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-slate-900 hover:bg-slate-700 text-white font-bold py-4 px-4 transition duration-300 font-sans uppercase tracking-widest text-xs rounded-none"
                    >
                        {loading ? "Updating..." : "Update Password"}
                    </button>
                    <div className="mt-6 text-center">
                         <Link to="/profile" className="text-slate-500 hover:text-slate-800 text-xs font-bold uppercase tracking-widest transition">
                            Cancel
                        </Link>
                    </div>
                </form>
            </div>
        </Layout>
    );
}

export default ChangePassword;
