import React from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center">
      <div className="font-bold text-xl text-gray-900">
        AI Quiz Generator
      </div>
      <div className="flex items-center gap-6 text-sm font-medium">
        <span className="text-gray-900">User</span>
        <button 
          className="text-gray-500 hover:text-error transition-colors duration-200 bg-transparent border-none cursor-pointer font-medium text-sm"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
