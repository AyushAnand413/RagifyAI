"use client"
import { Header } from '../components/Header'
import { Sidebar } from '../components/Sidebar'
import { ChatArea } from '../components/ChatArea'

export default function Home() {
  return (
    <main className="flex flex-col h-full w-full overflow-hidden bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden flex-col md:flex-row relative">
        {/* Left Pane (35%) */}
        <div className="w-full md:w-[35%] h-[40%] md:h-full border-b md:border-b-0 md:border-r border-border-subtle bg-background overflow-y-auto shrink-0 z-10">
          <Sidebar />
        </div>
        
        {/* Right Pane (65%) */}
        <div className="flex-1 h-[60%] md:h-full bg-background flex flex-col min-w-0 z-0 relative">
          <ChatArea />
        </div>
      </div>
    </main>
  )
}
