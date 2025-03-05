// NOT USED!!
import React, { useState } from 'react';

const Think = ({ children, ...rest }) => {
  const [isOpen, setIsOpen] = useState(true);

  const toggleSection = () => setIsOpen(prevState => !prevState);

  return (
    <div {...rest} >
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