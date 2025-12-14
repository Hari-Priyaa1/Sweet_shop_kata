import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import LoginForm from './components/LoginForm';       
import RegistrationForm from './components/RegistrationForm'; 
import SweetShop from './pages/SweetShop';          
import { AuthProvider, useAuth } from './auth/authContext';

// ------------------------------------------------------------------
// IMPORTANT: The "NavBar" definition below is used directly.
// We remove the conflicting 'import NavBar from ...' line.
// ------------------------------------------------------------------


// Simple component to protect routes that require login
const ProtectedRoute = ({ element: Element }) => {
    const { isLoggedIn } = useAuth();
    return isLoggedIn ? <Element /> : <Navigate to="/login" replace />;
};

// Component that handles the overall routing structure
const AppRoutes = () => {
    return (
        <>
            <NavBar />
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginForm />} />
                <Route path="/register" element={<RegistrationForm />} />
                
                {/* Protected Route: The SweetShop dashboard */}
                <Route path="/shop" element={<ProtectedRoute element={SweetShop} />} />
                
                {/* Default route redirects to /shop if logged in, otherwise /login */}
                <Route path="/" element={<Navigate to="/shop" replace />} />
            </Routes>
        </>
    );
};

// Simple Navigation Bar component (Defined here)
const NavBar = () => {
    const { isLoggedIn, userRole, logout } = useAuth();
    return (
        <div style={{ padding: '10px 20px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f4f4f4' }}>
            <h1 style={{ margin: 0, color: '#ff69b4' }}>Sweet Shop Kata</h1>
            <div style={{ display: 'flex', alignItems: 'center' }}>
                {isLoggedIn && <span style={{ marginRight: '20px' }}>Logged in as: **{userRole}**</span>}
                {isLoggedIn ? (
                    <button onClick={logout} style={{ padding: '8px 15px', backgroundColor: 'red', color: 'white', border: 'none', cursor: 'pointer' }}>Logout</button>
                ) : (
                    <Link to="/login" style={{ textDecoration: 'none', color: 'blue' }}>Login</Link>
                )}
            </div>
        </div>
    );
};


const App = () => {
    return (
        <AuthProvider>
            <Router>
               <AppRoutes />
            </Router>
        </AuthProvider>
    );
};

export default App;