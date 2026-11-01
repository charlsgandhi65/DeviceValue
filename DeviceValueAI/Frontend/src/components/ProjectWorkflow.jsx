import { motion } from 'framer-motion'
import {
  ArrowRight,
  BarChart3,
  Cpu,
  Laptop,
  LineChart,
  Sparkles,
} from 'lucide-react'

const STEPS = [
  { step: 1, title: 'Enter specifications', text: 'User provides laptop brand, model, CPU, RAM, storage, GPU, and screen size.', icon: Laptop },
  { step: 2, title: 'Feature preparation', text: 'Inputs are validated and transformed to match the training pipeline (server-side).', icon: Cpu },
  { step: 3, title: 'ML pipeline', text: 'The trained scikit-learn pipeline processes encoded features.', icon: LineChart },
  { step: 4, title: 'Model inference', text: 'The tuned Random Forest regressor predicts price in EUR.', icon: BarChart3 },
  { step: 5, title: 'Display estimate', text: 'DeviceValue AI presents the estimate with context and disclaimers.', icon: Sparkles },
]

const TECH_STACK = [
  { name: 'React', role: 'Interactive UI & forms' },
  { name: 'Python', role: 'Training & API (planned)' },
  { name: 'scikit-learn', role: 'Random Forest model' },
  { name: 'Pandas', role: 'Data preparation' },
  { name: 'NumPy', role: 'Numerical operations' },
]

export default function ProjectWorkflow() {
  return (
    <>
      <section id="overview" className="section-anchor border-t border-white/5 py-20 sm:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <p className="text-sm font-medium uppercase tracking-wider text-violet-400">Overview</p>
          <h2 className="mt-2 font-display text-3xl font-bold text-white sm:text-4xl">How DeviceValue AI works</h2>
          <p className="mt-3 max-w-2xl text-slate-400">
            A streamlined flow from user input to model-backed price estimation, designed for clarity in academic
            presentation and future backend integration.
          </p>

          <ol className="mt-12 space-y-0">
            {STEPS.map((item, index) => (
              <motion.li
                key={item.step}
                initial={{ opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="relative flex gap-4 pb-10 last:pb-0 sm:gap-6"
              >
                {index < STEPS.length - 1 && (
                  <span
                    className="absolute left-5 top-12 hidden h-[calc(100%-2rem)] w-px bg-gradient-to-b from-blue-500/40 to-transparent sm:block"
                    aria-hidden
                  />
                )}
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600/30 to-violet-600/30 text-sm font-bold text-blue-300 ring-1 ring-white/10">
                  {item.step}
                </span>
                <div className="flex-1 rounded-2xl border border-white/5 bg-navy-800/40 p-5 sm:flex sm:items-start sm:gap-4">
                  <item.icon className="mb-3 h-6 w-6 text-blue-400 sm:mb-0 sm:shrink-0" aria-hidden />
                  <div>
                    <h3 className="font-display font-semibold text-white">{item.title}</h3>
                    <p className="mt-1 text-sm text-slate-500">{item.text}</p>
                  </div>
                  {index < STEPS.length - 1 && (
                    <ArrowRight className="ml-auto hidden h-5 w-5 text-slate-600 lg:block" aria-hidden />
                  )}
                </div>
              </motion.li>
            ))}
          </ol>
        </div>
      </section>

      <section id="about" className="section-anchor border-t border-white/5 py-20 sm:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid gap-12 lg:grid-cols-2">
            <div>
              <p className="text-sm font-medium uppercase tracking-wider text-blue-400">About Project</p>
              <h2 className="mt-2 font-display text-3xl font-bold text-white">Technology stack</h2>
              <p className="mt-3 text-slate-400">
                Built for Navrachana University&apos;s Data Science and Machine Learning capstone — combining modern
                frontend engineering with a reproducible ML workflow.
              </p>
              <ul className="mt-8 space-y-3">
                {TECH_STACK.map((tech) => (
                  <li
                    key={tech.name}
                    className="flex items-center justify-between rounded-xl border border-white/5 bg-navy-800/50 px-4 py-3"
                  >
                    <span className="font-medium text-white">{tech.name}</span>
                    <span className="text-sm text-slate-500">{tech.role}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-display text-xl font-semibold text-white">Device categories</h3>
              <p className="mt-2 text-sm text-slate-500">
                Modular architecture supports separate datasets and models per device type.
              </p>
              <div className="mt-6 space-y-4">
                <article className="card-glow flex items-start gap-4 rounded-2xl border border-emerald-500/20 bg-emerald-950/20 p-5">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/15">
                    <Laptop className="h-6 w-6 text-emerald-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-white">Laptops</h4>
                      <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-300">
                        Available
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      Random Forest price model trained on 3,363 laptop records — active in this
                      release.
                    </p>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
