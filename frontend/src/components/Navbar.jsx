import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-4 md:px-8 py-4 flex justify-between items-center sticky top-0 z-50 shadow-sm">
      <div className="flex items-center gap-8">
        <div className="font-bold text-xl text-primary cursor-pointer" onClick={() => navigate('/dashboard')}>
          AI Quiz Generator
        </div>
        
        <div className="hidden md:flex gap-6 text-sm font-medium">
          <Link to="/dashboard" className="text-gray-600 hover:text-primary transition-colors">Home</Link>
          <a href="#learning" className="text-gray-600 hover:text-primary transition-colors">Learning</a>
          <a href="#quizzes" className="text-gray-600 hover:text-primary transition-colors">Quizzes</a>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm font-medium">
        <div className="hidden sm:flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
            U
          </div>
          <span className="text-gray-900">User</span>
        </div>
        <button 
          className="text-gray-500 hover:text-error transition-colors duration-200 bg-transparent border-none cursor-pointer font-medium text-sm px-3 py-1.5 rounded-md hover:bg-red-50"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
