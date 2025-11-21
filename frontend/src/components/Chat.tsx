
import React from 'react'
import { chat } from '../lib/api'

type Source = { source:string, uri:string, page:number, chunk_id:string, content:string, score:number }

export default function Chat(){
  const [q, setQ] = React.useState('Como calibrar a válvula FV-101?')
  const [a, setA] = React.useState('')
  const [hits, setHits] = React.useState<Source[]>([])
  const [busy, setBusy] = React.useState(false)

  async function ask(){
    setBusy(true)
    setA('')
    try {
      const res = await chat(q)
      setA(res.answer)
      setHits(res.sources)
    } catch (error: any) {
      setA('Erro ao processar a pergunta. Verifique se a API está configurada corretamente.')
    } finally {
      setBusy(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask()
    }
  }

  return (
    <div className="card">
      <div style={{marginBottom: '1rem'}}>
        <h2 style={{fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-primary)'}}>
          💬 Chat com Documentos
        </h2>
        <p style={{fontSize: '0.875rem', color: 'var(--text-muted)'}}>
          Faça perguntas sobre seus documentos industriais
        </p>
      </div>
      
      <div className="row" style={{marginBottom: '1rem'}}>
        <input 
          style={{flex: 1}} 
          value={q} 
          onChange={e=>setQ(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Faça sua pergunta…" 
        />
        <button className="btn" onClick={ask} disabled={busy}>
          {busy ? (
            <>
              <span className="spinner"></span>
              Pensando...
            </>
          ) : (
            '🔍 Perguntar'
          )}
        </button>
      </div>
      
      {a && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-secondary)'
        }}>
          <div style={{fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600}}>
            📝 RESPOSTA
          </div>
          <div style={{whiteSpace: 'pre-wrap', lineHeight: '1.7', color: 'var(--text-primary)'}}>
            {a}
          </div>
        </div>
      )}
      
      {!!hits.length && (
        <div style={{marginTop: '1.5rem'}}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--text-secondary)',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            📚 FONTES ({hits.length})
          </div>
          {hits.map((h,i)=> (
            <div key={i} className="source-item">
              <div className="source-meta">
                <span>📄 {h.uri}</span>
                <span>📄 Página {h.page}</span>
                <span className="score-badge">Score: {h.score?.toFixed(3)}</span>
              </div>
              <div className="source-content">{(h.content||'').slice(0, 280)}…</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
