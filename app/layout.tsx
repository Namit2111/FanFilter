import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Fanfilter',
  description: 'Fanfilter',
  generator: 'Fanfilter',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
