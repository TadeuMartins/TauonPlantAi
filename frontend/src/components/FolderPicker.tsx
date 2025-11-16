
import React from 'react'
import { ingestFolderUpload } from '../lib/api'

export default function FolderPicker() {
  const [busy, setBusy] = React.useState(false)
  const [msg, setMsg] = React.useState('')

  async function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files ? Array.from(e.target.files) : []
    if (!files.length) return
    setBusy(true)
    setMsg('Ingesting folder…')
    try {
      await ingestFolderUpload(files)
      setMsg('✅ Ingestion complete')
    } catch (err: any) {
      setMsg('❌ ' + (err?.message || 'Failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <div className="row">
        <span className="pill">Local Folder</span>
        <input type="file" webkitdirectory="" multiple onChange={onPick} />
      </div>
      <div style={{marginTop:8, opacity:.9}}>{busy ? 'Working…' : msg}</div>
    </div>
  )
}
