import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <div 
      style={{
        margin: '-5px',
        borderRadius: '10px',
      }}
    >
    <App />
    </div>
  </React.StrictMode>,
)
