import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { cn } from '../lib/utils'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'RagifyAI Dashboard',
  description: 'Enterprise RAG interface tailored for sophisticated searching',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={cn(inter.variable, jetbrainsMono.variable)}>
      <body className="bg-background text-text-primary h-[calc(100dvh)] w-screen overflow-hidden flex flex-col font-sans antialiased text-[15px] leading-[22px]">
        {children}
      </body>
    </html>
  )
}
