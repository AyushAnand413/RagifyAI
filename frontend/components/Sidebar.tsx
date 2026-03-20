"use client"
import { useState, useRef } from 'react'
import { FileText, Trash2, Eye, UploadCloud, CheckCircle } from 'lucide-react'
import { useStore, type Document } from '../store/useStore'
import { cn } from '../lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

export function Sidebar() {
  const { documents, addDocument, removeDocument, updateDocument } = useStore()
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const simulateUpload = (file: File) => {
    const id = crypto.randomUUID()
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1) + ' MB'
    const newDoc: Document = {
      id,
      name: file.name,
      size: sizeMb,
      pages: Math.floor(Math.random() * 50) + 1, // Simulated
      indexedAt: 'Just now',
      status: 'uploading',
      progress: 0
    }
    
    addDocument(newDoc)

    // Simulate progress
    let prog = 0
    const interval = setInterval(() => {
      prog += 20
      if (prog <= 100) {
        updateDocument(id, { progress: prog })
      }
      
      if (prog === 40) updateDocument(id, { status: 'parsing' })
      if (prog === 60) updateDocument(id, { status: 'chunking' })
      if (prog === 80) updateDocument(id, { status: 'embedding' })
      if (prog >= 100) {
        updateDocument(id, { status: 'indexed', progress: 100 })
        clearInterval(interval)
      }
    }, 500)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    const pdfs = files.filter(f => f.type === 'application/pdf' || f.name.endsWith('.pdf'))
    pdfs.forEach(simulateUpload)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    files.forEach(simulateUpload)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="p-6 h-full flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-[14px] font-semibold text-text-primary">Uploaded Documents ({documents.length})</h2>
      </div>

      <div className="flex flex-col gap-3 flex-1 overflow-y-auto scrollbar-hide">
        <AnimatePresence>
          {documents.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center p-8 text-center"
            >
              <div className="w-12 h-12 rounded-full bg-background-hover flex items-center justify-center mb-4 text-text-tertiary">
                <FileText size={20} />
              </div>
              <p className="text-text-secondary text-[14px]">No documents yet</p>
              <p className="text-text-tertiary text-[13px] mt-1">Upload a PDF to start analyzing</p>
            </motion.div>
          )}

          {documents.map(doc => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="group relative bg-background-card border border-border-subtle rounded-md p-4 transition-all hover:-translate-y-1 hover:shadow-lg hover:border-border-emphasized overflow-hidden"
              style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="mt-1 text-accent-primary">
                    <FileText size={18} />
                  </div>
                  <div>
                    <h3 className="text-[14px] font-medium text-text-primary truncate max-w-[200px]" title={doc.name}>
                      {doc.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1 text-[13px] text-text-secondary">
                      <span>{doc.size}</span>
                      <span>•</span>
                      <span>{doc.pages} pages</span>
                    </div>
                    {doc.status !== 'indexed' ? (
                      <div className="mt-3">
                        <div className="flex justify-between text-[12px] text-text-tertiary mb-1 capitalize">
                          <span>{doc.status}...</span>
                          <span>{doc.progress}%</span>
                        </div>
                        <div className="w-full h-1 bg-border-subtle rounded-full overflow-hidden">
                          <motion.div 
                            className="h-full bg-accent-primary"
                            initial={{ width: 0 }}
                            animate={{ width: `${doc.progress}%` }}
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 mt-2 text-[12px] text-text-tertiary">
                        <CheckCircle size={12} className="text-accent-success" />
                        Indexed {doc.indexedAt}
                      </div>
                    )}
                  </div>
                </div>

                <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 absolute top-4 right-4 bg-background-card pl-2">
                  <button className="p-1.5 text-text-tertiary hover:text-accent-primary hover:bg-background rounded transition-colors" title="View Chunks">
                    <Eye size={16} />
                  </button>
                  <button 
                    onClick={() => removeDocument(doc.id)}
                    className="p-1.5 text-text-tertiary hover:text-accent-warning hover:bg-background rounded transition-colors" 
                    title="Remove"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "shrink-0 mt-4 border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-all duration-200",
          isDragging 
            ? "border-accent-primary bg-accent-primary/5" 
            : "border-border-emphasized hover:border-text-tertiary hover:bg-background-hover"
        )}
      >
        <UploadCloud className={cn("mb-2 transition-colors", isDragging ? "text-accent-primary" : "text-text-tertiary")} size={24} />
        <p className="text-[14px] font-medium text-text-primary mb-1">
          {isDragging ? 'Drop PDFs here' : 'Select or drag PDFs'}
        </p>
        <p className="text-[13px] text-text-tertiary font-mono">Max 10MB per file</p>
        <input 
          type="file" 
          accept="application/pdf" 
          multiple 
          className="hidden" 
          ref={fileInputRef}
          onChange={handleFileSelect}
        />
      </div>
    </div>
  )
}
