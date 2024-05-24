import React, { useState } from 'react';
import axios from 'axios';
import './styles/App.css';

function App() {
  const [file, setFile] = useState(null);
  const [topText, setTopText] = useState('');
  const [bottomText, setBottomText] = useState('');
  const [taskId, setTaskId] = useState('');
  const [status, setStatus] = useState('');
  const [imageUrl, setImageUrl] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_text', topText);
    formData.append('bottom_text', bottomText);

    const response = await axios.post('http://localhost:8000/api/create_meme/', formData);
    setTaskId(response.data.task_id);
    setStatus('pending');
    checkStatus(response.data.task_id);
  };

  const checkStatus = async (task_id) => {
    const response = await axios.get(`http://localhost:8000/api/task_status/${task_id}`);
    const currentStatus = response.data.status;
    setStatus(currentStatus);
    if (currentStatus === 'completed') {
      setImageUrl(`http://localhost:8000/api/download_meme/${task_id}`);
    } else if (currentStatus === 'processing') {
      setTimeout(() => checkStatus(task_id), 1000);
    } else if (currentStatus === 'pending') {
      setTimeout(() => checkStatus(task_id), 1000);
    } else {
      setStatus('failed');
    }
  };

  return (
    <div className="App">
      <h1>Meme Generator</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} className="file-input" />
        <input
          type="text"
          placeholder="Top text"
          value={topText}
          onChange={(e) => setTopText(e.target.value)}
          className="text-input"
        />
        <input
          type="text"
          placeholder="Bottom text"
          value={bottomText}
          onChange={(e) => setBottomText(e.target.value)}
          className="text-input"
        />
        <button type="submit" className="submit-button">Create Meme</button>
      </form>
      {status && status === 'pending' && <p className="status-text">Task {taskId} is pending...</p>}
      {status && status !== 'pending' && <p className="status-text">Status: {status}</p>}
      {imageUrl && (
        <div className="image-container">
          <h2>Generated Meme</h2>
          <img src={imageUrl} alt="Generated Meme" className="meme-image" />
        </div>
      )}
    </div>
  );
}

export default App;
