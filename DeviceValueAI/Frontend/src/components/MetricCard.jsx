import { motion } from 'framer-motion'

export default function MetricCard({ icon: Icon, label, value, subtext, accent = 'blue' }) {
  const accentClasses =
    accent === 'violet'
      ? 'from-violet-500/20 to-transparent text-violet-400'
      : 'from-blue-500/20 to-transparent text-blue-400'

  return (
    <motion.article
      whileHover={{ y: -2 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className="card-glow rounded-2xl border border-white/5 bg-navy-800/60 p-5 backdrop-blur-sm"
    >
      <div className={`mb-3 inline-flex rounded-lg bg-gradient-to-br p-2.5 ${accentClasses}`}>
        {Icon && <Icon className="h-5 w-5" aria-hidden />}
      </div>
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-1 font-display text-2xl font-bold text-white">{value}</p>
      {subtext && <p className="mt-2 text-xs leading-relaxed text-slate-500">{subtext}</p>}
    </motion.article>
  )
}
