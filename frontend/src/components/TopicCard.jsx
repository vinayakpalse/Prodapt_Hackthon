import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import Button from './Button';

const TopicCard = ({ topic }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col">
      <div className="flex-1">
        <h3 className="text-lg font-bold text-gray-900 mb-1">{topic.name}</h3>
        <p className="text-gray-500 text-sm flex items-center gap-1.5 mb-4">
          <BookOpen size={16} />
          {topic.flashcardCount} flashcards
        </p>
      </div>
      
      <div className="w-full bg-gray-100 rounded-full h-2 mb-4">
        <div className="bg-green-500 h-2 rounded-full" style={{ width: '0%' }}></div>
      </div>
      
      <Button 
        variant="secondary" 
        className="w-full text-primary bg-primary/5 hover:bg-primary/10 border-none"
        onClick={() => navigate(`/learning/${topic.id}`)}
      >
        Start Learning
      </Button>
    </div>
  );
};

export default TopicCard;
