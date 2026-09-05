import React, { useState } from 'react';

const Flashcard = ({ card, onNext, onPrev, onScore, current, total }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleAction = (status) => {
    onScore(status);
    setIsFlipped(false);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mb-4 text-center text-sm font-medium text-gray-500">
        Card {current} / {total}
      </div>
      
      {/* Perspective wrapper for 3D flip */}
      <div 
        className="relative w-full h-80 [perspective:1000px] cursor-pointer group"
        onClick={handleFlip}
      >
        {/* Card container that flips */}
        <div 
          className={`w-full h-full transition-transform duration-500 [transform-style:preserve-3d] relative ${isFlipped ? '[transform:rotateY(180deg)]' : ''}`}
        >
          {/* Front */}
          <div 
            className="absolute w-full h-full [backface-visibility:hidden] bg-white border border-gray-200 rounded-2xl shadow-sm p-8 flex flex-col items-center justify-center text-center"
          >
            <h3 className="text-2xl font-semibold text-gray-900 mb-8">{card.question}</h3>
            <p className="text-sm text-gray-400 absolute bottom-6">Click to reveal</p>
          </div>
          
          {/* Back */}
          <div 
            className="absolute w-full h-full [backface-visibility:hidden] bg-primary text-white border border-primary-hover rounded-2xl shadow-sm p-8 flex flex-col items-center justify-center text-center [transform:rotateY(180deg)]"
          >
            <span className="text-sm font-medium text-white/70 absolute top-6 tracking-widest uppercase">Answer</span>
            <p className="text-xl font-medium leading-relaxed">{card.answer}</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="mt-8 flex items-center justify-between">
        <button 
          onClick={(e) => { e.stopPropagation(); setIsFlipped(false); onPrev(); }}
          disabled={current === 1}
          className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          &larr; Previous
        </button>
        
        <div className="flex gap-3">
          <button 
            onClick={(e) => { e.stopPropagation(); handleAction('know'); }}
            className="px-6 py-2 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
          >
            I Know
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); handleAction('revise'); }}
            className="px-6 py-2 text-sm font-medium text-orange-700 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
          >
            Need Revision
          </button>
        </div>

        <button 
          onClick={(e) => { e.stopPropagation(); setIsFlipped(false); onNext(); }}
          disabled={current === total}
          className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next &rarr;
        </button>
      </div>
    </div>
  );
};

export default Flashcard;
