import React, { useState } from 'react';
import { Tooltip } from 'react-tooltip';

const SystemPrompt = () => {
  const [llmRole, setLlmRole] = useState('');

  const handleChange = (event) => {
    setLlmRole(event.target.value);
  };

  const handleSave = () => {
    // Implement your save logic here
    console.log('Saved:', llmRole);
    // Optionally, you can clear the input after saving
    // setLlmRole('');
  };

  const tooltipStyles = {
    padding: '10px', // Add some padding around the text
    width: '300px',  // Set a fixed width for the tooltip box
    wordWrap: 'break-word', // Allow text to wrap to multiple lines
  };

  return (
    <div className="p-4">
      <div className="flex items-center">
        <label
          htmlFor="llmRole"
          className="mr-2 text-lg font-semibold"
        >
          Enter the role your LLM will play in this project.
        </label>
        <span
          data-tooltip-id="llmRoleTooltip"
          className="ml-2 text-gray-500 cursor-pointer"
        >
          ?
        </span>
      </div>
      <textarea
        id="llmRole"
        value={llmRole}
        onChange={handleChange}
        rows="4"
        className="w-full p-2 border border-gray-300 rounded-md"
        placeholder="Describe the LLM's role here..."
      />
      <button
        onClick={handleSave}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
      >
        Save
      </button>
      <Tooltip
        id="llmRoleTooltip"
        place="top"
        type="dark"
        effect="solid"
        style={tooltipStyles}
      >
        The 'LLM Role' should describe the responsibilities of the LLM for the project.<br/><br/>
        <b>For example:</b> Your role is to answer all questions to the best of your ability. Answer concisely but correctly.
        If you do not know the answer, just say 'I don’t know.'
      </Tooltip>
    </div>
  );
};

export default SystemPrompt;