import { useState, useEffect } from "react";
import Form from "../components/Form";
import { Link } from "react-router-dom";

const BENEFITS = [
    {
        text: "Register for access to publish papers, comment on findings, and participate in peer-review circles.",
        author: "Academic Blog Network",
        role: "Open Science Initiative"
    },
    {
        text: "Verify your credentials as a researcher to claim your citations, build reputation points, and gain credibility.",
        author: "Peer Review Board",
        role: "Verification Service"
    },
    {
        text: "Customize your research profile with bios, location data, and active publication summaries.",
        author: "User Experience Team",
        role: "Researcher Dashboard"
    }
];

function Register() {
    const [activeBenefit, setActiveBenefit] = useState(0);
    const [fadeState, setFadeState] = useState("opacity-100 translate-y-0");

    useEffect(() => {
        const interval = setInterval(() => {
            setFadeState("opacity-0 translate-y-4");
            setTimeout(() => {
                setActiveBenefit((prev) => (prev + 1) % BENEFITS.length);
                setFadeState("opacity-100 translate-y-0");
            }, 500); // matching transition duration
        }, 6000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen flex flex-col md:flex-row relative overflow-hidden bg-white text-zinc-900">
            {/* Background Grid Overlay */}
            <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                <div 
                    className="absolute inset-0 opacity-40 academic-grid-bg"
                ></div>
            </div>

            {/* Left Panel: Scientific Brand Showcase (Visible only on md+) */}
            <div className="hidden md:flex md:w-1/2 flex-col justify-between p-12 relative z-10 border-r border-zinc-200 bg-zinc-50">
                {/* Top Logo */}
                <div>
                    <Link to="/" className="inline-block group">
                        <span className="font-serif font-bold text-2xl tracking-tight text-zinc-900 group-hover:text-red-700 transition-colors duration-300">
                            Academic<span className="text-red-700">Blog</span>
                        </span>
                    </Link>
                </div>

                {/* Main Scientific Visual / Testimonial Carousel */}
                <div className="max-w-md my-auto space-y-10">
                    <div className="space-y-4">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-50 border border-red-200 rounded-none text-xs font-bold text-red-700 uppercase tracking-widest">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span>
                            Apply for Access
                        </span>
                        <h2 className="text-4xl font-serif font-bold tracking-tight text-zinc-900 leading-tight">
                            Join the next generation of academic sharing.
                        </h2>
                    </div>

                    {/* Interactive Citation Testimonial */}
                    <div className="relative p-6 rounded-none bg-white border border-zinc-200 border-l-4 border-l-red-700 shadow-sm min-h-[160px] flex flex-col justify-between">
                        <div className={`transition-all duration-500 transform ${fadeState} flex-grow`}>
                            <p className="text-zinc-700 italic font-serif leading-relaxed text-sm">
                                "{BENEFITS[activeBenefit].text}"
                            </p>
                        </div>
                        <div className={`mt-4 pt-4 border-t border-zinc-100 transition-all duration-500 transform ${fadeState}`}>
                            <p className="text-zinc-900 font-sans text-xs font-bold uppercase tracking-wider">
                                {BENEFITS[activeBenefit].author}
                            </p>
                            <p className="text-zinc-500 text-[11px] font-medium font-sans">
                                {BENEFITS[activeBenefit].role}
                            </p>
                        </div>
                    </div>

                    {/* Indicator dots for slides */}
                    <div className="flex gap-2 justify-start items-center">
                        {BENEFITS.map((_, idx) => (
                            <button
                                key={idx}
                                onClick={() => {
                                    setFadeState("opacity-0 translate-y-4");
                                    setTimeout(() => {
                                        setActiveBenefit(idx);
                                        setFadeState("opacity-100 translate-y-0");
                                    }, 400);
                                }}
                                className={`h-1 transition-all duration-300 rounded-none ${
                                    idx === activeBenefit ? "w-6 bg-red-700" : "w-2 bg-zinc-300 hover:bg-zinc-400"
                                }`}
                                aria-label={`Go to slide ${idx + 1}`}
                            />
                        ))}
                    </div>
                </div>

                {/* Bottom Footer Credits */}
                <div>
                    <p className="text-zinc-500 text-xs font-sans">
                        &copy; 2026 AcademicBlog. Built for global open science.
                    </p>
                </div>
            </div>

            {/* Right Panel: Auth Form */}
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center p-6 md:p-12 relative z-10 min-h-screen">
                {/* Mobile Header Logo */}
                <div className="md:hidden mb-8 text-center">
                    <Link to="/" className="inline-block">
                        <span className="font-serif font-bold text-3xl tracking-tight text-zinc-900">
                            Academic<span className="text-red-700">Blog</span>
                        </span>
                    </Link>
                </div>

                {/* Register Form component */}
                <Form method="register" />

                {/* Mobile Footer Links */}
                <div className="md:hidden mt-8 text-zinc-500 text-xs flex gap-4 font-sans justify-center">
                    <Link to="/privacy" className="hover:text-red-700 transition-colors">Privacy</Link>
                    <span>&bull;</span>
                    <Link to="/terms" className="hover:text-red-700 transition-colors">Terms</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
