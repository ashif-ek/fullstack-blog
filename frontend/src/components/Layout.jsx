import Navbar from "./Navbar";

function Layout({ children }) {
    return (
        <div className="min-h-screen bg-gray-100 font-sans leading-normal tracking-normal">
            <Navbar />
            <div className="container w-full md:max-w-3xl mx-auto pt-20 px-4">
                {children}
            </div>
        </div>
    );
}

export default Layout;
