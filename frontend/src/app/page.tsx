import type { ReactNode } from 'react';
import { FileTable } from '@/components/features/files/FileTable';
import { AlertTable } from '@/components/features/alerts/AlertTable';

const MARQUEE_ITEMS = [
  'Антивирусное сканирование',
  'Обработка файлов',
  'Алерты безопасности',
  'Любые форматы',
  'Мониторинг 24/7',
];

interface StatCardProps {
  icon: ReactNode;
  label: string;
  description: string;
  accent: string;
  sticker: string;
  rotate: string;
}

function StatCard({ icon, label, description, accent, sticker, rotate }: StatCardProps) {
  return (
    <div
      className={`group rounded-2xl border-2 border-ink p-5 shadow-brutal transition-all duration-150 hover:-translate-y-1 hover:shadow-brutal-lg ${accent}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex size-11 items-center justify-center rounded-xl border-2 border-ink bg-white shadow-brutal-xs transition-transform duration-150 group-hover:-rotate-6">
          {icon}
        </div>
        <span
          className={`${rotate} rounded-md border-2 border-ink bg-white px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider shadow-brutal-xs`}
        >
          {sticker}
        </span>
      </div>
      <div className="mt-4 font-display text-xs font-bold uppercase leading-snug tracking-wide">
        {label}
      </div>
      <div className="mt-1 text-sm font-semibold text-ink/60">{description}</div>
    </div>
  );
}

function Marquee() {
  return (
    <div
      aria-hidden="true"
      className="mt-8 overflow-hidden rounded-full border-2 border-ink bg-ink py-2.5 shadow-brutal-sm"
    >
      <div className="flex w-max animate-marquee items-center">
        {[0, 1].map((half) => (
          <div key={half} className="flex items-center">
            {MARQUEE_ITEMS.map((item) => (
              <span
                key={`${half}-${item}`}
                className="flex items-center gap-5 pr-5 font-mono text-[11px] font-bold uppercase tracking-[0.3em] text-paper"
              >
                {item}
                <svg viewBox="0 0 20 20" fill="currentColor" className="size-3 shrink-0 text-lime">
                  <path d="M10 0l2.4 7.6L20 10l-7.6 2.4L10 20l-2.4-7.6L0 10l7.6-2.4L10 0z" />
                </svg>
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <main className="mx-auto max-w-7xl px-6 pb-10 pt-6">
      {/* Hero: заголовок слева, описание справа */}
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between lg:gap-10">
        <h1 className="max-w-3xl font-display text-3xl font-extrabold uppercase leading-[1.05] tracking-tight sm:text-5xl">
          Файлы под <span className="text-outline">контролем</span>
          <span className="text-coral">.</span>
        </h1>
        <p className="max-w-sm border-l-4 border-lime pl-4 text-base font-semibold text-ink/60 lg:mb-1.5">
          Загружайте файлы, отслеживайте статус обработки и просматривайте алерты
          безопасности — всё в одном месте.
        </p>
      </div>

      <Marquee />

      {/* Stats strip */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <StatCard
          accent="bg-lime"
          sticker="01"
          rotate="-rotate-2"
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor" className="size-5">
              <path d="M3 3.5A1.5 1.5 0 014.5 2h6.879a1.5 1.5 0 011.06.44l4.122 4.12A1.5 1.5 0 0117 7.622V16.5a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 013 16.5v-13z" />
            </svg>
          }
          label="Загрузка файлов"
          description="Поддержка любых форматов"
        />
        <StatCard
          accent="bg-sky"
          sticker="02"
          rotate="rotate-2"
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor" className="size-5">
              <path
                fillRule="evenodd"
                d="M10 1a4.5 4.5 0 00-4.5 4.5V9H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2v-6a2 2 0 00-2-2h-.5V5.5A4.5 4.5 0 0010 1zm3 8V5.5a3 3 0 10-6 0V9h6z"
                clipRule="evenodd"
              />
            </svg>
          }
          label="Антивирусное сканирование"
          description="Автоматическая проверка угроз"
        />
        <StatCard
          accent="bg-sun"
          sticker="03"
          rotate="-rotate-3"
          icon={
            <svg viewBox="0 0 20 20" fill="currentColor" className="size-5">
              <path
                fillRule="evenodd"
                d="M10 1a9 9 0 100 18A9 9 0 0010 1zm.75 13.5a.75.75 0 01-1.5 0v-5.5a.75.75 0 011.5 0v5.5zm-.75-8.5a1 1 0 100-2 1 1 0 000 2z"
                clipRule="evenodd"
              />
            </svg>
          }
          label="Алерты безопасности"
          description="Уведомления о найденных угрозах"
        />
      </div>

      {/* Tables */}
      <div className="mt-12 flex flex-col gap-12">
        <div id="files" className="scroll-mt-24">
          <FileTable />
        </div>
        <div id="alerts" className="scroll-mt-24">
          <AlertTable />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-14 flex flex-wrap items-center justify-between gap-3 border-t-2 border-ink pb-2 pt-5 font-mono text-[10px] font-bold uppercase tracking-[0.25em] text-ink/50">
        <span>FileGuard © 2026</span>
        <span>Upload → Scan → Alert</span>
      </footer>
    </main>
  );
}
