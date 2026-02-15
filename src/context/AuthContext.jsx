import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    // Configure axios defaults
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            localStorage.setItem('token', token);
        } else {
            delete axios.defaults.headers.common['Authorization'];
            localStorage.removeItem('token');
        }
        setLoading(false);
    }, [token]);

    const login = async (email, password) => {
        try {
            const response = await axios.post('/api/user/login', { email, password });
            const { access_token, user_id } = response.data;
            setToken(access_token);
            setUser({ id: user_id, email }); // ideally backend would return more user info
            return { success: true };
        } catch (error) {
            console.error("Login error:", error);
            return {
                success: false,
                error: error.response?.data?.message || "Login failed"
            };
        }
    };

    const register = async (username, email, password) => {
        try {
            const response = await axios.post('/api/user/register', {
                username,
                email,
                password
            });
            return { success: true };
        } catch (error) {
            console.error("Registration error:", error);
            return {
                success: false,
                error: error.response?.data?.message || "Registration failed"
            };
        }
    };

    const logout = () => {
        setUser(null);
        setToken(null);
    };

    const value = {
        user,
        token,
        login,
        register,
        logout,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
