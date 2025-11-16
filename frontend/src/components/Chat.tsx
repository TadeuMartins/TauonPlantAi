
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
    const res = await chat(q)
    setA(res.answer)
    setHits(res.sources)
    setBusy(false)
  }

  return (
    <div className="card">
      <div className="row">
        <input style={{flex:1}} value={q} onChange={e=>setQ(e.target.value)} placeholder="Faça sua pergunta…" />
        <button className="btn" onClick={ask} disabled={busy}>Perguntar</button>
      </div>
      <div style={{marginTop:12, whiteSpace:'pre-wrap'}}>{busy ? 'Pensando…' : a}</div>
      {!!hits.length && (
        <div style={{marginTop:16}}>
          <div style={{opacity:.7, marginBottom:8}}>Fontes</div>
          {hits.map((h,i)=> (
            <div key={i} style={{marginBottom:8, padding:8, border:'1px solid #2a3352', borderRadius:12}}>
              <div style={{fontSize:12, opacity:.8}}>{h.uri} — p.{h.page} — score {h.score?.toFixed(3)}</div>
              <div style={{fontSize:13, opacity:.9}}>{(h.content||'').slice(0,240)}…</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
