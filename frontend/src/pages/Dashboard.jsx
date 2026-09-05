import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import UploadCard from '../components/UploadCard';
import TopicCard from '../components/TopicCard';
import QuizCard from '../components/QuizCard';
import ProgressCard from '../components/ProgressCard';
import { getTopics, getQuizzes, getProgress, getActivity } from '../services/api';
import { CheckCircle, BookOpen, Edit3 } from 'lucide-react';

const Dashboard = () => {
  const [topics, setTopics] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [progress, setProgress] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const [t, q, p, a] = await Promise.all([
        getTopics(),
        getQuizzes(),
        getProgress(),
        getActivity()
      ]);
      // Initially, we might show empty topics until upload, but let's show mock topics to demonstrate
      // If we want to be strict, we start with empty topics and populate them onUploadSuccess.
      // For this demo, let's start with some topics anyway, or we can use onUploadSuccess to append them.
      // I'll leave them empty to force the user to "upload" to see the magic.
      setQuizzes(q);
      setProgress(p);
      setActivity(a);
      setLoading(false);
    };
    fetchData();
  }, []);

  const handleUploadSuccess = (generatedTopics) => {
    setTopics(generatedTopics);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500 font-medium">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="max-w-7xl w-full mx-auto p-4 md:p-8 flex-1">
        
        {/* Upload Section */}
        <section className="mb-16 mt-8">
          <UploadCard onUploadSuccess={handleUploadSuccess} />
        </section>

        {topics.length > 0 && (
          <section id="learning" className="mb-16 scroll-mt-24">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Learn & Revise</h2>
              <p className="text-gray-500 text-sm mt-1">Choose a topic to revise using AI-generated flashcards.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {topics.map(topic => (
                <TopicCard key={topic.id} topic={topic} />
              ))}
            </div>
          </section>
        )}

        <section id="quizzes" className="mb-16 scroll-mt-24">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Practice with AI Quiz</h2>
            <p className="text-gray-500 text-sm mt-1">Test your understanding with questions generated from your study material.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {quizzes.map(quiz => (
              <QuizCard key={quiz.id} quiz={quiz} />
            ))}
          </div>
        </section>

        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Progress</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <ProgressCard label="Quizzes Taken" value={progress?.quizzesTaken} />
            <ProgressCard label="Questions Answered" value={progress?.questionsAnswered} />
            <ProgressCard label="Average Score" value={`${progress?.averageScore}%`} />
            <ProgressCard label="Flashcards Reviewed" value={progress?.flashcardsReviewed} />
          </div>
          
          <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {activity.map(item => (
                <div key={item.id} className="flex items-start gap-4 pb-4 border-b border-gray-50 last:border-0 last:pb-0">
                  <div className={`mt-1 rounded-full p-1.5 ${item.type === 'quiz' ? 'bg-blue-50 text-blue-500' : 'bg-green-50 text-green-500'}`}>
                    {item.type === 'quiz' ? <Edit3 size={16} /> : <BookOpen size={16} />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.text}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {item.score && <span className="font-medium text-green-600">Score: {item.score}%</span>}
                      {item.count && <span>{item.count} cards</span>}
                      <span>&bull;</span>
                      <span>{item.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

      </main>
    </div>
  );
};

export default Dashboard;
