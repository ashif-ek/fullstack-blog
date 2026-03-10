/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error("useToast must be used within a ToastProvider");
    }
    return context;
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback((message, type = 'info') => {
        const id = Date.now();
        setToasts((prev) => [...prev, { id, message, type }]);
        setTimeout(() => {
            setToasts((prev) => prev.filter((toast) => toast.id !== id));
        }, 3000); // Auto remove after 3s
    }, []);

    const removeToast = (id) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
    };

    return (
        <ToastContext.Provider value={{ addToast }}>
            {children}
            <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3">
                {toasts.map((toast) => (
                    <div
                        key={toast.id}
                        onClick={() => removeToast(toast.id)}
                        className={`
                            min-w-[300px] p-4 border border-x-[6px] shadow-lg cursor-pointer transform transition-all duration-300 animate-slide-in-right bg-white
                            ${toast.type === 'success' ? 'border-l-green-600 border-y-gray-200 border-r-gray-200' : ''}
                            ${toast.type === 'error' ? 'border-l-red-600 border-y-gray-200 border-r-gray-200' : ''}
                            ${toast.type === 'info' ? 'border-l-blue-600 border-y-gray-200 border-r-gray-200' : ''}
                        `}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className={`font-bold text-xs uppercase tracking-widest mb-1 
                                     ${toast.type === 'success' ? 'text-green-700' : ''}
                                     ${toast.type === 'error' ? 'text-red-700' : ''}
                                     ${toast.type === 'info' ? 'text-blue-700' : ''}
                                `}>
                                    {toast.type}
                                </h4>
                                <p className="text-slate-800 font-sans text-sm">{toast.message}</p>
                            </div>
                            <span className="text-slate-400 text-xs hover:text-slate-600">✕</span>
                        </div>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};
