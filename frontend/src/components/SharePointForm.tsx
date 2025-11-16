
import React from 'react'
import { ingestSharePoint } from '../lib/api'

export default function SharePointForm(){
  const [path, setPath] = React.useState('Documents/PlantSpecs')
  const [status, setStatus] = React.useState('')
  const [busy, setBusy] = React.useState(false)

  async function run(){
    setBusy(true)
    setStatus('Connecting to SharePoint and ingesting…')
    try {
      await ingestSharePoint(path)
      setStatus('✅ Ingestion complete from SharePoint')
    } catch (e:any){
      setStatus('❌ ' + (e?.message || 'Failed'))
    } finally { setBusy(false) }
  }

  return (
    <div className="card">
      <div className="row">
        <span className="pill">SharePoint</span>
        <input value={path} onChange={e=>setPath(e.target.value)} placeholder="Documents/Folder/Subfolder" />
        <button className="btn" onClick={run} disabled={busy}>Ingest</button>
      </div>
      <div style={{marginTop:8, opacity:.9}}>{busy ? 'Working…' : status}</div>
    </div>
  )
}
