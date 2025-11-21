
import React from 'react'
import { chat } from '../lib/api'

type Source = { source:string, uri:string, page:number, chunk_id:string, content:string, score:number }

type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  sources?: Source[]
}

export default function Chat(){
  const [input, setInput] = React.useState('')
  const [messages, setMessages] = React.useState<Message[]>(() => {
    const saved = localStorage.getItem('chat_history')
    return saved ? JSON.parse(saved) : []
  })
  const [busy, setBusy] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  React.useEffect(() => {
    scrollToBottom()
  }, [messages])

  React.useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages.slice(-10)))
  }, [messages])

  async function ask(){
    if (!input.trim() || busy) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setBusy(true)
    
    try {
      const res = await chat(input.trim())
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        timestamp: Date.now(),
        sources: res.sources
      }
      setMessages(prev => [...prev.slice(-9), assistantMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Erro ao processar a pergunta. Verifique se a API está configurada corretamente.',
        timestamp: Date.now()
      }
      setMessages(prev => [...prev.slice(-9), errorMessage])
    } finally {
      setBusy(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !busy) {
      e.preventDefault()
      ask()
    }
  }

  const clearHistory = () => {
    setMessages([])
    localStorage.removeItem('chat_history')
  }

  return (
    <div className="card" style={{display: 'flex', flexDirection: 'column', height: '600px', maxHeight: '70vh'}}>
      <div style={{
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        paddingBottom: '1rem',
        borderBottom: '1px solid var(--border-secondary)'
      }}>
        <div>
          <h2 style={{fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-primary)'}}>
            💬 Chat com Documentos
          </h2>
          <p style={{fontSize: '0.875rem', color: 'var(--text-muted)'}}>
            Converse sobre seus documentos industriais
          </p>
        </div>
        {messages.length > 0 && (
          <button 
            className="btn" 
            onClick={clearHistory}
            style={{
              padding: '0.5rem 0.75rem',
              fontSize: '0.8rem',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-secondary)'
            }}
          >
            🗑️ Limpar
          </button>
        )}
      </div>
      
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem 0',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: 'var(--text-muted)',
            textAlign: 'center',
            gap: '1rem'
          }}>
            <div style={{fontSize: '3rem'}}>💬</div>
            <div>
              <div style={{fontSize: '1.1rem', marginBottom: '0.5rem', color: 'var(--text-secondary)'}}>
                Como posso ajudar?
              </div>
              <div style={{fontSize: '0.9rem'}}>
                Faça perguntas sobre seus documentos industriais
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} className="chat-message" data-role={msg.role}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">
                      {msg.role === 'user' ? 'Você' : 'Assistente'}
                    </span>
                    <span className="message-time">
                      {new Date(msg.timestamp).toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <div className="message-text">
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{marginTop: '1rem'}}>
                      <div style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: 'var(--text-muted)',
                        marginBottom: '0.5rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                      }}>
                        📚 Fontes ({msg.sources.length})
                      </div>
                      {msg.sources.map((source, i) => (
                        <div key={i} className="source-item" style={{marginBottom: '0.5rem'}}>
                          <div className="source-meta">
                            <span>📄 {source.uri}</span>
                            <span>Página {source.page}</span>
                            <span className="score-badge">Score: {source.score?.toFixed(3)}</span>
                          </div>
                          <div className="source-content">
                            {(source.content || '').slice(0, 200)}…
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {busy && (
              <div className="chat-message" data-role="assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">Assistente</span>
                  </div>
                  <div className="message-text">
                    <span className="spinner"></span>
                    Pensando...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      <div style={{
        paddingTop: '1rem',
        borderTop: '1px solid var(--border-secondary)'
      }}>
        <div className="row" style={{gap: '0.5rem'}}>
          <input 
            style={{flex: 1}} 
            value={input} 
            onChange={e=>setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua pergunta..." 
            disabled={busy}
          />
          <button className="btn" onClick={ask} disabled={busy || !input.trim()}>
            {busy ? (
              <>
                <span className="spinner"></span>
                Enviando...
              </>
            ) : (
              '📤 Enviar'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
