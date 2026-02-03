import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import "./index.css"

// Simple Performance Logger
if (import.meta.env.DEV) {
    const startTime = performance.now();
    window.addEventListener("load", () => {
        const loadTime = performance.now() - startTime;
        console.log(`🚀 App Loaded in ${loadTime.toFixed(2)}ms`); // Logs total load time
    });
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
