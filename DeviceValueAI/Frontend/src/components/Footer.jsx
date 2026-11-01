import { Cpu } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-navy-950 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-6 px-4 sm:flex-row sm:px-6">
        <div className="flex items-center gap-2 text-slate-400">
          <Cpu className="h-5 w-5 text-blue-500" aria-hidden />
          <span className="text-sm">
            <span className="font-medium text-slate-300">DeviceValue AI</span> — Electronic Device Value Prediction
            System
          </span>
        </div>
        <p className="text-center text-xs text-slate-600">
          Academic project · Data Science &amp; Machine Learning · Navrachana University
        </p>
      </div>
    </footer>
  )
}
