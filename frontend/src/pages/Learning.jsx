import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Flashcard from '../components/Flashcard';
import { getFlashcardsByTopic, getTopics } from '../services/api';
import Button from '../components/Button';

const Learning = () => {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [flashcards, setFlashcards] = useState([]);
  const [topicName, setTopicName] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [sessionCompleted, setSessionCompleted] = useState(false);

  useEffect(() => {
    const fetchCards = async () => {
      const cards = await getFlashcardsByTopic(topicId);
      const topics = await getTopics();
      const topic = topics.find(t => t.id === topicId);
      setFlashcards(cards);
      if (topic) setTopicName(topic.name);
      setLoading(false);
    };
    fetchCards();
  }, [topicId]);

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const handleScore = (status) => {
    // Record status ('know' or 'revise') in real app
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setSessionCompleted(true);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-gray-500">Loading flashcards...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="max-w-4xl w-full mx-auto p-4 md:p-8 flex-1 flex flex-col">
        <div className="mb-8">
          <button onClick={() => navigate('/dashboard')} className="text-sm text-gray-500 hover:text-primary mb-4 flex items-center gap-1">
            &larr; Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{topicName} Flashcards</h1>
          <p className="text-gray-500 text-sm mt-1">Review your generated cards. Flip to see the answers.</p>
        </div>

        {sessionCompleted ? (
          <div className="bg-white border border-gray-200 rounded-xl p-10 text-center max-w-lg mx-auto w-full shadow-sm mt-10">
            <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Session Completed!</h2>
            <p className="text-gray-500 mb-8">You have reviewed all flashcards for this topic.</p>
            <div className="flex flex-col gap-3">
              <Button onClick={() => { setSessionCompleted(false); setCurrentIndex(0); }}>Review Again</Button>
              <Button variant="secondary" onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center mb-10">
            {flashcards.length > 0 && (
              <Flashcard 
                card={flashcards[currentIndex]} 
                current={currentIndex + 1}
                total={flashcards.length}
                onNext={handleNext}
                onPrev={handlePrev}
                onScore={handleScore}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Learning;
