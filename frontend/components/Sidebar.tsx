"use client"
import { useState, useRef } from 'react'
import { FileText, Trash2, UploadCloud, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { useStore, type Document } from '../store/useStore'
import { cn } from '../lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { uploadPdf } from '../lib/api/client'

const STATUS_LABEL: Record<Document['status'], string> = {
  uploading: 'Uploading',
  parsing: 'Parsing',
  chunking: 'Chunking',
  embedding: 'Embedding',
  indexed: 'Indexed',
  error: 'Error',
}

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

  const handleUpload = async (file: File) => {
    const id = crypto.randomUUID()
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1) + ' MB'
    const newDoc: Document = {
      id,
      name: file.name,
      size: sizeMb,
      pages: 1,
      indexedAt: 'Processing...',
      status: 'uploading',
      progress: 0,
    }

    addDocument(newDoc)
    updateDocument(id, { progress: 50, status: 'parsing' })

    try {
      const res = await uploadPdf(file)
      if (res.success) {
        updateDocument(id, {
          progress: 100,
          status: 'indexed',
          indexedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        })
      } else {
        updateDocument(id, { status: 'error', progress: 0 })
      }
    } catch {
      updateDocument(id, { status: 'error', progress: 0 })
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    Array.from(e.dataTransfer.files)
      .filter(f => f.type === 'application/pdf' || f.name.endsWith('.pdf'))
      .forEach(handleUpload)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files || []).forEach(handleUpload)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const indexedCount = documents.filter(d => d.status === 'indexed').length

  return (
    <div className="h-full flex flex-col gap-0">
      {/* Header */}
      <div className="px-5 pt-5 pb-4 border-b border-border-subtle shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-[13px] font-semibold text-text-primary tracking-wide uppercase">
            Documents
          </h2>
          {documents.length > 0 && (
            <span className="text-[11px] font-mono text-text-tertiary">
              {indexedCount}/{documents.length} indexed
            </span>
          )}
        </div>
      </div>

      {/* Upload zone */}
      <div className="px-4 pt-4 shrink-0">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "relative rounded-xl border-2 border-dashed p-5 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 group overflow-hidden",
            isDragging
              ? "border-accent-primary bg-accent-primary/5 scale-[1.01]"
              : "border-border-emphasized hover:border-text-tertiary hover:bg-background-hover"
          )}
        >
          {/* Glow on drag */}
          {isDragging && (
            <div className="absolute inset-0 bg-accent-primary/5 rounded-xl pointer-events-none" />
          )}

          <div className={cn(
            "w-10 h-10 rounded-xl mb-3 flex items-center justify-center transition-colors",
            isDragging ? "bg-accent-primary/10" : "bg-background-hover group-hover:bg-background-card"
          )}>
            <UploadCloud
              size={20}
              className={cn(
                "transition-all duration-200",
                isDragging
                  ? "text-accent-primary translate-y-[-2px]"
                  : "text-text-tertiary group-hover:text-text-secondary group-hover:translate-y-[-2px]"
              )}
            />
          </div>

          <p className={cn(
            "text-[13px] font-medium mb-0.5 transition-colors",
            isDragging ? "text-accent-primary" : "text-text-primary"
          )}>
            {isDragging ? 'Drop PDFs here' : 'Upload PDFs'}
          </p>
          <p className="text-[12px] text-text-tertiary">
            Drag & drop or click to browse
          </p>
          <div className="flex items-center gap-1.5 mt-2.5">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-background-card border border-border-subtle text-text-tertiary">
              PDF
            </span>
            <span className="text-[11px] text-text-tertiary">· max 10 MB</span>
          </div>

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

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-4 pt-4 pb-4 scrollbar-thin">
        <AnimatePresence mode="popLayout">
          {documents.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-10 text-center"
            >
              <div className="w-10 h-10 rounded-full bg-background-hover flex items-center justify-center mb-3 text-text-tertiary">
                <FileText size={18} />
              </div>
              <p className="text-text-secondary text-[13px]">No documents yet</p>
              <p className="text-text-tertiary text-[12px] mt-1">Upload a PDF above to start</p>
            </motion.div>
          ) : (
            documents.map(doc => (
              <motion.div
                key={doc.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.96 }}
                transition={{ duration: 0.18 }}
                className={cn(
                  "group relative rounded-xl p-3.5 mb-3 border transition-all",
                  doc.status === 'error'
                    ? "bg-accent-warning/5 border-accent-warning/20"
                    : "bg-background-card border-border-subtle hover:border-border-emphasized hover:shadow-md"
                )}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className={cn(
                    "mt-0.5 p-1.5 rounded-lg shrink-0",
                    doc.status === 'error'
                      ? "bg-accent-warning/10"
                      : doc.status === 'indexed'
                        ? "bg-accent-success/10"
                        : "bg-accent-primary/10"
                  )}>
                    <FileText
                      size={15}
                      className={cn(
                        doc.status === 'error'
                          ? "text-accent-warning"
                          : doc.status === 'indexed'
                            ? "text-accent-success"
                            : "text-accent-primary"
                      )}
                    />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-[13px] font-medium text-text-primary truncate leading-tight"
                      title={doc.name}
                    >
                      {doc.name}
                    </p>
                    <p className="text-[12px] text-text-tertiary mt-0.5">{doc.size}</p>

                    {/* Status */}
                    <div className="mt-2">
                      {doc.status === 'indexed' ? (
                        <div className="flex items-center gap-1.5">
                          <CheckCircle2 size={12} className="text-accent-success" />
                          <span className="text-[11px] text-text-tertiary">Indexed at {doc.indexedAt}</span>
                        </div>
                      ) : doc.status === 'error' ? (
                        <div className="flex items-center gap-1.5">
                          <AlertCircle size={12} className="text-accent-warning" />
                          <span className="text-[11px] text-accent-warning">Upload failed</span>
                        </div>
                      ) : (
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Loader2 size={11} className="text-accent-primary animate-spin" />
                              <span className="text-[11px] text-text-tertiary capitalize">
                                {STATUS_LABEL[doc.status]}…
                              </span>
                            </div>
                            <span className="text-[11px] text-text-tertiary font-mono">{doc.progress}%</span>
                          </div>
                          <div className="h-1 bg-border-subtle rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-accent-primary to-blue-400 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${doc.progress}%` }}
                              transition={{ duration: 0.4, ease: 'easeOut' }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Remove button */}
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="shrink-0 p-1.5 rounded-lg text-text-tertiary hover:text-accent-warning hover:bg-accent-warning/10 opacity-0 group-hover:opacity-100 transition-all"
                    title="Remove"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
