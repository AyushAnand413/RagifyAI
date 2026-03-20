"use client"
import { useState, useRef, useEffect } from 'react'
import { Send, AlertCircle, Bot, User, ChevronDown } from 'lucide-react'
import { useStore, type Message } from '../store/useStore'
import { cn } from '../lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChat } from '../lib/api/client'

export function ChatArea() {
  const { messages, addMessage, documents, isGenerating, setGenerating } = useStore()
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isGenerating])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isGenerating) return

    const userQuery = input.trim()
    setInput('')
    
    // Add User Message
    addMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content: userQuery,
    })

    setGenerating(true)

    try {
      const hasDocs = documents.some(d => d.status === 'indexed')
      const assistantId = crypto.randomUUID()
      
      if (!hasDocs) {
        // Error state: No documents
        addMessage({
          id: assistantId,
          role: 'assistant',
          content: "I couldn't find information about this in the uploaded documents.\n\nTry uploading documents first.",
          error: true
        })
        setGenerating(false)
        return
      }

      const res = await sendChat({ query: userQuery });
      
      if (res.success && res.data && res.data.answer) {
        addMessage({
          id: assistantId,
          role: 'assistant',
          content: res.data.answer,
        })
      } else {
        addMessage({
          id: assistantId,
          role: 'assistant',
          content: "Sorry, I received an invalid response from the server.",
          error: true
        })
      }
    } catch (err: any) {
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: err?.message || "An error occurred while communicating with the backend.",
        error: true
      })
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-6 scrollbar-hide" ref={scrollRef}>
        <div className="max-w-3xl mx-auto flex flex-col gap-6 pb-20">
          
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full mt-32 text-center fade-in">
              <div className="w-12 h-12 rounded-full bg-background-card border border-border-subtle flex items-center justify-center mb-6">
                <Bot size={24} className="text-text-secondary" />
              </div>
              <h2 className="text-[16px] font-medium text-text-primary mb-2">Ask me anything about your docs</h2>
            </div>
          ) : (
            messages.map(msg => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          )}
          
          {isGenerating && (
            <div className="flex items-start gap-4 animate-fade-in">
              <div className="mt-1 bg-background-card rounded-md p-2 border border-border-subtle text-text-secondary">
                <Bot size={16} />
              </div>
              <div className="flex space-x-1 h-10 items-center">
                <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce"></div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="absolute bottom-0 w-full bg-gradient-to-t from-background via-background to-transparent pb-6 pt-10 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="max-w-3xl mx-auto flex flex-col gap-3">
            {messages.length === 0 && (
              <div className="flex flex-wrap items-center gap-2 pb-1">
                {['What are the key findings?', 'Summarize the main points', 'What topics are covered?'].map((q, i) => (
                  <button 
                    key={i}
                    onClick={() => setInput(q)}
                    className="px-4 py-1.5 rounded-full bg-background-card hover:bg-background-hover text-[13px] text-text-secondary hover:text-text-primary transition-colors border border-border-subtle"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
            <form 
              onSubmit={handleSubmit}
              className="relative flex items-center bg-background-card border border-border-emphasized rounded-lg overflow-hidden focus-within:border-accent-primary focus-within:ring-1 focus-within:ring-accent-primary transition-all shadow-sm"
            >
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                disabled={isGenerating}
                placeholder={isGenerating ? "Processing..." : "Ask a question..."}
                className="flex-1 bg-transparent px-4 py-4 text-[15px] outline-none text-text-primary placeholder:text-text-tertiary disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!input.trim() || isGenerating}
                className="absolute right-2 p-2 bg-accent-primary hover:bg-blue-600 text-white rounded-md disabled:opacity-50 transition-colors"
                style={{ backgroundColor: input.trim() ? '#4a7dff' : '' }}
              >
                <Send size={18} />
              </button>
            </form>
            <div className="text-center mt-1">
              <span className="text-[12px] text-text-tertiary font-mono">RagifyAI can make mistakes. Verify important info.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  const [citationExpanded, setCitationExpanded] = useState(false)

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div className={cn(
        "max-w-[85%] rounded-lg p-5 flex flex-col gap-3",
        isUser 
          ? "bg-background-hover border border-border-subtle text-text-primary" 
          : cn(
              "bg-background text-text-primary border-l-[3px]",
              message.error ? "border-l-accent-warning border-y border-r border-border-subtle" : "border-l-accent-success border-y border-r border-border-subtle"
            )
      )}>
        <div className="flex items-start gap-3">
          {!isUser && (
            <div className={cn(
              "mt-0.5",
               message.error ? "text-accent-warning" : "text-accent-success"
            )}>
              {message.error ? <AlertCircle size={18} /> : <Bot size={18} />}
            </div>
          )}
          
          <div className="flex-1 whitespace-pre-wrap leading-relaxed text-[15px]">
            {message.content}
          </div>
        </div>

        {message.citation && (
          <div className="mt-2 ml-7">
            <button 
              onClick={() => setCitationExpanded(!citationExpanded)}
              className="flex items-center gap-2 text-[13px] text-text-secondary hover:text-text-primary transition-colors bg-background-card px-3 py-1.5 rounded border border-border-subtle"
            >
              <span className="text-accent-primary">📌</span>
              Source: {message.citation.file} • Page {message.citation.page}
              <ChevronDown 
                size={14} 
                className={cn("ml-1 transition-transform", citationExpanded && "rotate-180")} 
              />
            </button>
            <AnimatePresence>
              {citationExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="mt-2 p-3 bg-background-card border border-border-subtle rounded text-[13px] text-text-secondary font-mono leading-relaxed relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-border-emphasized rounded-l" />
                    {message.citation.text}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  )
}
