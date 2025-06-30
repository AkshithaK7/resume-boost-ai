import React, { useState, useCallback } from 'react';
import { CloudUpload, BrainCircuit, FileText, Sparkles, AlertCircle } from 'lucide-react';

// --- Helper Components for UI ---
const IconWrapper = ({ children }) => <div className="icon-wrapper">{children}</div>;
const ResultCard = ({ icon, title, children }) => (
  <div className="result-card">
    <div className="result-header">{icon}<h3 className="result-title">{title}</h3></div>
    <div className="result-content">{children}</div>
  </div>
);
const BulletPointSuggestion = ({ original, rewrite }) => (
  <div className="bullet-suggestion">
    <p className="bullet-original">Original: "{original}"</p>
    <p className="bullet-rewrite">Suggested: "{rewrite}"</p>
  </div>
);

// --- Main App Component ---
export default function App() {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    if (!resumeFile || !jobDescription) {
      setError('Please provide both a job description and a resume file.');
      return;
    }
    setIsLoading(true);
    setError('');
    setAnalysisResult(null);

    try {
      // Step 1: Get pre-signed URL for S3 upload
      const uploadUrlResponse = await fetch('https://o9n0erkaca.execute-api.us-east-1.amazonaws.com/upload-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: resumeFile.name,
          jobDescription: jobDescription
        })
      });

      if (!uploadUrlResponse.ok) {
        throw new Error('Failed to get upload URL');
      }

      const uploadData = await uploadUrlResponse.json();
      const { jobId, uploadUrl } = uploadData;

      console.log(`Starting analysis for job ID: ${jobId}`);

      // Step 2: Upload file to S3 using pre-signed URL
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        body: resumeFile,
        headers: {
          'Content-Type': 'application/pdf',
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file to S3');
      }

      console.log('File uploaded successfully, starting analysis...');

      // Step 3: Poll for results
      const pollForResults = (id) => {
        const intervalId = setInterval(async () => {
          try {
            const API_GATEWAY_URL = `https://o9n0erkaca.execute-api.us-east-1.amazonaws.com/results/${id}`;

            const response = await fetch(API_GATEWAY_URL);
            if (response.status === 404) {
              console.log('Job still processing...');
              return;
            }
            if (!response.ok) throw new Error('API fetch failed.');

            const data = await response.json();
            if (data.status === 'COMPLETED') {
              clearInterval(intervalId);
              setAnalysisResult(data.feedback);
              setIsLoading(false);
            } else if (data.status === 'FAILED') {
              clearInterval(intervalId);
              setError('Analysis failed on the backend.');
              setIsLoading(false);
            }
          } catch (pollError) {
            console.error('Polling error:', pollError);
            clearInterval(intervalId);
            setError('Could not connect to the results service.');
            setIsLoading(false);
          }
        }, 5000);
      };
      pollForResults(jobId);

    } catch (error) {
      console.error('Upload error:', error);
      setError('Failed to start analysis. Please try again.');
      setIsLoading(false);
    }
  }, [resumeFile, jobDescription]);

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <BrainCircuit className="header-icon" />
          <h1 className="header-title">Resume-Boost AI</h1>
        </div>
        <p className="header-subtitle">Upload your resume and a job description to get AI-powered suggestions.</p>
        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
          🚀 <strong>Live Mode:</strong> Connected to real AI backend! Upload a PDF and paste a job description to get AI-powered suggestions.
        </p>
      </header>
      <div className="main-form">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-section">
              <label htmlFor="job-description" className="form-label">Job Description</label>
              <textarea
                id="job-description"
                rows="12"
                className="form-textarea"
                placeholder="Paste the full job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                required
              ></textarea>
            </div>
            <div className="form-section">
              <label htmlFor="resume-upload" className="form-label">Your Resume</label>
              <div className="file-upload">
                <div className="file-upload-content">
                  <FileText className="file-upload-icon" />
                  <div className="file-upload-text">
                    <label htmlFor="resume-upload-input" className="file-upload-link">
                      <span>Upload a file</span>
                      <input
                        id="resume-upload-input"
                        type="file"
                        className="file-upload-input"
                        onChange={(e) => setResumeFile(e.target.files[0])}
                        accept=".pdf"
                      />
                    </label>
                    <p>or drag and drop</p>
                  </div>
                  <p className="file-upload-info">PDF up to 10MB</p>
                  {resumeFile && <p className="file-selected">Selected: {resumeFile.name}</p>}
                </div>
              </div>
            </div>
          </div>
          <div className="submit-section">
            <button type="submit" disabled={isLoading} className="submit-button">
              <CloudUpload className="submit-button-icon" />
              {isLoading ? 'Analyzing...' : 'Boost My Resume'}
            </button>
          </div>
        </form>
        {error && (
          <div className="error-message">
            <AlertCircle className="error-icon" />
            {error}
          </div>
        )}
      </div>
      {isLoading && (
        <div className="loading-section">
          <div className="loading-spinner"></div>
          <p className="loading-text">AI is analyzing your documents. This may take a moment...</p>
        </div>
      )}
      {analysisResult && (
        <div className="results-section">
          <ResultCard
            icon={<IconWrapper><Sparkles className="result-icon" /></IconWrapper>}
            title="Achievement Miner"
          >
            <p className="result-description">Here are suggestions to reframe your responsibilities as impactful achievements.</p>
            {analysisResult.achievement_suggestions?.map((s, i) => (
              <BulletPointSuggestion key={i} original={s.original} rewrite={s.rewrite} />
            ))}
          </ResultCard>
          <ResultCard
            icon={<IconWrapper><BrainCircuit className="result-icon" /></IconWrapper>}
            title="Culture & Values Alignment"
          >
            <p className="result-description">
              The AI identified company values as: <strong>{analysisResult.identified_values?.join(', ')}</strong>.
              Here's how to echo this culture:
            </p>
            {analysisResult.alignment_suggestions?.map((s, i) => (
              <BulletPointSuggestion key={i} original={s.original} rewrite={s.rewrite} />
            ))}
          </ResultCard>
        </div>
      )}
    </div>
  );
}
