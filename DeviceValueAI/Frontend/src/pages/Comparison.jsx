import { useState, useEffect, useMemo } from 'react'
import { Plus, Trash2, ArrowRight, CheckCircle2, Loader2, Home } from 'lucide-react'
import { Link } from 'react-router-dom'
import { INITIAL_FORM_STATE } from '../data/laptopOptions'
import { validateLaptopFormWithWarnings } from '../services/predictionService'
import {
  loadCSVData,
  getLaptopCascadingOptions,
  verifyCombinationExists,
} from '../services/csvDataService'
import { predictBatchLaptops, formatInr, formatEur } from '../services/predictionService'
import { estimateResaleValue } from '../services/resaleService'

const MAX_LAPTOPS = 3
const MIN_LAPTOPS = 2

function LaptopCard({ laptop, index, availableOptions, onUpdate, onRemove, canRemove, csvLoaded, errors }) {
  const isDisabled = (field) => {
    if (!csvLoaded) return true
    if (field === 'model') return !laptop.brand
    if (field === 'cpu') return !laptop.model
    if (field === 'gpu') return !laptop.cpu
    if (field === 'ram') return !laptop.gpu
    if (field === 'storageCapacityGb') return !laptop.ram
    if (field === 'storageType') return !laptop.storageCapacityGb
    if (field === 'screenSize') return !laptop.storageType
    return false
  }

  const updateField = (field, value) => {
    onUpdate(index, field, value)
  }

  const options = availableOptions || {
    brands: [],
    models: [],
    cpus: [],
    gpus: [],
    rams: [],
    storageCapacities: [],
    storageTypes: [],
    screenSizes: [],
  }

  return (
    <div className="card-glow rounded-2xl border border-white/5 bg-navy-800/40 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-white">Laptop {index + 1}</h3>
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="p-2 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition"
            title={`Remove Laptop ${index + 1}`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="space-y-3">
        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Brand *</label>
          <select
            disabled={!csvLoaded}
            className={`input-field ${!csvLoaded ? 'opacity-50' : ''}`}
            value={laptop.brand}
            onChange={(e) => updateField('brand', e.target.value)}
          >
            <option value="">Select brand</option>
            {options.brands.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Model *</label>
          <select
            disabled={isDisabled('model')}
            className={`input-field ${isDisabled('model') ? 'opacity-50' : ''}`}
            value={laptop.model}
            onChange={(e) => updateField('model', e.target.value)}
          >
            <option value="">{isDisabled('model') ? 'Select brand first' : 'Select model'}</option>
            {options.models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">CPU *</label>
          <select
            disabled={isDisabled('cpu')}
            className={`input-field ${isDisabled('cpu') ? 'opacity-50' : ''}`}
            value={laptop.cpu}
            onChange={(e) => updateField('cpu', e.target.value)}
          >
            <option value="">{isDisabled('cpu') ? 'Select model first' : 'Select CPU'}</option>
            {options.cpus.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">GPU *</label>
          <select
            disabled={isDisabled('gpu')}
            className={`input-field ${isDisabled('gpu') ? 'opacity-50' : ''}`}
            value={laptop.gpu}
            onChange={(e) => updateField('gpu', e.target.value)}
          >
            <option value="">{isDisabled('gpu') ? 'Select CPU first' : 'Select GPU'}</option>
            {options.gpus.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-200">RAM (GB) *</label>
            <select
              disabled={isDisabled('ram')}
              className={`input-field ${isDisabled('ram') ? 'opacity-50' : ''}`}
              value={laptop.ram}
              onChange={(e) => updateField('ram', e.target.value)}
            >
              <option value="">{isDisabled('ram') ? 'Select GPU first' : 'Select RAM'}</option>
              {options.rams.map((gb) => (
                <option key={gb} value={gb}>{gb} GB</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-200">Storage (GB) *</label>
            <select
              disabled={isDisabled('storageCapacityGb')}
              className={`input-field ${isDisabled('storageCapacityGb') ? 'opacity-50' : ''}`}
              value={laptop.storageCapacityGb}
              onChange={(e) => updateField('storageCapacityGb', e.target.value)}
            >
              <option value="">{isDisabled('storageCapacityGb') ? 'Select RAM first' : 'Select capacity'}</option>
              {options.storageCapacities.map((gb) => (
                <option key={gb} value={gb}>{gb >= 1024 ? `${gb / 1024} TB` : `${gb} GB`}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Storage Type *</label>
          <div className="flex gap-2">
            {(options.storageTypes.length > 0 ? options.storageTypes : ['SSD', 'HDD']).map((type) => (
              <label
                key={type}
                className={`flex-1 cursor-pointer rounded-lg border px-3 py-2 text-center text-sm font-medium transition ${
                  laptop.storageType === type
                    ? 'border-blue-500/50 bg-blue-500/15 text-blue-200'
                    : 'border-white/10 bg-navy-900/50 text-slate-400 hover:border-white/20'
                } ${isDisabled('storageType') ? 'pointer-events-none opacity-50' : ''}`}
              >
                <input
                  type="radio"
                  name={`storageType-${index}`}
                  className="sr-only"
                  value={type}
                  checked={laptop.storageType === type}
                  onChange={() => updateField('storageType', type)}
                  disabled={isDisabled('storageType')}
                />
                {type}
              </label>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Screen Size (inches) *</label>
          <select
            disabled={isDisabled('screenSize')}
            className={`input-field ${isDisabled('screenSize') ? 'opacity-50' : ''}`}
            value={laptop.screenSize}
            onChange={(e) => updateField('screenSize', e.target.value)}
          >
            <option value="">{isDisabled('screenSize') ? 'Select storage first' : 'Select size'}</option>
            {options.screenSizes.map((size) => (
              <option key={size} value={size}>{size}"</option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Condition</label>
          <select
            className="input-field"
            value={laptop.condition || ''}
            onChange={(e) => updateField('condition', e.target.value)}
          >
            <option value="">Select condition (optional)</option>
            <option value="new">New</option>
            <option value="excellent">Excellent</option>
            <option value="good">Good</option>
            <option value="fair">Fair</option>
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-200">Purchase Age (years)</label>
          <input
            type="number"
            min="0"
            max="10"
            step="0.5"
            className="input-field"
            placeholder="e.g., 2 (optional)"
            value={laptop.purchaseAge || ''}
            onChange={(e) => updateField('purchaseAge', e.target.value)}
          />
        </div>

        {errors[index] && (
          <p className="text-xs text-red-400" role="alert">{errors[index]}</p>
        )}
      </div>
    </div>
  )
}


export default function Comparison() {
  const [laptops, setLaptops] = useState([
    { ...INITIAL_FORM_STATE, condition: '', purchaseAge: '' },
    { ...INITIAL_FORM_STATE, condition: '', purchaseAge: '' }
  ])
  const [csvLoaded, setCsvLoaded] = useState(false)
  const [errors, setErrors] = useState({})
  const [comparing, setComparing] = useState(false)
  const [results, setResults] = useState(null)
  const [resaleResults, setResaleResults] = useState([])

  useEffect(() => {
    loadCSVData().then(() => {
      setCsvLoaded(true)
    })
  }, [])

  // Calculate independent cascading options for each laptop card
  const availableOptionsPerLaptop = useMemo(() => {
    if (!csvLoaded) return laptops.map(() => null)
    return laptops.map((laptop) => getLaptopCascadingOptions(laptop))
  }, [laptops, csvLoaded])

  function updateLaptop(index, field, value) {
    setLaptops(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: value }

      // Reset downstream fields strictly in order:
      // Brand -> Model -> CPU -> GPU -> RAM -> Storage Capacity -> Storage Type -> Screen Size
      if (field === 'brand') {
        updated[index].model = ''
        updated[index].cpu = ''
        updated[index].gpu = ''
        updated[index].ram = ''
        updated[index].storageCapacityGb = ''
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'model') {
        updated[index].cpu = ''
        updated[index].gpu = ''
        updated[index].ram = ''
        updated[index].storageCapacityGb = ''
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'cpu') {
        updated[index].gpu = ''
        updated[index].ram = ''
        updated[index].storageCapacityGb = ''
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'gpu') {
        updated[index].ram = ''
        updated[index].storageCapacityGb = ''
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'ram') {
        updated[index].storageCapacityGb = ''
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'storageCapacityGb') {
        updated[index].storageType = ''
        updated[index].screenSize = ''
      } else if (field === 'storageType') {
        updated[index].screenSize = ''
      }

      return updated
    })
    setErrors(prev => {
      const next = { ...prev }
      delete next[index]
      return next
    })
  }

  function addLaptop() {
    if (laptops.length < MAX_LAPTOPS) {
      setLaptops(prev => [...prev, { ...INITIAL_FORM_STATE, condition: '', purchaseAge: '' }])
      setResults(null)
      setResaleResults([])
    }
  }

  function removeLaptop(index) {
    if (laptops.length > MIN_LAPTOPS) {
      setLaptops(prev => prev.filter((_, i) => i !== index))
      setResults(null)
      setResaleResults([])
    }
  }

  async function handleCompare() {
    // Validate all laptops
    const newErrors = {}
    const validLaptops = []

    laptops.forEach((laptop, index) => {
      const selections = {
        brand: laptop.brand,
        model: laptop.model,
        cpu: laptop.cpu,
        gpu: laptop.gpu,
        ram: laptop.ram ? Number(laptop.ram) : null,
        storageCapacityGb: laptop.storageCapacityGb ? Number(laptop.storageCapacityGb) : null,
        storageType: laptop.storageType,
        screenSize: laptop.screenSize ? Number(laptop.screenSize) : null,
      }

      if (!verifyCombinationExists(selections)) {
        newErrors[index] = 'This hardware combination does not exist in the dataset.'
        return
      }

      const { errors: validationErrors } = validateLaptopFormWithWarnings(laptop)
      if (Object.keys(validationErrors).length > 0) {
        newErrors[index] = Object.values(validationErrors).join(', ')
        return
      }

      validLaptops.push(laptop)
    })

    setErrors(newErrors)

    if (Object.keys(newErrors).length > 0) {
      return
    }

    if (validLaptops.length < MIN_LAPTOPS) {
      alert(`Please configure at least ${MIN_LAPTOPS} laptops to compare.`)
      return
    }

    setComparing(true)
    setResults(null)
    setResaleResults([null, null, null])

    try {
      // Get ML predictions
      const predictions = await predictBatchLaptops(validLaptops)
      setResults(predictions)

      // Get resale estimates for each laptop
      const resalePromises = validLaptops.map(async (laptop, idx) => {
        try {
          const payload = {
            brand: laptop.brand,
            model: laptop.model,
            cpu: laptop.cpu,
            ram: Number(laptop.ram),
            gpu: laptop.gpu,
            storage_capacity_gb: Number(laptop.storageCapacityGb),
            storage_type: laptop.storageType,
            screen_size: Number(laptop.screenSize),
            device_age_years: laptop.purchaseAge ? Number(laptop.purchaseAge) : null,
            physical_condition: laptop.condition || null,
          }
          const resale = await estimateResaleValue(payload)
          return resale
        } catch (err) {
          console.error(`Resale estimate failed for laptop ${idx}:`, err)
          return null
        }
      })

      const resaleData = await Promise.all(resalePromises)
      setResaleResults(resaleData)
    } catch (err) {
      alert(`Comparison failed: ${err.message}`)
    } finally {
      setComparing(false)
    }
  }

  function generateRecommendation() {
    if (!results || results.length === 0) return null

    // Simple recommendation logic based on price and specs
    const scored = results.map((result, idx) => {
      const laptop = laptops[idx]
      let score = 0
      let reasons = []

      // Higher RAM = better
      const ram = Number(laptop.ram) || 0
      if (ram >= 16) {
        score += 2
        reasons.push('High RAM for multitasking')
      } else if (ram >= 8) {
        score += 1
      }

      // SSD is better
      if (laptop.storageType === 'SSD') {
        score += 1
        reasons.push('Fast SSD storage')
      }

      // Dedicated GPU
      if (laptop.gpu && (laptop.gpu.toLowerCase().includes('nvidia') || laptop.gpu.toLowerCase().includes('amd'))) {
        score += 2
        reasons.push('Dedicated graphics for gaming/design')
      }

      // Price value (lower price per performance is better)
      const pricePerRam = result.priceEur / ram
      if (pricePerRam < 100) {
        score += 1
        reasons.push('Good value for money')
      }

      return { index: idx, score, reasons, priceEur: result.priceEur }
    })

    scored.sort((a, b) => b.score - a.score)

    const best = scored[0]
    return {
      laptopIndex: best.index,
      reasons: best.reasons,
      priceEur: best.priceEur
    }
  }

  const recommendation = results ? generateRecommendation() : null

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100">
      <header className="border-b border-white/5 bg-navy-950/90 backdrop-blur-md">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-4">
          <Link to="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition">
            <Home className="h-5 w-5" />
            <span className="text-sm font-medium">Back to Home</span>
          </Link>
          <span className="font-display text-lg font-semibold text-white">
            DeviceValue <span className="text-blue-400">AI</span>
          </span>
        </nav>
      </header>

      <main className="mx-auto max-w-7xl px-4 sm:px-6 py-12">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-white sm:text-4xl">Laptop Comparison</h1>
          <p className="mt-2 text-slate-400">
            Compare {MIN_LAPTOPS} to {MAX_LAPTOPS} laptops side by side with ML price predictions and resale estimates.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {laptops.map((laptop, index) => (
            <LaptopCard
              key={index}
              laptop={laptop}
              index={index}
              availableOptions={availableOptionsPerLaptop[index]}
              onUpdate={updateLaptop}
              onRemove={removeLaptop}
              canRemove={laptops.length > MIN_LAPTOPS}
              csvLoaded={csvLoaded}
              errors={errors}
            />
          ))}

          {laptops.length < MAX_LAPTOPS && (
            <button
              type="button"
              onClick={addLaptop}
              className="card-glow flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-navy-800/40 p-6 hover:border-white/20 transition min-h-[500px]"
            >
              <Plus className="h-12 w-12 text-slate-500 mb-4" />
              <span className="text-slate-400">Add Laptop</span>
            </button>
          )}
        </div>

        <div className="mt-8 flex justify-center">
          <button
            onClick={handleCompare}
            disabled={comparing || laptops.length < MIN_LAPTOPS}
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:from-blue-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {comparing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Comparing...
              </>
            ) : (
              <>
                <ArrowRight className="h-4 w-4" />
                Compare Laptops
              </>
            )}
          </button>
        </div>

        {results && (
          <div className="mt-12 space-y-8">
            <h2 className="font-display text-2xl font-bold text-white">Comparison Results</h2>

            {/* Recommendation */}
            {recommendation && (
              <div className="card-glow rounded-2xl border border-green-500/20 bg-green-500/10 p-6">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-400 shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-green-200 text-lg">Recommendation</h3>
                    <p className="mt-2 text-green-300/90">
                      Based on specifications and value, <strong>Laptop {recommendation.laptopIndex + 1}</strong> appears to be the best choice.
                    </p>
                    <ul className="mt-3 space-y-1">
                      {recommendation.reasons.map((reason, idx) => (
                        <li key={idx} className="text-sm text-green-300/80 flex items-center gap-2">
                          <span className="text-green-400">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Comparison Table */}
            <div className="card-glow overflow-x-auto rounded-2xl border border-white/5 bg-navy-800/40">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-white">Specification</th>
                    {results.map((_, idx) => (
                      <th key={idx} className="px-6 py-4 text-left text-sm font-semibold text-white">
                        Laptop {idx + 1}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">Brand</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.brand}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">Model</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.model}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">CPU</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.cpu}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">GPU</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.gpu}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">RAM</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.ram} GB</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">Storage</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">
                        {laptop.storageCapacityGb >= 1024 ? `${laptop.storageCapacityGb / 1024} TB` : `${laptop.storageCapacityGb} GB`} {laptop.storageType}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="px-6 py-4 text-sm text-slate-400">Screen Size</td>
                    {laptops.map((laptop, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm text-white">{laptop.screenSize}"</td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5 bg-blue-500/5">
                    <td className="px-6 py-4 text-sm font-semibold text-blue-300">Predicted Price (New)</td>
                    {results.map((result, idx) => (
                      <td key={idx} className="px-6 py-4 text-sm font-semibold text-white">
                        <div>{formatEur(result.priceEur)}</div>
                        <div className="text-slate-400 text-xs">{formatInr(result.priceInr)}</div>
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-white/5 bg-violet-500/5">
                    <td className="px-6 py-4 text-sm font-semibold text-violet-300">Resale Estimate</td>
                    {results.map((_, idx) => {
                      const resale = resaleResults[idx]
                      return (
                        <td key={idx} className="px-6 py-4 text-sm text-white">
                          {resale && resale.status === 'success' ? (
                            <div>
                              <div className="font-semibold">{formatInr(resale.estimated_range_min_inr)} - {formatInr(resale.estimated_range_max_inr)}</div>
                              <div className="text-slate-400 text-xs">{resale.comparable_listings_count} listings</div>
                            </div>
                          ) : resale && resale.status === 'insufficient_data' ? (
                            <span className="text-slate-500 text-xs">Insufficient data</span>
                          ) : resale && resale.status === 'error' ? (
                            <span className="text-slate-500 text-xs" title={resale.error_message}>
                              Unavailable
                            </span>
                          ) : (
                            <span className="text-slate-500 text-xs">Not available</span>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Limitations */}
            <div className="rounded-lg border border-white/5 bg-navy-900/30 p-4">
              <p className="text-xs font-medium text-slate-400 mb-2">Limitations:</p>
              <ul className="space-y-1">
                <li className="text-xs text-slate-500">• Predicted prices are estimates based on the ML model training data</li>
                <li className="text-xs text-slate-500">• Resale estimates are based on asking prices, not confirmed sale prices</li>
                <li className="text-xs text-slate-500">• Actual prices may vary by retailer, location, and market conditions</li>
                <li className="text-xs text-slate-500">• Recommendation is based on simplified scoring, not comprehensive benchmarking</li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
