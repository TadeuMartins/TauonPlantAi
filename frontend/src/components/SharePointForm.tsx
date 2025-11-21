
import React from 'react'
import { ingestSharePoint } from '../lib/api'

export default function SharePointForm(){
  const [path, setPath] = React.useState('Documents/PlantSpecs')
  const [status, setStatus] = React.useState('')
  const [busy, setBusy] = React.useState(false)

  async function run(){
    setBusy(true)
    setStatus('Conectando ao SharePoint e processando...')
    try {
      await ingestSharePoint(path)
      setStatus('✅ Ingestão concluída do SharePoint')
    } catch (e:any){
      setStatus('❌ Erro: ' + (e?.message || 'Falha na conexão'))
    } finally { 
      setBusy(false) 
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !busy) {
      run()
    }
  }

  const getStatusClass = () => {
    if (busy) return 'status-message working'
    if (status.includes('✅')) return 'status-message success'
    if (status.includes('❌')) return 'status-message error'
    return ''
  }

  return (
    <div className="card">
      <div style={{marginBottom: '1rem'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
          <span className="pill">☁️ SharePoint</span>
        </div>
        <p style={{fontSize: '0.875rem', color: 'var(--text-muted)'}}>
          Ingira documentos do Microsoft SharePoint
        </p>
      </div>
      
      <div className="row" style={{marginBottom: status ? '0.5rem' : '0'}}>
        <input 
          value={path} 
          onChange={e=>setPath(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Documents/Folder/Subfolder"
          disabled={busy}
          style={{flex: 1}}
        />
        <button className="btn" onClick={run} disabled={busy}>
          {busy ? (
            <>
              <span className="spinner"></span>
              Processando...
            </>
          ) : (
            '📤 Ingerir'
          )}
        </button>
      </div>
      
      {status && (
        <div className={getStatusClass()}>
          {status}
        </div>
      )}
    </div>
  )
}
