function LoadingFallback() {
    return (
        <div className="min-h-screen bg-white font-sans text-slate-900">
            {/* Navbar Placeholder */}
            <div className="border-b border-gray-200 h-16 w-full bg-white sticky top-0 z-50"></div>
            
            <div className="container w-full md:max-w-4xl mx-auto pt-12 px-6 pb-20">
                {/* Header Skeleton */}
                <div className="flex justify-between items-center mb-12 border-b-2 border-gray-100 pb-6">
                    <div className="space-y-3">
                        <div className="h-8 bg-gray-200 rounded-none w-64 animate-pulse"></div>
                        <div className="h-4 bg-gray-100 rounded-none w-48 animate-pulse"></div>
                    </div>
                    <div className="h-10 bg-gray-200 rounded-none w-32 animate-pulse"></div>
                </div>

                {/* Posts Grid Skeleton */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="border border-gray-100 bg-white p-6 shadow-sm">
                            <div className="h-40 bg-gray-100 mb-6 animate-pulse w-full"></div>
                            <div className="h-6 bg-gray-200 rounded-none w-3/4 mb-4 animate-pulse"></div>
                            <div className="h-4 bg-gray-100 rounded-none w-1/2 mb-6 animate-pulse"></div>
                            <div className="space-y-2 mb-6">
                                <div className="h-3 bg-gray-100 rounded-none w-full animate-pulse"></div>
                                <div className="h-3 bg-gray-100 rounded-none w-full animate-pulse"></div>
                                <div className="h-3 bg-gray-100 rounded-none w-2/3 animate-pulse"></div>
                            </div>
                            <div className="flex justify-between pt-4 border-t border-gray-50">
                                <div className="h-4 bg-gray-200 rounded-none w-24 animate-pulse"></div>
                                <div className="h-4 bg-gray-200 rounded-none w-12 animate-pulse"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default LoadingFallback;
