import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../auth/authContext';

const API_BASE_URL = ''; // Uses proxy

const SweetShop = () => {
    const { userRole, token, logout } = useAuth();
    const [sweets, setSweets] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    // Admin Panel States (Seller only)
    const [newSweetName, setNewSweetName] = useState('');
    const [newSweetPrice, setNewSweetPrice] = useState('');
    const [newSweetQuantity, setNewSweetQuantity] = useState('');
    const [restockId, setRestockId] = useState('');
    const [restockQuantity, setRestockQuantity] = useState('');

    const isSeller = userRole === 'seller';

    // FIX: Wrapping fetchSweets in useCallback to stabilize the dependency array
    const fetchSweets = useCallback(async () => {
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/products?search=${searchTerm}`, {
                headers: {
                    'Authorization': `Bearer ${token}`, 
                    'Content-Type': 'application/json',
                },
            });

            if (response.status === 401) {
                setError("Session expired or unauthorized. Please log in again.");
                logout(); 
                return;
            }

            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || 'Failed to fetch sweets.');
                return;
            }

            setSweets(data);
        } catch (err) {
            setError('Could not connect to the API. Check the backend server.');
        }
    }, [token, searchTerm, logout]); // Dependencies for useCallback

    // FIX: Calling the correctly named function inside useEffect
    useEffect(() => {
        if (token) {
            fetchSweets(); // CORRECT: Plural name
        }
    }, [token, searchTerm, fetchSweets]); // CORRECT: dependency array now stable

    // --- Purchase Logic ---
    const handlePurchase = async (productId) => {
        setMessage(null);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/purchase/${productId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });
            // ... (rest of the purchase logic)
            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || 'Purchase failed.');
            } else {
                setMessage(`Purchased ${data.name}! New stock: ${data.quantity}`);
                fetchSweets(); // Refresh the list
            }
        } catch (err) {
            setError('Purchase failed: Network error.');
        }
    };

    // --- Admin: Restock Logic (Omitted for brevity, but contained in full file) ---
    const handleRestock = async (e) => {
        e.preventDefault();
        setMessage(null);
        setError(null);
        // ... (restock logic)
        if (!restockId || !restockQuantity) {
            setError("Must provide Product ID and Quantity for restock.");
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/restock/${restockId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', },
                body: JSON.stringify({ quantity: parseInt(restockQuantity) }),
            });
            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || 'Restock failed.');
            } else {
                setMessage(`Restocked ${data.name}. New quantity: ${data.quantity}`);
                setRestockId('');
                setRestockQuantity('');
                fetchSweets(); 
            }
        } catch (err) { setError('Restock failed: Network error.'); }
    };

    // --- Admin: Add New Sweet Logic (Omitted for brevity, but contained in full file) ---
    const handleAddSweet = async (e) => {
        e.preventDefault();
        setMessage(null);
        setError(null);
        // ... (add sweet logic)
        try {
            const response = await fetch(`${API_BASE_URL}/products`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', },
                body: JSON.stringify({ name: newSweetName, price: parseFloat(newSweetPrice), quantity: parseInt(newSweetQuantity), }),
            });
            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || 'Failed to add sweet.');
            } else {
                setMessage(`Sweet '${data.name}' added successfully!`);
                setNewSweetName(''); setNewSweetPrice(''); setNewSweetQuantity('');
                fetchSweets();
            }
        } catch (err) { setError('Failed to add sweet: Network error.'); }
    };

    // --- Render Component ---
    return (
        <div style={{ padding: '20px', maxWidth: '900px', margin: 'auto' }}>
            <h2>Welcome to the Sweet Shop, {userRole}!</h2>
            {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}
            {message && <p style={{ color: 'green', fontWeight: 'bold' }}>{message}</p>}
            
            {/* --- ADMIN PANEL --- */}
            {isSeller && (
                <div style={{ border: '2px solid #fff369d6', padding: '20px', margin: '20px 0', backgroundColor: '#fff0f5ae' }}>
                    <h3>Admin Panel 🍬</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        {/* Add New Sweet */}
                        <form onSubmit={handleAddSweet} style={{ display: 'flex', flexDirection: 'column', gap: '10px', borderRight: '1px solid #cccccc9f', paddingRight: '20px' }}>
                            <h4>Add New Sweet</h4>
                            <input type="text" placeholder="Name" value={newSweetName} onChange={(e) => setNewSweetName(e.target.value)} required />
                            <input type="number" placeholder="Price" step="0.01" value={newSweetPrice} onChange={(e) => setNewSweetPrice(e.target.value)} required />
                            <input type="number" placeholder="Quantity" value={newSweetQuantity} onChange={(e) => setNewSweetQuantity(e.target.value)} required />
                            <button type="submit">Add Sweet</button>
                        </form>
                        {/* Restock Sweet */}
                        <form onSubmit={handleRestock} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            <h4>Restock Sweet</h4>
                            <input type="number" placeholder="Product ID (from list below)" value={restockId} onChange={(e) => setRestockId(e.target.value)} required />
                            <input type="number" placeholder="Quantity to Add" value={restockQuantity} onChange={(e) => setRestockQuantity(e.target.value)} required />
                            <button type="submit">Restock</button>
                        </form>
                    </div>
                </div>
            )}
            
            {/* --- SEARCH BAR --- */}
            <div style={{ margin: '30px 0', display: 'flex', gap: '10px' }}>
                <input type="text" placeholder="Search sweets by name..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ flexGrow: 1, padding: '10px', border: '1px solid #ccc' }} />
                <button onClick={() => setSearchTerm('')}>Clear Search</button>
            </div>

            {/* --- SWEET LIST --- */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px' }}>
                {sweets.length === 0 && !error && <p>No sweets found. {isSeller ? 'Use the Admin Panel to add some!' : ''}</p>}
                {sweets.map((sweet) => (
                    <div key={sweet.id} style={{ border: '1px solid #ff6969e3', padding: '15px', borderRadius: '5px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                            {isSeller && <small>ID: {sweet.id}</small>}
                            <h4>{sweet.name}</h4>
                            <p>Price: ₹{sweet.price.toFixed(2)}</p>
                            <p style={{ color: sweet.quantity === 0 ? 'red' : 'green' }}>Stock: {sweet.quantity}</p>
                        </div>
                        <button
                            onClick={() => handlePurchase(sweet.id)}
                            disabled={sweet.quantity === 0}
                            style={{ padding: '10px', backgroundColor: sweet.quantity === 0 ? '#00516fa4' : '#00ff3caf', color: 'white', border: 'none', cursor: sweet.quantity === 0 ? 'not-allowed' : 'pointer', marginTop: '10px' }}
                        >
                            {sweet.quantity === 0 ? 'Out of Stock' : 'Buy One'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SweetShop;