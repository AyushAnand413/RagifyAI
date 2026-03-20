"use client"
import { Settings, UploadCloud } from 'lucide-react'
import { useStore } from '../store/useStore'

export function Header() {
  const documents = useStore(state => state.documents)
  const indexedCount = documents.filter(d => d.status === 'indexed').length

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-border-subtle bg-background shrink-0">
      <div className="flex items-center">
        <h1 className="text-lg tracking-[0.12em] font-medium text-text-primary">Ragify·AI</h1>
      </div>
      
      <div className="hidden md:flex items-center gap-2 text-sm text-text-secondary">
        <span className="w-2 h-2 rounded-full bg-accent-success" />
        Connected • {documents.length} docs ({indexedCount} indexed)
      </div>

      <div className="flex items-center gap-3">
        <button 
          className="group flex items-center gap-2 bg-accent-primary hover:bg-blue-600 text-white px-4 py-2 rounded-[4px] text-[14px] font-medium transition-all active:scale-[0.98] shadow-sm"
        >
          <UploadCloud size={16} className="group-hover:translate-y-[-1px] transition-transform" />
          Upload
        </button>
        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-hover rounded-[4px] transition-colors">
          <Settings size={18} />
        </button>
      </div>
    </header>
  )
}
