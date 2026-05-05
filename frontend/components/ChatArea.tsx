"use client"
import { useState, useRef, useEffect } from 'react'
import { Send, AlertCircle, Bot, Sparkles, ChevronDown } from 'lucide-react'
import { useStore, type Message } from '../store/useStore'
import { cn } from '../lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChat } from '../lib/api/client'

const SUGGESTIONS = [
  'What are the key findings?',
  'Summarize the main points',
  'What topics are covered?',
]

export function ChatArea() {
  const { messages, addMessage, documents, isGenerating, setGenerating } = useStore()
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isGenerating])

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 140) + 'px'
  }, [input])

  const submit = async () => {
    if (!input.trim() || isGenerating) return

    const userQuery = input.trim()
    setInput('')

    addMessage({ id: crypto.randomUUID(), role: 'user', content: userQuery })
    setGenerating(true)

    try {
      const hasDocs = documents.some(d => d.status === 'indexed')
      const assistantId = crypto.randomUUID()

      if (!hasDocs) {
        addMessage({
          id: assistantId,
          role: 'assistant',
          content: 'No indexed documents found. Upload and index a PDF first, then ask your question.',
          error: true,
        })
        return
      }

      const res = await sendChat({ query: userQuery })

      if (res.success && res.data?.answer) {
        addMessage({ id: assistantId, role: 'assistant', content: res.data.answer })
      } else {
        addMessage({
          id: assistantId,
          role: 'assistant',
          content: 'Received an unexpected response from the server. Please try again.',
          error: true,
        })
      }
    } catch (err: any) {
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: err?.message || 'Network error — check that the backend is running.',
        error: true,
      })
    } finally {
      setGenerating(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* Messages scroll area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-6 pt-6 scrollbar-hide" ref={scrollRef}>
        <div className="max-w-3xl mx-auto flex flex-col gap-4 pb-52">

          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="flex flex-col items-center justify-center mt-24 text-center select-none"
            >
              <div className="relative mb-5">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-primary/20 to-accent-success/10 border border-accent-primary/20 flex items-center justify-center">
                  <Sparkles size={22} className="text-accent-primary" />
                </div>
                <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-accent-success border-2 border-background" />
              </div>
              <h2 className="text-[17px] font-semibold text-text-primary mb-1.5">Ask me anything</h2>
              <p className="text-[13px] text-text-secondary max-w-xs leading-relaxed">
                Upload a PDF in the sidebar, then ask questions about its content.
              </p>
            </motion.div>
          ) : (
            messages.map(msg => <MessageBubble key={msg.id} message={msg} />)
          )}

          {/* Typing indicator bubble */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                key="typing"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-end gap-2.5"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent-primary/20 to-accent-success/10 border border-border-emphasized flex items-center justify-center shrink-0">
                  <Bot size={13} className="text-accent-primary" />
                </div>
                <div className="bg-background-card border border-border-subtle rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    {[0, 1, 2].map(i => (
                      <motion.span
                        key={i}
                        className="block w-1.5 h-1.5 rounded-full bg-text-tertiary"
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.7, repeat: Infinity, delay: i * 0.14, ease: 'easeInOut' }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>

      {/* Floating input bar */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background/95 to-transparent pt-10 pb-4 px-4 md:px-6">
        <div className="max-w-3xl mx-auto flex flex-col gap-2">

          {/* Suggestion chips — shown only on empty state */}
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-wrap gap-2 pb-1"
              >
                {SUGGESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => { setInput(q); textareaRef.current?.focus() }}
                    className="px-3.5 py-1.5 rounded-full bg-background-card hover:bg-background-hover text-[12px] text-text-secondary hover:text-text-primary transition-colors border border-border-subtle"
                  >
                    {q}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Input box */}
          <div className={cn(
            "relative flex items-end bg-background-card border rounded-2xl shadow-lg transition-all duration-200",
            isGenerating
              ? "border-border-subtle opacity-75"
              : "border-border-emphasized focus-within:border-accent-primary focus-within:ring-1 focus-within:ring-accent-primary/25"
          )}>
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isGenerating}
              placeholder={isGenerating ? 'Generating response…' : 'Ask about your documents…'}
              className="flex-1 resize-none bg-transparent px-4 py-3.5 text-[14px] outline-none text-text-primary placeholder:text-text-tertiary disabled:cursor-not-allowed leading-relaxed overflow-y-auto scrollbar-hide"
              style={{ maxHeight: 140 }}
            />
            <div className="p-2 shrink-0 flex items-end">
              <button
                onClick={submit}
                disabled={!input.trim() || isGenerating}
                className={cn(
                  "p-2 rounded-xl transition-all active:scale-95",
                  input.trim() && !isGenerating
                    ? "bg-accent-primary hover:bg-blue-500 text-white shadow-sm"
                    : "bg-background-hover text-text-tertiary cursor-not-allowed"
                )}
              >
                {isGenerating ? (
                  <motion.span
                    className="block w-[18px] h-[18px] border-2 border-text-tertiary border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
                  />
                ) : (
                  <Send size={16} />
                )}
              </button>
            </div>
          </div>

          <p className="text-center text-[11px] text-text-tertiary font-mono">
            Enter to send · Shift+Enter for new line
          </p>
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
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn('flex gap-2.5', isUser ? 'justify-end' : 'justify-start items-end')}
    >
      {/* Bot avatar */}
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent-primary/20 to-accent-success/10 border border-border-emphasized flex items-center justify-center shrink-0 mb-0.5">
          {message.error
            ? <AlertCircle size={13} className="text-accent-warning" />
            : <Bot size={13} className="text-accent-primary" />
          }
        </div>
      )}

      <div className={cn('max-w-[80%] flex flex-col gap-2', isUser ? 'items-end' : 'items-start')}>
        {/* Bubble */}
        <div className={cn(
          'px-4 py-3 text-[14px] leading-relaxed whitespace-pre-wrap break-words',
          isUser
            ? 'bg-accent-primary text-white rounded-2xl rounded-tr-sm shadow-md'
            : message.error
              ? 'bg-accent-warning/10 border border-accent-warning/25 text-text-primary rounded-2xl rounded-bl-sm'
              : 'bg-background-card border border-border-subtle text-text-primary rounded-2xl rounded-bl-sm'
        )}>
          {message.content}
        </div>

        {/* Citation accordion */}
        {message.citation && (
          <div className="w-full">
            <button
              onClick={() => setCitationExpanded(!citationExpanded)}
              className="flex items-center gap-2 text-[12px] text-text-secondary hover:text-text-primary transition-colors bg-background-card px-3 py-1.5 rounded-lg border border-border-subtle w-full"
            >
              <span>📌</span>
              <span className="flex-1 text-left truncate">
                {message.citation.file} · Page {message.citation.page}
              </span>
              <ChevronDown
                size={12}
                className={cn('shrink-0 transition-transform', citationExpanded && 'rotate-180')}
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
                  <div className="mt-1.5 p-3 bg-background-card border border-border-subtle border-l-2 border-l-accent-primary rounded-lg text-[12px] text-text-secondary font-mono leading-relaxed">
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
