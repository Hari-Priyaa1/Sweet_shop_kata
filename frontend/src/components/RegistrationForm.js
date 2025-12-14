// frontend/src/components/RegistrationForm.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE_URL = ''; 

const RegistrationForm = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('customer'); // Default role
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setMessage(null);

        // Data structure matching the schemas.UserCreate expected by /register
        const userData = {
            username: username,
            email: email,
            password: password,
            role: role 
        };

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (!response.ok) {
                // If backend returns an error (like user already exists)
                setError(data.detail || 'Registration failed.');
                return;
            }

            // SUCCESS
            setMessage('Registration successful! Redirecting to login...');
            
            setTimeout(() => {
                 navigate('/login');
            }, 1500);

        } catch (err) {
            console.error("Registration Network Error:", err);
            // This error typically only happens if the backend server is truly down.
            setError('Network error: Could not reach the API server.');
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: '50px auto' }}>
            <h2>Register for Sweet Shop</h2>
            <p>Already have an account? <Link to="/login">Login</Link></p>

            {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}
            {message && <p style={{ color: 'green', fontWeight: 'bold' }}>{message}</p>}
            
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                
                {/* Input for Username */}
                <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required style={{ padding: '10px', border: '1px solid #ccc' }} />
                
                {/* Input for Email */}
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ padding: '10px', border: '1px solid #ccc' }} />
                
                {/* Input for Password */}
                <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ padding: '10px', border: '1px solid #ccc' }} />
                
                {/* Role Selection */}
                <label style={{ textAlign: 'left', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    Register As:
                    <select value={role} onChange={(e) => setRole(e.target.value)} style={{ marginLeft: '10px', padding: '10px' }}>
                        <option value="customer">Customer</option>
                        <option value="seller">Seller (Admin)</option>
                    </select>
                </label>

                <button type="submit" style={{ padding: '10px', width: '100%', backgroundColor: 'green', color: 'white', border: 'none', cursor: 'pointer' }}>
                    Register
                </button>
            </form>
        </div>
    );
};

export default RegistrationForm;