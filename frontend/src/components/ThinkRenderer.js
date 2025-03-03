import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

const ThinkRenderer = ({ markdownContent }) => {
  // Define state to manage the visibility of the section
  const [isOpen, setIsOpen] = useState(false);

  // Function to toggle the visibility state
  const toggleSection = () => {
    setIsOpen(prevState => !prevState);
  };



  // Components object to define custom renderers
  const components = {
    // Custom rendering for <think> tags
    think: ({ node, ...props }) => (
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
          {isOpen ? 'Hide Details' : 'Show Details'}
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
            {props.children}
          </div>
        )}
      </div>
    ),
  };

  return (
    <ReactMarkdown components={components}>
      {markdownContent}
    </ReactMarkdown>
  );
};

export default ThinkRenderer;