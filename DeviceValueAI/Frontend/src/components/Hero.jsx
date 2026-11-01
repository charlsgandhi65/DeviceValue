import { motion } from 'framer-motion'
import { Brain, Layers, Sparkles } from 'lucide-react'

function LaptopIllustration() {
  return (
    <div className="relative mx-auto w-full max-w-md" aria-hidden>
      <div className="absolute inset-0 rounded-full bg-blue-500/20 blur-3xl" />
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="relative"
      >
        <svg viewBox="0 0 400 280" className="w-full drop-shadow-2xl">
          <defs>
            <linearGradient id="screenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1e3a5f" />
              <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>
            <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>
          <rect x="60" y="30" width="280" height="175" rx="12" fill="#1c2744" stroke="url(#accentGrad)" strokeWidth="2" />
          <rect x="72" y="42" width="256" height="140" rx="6" fill="url(#screenGrad)" />
          <rect x="88" y="58" width="100" height="8" rx="4" fill="#3b82f6" opacity="0.8" />
          <rect x="88" y="76" width="160" height="6" rx="3" fill="#64748b" opacity="0.5" />
          <rect x="88" y="90" width="140" height="6" rx="3" fill="#64748b" opacity="0.35" />
          <rect x="88" y="104" width="120" height="6" rx="3" fill="#64748b" opacity="0.35" />
          <circle cx="320" cy="170" r="4" fill="#8b5cf6" />
          <path d="M40 210 H360 L380 240 H20 Z" fill="#151d35" stroke="#334155" strokeWidth="1.5" />
          <rect x="170" y="218" width="60" height="8" rx="4" fill="#0f1629" />
        </svg>
      </motion.div>
    </div>
  )
}

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-24">
      <div className="gradient-mesh absolute inset-0 pointer-events-none" />
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:gap-16">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-blue-300">
            <Sparkles className="h-3.5 w-3.5" />
            Electronic Device Value Prediction System
          </p>
          <h1 className="font-display text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl lg:text-[3.25rem]">
            Know What Your Device Is Worth.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-slate-400">
            Estimate your laptop&apos;s value using machine learning and hardware specifications.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a
              href="#predictor"
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition hover:from-blue-500 hover:to-violet-500"
            >
              Predict Laptop Price
            </a>
            <a
              href="#overview"
              className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              How It Works
            </a>
          </div>
          <ul className="mt-10 flex flex-col gap-4 sm:flex-row sm:flex-wrap">
            <li className="flex items-center gap-3 text-sm text-slate-400">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/15 text-blue-400">
                <Brain className="h-4 w-4" />
              </span>
              ML-powered price estimation
            </li>
            <li className="flex items-center gap-3 text-sm text-slate-400">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-500/15 text-violet-400">
                <Layers className="h-4 w-4" />
              </span>
              Hardware-aware predictions
            </li>
          </ul>
        </motion.div>
        <LaptopIllustration />
      </div>
    </section>
  )
}
