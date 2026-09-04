export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b-2 border-ink bg-paper/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-3">
        {/* Логотип */}
        <a href="#" className="group flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl border-2 border-ink bg-ink shadow-brutal-xs transition-transform duration-150 group-hover:-rotate-6">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="size-5 text-lime"
              aria-hidden="true"
            >
              <path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6l7-3z" />
              <path d="M9.2 12.2l2 2 3.6-4" />
            </svg>
          </div>
          <div>
            <div className="font-display text-base font-extrabold tracking-tight">
              File<span className="text-coral">Guard</span>
            </div>
            <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink/50">
              secure file pipeline
            </div>
          </div>
        </a>

        <div className="flex items-center gap-3">
          <nav className="flex items-center gap-2">
            <a
              href="#files"
              className="rounded-full border-2 border-transparent px-4 py-1.5 text-sm font-bold transition-all duration-100 hover:border-ink hover:bg-lime hover:shadow-brutal-xs"
            >
              Файлы
            </a>
            <a
              href="#alerts"
              className="rounded-full border-2 border-transparent px-4 py-1.5 text-sm font-bold transition-all duration-100 hover:border-ink hover:bg-sun hover:shadow-brutal-xs"
            >
              Алерты
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}
