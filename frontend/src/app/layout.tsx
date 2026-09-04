import type { Metadata } from "next";
import { Manrope, Unbounded, JetBrains_Mono } from "next/font/google";
import './globals.css';
import { QueryProvider } from '@/providers/QueryProvider';
import { Header } from '@/components/layout/Header';

const manrope = Manrope({
  subsets: ['latin', 'cyrillic'],
  variable: '--font-manrope',
});

const unbounded = Unbounded({
  subsets: ['latin', 'cyrillic'],
  variable: '--font-unbounded',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin', 'cyrillic'],
  variable: '--font-jetbrains',
});

export const metadata: Metadata = {
  title: 'FileGuard — Управление файлами',
  description: 'Загрузка, обработка и сканирование файлов',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={`${manrope.variable} ${unbounded.variable} ${jetbrainsMono.variable}`}>
      <body>
        <QueryProvider>
          <Header />
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
