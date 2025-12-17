import { Link, useNavigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";

function Navbar() {
    const navigate = useNavigate();
    const isLoggedIn = localStorage.getItem(ACCESS_TOKEN);

    const handleLogout = () => {
        navigate("/logout");
    };

    return (
        <nav className="bg-white shadow-lg">
            <div className="max-w-6xl mx-auto px-4">
                <div className="flex justify-between">
                    {/* Logo / Brand */}
                    <div className="flex space-x-7">
                        <div>
                            <Link to="/" className="flex items-center py-4 px-2">
                                <span className="font-semibold text-gray-500 text-lg hover:text-blue-500 transition duration-300">
                                    MyBlog
                                </span>
                            </Link>
                        </div>
                    </div>

                    {/* Primary Navbar items */}
                    <div className="hidden md:flex items-center space-x-3">
                        {isLoggedIn ? (
                            <>
                                <Link to="/" className="py-2 px-2 font-medium text-gray-500 rounded hover:bg-blue-500 hover:text-white transition duration-300">Home</Link>
                                <button onClick={handleLogout} className="py-2 px-2 font-medium text-white bg-red-500 rounded hover:bg-red-400 transition duration-300">Log Out</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="py-2 px-2 font-medium text-gray-500 rounded hover:bg-green-500 hover:text-white transition duration-300">Log In</Link>
                                <Link to="/register" className="py-2 px-2 font-medium text-white bg-blue-500 rounded hover:bg-blue-400 transition duration-300">Sign Up</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
