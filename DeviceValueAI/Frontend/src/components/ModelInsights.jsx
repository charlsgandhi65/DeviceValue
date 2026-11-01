import { motion } from 'framer-motion'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  METRIC_EXPLANATIONS,
  MODEL_INFO,
  SPLIT_CHART_DATA,
  TEST_ERROR_CHART_DATA,
} from '../data/modelMetrics'
import MetricCard from './MetricCard'
import { Activity, Database, Divide, Target, TreeDeciduous } from 'lucide-react'

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-navy-800 px-3 py-2 text-xs shadow-xl">
      <p className="font-medium text-white">{label ?? payload[0].name}</p>
      <p className="text-slate-400">{payload[0].value}</p>
    </div>
  )
}

export default function ModelInsights() {
  return (
    <section id="insights" className="section-anchor py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="text-sm font-medium uppercase tracking-wider text-blue-400">Model Insights</p>
          <h2 className="mt-2 font-display text-3xl font-bold text-white sm:text-4xl">
            Evaluation on held-out test data
          </h2>
          <p className="mt-3 max-w-3xl text-slate-400">
            {METRIC_EXPLANATIONS.disclaimer}
          </p>
        </motion.div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            icon={TreeDeciduous}
            label="Model"
            value={MODEL_INFO.name}
            accent="blue"
          />
          <MetricCard
            icon={Target}
            label="MAE (test set)"
            value={`€${MODEL_INFO.maeEur.toFixed(2)}`}
            subtext={METRIC_EXPLANATIONS.mae}
            accent="violet"
          />
          <MetricCard
            icon={Activity}
            label="RMSE (test set)"
            value={`€${MODEL_INFO.rmseEur.toFixed(2)}`}
            subtext={METRIC_EXPLANATIONS.rmse}
            accent="blue"
          />
          <MetricCard
            icon={Divide}
            label="R² (test set)"
            value={MODEL_INFO.r2.toFixed(4)}
            subtext={METRIC_EXPLANATIONS.r2}
            accent="violet"
          />
          <MetricCard
            icon={Database}
            label="Dataset"
            value={`${MODEL_INFO.datasetRecords.toLocaleString()} records`}
            subtext={`${MODEL_INFO.trainSplitPercent}% train · ${MODEL_INFO.testSplitPercent}% test (${MODEL_INFO.testRecords} test records)`}
            accent="blue"
          />
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          <article className="card-glow rounded-2xl border border-white/5 bg-navy-800/40 p-6">
            <h3 className="font-display text-lg font-semibold text-white">Test-set error magnitudes (EUR)</h3>
            <p className="mt-1 text-xs text-slate-500">
              Documented MAE and RMSE only — not fabricated feature importance or training curves.
            </p>
            <div className="mt-6 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={TEST_ERROR_CHART_DATA} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    unit=" €"
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={80}>
                    {TEST_ERROR_CHART_DATA.map((entry) => (
                      <Cell key={entry.metric} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="card-glow rounded-2xl border border-white/5 bg-navy-800/40 p-6">
            <h3 className="font-display text-lg font-semibold text-white">Train / test split</h3>
            <p className="mt-1 text-xs text-slate-500">
              80% training ({MODEL_INFO.datasetRecords - MODEL_INFO.testRecords} records) and 20% test (
              {MODEL_INFO.testRecords} records).
            </p>
            <div className="mt-6 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={SPLIT_CHART_DATA}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                  >
                    {SPLIT_CHART_DATA.map((entry) => (
                      <Cell key={entry.name} fill={entry.fill} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ul className="mt-2 flex flex-wrap justify-center gap-4 text-xs text-slate-400">
              {SPLIT_CHART_DATA.map((d) => (
                <li key={d.name} className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: d.fill }} />
                  {d.name}: {d.value}
                </li>
              ))}
            </ul>
          </article>
        </div>
      </div>
    </section>
  )
}
