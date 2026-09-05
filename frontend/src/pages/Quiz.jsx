import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Button from '../components/Button';
import { getQuizQuestions, getQuizzes } from '../services/api';
import { Check, X } from 'lucide-react';

const Quiz = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [quizInfo, setQuizInfo] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuiz = async () => {
      const q = await getQuizQuestions(quizId);
      const allQuizzes = await getQuizzes();
      setQuestions(q);
      setQuizInfo(allQuizzes.find(x => x.id === quizId));
      setLoading(false);
    };
    fetchQuiz();
  }, [quizId]);

  const handleOptionSelect = (option) => {
    if (isAnswered) return;
    setSelectedOption(option);
    setIsAnswered(true);
    
    if (option === questions[currentIndex].correctAnswer) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setSelectedOption(null);
      setIsAnswered(false);
    } else {
      setQuizCompleted(true);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-gray-500">Loading quiz...</div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  const progressPercent = ((currentIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="max-w-3xl w-full mx-auto p-4 md:p-8 flex-1 flex flex-col">
        <div className="mb-6">
          <button onClick={() => navigate('/dashboard')} className="text-sm text-gray-500 hover:text-primary mb-4 flex items-center gap-1">
            &larr; Exit Quiz
          </button>
          <div className="flex justify-between items-end mb-2">
            <h1 className="text-xl font-bold text-gray-900">{quizInfo?.title}</h1>
            <span className="text-sm font-medium text-gray-500">Question {currentIndex + 1} of {questions.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary h-2 rounded-full transition-all duration-300" style={{ width: `${progressPercent}%` }}></div>
          </div>
        </div>

        {quizCompleted ? (
          <div className="bg-white border border-gray-200 rounded-xl p-10 text-center shadow-sm mt-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Quiz Completed!</h2>
            
            <div className="flex flex-col items-center justify-center my-8">
              <div className="text-5xl font-bold text-primary mb-2">{Math.round((score / questions.length) * 100)}%</div>
              <p className="text-gray-500 font-medium">Score: {score} / {questions.length}</p>
            </div>

            <div className="bg-orange-50 border border-orange-100 rounded-lg p-6 mb-8 text-left">
              <h3 className="font-semibold text-orange-800 mb-1">Your weak area</h3>
              <p className="text-orange-900 font-bold text-lg mb-2">Deadlocks</p>
              <p className="text-sm text-orange-700">Practice 5 more questions to improve this topic.</p>
            </div>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button>Practice Weak Topic</Button>
              <Button variant="secondary" onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
            </div>
          </div>
        ) : (
          <div className="bg-white border border-gray-100 rounded-xl p-6 md:p-10 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 mb-8 leading-relaxed">
              {currentQ.question}
            </h2>
            
            <div className="space-y-3 mb-8">
              {currentQ.options.map((option, idx) => {
                const isSelected = selectedOption === option;
                const isCorrect = option === currentQ.correctAnswer;
                
                let optionStyle = "border-gray-200 hover:border-primary hover:bg-primary/5 text-gray-700 cursor-pointer";
                
                if (isAnswered) {
                  if (isCorrect) {
                    optionStyle = "border-green-500 bg-green-50 text-green-800 font-medium cursor-default";
                  } else if (isSelected && !isCorrect) {
                    optionStyle = "border-red-500 bg-red-50 text-red-800 font-medium cursor-default";
                  } else {
                    optionStyle = "border-gray-100 bg-gray-50 text-gray-400 opacity-70 cursor-default";
                  }
                }

                return (
                  <div 
                    key={idx}
                    onClick={() => handleOptionSelect(option)}
                    className={`border-2 rounded-lg p-4 transition-all flex items-center justify-between ${optionStyle}`}
                  >
                    <span>{option}</span>
                    {isAnswered && isCorrect && <Check size={20} className="text-green-600" />}
                    {isAnswered && isSelected && !isCorrect && <X size={20} className="text-red-600" />}
                  </div>
                );
              })}
            </div>

            {isAnswered && (
              <div className={`p-5 rounded-lg mb-8 ${selectedOption === currentQ.correctAnswer ? 'bg-green-50 border border-green-100' : 'bg-red-50 border border-red-100'}`}>
                <div className="flex items-center gap-2 mb-2">
                  {selectedOption === currentQ.correctAnswer ? (
                    <><Check size={20} className="text-green-600" /> <span className="font-bold text-green-800">Correct!</span></>
                  ) : (
                    <><X size={20} className="text-red-600" /> <span className="font-bold text-red-800">Incorrect</span></>
                  )}
                </div>
                {! (selectedOption === currentQ.correctAnswer) && (
                  <p className="text-sm font-medium text-gray-900 mb-2">Correct answer: {currentQ.correctAnswer}</p>
                )}
                <p className="text-sm text-gray-700">{currentQ.explanation}</p>
              </div>
            )}

            {isAnswered && (
              <div className="flex justify-end">
                <Button onClick={handleNext} className="w-auto px-8">
                  {currentIndex === questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
                </Button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Quiz;
