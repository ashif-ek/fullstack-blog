import { Link, useNavigate } from "react-router-dom"
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants"
import Cookies from "js-cookie"
import { useState, useEffect } from "react"
import { profileService } from "../api"
import NotificationBell from "./interactions/NotificationBell"

function Navbar() {
    const [isLoggedIn, setIsLoggedIn] = useState(() => !!Cookies.get(ACCESS_TOKEN));
    const [profilePic, setProfilePic] = useState(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false); // Mobile menu state
    const navigate = useNavigate();

    const fetchProfilePic = async () => {
        try {
            const res = await profileService.getProfile();
            if (res.data.image) {
                setProfilePic(res.data.image);
            }
        } catch {
            // silent fail
        }
    }

    useEffect(() => {
        if (isLoggedIn) {
            fetchProfilePic();
        }
    }, [isLoggedIn]);

    const handleLogout = () => {
        Cookies.remove(ACCESS_TOKEN);
        Cookies.remove(REFRESH_TOKEN); // Also remove refresh token if possible, though constant not imported yet
        setIsLoggedIn(false);
        setProfilePic(null);
        navigate("/login");
        setIsMenuOpen(false);
    };

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    {/* Logo / Brand */}
                    <Link to="/" className="flex items-center py-4 px-2 group">
                        <span className="font-serif font-bold text-slate-900 text-xl tracking-tight group-hover:text-blue-900 transition duration-300">
                            Academic<span className="text-blue-700">Blog</span>
                        </span>
                    </Link>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center">
                         <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-slate-600 hover:text-slate-900 focus:outline-none p-2">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                {isMenuOpen ? (
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                ) : (
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                )}
                            </svg>
                        </button>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center space-x-6">
                        {isLoggedIn ? (
                            <>
                                <Link to="/" className="text-slate-600 hover:text-blue-900 font-sans uppercase tracking-widest text-xs font-bold transition">Research Feed</Link>
                                <Link to="/profile" className="flex items-center text-slate-600 hover:text-blue-900 font-sans uppercase tracking-widest text-xs font-bold transition">
                                    {profilePic && (
                                        <img src={profilePic} alt="Me" className="w-6 h-6 rounded-full object-cover mr-2 border border-gray-300" />
                                    )}
                                    Profile
                                </Link>
                                <NotificationBell />
                                <button onClick={handleLogout} className="text-slate-400 hover:text-red-700 font-sans uppercase tracking-widest text-xs font-bold transition">Log Out</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="text-slate-600 hover:text-blue-900 font-sans uppercase tracking-widest text-xs font-bold transition">Log In</Link>
                                <Link to="/register" className="px-5 py-2 text-white bg-slate-900 hover:bg-slate-700 rounded-none font-sans uppercase tracking-widest text-xs font-bold transition shadow-sm">Sign Up</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Menu Dropdown */}
            {isMenuOpen && (
                <div className="md:hidden border-t border-gray-100 bg-white animate-fade-in-down shadow-lg">
                    <div className="px-4 pt-2 pb-6 space-y-2">
                        {isLoggedIn ? (
                            <>
                                <div className="flex items-center py-4 border-b border-gray-100 mb-2">
                                     {profilePic ? (
                                        <img src={profilePic} alt="Me" className="w-10 h-10 rounded-full object-cover mr-3 border border-gray-300" />
                                    ) : (
                                        <div className="w-10 h-10 rounded-full bg-slate-200 mr-3 flex items-center justify-center font-serif font-bold text-slate-500">U</div>
                                    )}
                                    <div className="flex flex-col">
                                         <span className="text-sm font-bold text-slate-900">Signed In</span>
                                         <Link to="/profile" className="text-xs text-blue-700 font-sans font-bold uppercase tracking-widest mt-1" onClick={() => setIsMenuOpen(false)}>Manage Profile</Link>
                                    </div>
                                </div>

                                <Link to="/" className="block px-2 py-3 text-slate-700 hover:bg-slate-50 font-sans uppercase tracking-widest text-xs font-bold rounded" onClick={() => setIsMenuOpen(false)}>Research Feed</Link>
                                <button onClick={handleLogout} className="w-full text-left px-2 py-3 text-red-600 hover:bg-red-50 font-sans uppercase tracking-widest text-xs font-bold rounded">Log Out</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="block px-2 py-3 text-slate-700 hover:bg-slate-50 font-sans uppercase tracking-widest text-xs font-bold rounded" onClick={() => setIsMenuOpen(false)}>Log In</Link>
                                <Link to="/register" className="block px-2 py-3 text-slate-700 hover:bg-slate-50 font-sans uppercase tracking-widest text-xs font-bold rounded" onClick={() => setIsMenuOpen(false)}>Sign Up</Link>
                            </>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
}

export default Navbar;
