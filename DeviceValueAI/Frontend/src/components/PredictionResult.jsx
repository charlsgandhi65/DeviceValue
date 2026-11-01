import { motion } from 'framer-motion'
import { AlertCircle, Loader2, RotateCcw, Sparkles } from 'lucide-react'
import { formatEur, formatInr } from '../services/predictionService'

function SpecRow({ label, value }) {
  return (
    <div className="flex justify-between gap-4 border-b border-white/5 py-2 text-sm last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium text-slate-200">{value}</span>
    </div>
  )
}

export default function PredictionResult({ state, result, error, onReset }) {
  const { status } = state

  if (status === 'idle') {
    return (
      <div className="card-glow flex h-full min-h-[420px] flex-col items-center justify-center rounded-2xl border border-white/5 bg-navy-800/40 p-8 text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/20 to-violet-500/20">
          <Sparkles className="h-7 w-7 text-blue-400" />
        </div>
        <h3 className="font-display text-xl font-semibold text-white">Your estimate will appear here</h3>
        <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-500">
          Complete the laptop specification form and select <strong className="font-medium text-slate-400">Estimate Device Value</strong> to generate a price prediction using the trained ML model.
        </p>
      </div>
    )
  }

  if (status === 'loading') {
    return (
      <div className="card-glow flex h-full min-h-[420px] flex-col items-center justify-center rounded-2xl border border-white/5 bg-navy-800/40 p-8">
        <Loader2 className="h-10 w-10 animate-spin text-blue-400" aria-hidden />
        <p className="mt-4 text-sm text-slate-400">Preparing estimate…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="card-glow rounded-2xl border border-red-500/20 bg-red-950/20 p-8">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 shrink-0 text-red-400" />
          <div>
            <h3 className="font-semibold text-red-200">Something went wrong</h3>
            <p className="mt-1 text-sm text-red-300/80">{error}</p>
            <button
              type="button"
              onClick={onReset}
              className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-blue-400 hover:text-blue-300"
            >
              <RotateCcw className="h-4 w-4" />
              Try again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!result) return null

  const { payload, priceEur, priceInr, demoNotice, mode } = result

  const storageDisplay =
    payload.storage ||
    (payload.storage_capacity_gb != null
      ? `${Number(payload.storage_capacity_gb) >= 1024 ? `${Number(payload.storage_capacity_gb) / 1024} TB` : `${payload.storage_capacity_gb} GB`} ${payload.storage_type || ''}`.trim()
      : '—')

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-glow rounded-2xl border border-white/5 bg-navy-800/50 p-6 sm:p-8"
    >
      {mode === 'demo' && (
        <span className="mb-4 inline-block rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200">
          Demo preview — not model output
        </span>
      )}

      <p className="text-sm font-medium text-slate-400">Estimated value</p>
      <p className="mt-2 font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
        {priceInr != null ? formatInr(priceInr) : '—'}
      </p>
      {priceInr != null && (
        <p className="mt-1 text-xs text-slate-500">
          INR converted at a standard benchmark rate (₹90 / €1).
        </p>
      )}

      {priceEur != null && (
        <p className="mt-3 text-sm text-slate-400">
          Reference (EUR): <span className="font-medium text-slate-300">{formatEur(priceEur)}</span>
          <span className="text-slate-600"> · training target currency</span>
        </p>
      )}

      {demoNotice && (
        <p className="mt-4 rounded-lg border border-white/5 bg-navy-900/80 p-3 text-xs leading-relaxed text-slate-500">
          {demoNotice}
        </p>
      )}

      <div className="mt-6">
        <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Submitted specifications
        </h4>
        <div className="rounded-xl bg-navy-950/50 px-4 py-2">
          <SpecRow label="Brand" value={payload.brand} />
          <SpecRow label="Model" value={payload.model} />
          <SpecRow label="CPU" value={payload.cpu} />
          <SpecRow label="RAM" value={`${payload.ram} GB`} />
          <SpecRow label="Storage" value={storageDisplay} />
          <SpecRow label="GPU" value={payload.gpu} />
          <SpecRow label="Screen" value={`${payload.screen_size}"`} />
        </div>
      </div>

      <p className="mt-6 text-xs leading-relaxed text-slate-500">
        This estimate is based on historical training data and model inference. It is not a live market quotation,
        appraisal, or guaranteed selling price. Actual resale value depends on condition, region, and demand.
      </p>

      <button
        type="button"
        onClick={onReset}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-2.5 text-sm font-medium text-white transition hover:bg-white/10 sm:w-auto sm:px-5"
      >
        <RotateCcw className="h-4 w-4" />
        Reset & try again
      </button>
    </motion.div>
  )
}
