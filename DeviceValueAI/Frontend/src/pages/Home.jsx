import { useCallback, useRef, useState } from 'react'
import Footer from '../components/Footer'
import Hero from '../components/Hero'
import Navbar from '../components/Navbar'
import PredictorForm from '../components/PredictorForm'
import PredictionResult from '../components/PredictionResult'
import ProjectWorkflow from '../components/ProjectWorkflow'
import { INITIAL_FORM_STATE } from '../data/laptopOptions'
import { predictLaptopPrice } from '../services/predictionService'

export default function Home() {
  const [form, setForm] = useState({ ...INITIAL_FORM_STATE })
  const [resultState, setResultState] = useState({ status: 'idle' })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const resultRef = useRef(null)

  const handleReset = useCallback(() => {
    setForm({ ...INITIAL_FORM_STATE })
    setResultState({ status: 'idle' })
    setResult(null)
    setError('')
  }, [])

  const handleSubmit = useCallback(async (formValues) => {
    setResultState({ status: 'loading' })
    setError('')
    setResult(null)

    resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })

    try {
      const prediction = await predictLaptopPrice(formValues, { mode: 'api' })
      setResult(prediction)
      setResultState({ status: 'success' })
    } catch (err) {
      setError(err.message || 'Unable to complete prediction. Ensure the backend is running.')
      setResultState({ status: 'error' })
    }
  }, [])

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100">
      <Navbar />
      <main>
        <Hero />

        <section id="predictor" className="section-anchor border-t border-white/5 py-16 sm:py-20">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mb-10 max-w-2xl">
              <p className="text-sm font-medium uppercase tracking-wider text-blue-400">DeviceValue AI</p>
              <h2 className="mt-2 font-display text-3xl font-bold text-white sm:text-4xl">Laptop Valuation Tools</h2>
              <p className="mt-3 text-slate-400">
                Machine learning price estimation based on hardware specifications and market benchmarks. Connect{' '}
                <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs text-violet-300">VITE_API_BASE_URL</code>{' '}
                to route requests to your FastAPI backend serving{' '}
                <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs text-violet-300">final_laptop_price_model.joblib</code>.
              </p>
            </div>

            <div className="grid gap-8 lg:grid-cols-2 lg:items-start">
              <PredictorForm
                form={form}
                setForm={setForm}
                onSubmit={handleSubmit}
                onReset={handleReset}
              />
              <div ref={resultRef}>
                <PredictionResult
                  state={resultState}
                  result={result}
                  error={error}
                  onReset={handleReset}
                />
              </div>
            </div>
          </div>
        </section>

        <ProjectWorkflow />
      </main>
      <Footer />
    </div>
  )
}
