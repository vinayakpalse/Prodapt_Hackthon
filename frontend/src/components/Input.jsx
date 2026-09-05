import React from 'react';

const Input = ({ label, id, type = 'text', error, ...props }) => {
  return (
    <div className="mb-5">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-900 mb-2">
          {label}
        </label>
      )}
      <input
        id={id}
        type={type}
        className={`w-full px-3 py-2.5 border rounded-md text-sm font-sans transition-colors duration-200 outline-none
          ${error 
            ? 'border-error focus:border-error focus:ring-4 focus:ring-error/10' 
            : 'border-gray-200 focus:border-primary focus:ring-4 focus:ring-primary/10'
          }`}
        {...props}
      />
      {error && <span className="text-error text-xs mt-1.5 block">{error}</span>}
    </div>
  );
};

export default Input;
