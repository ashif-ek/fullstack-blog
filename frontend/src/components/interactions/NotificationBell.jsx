import React, { useState, useEffect, useRef } from "react";
import api from "../../api";
import { Link } from "react-router-dom";

const NotificationBell = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const fetchNotifications = async () => {
        try {
            const res = await api.get("/api/interactions/notifications/");
            setNotifications(res.data.results || res.data); // Handle both paginated and non-paginated
            setUnreadCount((res.data.results || res.data).filter(n => !n.is_read).length);
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    };

    useEffect(() => {
        fetchNotifications();
        // Polling every 60 seconds (Real-world: use WebSockets/SSE)
        const interval = setInterval(fetchNotifications, 60000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const markAsRead = async (id) => {
        try {
            await api.post(`/api/interactions/notifications/${id}/mark_as_read/`);
            fetchNotifications();
        } catch (err) {
            console.error("Failed to mark as read", err);
        }
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 text-slate-600 hover:text-blue-900 transition duration-300 focus:outline-none"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                </svg>
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                        {unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 shadow-xl rounded-lg overflow-hidden z-50">
                    <div className="p-4 border-b border-gray-100 flex justify-between items-center">
                        <h4 className="text-sm font-bold text-slate-900 uppercase tracking-widest">Notifications</h4>
                        <span className="text-[10px] text-slate-400 font-bold uppercase">{unreadCount} New</span>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                        {notifications.length > 0 ? (
                            notifications.map((n) => (
                                <div
                                    key={n.id}
                                    className={`p-4 border-b border-gray-50 hover:bg-slate-50 transition duration-200 cursor-pointer ${
                                        !n.is_read ? "bg-blue-50/30" : ""
                                    }`}
                                    onClick={() => markAsRead(n.id)}
                                >
                                    <div className="flex items-start space-x-3">
                                        <div className="flex-1">
                                            <p className="text-sm text-slate-800">
                                                <span className="font-bold">{n.actor?.email}</span> {n.verb}ed your post.
                                            </p>
                                            <p className="text-[10px] text-slate-400 mt-1 uppercase font-bold">
                                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                        {!n.is_read && (
                                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
                                        )}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="p-8 text-center text-slate-400 italic text-sm">
                                No notifications yet.
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationBell;
