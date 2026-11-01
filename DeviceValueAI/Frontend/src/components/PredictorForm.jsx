import { useState, useEffect, useMemo } from 'react'
import { RotateCcw } from 'lucide-react'
import { INITIAL_FORM_STATE } from '../data/laptopOptions'
import { validateLaptopFormWithWarnings } from '../services/predictionService'
import {
  loadCSVData,
  getLaptopCascadingOptions,
  verifyCombinationExists,
} from '../services/csvDataService'

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

export default function PredictorForm({ form, setForm, onSubmit, onReset }) {
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

  function handleSubmit(e) {
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
    onSubmit(form)
  }

  function handleReset() {
    setForm({ ...INITIAL_FORM_STATE })
    setErrors({})
    setWarnings({})
    onReset()
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
          className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:from-blue-500 hover:to-violet-500"
        >
          Estimate Device Value
        </button>
      </div>
    </form>
  )
}
