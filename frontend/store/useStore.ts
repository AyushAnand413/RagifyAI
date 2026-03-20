import { create } from 'zustand'

export interface Document {
  id: string;
  name: string;
  size: string;
  pages: number;
  indexedAt: string;
  status: 'uploading' | 'parsing' | 'chunking' | 'embedding' | 'indexed' | 'error';
  progress: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citation?: {
    file: string;
    page: number;
    text: string;
  };
  error?: boolean;
}

interface RagifyState {
  documents: Document[];
  messages: Message[];
  isUploading: boolean;
  isGenerating: boolean;
  addDocument: (doc: Document) => void;
  updateDocument: (id: string, updates: Partial<Document>) => void;
  removeDocument: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setUploading: (status: boolean) => void;
  setGenerating: (status: boolean) => void;
}

export const useStore = create<RagifyState>((set) => ({
  documents: [],
  messages: [],
  isUploading: false,
  isGenerating: false,
  addDocument: (doc) => set((state) => ({ documents: [...state.documents, doc] })),
  updateDocument: (id, updates) => set((state) => ({
    documents: state.documents.map(d => d.id === id ? { ...d, ...updates } : d)
  })),
  removeDocument: (id) => set((state) => ({
    documents: state.documents.filter(d => d.id !== id)
  })),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map(m => m.id === id ? { ...m, ...updates } : m)
  })),
  setUploading: (status) => set({ isUploading: status }),
  setGenerating: (status) => set({ isGenerating: status }),
}))
