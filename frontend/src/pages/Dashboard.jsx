import React from 'react';
import Navbar from '../components/Navbar';
import { FileText, Edit3, BookOpen } from 'lucide-react';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Navbar />
      
      <main className="max-w-7xl w-full mx-auto p-8 flex-1">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to AI Quiz Generator</h1>
          <p className="text-gray-500 text-sm mt-2">Here's an overview of your learning journey.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <div className="bg-white border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <FileText size={24} className="text-primary" />
              Study Materials
            </h2>
            <p className="text-gray-500">Upload and manage your study documents.</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <Edit3 size={24} className="text-primary" />
              Generate Quiz
            </h2>
            <p className="text-gray-500">Create quizzes from your study material.</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <BookOpen size={24} className="text-primary" />
              Flashcards
            </h2>
            <p className="text-gray-500">Review important concepts using flashcards.</p>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-5 text-gray-900">Your Learning</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary mb-2">0</div>
              <div className="text-sm font-medium text-gray-500">Quizzes Taken</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary mb-2">0</div>
              <div className="text-sm font-medium text-gray-500">Questions Answered</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary mb-2">0%</div>
              <div className="text-sm font-medium text-gray-500">Average Score</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
