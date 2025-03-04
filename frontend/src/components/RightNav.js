import React, { useState, useContext, useEffect } from 'react';
import { useConfig } from './ConfigContext';
import SelectLLM from './SelectLLM';
import SystemPrompt from './SystemPrompt';
import { getProjectState, updateProjectState } from "../api/projectAPI.mjs"
import { getAvailableModels } from "../api/ollamaAPI.mjs"

const RightNav = ({ isOpen }) => {
  const { persistentConfig, ephemeralConfig, updateConfig } = useConfig();
  
  const [llmRole, setLlmRole] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [researchDataLocation, setResearchDataLocation] = useState('');
  const [useLocalData, setUseLocalData] = useState(false);
  const [models, setModels] = useState('');
  const [currentProjectState, setCurrentProjectState] = useState(null); // For storing API data
  const [loading, setLoading] = useState(true); // For loading state
  const [error, setError] = useState(null); // For handling errors


  function modelDropDownSetup(availableModels, activeModel) {
    return availableModels.map(model => ({
      label: model,
      value: model,
      selected: model === activeModel
    }));
  }

  // API call to get data when RightNav is loaded
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
    
        const availableModels = await getAvailableModels()
        const projectState = await getProjectState(persistentConfig.project_id);
        setLlmRole(projectState.project_system_prompt)
        setSelectedModel(projectState.project_llm_name)
        const dropdownList = modelDropDownSetup(availableModels, projectState.project_llm_name)
        setModels(dropdownList)
        //setCurrentProjectState(projectState)
        // Check if the projectState attributes exist before setting values
        if (projectState.project_system_prompt) {
          setLlmRole(projectState.project_system_prompt);
        }

        if (projectState.project_data_dir) {
          setResearchDataLocation(projectState.project_data_dir);
        }

        if (projectState.project_data_toggle !== undefined) { // Checking specifically for undefined, assuming toggle can be true/false
          setUseLocalData(projectState.project_data_toggle);
        }
      } catch (error) {
        setError('Failed to load data'); // Handle errors
      } finally {
        setLoading(false); // Stop loading
      }
    };

    fetchData();
  }, []); // Empty dependency array means it runs once on component load

  const handleSave = () => {
    const projectData = {
      project_name: persistentConfig.project_id,
      project_llm_name: selectedModel,
      project_system_prompt: llmRole,
      project_data_dir:researchDataLocation,
      project_data_toggle:useLocalData
    };
    updateProjectState(persistentConfig.project_id,projectData);
  };

  return (
<div
  className={`transition-all duration-300 ${
    persistentConfig.isRightNavOpen ? 'w-7/12' : 'w-0 overflow-hidden'
  } bg-gray-200 h-full text-black p-6 ${!persistentConfig.isRightNavOpen ? 'hidden' : ''}`}
>
  {/* Centered Project Details Header */}
  <div className="text-center py-4">
    <h2 className="text-xl font-semibold">Project Details</h2>
  </div>

  {/* Handle Loading and Error */}
  {loading && <div>Loading...</div>}
  {error && <div>Error: {error}</div>}

  <SelectLLM models={models} selectedModel={selectedModel} setSelectedModel={setSelectedModel} />
  <SystemPrompt llmRole={llmRole} setLlmRole={setLlmRole} />

  {/* Location of Research Data entry field */}
  <div className="p-4">
    <label htmlFor="researchDataLocation" className="mr-2 text-lg font-semibold">
      Location of Research Data
    </label>
    <input
      id="researchDataLocation"
      type="text"
      className="w-full p-2 border border-gray-300 rounded-md"
      placeholder="Enter the data location"
      value={researchDataLocation} // Assuming this state exists and is handled
      onChange={(e) => setResearchDataLocation(e.target.value)} // Assuming setResearchDataLocation handler exists
    />
  </div>

  {/* Toggle for "Use Local Data" */}
  <div className="p-4">
    <label htmlFor="useLocalData" className="mr-4 text-lg font-semibold">
      Use Local Data
    </label>
    <input
      type="checkbox"
      id="useLocalData"
      checked={useLocalData} // Assuming this state exists
      onChange={(e) => setUseLocalData(e.target.checked)} // Assuming setUseLocalData handler exists
      className="h-4 w-4"
    />
  </div>

  {/* Centered Save Button spanning full width */}
  <button
    onClick={handleSave}
    className="mt-6 w-full px-4 py-2 bg-blue-500 text-white text-center rounded-md hover:bg-blue-600"
  >
    Save Project Details
  </button>
</div>
  );
};

export default RightNav;