import React, { useState } from 'react';
import RegistrationForm from './RegistrationForm';
import LoginForm from './LoginForm';

const AuthPage = () => {
  // State to toggle between 'login' and 'register' view
  const [isLoginView, setIsLoginView] = useState(true);

  // NOTE: These handlers are placeholders. They will use Axios later.
  const handleLogin = (credentials) => {
    console.log('Attempting to Log In with:', credentials);
    // TODO: Implement API call to POST /api/auth/login
  };

  const handleRegister = (userData) => {
    console.log('Attempting to Register with:', userData);
    // TODO: Implement API call to POST /api/auth/register
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>{isLoginView ? 'Login to Sweet Shop' : 'Register for Sweet Shop'}</h2>
      
      {/* View Switcher Button */}
      <p style={{marginBottom: '20px'}}>
        {isLoginView ? 
          "Don't have an account? " : 
          "Already have an account? "
        }
        <button onClick={() => setIsLoginView(!isLoginView)}>
          {isLoginView ? 'Register' : 'Login'}
        </button>
      </p>

      {/* Conditional Rendering of Forms */}
      {isLoginView ? (
        <LoginForm onSubmit={handleLogin} />
      ) : (
        <RegistrationForm onSubmit={handleRegister} />
      )}
    </div>
  );
};

export default AuthPage;