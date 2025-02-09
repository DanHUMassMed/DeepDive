import React from 'react';

const RightNav = ({ isOpen }) => {
  return (
    <div className={`transition-all duration-300 ${isOpen ? 'w-64' : 'w-0'} bg-gray-200 h-full text-black`}></div>
  );
};

export default RightNav;
