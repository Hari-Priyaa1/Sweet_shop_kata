import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    // Check localStorage for persistent login state
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole'));
    const [isLoggedIn, setIsLoggedIn] = useState(!!token);

    useEffect(() => {
        setIsLoggedIn(!!token);
        if (!token) {
            setUserRole(null);
            localStorage.removeItem('userRole');
        }
    }, [token]);

    const login = (jwtToken, role) => {
        localStorage.setItem('token', jwtToken);
        localStorage.setItem('userRole', role);
        setToken(jwtToken);
        setUserRole(role);
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        setToken(null);
        setUserRole(null);
    };

    return (
        <AuthContext.Provider value={{ token, userRole, isLoggedIn, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);