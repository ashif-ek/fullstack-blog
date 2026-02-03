import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import Layout from "../components/Layout";
import { useToast } from "../context/ToastContext";

function Profile() {
    const [profile, setProfile] = useState({ full_name: "", bio: "", institution: "" });
    const [email, setEmail] = useState("");
    const [image, setImage] = useState(null); // For new upload
    const [preview, setPreview] = useState(null); // For previewing upload
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    
    const { addToast } = useToast();

    useEffect(() => {
        getProfile();
    }, []);

    const getProfile = async () => {
        try {
            const res = await api.get("/api/profile/");
            setProfile(res.data);
            setEmail(res.data.email);
            setLoading(false);
        } catch (err) {
            addToast("Failed to retrieve profile credentials.", "error");
            setLoading(false);
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        setSaving(true);
        
        const formData = new FormData();
        formData.append("full_name", profile.full_name);
        formData.append("institution", profile.institution);
        formData.append("bio", profile.bio);
        if (image) {
            formData.append("image", image);
        }

        try {
            // Using PATCH for partial update
            const res = await api.patch("/api/profile/", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            setProfile(res.data); // Update state with response (which includes new image URL)
            setPreview(null);
            setImage(null);
            addToast("Profile updated successfully.", "success");
        } catch (err) {
            console.error(err);
            addToast("Failed to update profile.", "error");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <Layout><div className="text-center mt-20 text-slate-500 font-serif animate-pulse">Loading Credentials...</div></Layout>;

    return (
        <Layout>
            <div className="bg-white border border-gray-200 p-10 shadow-sm max-w-3xl mx-auto">
                <div className="flex flex-col md:flex-row items-center gap-8 mb-4 border-b-2 border-slate-900 pb-8">
                     {/* Photo Section */}
                    <div className="relative group">
                        <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white shadow-lg bg-gray-100 flex items-center justify-center">
                             {preview ? (
                                <img src={preview} alt="Preview" className="w-full h-full object-cover" />
                             ) : profile.image ? (
                                <img src={profile.image} alt="Profile" className="w-full h-full object-cover" />
                             ) : (
                                <div className="text-4xl font-bold text-slate-400 font-serif">
                                    {profile.full_name ? profile.full_name.charAt(0) : "U"}
                                </div>
                             )}
                        </div>
                        <label htmlFor="profile-upload" className="absolute bottom-0 right-0 bg-slate-900 text-white p-2 rounded-full cursor-pointer hover:bg-slate-700 transition shadow-md">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
                            </svg>
                        </label>
                        <input id="profile-upload" type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                    </div>

                    <div className="text-center md:text-left">
                         <h1 className="text-3xl font-serif font-bold text-slate-900">Researcher Profile</h1>
                         <p className="text-slate-500 font-sans text-xs uppercase tracking-widest font-bold mt-1">Manage Personal Information</p>
                    </div>
                </div>

                <form onSubmit={handleUpdate} className="space-y-8 mt-10">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-3 font-sans">Email (ReadOnly)</label>
                            <input
                                type="text"
                                value={email}
                                disabled
                                className="w-full bg-gray-100 border border-gray-300 px-4 py-3 text-slate-500 font-mono text-sm rounded-none"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold uppercase tracking-widest text-slate-900 mb-3 font-sans">Full Name</label>
                            <input
                                type="text"
                                value={profile.full_name}
                                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                                className="w-full bg-white border border-gray-300 px-4 py-3 text-slate-900 focus:outline-none focus:border-blue-900 transition font-serif rounded-none placeholder-gray-400"
                                placeholder="Dr. Jane Doe"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-slate-900 mb-3 font-sans">Institution / Affiliation</label>
                        <input
                            type="text"
                            value={profile.institution}
                            onChange={(e) => setProfile({ ...profile, institution: e.target.value })}
                            className="w-full bg-white border border-gray-300 px-4 py-3 text-slate-900 focus:outline-none focus:border-blue-900 transition font-serif rounded-none placeholder-gray-400"
                            placeholder="Department of Computer Science..."
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-slate-900 mb-3 font-sans">Bio / Research Interests</label>
                        <textarea
                            value={profile.bio}
                            onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                            className="w-full bg-white border border-gray-300 px-4 py-3 h-40 text-slate-900 focus:outline-none focus:border-blue-900 transition font-serif rounded-none placeholder-gray-400 resize-none leading-relaxed"
                            placeholder="Detail your primary research focus..."
                        ></textarea>
                    </div>

                    <div className="flex justify-end pt-6">
                        <button
                            type="submit"
                            disabled={saving}
                            className="bg-slate-900 hover:bg-slate-700 text-white font-sans font-bold py-3 px-8 uppercase tracking-widest text-xs rounded-none transition duration-300 shadow-sm"
                        >
                            {saving ? "Updating..." : "Update Credentials"}
                        </button>
                    </div>
                </form>
                <div className="mt-12 pt-10 border-t border-gray-100">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-lg font-serif font-bold text-slate-900">Security Settings</h2>
                            <p className="text-slate-500 font-sans text-xs mt-1">Update your password to keep your account secure.</p>
                        </div>
                        <Link 
                            to="/change-password" 
                            className="border-2 border-slate-100 hover:border-slate-900 text-slate-700 hover:text-slate-900 font-sans font-bold py-3 px-6 uppercase tracking-widest text-xs rounded-none transition duration-300"
                        >
                            Change Password
                        </Link>
                    </div>
                </div>
            </div>
        </Layout>
    );
}

export default Profile;
