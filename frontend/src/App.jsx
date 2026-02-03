import ProtectedRoute from "./components/ProtectedRoute"
import React, { Suspense, lazy } from 'react';
import LoadingFallback from "./components/LoadingFallback";
import ErrorBoundary from "./components/ErrorBoundary";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";  
import Cookies from "js-cookie";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "./constants";  

import { ToastProvider } from "./context/ToastContext";
import { OurStory, Documentation, SubmissionGuidelines, PrivacyPolicy, TermsOfService, CookiePolicy } from "./pages/StaticPages";

const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Home = lazy(() => import("./pages/Home"));
const PostDetail = lazy(() => import("./pages/PostDetail"));
const Profile = lazy(() => import("./pages/Profile"));
const NotFound = lazy(() => import("./pages/NotFound"));

function Logout() {
    Cookies.remove(ACCESS_TOKEN)
    Cookies.remove(REFRESH_TOKEN)
    return <Navigate to="/login" />
}

function RegisterAndLogout() {
    Cookies.remove(ACCESS_TOKEN)
    Cookies.remove(REFRESH_TOKEN)
    return <Register />
}

const PageWrapper = ({ children }) => (
  <ErrorBoundary>
    <Suspense fallback={<LoadingFallback />}>
      {children}
    </Suspense>
  </ErrorBoundary>
);

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route
            path="/"
            element={
            <PageWrapper>
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            </PageWrapper>
          }
        />
        <Route
          path="/post/:id"
          element={
            <PageWrapper>
              <ProtectedRoute>
                <PostDetail />
              </ProtectedRoute>
            </PageWrapper>
          }
        />
        <Route
          path="/profile"
          element={
            <PageWrapper>
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            </PageWrapper>
          }
        />
        <Route path="/login" element={<PageWrapper><Login /></PageWrapper>} />
        <Route path="/logout" element={<PageWrapper><Logout /></PageWrapper>} />
        <Route path="/register" element={<PageWrapper><RegisterAndLogout /></PageWrapper>} />
        
        {/* Static Pages */}
        <Route path="/our-story" element={<PageWrapper><OurStory /></PageWrapper>} />
        <Route path="/documentation" element={<PageWrapper><Documentation /></PageWrapper>} />
        <Route path="/submission-guidelines" element={<PageWrapper><SubmissionGuidelines /></PageWrapper>} />
        <Route path="/privacy" element={<PageWrapper><PrivacyPolicy /></PageWrapper>} />
        <Route path="/terms" element={<PageWrapper><TermsOfService /></PageWrapper>} />
        <Route path="/cookies" element={<PageWrapper><CookiePolicy /></PageWrapper>} />

        <Route path="*" element={<PageWrapper><NotFound /></PageWrapper>} />
      </Routes>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
