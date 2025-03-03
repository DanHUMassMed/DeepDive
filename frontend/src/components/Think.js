import React, { useState, useEffect, useRef } from 'react';

const Think = ({ children }) => {
  const [isOpen, setIsOpen] = useState(true);
  const isMounted = useRef(true);

  useEffect(() => {
    // Set the flag to true when the component mounts
    isMounted.current = true;

    // Cleanup function to set the flag to false when the component unmounts
    return () => {
      isMounted.current = false;
    };
  }, []);

  const toggleSection = () => {
    setIsOpen(prevState => !prevState);
  };



  return (
    <div>
      <button
        onClick={toggleSection}
        style={{
          backgroundColor: '#007bff',
          color: '#fff',
          border: 'none',
          padding: '10px',
          cursor: 'pointer',
          width: '100%',
          textAlign: 'left',
        }}
      >
        {isOpen ? 'Hide Thinking Process' : 'Reveal Thinking Process'}
      </button>
      {isOpen && (
        <div
          style={{
            marginTop: '10px',
            padding: '10px',
            backgroundColor: '#f9f9f9',
            border: '1px solid #ddd',
            borderRadius: '5px',
            whiteSpace: 'pre-wrap',
          }}
        >
          {children}
        </div>
      )}
    </div>
  );
};

export default Think;