import { useState, useEffect, useMemo } from 'react'
import { RotateCcw, Search, ExternalLink, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { INITIAL_FORM_STATE } from '../data/laptopOptions'
import { validateLaptopFormWithWarnings } from '../services/predictionService'
import {
  loadCSVData,
  getLaptopCascadingOptions,
  verifyCombinationExists,
} from '../services/csvDataService'
import { estimateResaleValue, formatInr } from '../services/resaleService'

function FormSection({ title, description, children }) {
  return (
    <fieldset className="space-y-4 rounded-xl border border-white/5 bg-navy-950/30 p-5">
      <legend className="px-1">
        <span className="font-display text-base font-semibold text-white">{title}</span>
        {description && <p className="mt-0.5 text-xs text-slate-500">{description}</p>}
      </legend>
      {children}
    </fieldset>
  )
}

function FieldWarning({ message }) {
  if (!message) return null
  return (
    <p className="text-xs text-amber-400/90" role="status">
      {message}
    </p>
  )
}

export default function ResaleEstimator() {
  const [form, setForm] = useState({ ...INITIAL_FORM_STATE })
  const [errors, setErrors] = useState({})
  const [warnings, setWarnings] = useState({})
  const [csvLoaded, setCsvLoaded] = useState(false)
  const availableOptions = useMemo(
    () =>
      csvLoaded
        ? getLaptopCascadingOptions(form)
        : {
            brands: [],
            models: [],
            cpus: [],
            gpus: [],
            rams: [],
            storageCapacities: [],
            storageTypes: [],
            screenSizes: [],
          },
    [csvLoaded, form],
  )

  // Resale-specific fields
  const [deviceAge, setDeviceAge] = useState('')
  const [physicalCondition, setPhysicalCondition] = useState('')
  const [batteryHealth, setBatteryHealth] = useState('')

  // Result state
  const [resultState, setResultState] = useState({ status: 'idle' })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Load CSV data on mount
  useEffect(() => {
    loadCSVData().then(() => {
      setCsvLoaded(true)
    })
  }, [])

  function clearFieldFeedback(field) {
    setErrors((prev) => {
      const next = { ...prev }
      delete next[field]
      return next
    })
    setWarnings((prev) => {
      const next = { ...prev }
      delete next[field]
      delete next.form
      return next
    })
  }

  function updateField(field, value) {
    setForm((prev) => {
      const updated = { ...prev, [field]: value }

      // Reset downstream fields that depend on this field
      if (field === 'brand') {
        updated.model = ''
        updated.cpu = ''
        updated.gpu = ''
        updated.ram = ''
        updated.storageCapacityGb = ''
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'model') {
        updated.cpu = ''
        updated.gpu = ''
        updated.ram = ''
        updated.storageCapacityGb = ''
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'cpu') {
        updated.gpu = ''
        updated.ram = ''
        updated.storageCapacityGb = ''
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'gpu') {
        updated.ram = ''
        updated.storageCapacityGb = ''
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'ram') {
        updated.storageCapacityGb = ''
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'storageCapacityGb') {
        updated.storageType = ''
        updated.screenSize = ''
      } else if (field === 'storageType') {
        updated.screenSize = ''
      }

      return updated
    })
    clearFieldFeedback(field)
  }

  async function handleSubmit(e) {
    e.preventDefault()

    // Verify combination exists in CSV
    const selections = {
      brand: form.brand,
      model: form.model,
      cpu: form.cpu,
      gpu: form.gpu,
      ram: form.ram ? Number(form.ram) : null,
      storageCapacityGb: form.storageCapacityGb ? Number(form.storageCapacityGb) : null,
      storageType: form.storageType,
      screenSize: form.screenSize ? Number(form.screenSize) : null,
    }

    if (!verifyCombinationExists(selections)) {
      setErrors({
        form: 'This hardware combination does not exist in the dataset. Please select compatible options.',
      })
      return
    }

    const { errors: validationErrors, warnings: validationWarnings } = validateLaptopFormWithWarnings(form)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      setWarnings(validationWarnings)
      return
    }
    setErrors({})
    setWarnings(validationWarnings)

    // Start loading
    setResultState({ status: 'loading' })
    setError('')
    setResult(null)

    try {
      const payload = {
        brand: form.brand,
        model: form.model,
        cpu: form.cpu,
        ram: Number(form.ram),
        gpu: form.gpu,
        storage_capacity_gb: Number(form.storageCapacityGb),
        storage_type: form.storageType,
        screen_size: Number(form.screenSize),
        device_age_years: deviceAge ? Number(deviceAge) : null,
        physical_condition: physicalCondition || null,
        battery_health: batteryHealth || null,
      }

      const response = await estimateResaleValue(payload)
      setResult(response)

      if (response.status === 'success') {
        setResultState({ status: 'success' })
      } else if (response.status === 'insufficient_data') {
        setResultState({ status: 'insufficient_data' })
      } else {
        setResultState({ status: 'error' })
        setError(response.error_message || 'Unable to estimate resale value')
      }
    } catch (err) {
      setError(err.message || 'Unable to complete resale estimation.')
      setResultState({ status: 'error' })
    }
  }

  function handleReset() {
    setForm({ ...INITIAL_FORM_STATE })
    setDeviceAge('')
    setPhysicalCondition('')
    setBatteryHealth('')
    setErrors({})
    setWarnings({})
    setResult(null)
    setResultState({ status: 'idle' })
    setError('')
  }

  const isDisabled = (field) => {
    if (!csvLoaded) return true
    if (field === 'model') return !form.brand
    if (field === 'cpu') return !form.model
    if (field === 'gpu') return !form.cpu
    if (field === 'ram') return !form.gpu
    if (field === 'storageCapacityGb') return !form.ram
    if (field === 'storageType') return !form.storageCapacityGb
    if (field === 'screenSize') return !form.storageType
    return false
  }

  return (
    <div className="space-y-8">
      <div className="grid gap-8 lg:grid-cols-2 lg:items-start">
        {/* Form Section */}
        <form onSubmit={handleSubmit} className="card-glow space-y-6 rounded-2xl border border-white/5 bg-navy-800/40 p-6 sm:p-8" noValidate>
          <div>
            <h2 className="font-display text-2xl font-bold text-white">Laptop specifications</h2>
            <p className="mt-1 text-sm text-slate-500">
              Fields marked with <span className="text-blue-400">*</span> are required.
            </p>
          </div>

          {warnings.form && (
            <p className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-xs text-amber-200/90" role="status">
              {warnings.form}
            </p>
          )}

          {errors.form && (
            <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs text-red-200/90" role="alert">
              {errors.form}
            </p>
          )}

          {!csvLoaded && (
            <p className="rounded-lg border border-blue-500/20 bg-blue-500/10 px-3 py-2 text-xs text-blue-200/90" role="status">
              Loading laptop data…
            </p>
          )}

          <FormSection title="Device Identity" description="Brand and model identify the device category.">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="brand" className="block text-sm font-medium text-slate-200">
                  Brand <span className="text-blue-400">*</span>
                </label>
                <select
                  id="brand"
                  disabled={!csvLoaded}
                  className={`input-field ${errors.brand ? 'input-field-error' : ''} ${!csvLoaded ? 'opacity-50' : ''}`}
                  value={form.brand}
                  onChange={(e) => updateField('brand', e.target.value)}
                >
                  <option value="">Select brand</option>
                  {availableOptions.brands.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
                {errors.brand && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.brand}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <label htmlFor="model" className="block text-sm font-medium text-slate-200">
                  Laptop model <span className="text-blue-400">*</span>
                </label>
                <select
                  id="model"
                  disabled={isDisabled('model')}
                  className={`input-field ${errors.model ? 'input-field-error' : ''} ${isDisabled('model') ? 'opacity-50' : ''}`}
                  value={form.model}
                  onChange={(e) => updateField('model', e.target.value)}
                >
                  <option value="">Select model</option>
                  {availableOptions.models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
                {errors.model && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.model}
                  </p>
                )}
                <FieldWarning message={warnings.model} />
              </div>
            </div>
          </FormSection>

          <FormSection title="Performance & Storage" description="Core hardware that drives the valuation model.">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="cpu" className="block text-sm font-medium text-slate-200">
                  CPU / Processor <span className="text-blue-400">*</span>
                </label>
                <select
                  id="cpu"
                  disabled={isDisabled('cpu')}
                  className={`input-field ${errors.cpu ? 'input-field-error' : ''} ${isDisabled('cpu') ? 'opacity-50' : ''}`}
                  value={form.cpu}
                  onChange={(e) => updateField('cpu', e.target.value)}
                >
                  <option value="">Select CPU</option>
                  {availableOptions.cpus.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                {errors.cpu && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.cpu}
                  </p>
                )}
                <FieldWarning message={warnings.cpu} />
              </div>
              <div className="space-y-1.5">
                <label htmlFor="ram" className="block text-sm font-medium text-slate-200">
                  RAM <span className="text-blue-400">*</span>
                </label>
                <select
                  id="ram"
                  disabled={isDisabled('ram')}
                  className={`input-field ${errors.ram ? 'input-field-error' : ''} ${isDisabled('ram') ? 'opacity-50' : ''}`}
                  value={form.ram}
                  onChange={(e) => updateField('ram', e.target.value)}
                >
                  <option value="">Select RAM</option>
                  {availableOptions.rams.map((gb) => (
                    <option key={gb} value={gb}>
                      {gb} GB
                    </option>
                  ))}
                </select>
                {errors.ram && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.ram}
                  </p>
                )}
                <FieldWarning message={warnings.ram} />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="storageCapacity" className="block text-sm font-medium text-slate-200">
                  Storage capacity <span className="text-blue-400">*</span>
                </label>
                <select
                  id="storageCapacity"
                  disabled={isDisabled('storageCapacityGb')}
                  className={`input-field ${errors.storageCapacityGb ? 'input-field-error' : ''} ${isDisabled('storageCapacityGb') ? 'opacity-50' : ''}`}
                  value={form.storageCapacityGb}
                  onChange={(e) => updateField('storageCapacityGb', e.target.value)}
                >
                  <option value="">Select capacity</option>
                  {availableOptions.storageCapacities.map((gb) => (
                    <option key={gb} value={gb}>
                      {gb >= 1024 ? `${gb / 1024} TB` : `${gb} GB`}
                    </option>
                  ))}
                </select>
                {errors.storageCapacityGb && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.storageCapacityGb}
                  </p>
                )}
                <FieldWarning message={warnings.storageCapacityGb} />
              </div>
              <div className="space-y-1.5">
                <span className="block text-sm font-medium text-slate-200">
                  Storage type <span className="text-blue-400">*</span>
                </span>
                <div className="flex gap-3 pt-1">
                  {availableOptions.storageTypes.map((type) => (
                    <label
                      key={type}
                      className={`flex flex-1 cursor-pointer items-center justify-center rounded-xl border px-4 py-2.5 text-sm font-medium transition ${
                        form.storageType === type
                          ? 'border-blue-500/50 bg-blue-500/15 text-blue-200'
                          : 'border-white/10 bg-navy-900/50 text-slate-400 hover:border-white/20'
                      } ${isDisabled('storageType') ? 'pointer-events-none opacity-50' : ''}`}
                    >
                      <input
                        type="radio"
                        name="storageType"
                        className="sr-only"
                        value={type}
                        checked={form.storageType === type}
                        onChange={() => updateField('storageType', type)}
                        disabled={isDisabled('storageType')}
                      />
                      {type}
                    </label>
                  ))}
                </div>
                {errors.storageType && (
                  <p className="text-xs text-red-400" role="alert">
                    {errors.storageType}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="gpu" className="block text-sm font-medium text-slate-200">
                GPU <span className="text-blue-400">*</span>
              </label>
              <select
                id="gpu"
                disabled={isDisabled('gpu')}
                className={`input-field ${errors.gpu ? 'input-field-error' : ''} ${isDisabled('gpu') ? 'opacity-50' : ''}`}
                value={form.gpu}
                onChange={(e) => updateField('gpu', e.target.value)}
              >
                <option value="">Select GPU</option>
                {availableOptions.gpus.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
              {errors.gpu && (
                <p className="text-xs text-red-400" role="alert">
                  {errors.gpu}
                </p>
              )}
              <FieldWarning message={warnings.gpu} />
            </div>
          </FormSection>

          <FormSection title="Display" description="Screen size in inches (typical laptop range).">
            <div className="max-w-xs space-y-1.5">
              <label htmlFor="screenSize" className="block text-sm font-medium text-slate-200">
                Screen size (inches) <span className="text-blue-400">*</span>
              </label>
              <select
                id="screenSize"
                disabled={isDisabled('screenSize')}
                className={`input-field ${errors.screenSize ? 'input-field-error' : ''} ${isDisabled('screenSize') ? 'opacity-50' : ''}`}
                value={form.screenSize}
                onChange={(e) => updateField('screenSize', e.target.value)}
              >
                <option value="">Select screen size</option>
                {availableOptions.screenSizes.map((size) => (
                  <option key={size} value={size}>
                    {size}"
                  </option>
                ))}
              </select>
              {errors.screenSize && (
                <p className="text-xs text-red-400" role="alert">
                  {errors.screenSize}
                </p>
              )}
              <FieldWarning message={warnings.screenSize} />
            </div>
          </FormSection>

          <FormSection title="Device Condition" description="Additional details for more accurate estimation.">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label htmlFor="deviceAge" className="block text-sm font-medium text-slate-200">
                  Device age (years)
                </label>
                <input
                  type="number"
                  id="deviceAge"
                  min="0"
                  max="10"
                  step="0.5"
                  className="input-field"
                  placeholder="e.g., 2.5"
                  value={deviceAge}
                  onChange={(e) => setDeviceAge(e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="physicalCondition" className="block text-sm font-medium text-slate-200">
                  Physical condition
                </label>
                <select
                  id="physicalCondition"
                  className="input-field"
                  value={physicalCondition}
                  onChange={(e) => setPhysicalCondition(e.target.value)}
                >
                  <option value="">Select condition</option>
                  <option value="excellent">Excellent</option>
                  <option value="good">Good</option>
                  <option value="fair">Fair</option>
                  <option value="poor">Poor</option>
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="batteryHealth" className="block text-sm font-medium text-slate-200">
                Battery health
              </label>
              <input
                type="text"
                id="batteryHealth"
                className="input-field"
                placeholder="e.g., 85% or Good"
                value={batteryHealth}
                onChange={(e) => setBatteryHealth(e.target.value)}
              />
            </div>
          </FormSection>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/5"
            >
              <RotateCcw className="h-4 w-4" />
              Reset form
            </button>
            <button
              type="submit"
              disabled={resultState.status === 'loading'}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:from-blue-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resultState.status === 'loading' ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  Estimate Resale Value
                </>
              )}
            </button>
          </div>
        </form>

        {/* Results Section */}
        <div className="card-glow space-y-6 rounded-2xl border border-white/5 bg-navy-800/40 p-6 sm:p-8">
          <h2 className="font-display text-2xl font-bold text-white">Resale estimate</h2>

          {resultState.status === 'idle' && (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-navy-900/30 py-12 text-center">
              <Search className="h-12 w-12 text-slate-600 mb-4" />
              <p className="text-slate-400">Enter laptop specifications to get a resale value estimate</p>
            </div>
          )}

          {resultState.status === 'loading' && (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-navy-900/30 py-12 text-center">
              <Loader2 className="h-12 w-12 text-blue-400 animate-spin mb-4" />
              <p className="text-slate-400">Searching for comparable listings...</p>
            </div>
          )}

          {resultState.status === 'error' && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-200">Estimation failed</p>
                  <p className="mt-1 text-sm text-red-300/80">{error}</p>
                </div>
              </div>
            </div>
          )}

          {resultState.status === 'insufficient_data' && result && (
            <div className="space-y-4">
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-amber-200">Insufficient data</p>
                    <p className="mt-1 text-sm text-amber-300/80">
                      Could not find enough comparable listings with prices to generate a reliable estimate.
                    </p>
                  </div>
                </div>
              </div>

              {result.listings && result.listings.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center justify-between">
                    <span>Discovered Listings ({result.listings.length})</span>
                    <span className="text-xs text-slate-500 font-normal">Need 3+ priced listings for valuation</span>
                  </h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {result.listings.map((listing, idx) => (
                      <a
                        key={idx}
                        href={listing.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block rounded-lg border border-white/5 bg-navy-900/50 p-3 hover:border-white/10 hover:bg-navy-900/80 transition"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{listing.title}</p>
                            <div className="flex flex-wrap items-center gap-2 mt-1.5">
                              <p className="text-xs text-slate-400">{listing.source_name}</p>
                              {listing.match_type && (
                                <span className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded font-medium ${
                                  listing.match_type === 'exact'
                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                }`}>
                                  {listing.match_type} match
                                </span>
                              )}
                              {listing.condition && (
                                <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-slate-400">
                                  {listing.condition}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex flex-col items-end shrink-0">
                            {listing.price_inr ? (
                              <span className="text-sm font-semibold text-blue-300">
                                {formatInr(listing.price_inr)}
                              </span>
                            ) : (
                              <span className="text-xs text-slate-500 italic">Price unlisted</span>
                            )}
                            <ExternalLink className="h-3.5 w-3.5 text-slate-500 mt-1" />
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {result.limitations && result.limitations.length > 0 && (
                <div className="rounded-lg border border-white/5 bg-navy-900/30 p-4">
                  <p className="text-xs font-medium text-slate-400 mb-2">Limitations:</p>
                  <ul className="space-y-1">
                    {result.limitations.map((limitation, idx) => (
                      <li key={idx} className="text-xs text-slate-500 flex items-start gap-2">
                        <span className="text-slate-600">•</span>
                        {limitation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {resultState.status === 'success' && result && (
            <div className="space-y-4">
              <div className="rounded-xl border border-green-500/20 bg-green-500/10 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-green-200">Resale Valuation Available</p>
                      <p className="mt-1 text-xs text-green-300/80">
                        Derived from {result.comparable_listings_count} comparable listings ({result.exact_matches_count || 0} exact, {result.similar_matches_count || 0} similar)
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 justify-end">
                    {result.match_quality && (
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${
                        result.match_quality === 'exact'
                          ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                          : result.match_quality === 'similar'
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                          : 'bg-blue-500/10 text-blue-300 border-blue-500/30'
                      }`}>
                        {result.match_quality === 'exact'
                          ? 'Exact Model Match'
                          : result.match_quality === 'similar'
                          ? 'Similar Spec Match'
                          : 'Mixed Match'}
                      </span>
                    )}

                    {result.confidence_level && (
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${
                        result.confidence_level === 'high'
                          ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                          : result.confidence_level === 'medium'
                          ? 'bg-blue-500/10 text-blue-300 border-blue-500/30'
                          : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                      }`}>
                        {result.confidence_level.charAt(0).toUpperCase() + result.confidence_level.slice(1)} Confidence
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-white/5 bg-navy-900/50 p-6 space-y-4">
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">
                    Estimated Resale Value
                  </p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold text-blue-400">
                      {formatInr(result.estimated_value_inr ?? result.estimated_range_min_inr)}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      (Median asking price)
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-white/5">
                  <p className="text-xs text-slate-400 mb-1">Estimated Resale Price Range</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-xl font-bold text-white">
                      {formatInr(result.estimated_range_min_inr)}
                    </span>
                    <span className="text-slate-500">—</span>
                    <span className="text-xl font-bold text-white">
                      {formatInr(result.estimated_range_max_inr)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    Calculated from validated asking prices of comparable second-hand listings
                  </p>
                </div>
              </div>

              {result.listings && result.listings.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center justify-between">
                    <span>Comparable Listings ({result.listings.length})</span>
                    <span className="text-xs text-slate-500 font-normal">Stored in local database</span>
                  </h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {result.listings.map((listing, idx) => (
                      <a
                        key={idx}
                        href={listing.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block rounded-lg border border-white/5 bg-navy-900/50 p-3 hover:border-white/10 hover:bg-navy-900/80 transition"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{listing.title}</p>
                            <div className="flex flex-wrap items-center gap-2 mt-1.5">
                              <p className="text-xs text-slate-400">{listing.source_name}</p>
                              {listing.match_type && (
                                <span className={`text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded font-medium ${
                                  listing.match_type === 'exact'
                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                }`}>
                                  {listing.match_type} match
                                </span>
                              )}
                              {listing.condition && (
                                <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-slate-400">
                                  {listing.condition}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex flex-col items-end shrink-0">
                            {listing.price_inr ? (
                              <span className="text-sm font-semibold text-blue-300">
                                {formatInr(listing.price_inr)}
                              </span>
                            ) : (
                              <span className="text-xs text-slate-500 italic">Price unlisted</span>
                            )}
                            <ExternalLink className="h-3.5 w-3.5 text-slate-500 mt-1" />
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {result.limitations && result.limitations.length > 0 && (
                <div className="rounded-lg border border-white/5 bg-navy-900/30 p-4">
                  <p className="text-xs font-medium text-slate-400 mb-2">Valuation Insights & Limitations:</p>
                  <ul className="space-y-1">
                    {result.limitations.map((limitation, idx) => (
                      <li key={idx} className="text-xs text-slate-500 flex items-start gap-2">
                        <span className="text-slate-600">•</span>
                        {limitation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <p className="text-xs text-slate-500">
                Retrieved: {new Date(result.retrieval_timestamp).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
