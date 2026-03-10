import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
                    <div className="max-w-md w-full bg-white border border-gray-200 shadow-lg p-8 text-center">
                        <h2 className="text-2xl font-serif font-bold text-slate-900 mb-4">Something went wrong</h2>
                        <p className="text-slate-600 mb-8 font-sans">We encountered an unexpected error properly loading this page.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-6 text-xs uppercase tracking-widest transition duration-300 rounded-none"
                        >
                            Reload Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
