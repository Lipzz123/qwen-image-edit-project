import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Qwen Image Studio', description: 'AI image editing powered by Qwen Image Edit 2.1 on your own Colab runtime.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
