
import React from 'react'
import FolderPicker from './components/FolderPicker'
import SharePointForm from './components/SharePointForm'
import Chat from './components/Chat'

export default function App(){
  return (
    <div style={{maxWidth:980, margin:'40px auto', padding:'0 16px'}}>
      <h1 style={{fontSize:28, marginBottom:8}}>TauON PlantAI</h1>
      <div style={{opacity:.8, marginBottom:16}}>RAG para documentos industriais com ingestão local e SharePoint.</div>
      <div className="row" style={{gap:16}}>
        <div style={{flex:1}}><FolderPicker/></div>
        <div style={{flex:1}}><SharePointForm/></div>
      </div>
      <div style={{marginTop:16}}><Chat/></div>
    </div>
  )
}
