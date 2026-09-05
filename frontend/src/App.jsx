import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Learning from './pages/Learning';
import Quiz from './pages/Quiz';
import './styles/global.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/learning/:topicId" element={<Learning />} />
        <Route path="/quiz/:quizId" element={<Quiz />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
