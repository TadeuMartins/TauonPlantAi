
import React from 'react'
import { ingestFolderUpload } from '../lib/api'

export default function FolderPicker() {
  const [busy, setBusy] = React.useState(false)
  const [msg, setMsg] = React.useState('')

  async function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files ? Array.from(e.target.files) : []
    if (!files.length) return
    setBusy(true)
    setMsg('Processando arquivos...')
    try {
      await ingestFolderUpload(files)
      setMsg('✅ Ingestão concluída com sucesso!')
    } catch (err: any) {
      setMsg('❌ Erro: ' + (err?.message || 'Falha na ingestão'))
    } finally {
      setBusy(false)
    }
  }

  const getStatusClass = () => {
    if (busy) return 'status-message working'
    if (msg.includes('✅')) return 'status-message success'
    if (msg.includes('❌')) return 'status-message error'
    return ''
  }

  return (
    <div className="card">
      <div style={{marginBottom: '1rem'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
          <span className="pill">📁 Local Folder</span>
        </div>
        <p style={{fontSize: '0.875rem', color: 'var(--text-muted)'}}>
          Selecione uma pasta do seu computador
        </p>
      </div>
      
      <input 
        type="file" 
        webkitdirectory="" 
        multiple 
        onChange={onPick}
        disabled={busy}
        style={{marginBottom: msg ? '0.5rem' : '0'}}
      />
      
      {msg && (
        <div className={getStatusClass()}>
          {busy && <span className="spinner"></span>}
          {msg}
        </div>
      )}
    </div>
  )
}
