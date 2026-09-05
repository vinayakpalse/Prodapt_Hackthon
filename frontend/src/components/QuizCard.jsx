import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BrainCircuit, Clock } from 'lucide-react';
import Button from './Button';

const QuizCard = ({ quiz }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col">
      <div className="flex-1">
        <h3 className="text-lg font-bold text-gray-900 mb-3">{quiz.title}</h3>
        
        <div className="flex flex-col gap-2 mb-6 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <BrainCircuit size={16} className="text-gray-400" />
            <span>{quiz.questionCount} Questions &bull; <span className={`font-medium ${quiz.difficulty === 'Hard' ? 'text-orange-500' : 'text-blue-500'}`}>{quiz.difficulty}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={16} className="text-gray-400" />
            <span>Estimated time: {quiz.estimatedTime} min</span>
          </div>
        </div>
      </div>
      
      <Button 
        className="w-full"
        onClick={() => navigate(`/quiz/${quiz.id}`)}
      >
        Start Quiz
      </Button>
    </div>
  );
};

export default QuizCard;
