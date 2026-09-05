import React from 'react';

const ProgressCard = ({ label, value }) => {
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm text-center">
      <div className="text-3xl font-bold text-primary mb-2">{value}</div>
      <div className="text-sm font-medium text-gray-500">{label}</div>
    </div>
  );
};

export default ProgressCard;
