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
        <div className="min-h-screen flex flex-col md:flex-row relative overflow-hidden bg-[#090d16] text-white">
            {/* Background Animations */}
            <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                {/* Radial Glowing Blobs */}
                <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] rounded-full bg-indigo-900/20 blur-[130px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-blue-900/15 blur-[130px] animate-pulse-slow" style={{ animationDelay: "-3s" }}></div>
                
                {/* Floating Orbs */}
                <div className="absolute top-[25%] right-[15%] w-[280px] h-[280px] rounded-full bg-indigo-950/20 blur-[100px] animate-float-slow-reverse"></div>
                <div className="absolute bottom-[25%] left-[10%] w-[320px] h-[320px] rounded-full bg-blue-950/25 blur-[100px] animate-float-slow"></div>
                
                {/* Scientific Grid Overlay */}
                <div 
                    className="absolute inset-0 opacity-15"
                    style={{
                        backgroundImage: "radial-gradient(rgba(255, 255, 255, 0.08) 1.5px, transparent 0)",
                        backgroundSize: "32px 32px"
                    }}
                ></div>
            </div>

            {/* Left Panel: Scientific Brand Showcase (Visible only on md+) */}
            <div className="hidden md:flex md:w-1/2 flex-col justify-between p-12 relative z-10 border-r border-slate-900/60 bg-slate-950/20 backdrop-blur-[2px]">
                {/* Top Logo */}
                <div>
                    <Link to="/" className="inline-block group">
                        <span className="font-serif font-bold text-2xl tracking-tight text-white group-hover:text-indigo-400 transition-colors duration-300">
                            Academic<span className="text-indigo-500">Blog</span>
                        </span>
                    </Link>
                </div>

                {/* Main Scientific Visual / Testimonial Carousel */}
                <div className="max-w-md my-auto space-y-10">
                    <div className="space-y-4">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-xs font-bold text-indigo-400 uppercase tracking-widest">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
                            Apply for Access
                        </span>
                        <h2 className="text-4xl font-serif font-bold tracking-tight text-white leading-tight">
                            Join the next generation of academic sharing.
                        </h2>
                    </div>

                    {/* Interactive Citation Testimonial */}
                    <div className="relative p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm shadow-xl min-h-[160px] flex flex-col justify-between">
                        <div className={`transition-all duration-500 transform ${fadeState} flex-grow`}>
                            <p className="text-slate-300 italic font-serif leading-relaxed text-sm">
                                "{BENEFITS[activeBenefit].text}"
                            </p>
                        </div>
                        <div className={`mt-4 pt-4 border-t border-slate-800/80 transition-all duration-500 transform ${fadeState}`}>
                            <p className="text-white font-sans text-xs font-bold uppercase tracking-wider">
                                {BENEFITS[activeBenefit].author}
                            </p>
                            <p className="text-slate-500 text-[11px] font-medium font-sans">
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
                                className={`h-1.5 rounded-full transition-all duration-300 ${
                                    idx === activeBenefit ? "w-6 bg-indigo-500" : "w-1.5 bg-slate-700 hover:bg-slate-600"
                                }`}
                                aria-label={`Go to slide ${idx + 1}`}
                            />
                        ))}
                    </div>
                </div>

                {/* Bottom Footer Credits */}
                <div>
                    <p className="text-slate-600 text-xs font-sans">
                        &copy; 2026 AcademicBlog. Built for global open science.
                    </p>
                </div>
            </div>

            {/* Right Panel: Auth Form */}
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center p-6 md:p-12 relative z-10 min-h-screen">
                {/* Mobile Header Logo */}
                <div className="md:hidden mb-8 text-center">
                    <Link to="/" className="inline-block">
                        <span className="font-serif font-bold text-3xl tracking-tight text-white">
                            Academic<span className="text-indigo-500">Blog</span>
                        </span>
                    </Link>
                </div>

                {/* Register Form component */}
                <Form method="register" />

                {/* Mobile Footer Links */}
                <div className="md:hidden mt-8 text-slate-500 text-xs flex gap-4 font-sans justify-center">
                    <Link to="/privacy" className="hover:text-indigo-400 transition-colors">Privacy</Link>
                    <span>&bull;</span>
                    <Link to="/terms" className="hover:text-indigo-400 transition-colors">Terms</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
