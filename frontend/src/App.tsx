
import React from 'react'
import FolderPicker from './components/FolderPicker'
import SharePointForm from './components/SharePointForm'
import Chat from './components/Chat'

export default function App(){
  return (
    <div style={{maxWidth: '1100px', margin: '0 auto', padding: '2.5rem 1rem'}}>
      <header style={{marginBottom: '2rem'}}>
        <h1>TauON PlantAI</h1>
        <p style={{fontSize: '1rem', color: 'var(--text-secondary)', marginTop: '0.5rem'}}>
          RAG para documentos industriais com ingestão local e SharePoint
        </p>
      </header>
      
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '1rem'}}>
        <FolderPicker/>
        <SharePointForm/>
      </div>
      
      <Chat/>
    </div>
  )
}
