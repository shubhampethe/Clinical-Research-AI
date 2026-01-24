import { useState } from 'react'
import './App.css'

interface DiagnosisResponse {
  symptom: string[];
  pubmed_summary: string;
}

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<DiagnosisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResponse(null)

    try {
// ✅ Correct way to access it
      const apiUrl ='http://ec2-3-108-196-32.ap-south-1.compute.amazonaws.com';
      const res = await fetch(`${apiUrl}/diagnosis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: query }),
      })

      if (!res.ok) {
        throw new Error('Failed to get diagnosis')
      }

      const data: DiagnosisResponse = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const sampleQueries = [
    "What are common cold symptoms?",
    "How to improve sleep quality?",
    "Tips for managing stress",
    "When should I see a doctor?"
  ]

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🩺</div>
          <div>
            <h1>MediAssist</h1>
            <p>AI Health Assistant</p>
          </div>
        </div>
        <nav>
          <a href="#about">About</a>
          <a href="#resources">Resources</a>
          <button className="get-started-btn">Get Started</button>
        </nav>
      </header>

      <main className="main">
        <div className="hero">
          <div className="hero-icon">🩺</div>
          <h2>Your Health Assistant</h2>
          <p>Ask me anything about health, symptoms, medications, or wellness tips. I'm here to help you stay informed.</p>

          <div className="feature-tags">
            <span className="tag">💚 Symptom Info</span>
            <span className="tag">💡 Health Tips</span>
            <span className="tag">✨ Wellness</span>
          </div>
        </div>

        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-container">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about symptoms, medications, health tips..."
                className="query-input"
                disabled={loading}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !query.trim()}
              >
                {loading ? '⏳' : '→'}
              </button>
            </div>
          </form>

          {!response && !loading && (
            <div className="sample-queries">
              <p>Try asking:</p>
              <div className="sample-grid">
                {sampleQueries.map((sample, index) => (
                  <button
                    key={index}
                    className="sample-query"
                    onClick={() => setQuery(sample)}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="error">
              <p>❌ {error}</p>
            </div>
          )}

          {response && (
            <div className="response">
              <div className="response-section">
                <h3>🔍 Identified Symptoms</h3>
                <div className="symptoms">
                  {Array.isArray(response.symptom) && response.symptom.length > 0 ? (
                    response.symptom.map((symptom, index) => (
                      <span key={index} className="symptom-tag">{symptom}</span>
                    ))
                  ) : (
                    <p>No symptoms identified</p>
                  )}
                </div>
              </div>

              <div className="response-section">
                <h3>📚 Medical Summary</h3>
                <div className="summary">
                  {response.pubmed_summary || 'No summary available'}
                </div>
              </div>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>This is for informational purposes only. Always consult a healthcare professional.</p>
        </footer>
      </main>
    </div>
  )
}

export default App
