"use client"
import { Settings } from 'lucide-react'
import { useStore } from '../store/useStore'

export function Header() {
  const documents = useStore(state => state.documents)
  const indexedCount = documents.filter(d => d.status === 'indexed').length
  return (
    <header className="h-14 flex items-center justify-between px-5 border-b border-border-subtle bg-background shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-accent-primary to-blue-400 flex items-center justify-center shrink-0">
          <span className="text-[10px] font-bold text-white leading-none">R</span>
        </div>
        <h1 className="text-[15px] font-semibold text-text-primary tracking-tight">
          Ragify<span className="text-accent-primary">·</span>AI
        </h1>
      </div>

      {/* Status indicator */}
      <div className="hidden md:flex items-center gap-2 text-[12px] text-text-secondary">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-success opacity-60" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-success" />
        </span>
        <span>Connected</span>
        {documents.length > 0 && (
          <>
            <span className="text-border-emphasized">·</span>
            <span className="font-mono">{indexedCount}/{documents.length} docs</span>
          </>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-hover rounded-lg transition-colors">
          <Settings size={16} />
        </button>
      </div>
    </header>
  )
}
