import { validateLaptopFormExtended } from './laptopValidation'

/**
 * Prediction API layer — uses FastAPI backend with trained ML model.
 * Model artifact: final_laptop_price_model.joblib (server-side).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const PREDICTION_MODE = {
  DEMO: 'demo',
  API: 'api',
}

function resolveCpu(form) {
  return form.cpu.trim()
}

function resolveGpu(form) {
  return form.gpu.trim()
}

/**
 * Payload shape expected by the backend preprocessing pipeline.
 */
export function buildPredictionPayload(form) {
  const cpu = resolveCpu(form)
  const gpu = resolveGpu(form)
  const storageCapacityGb = Number(form.storageCapacityGb)

  return {
    brand: form.brand.trim(),
    model: form.model.trim(),
    cpu,
    ram: Number(form.ram),
    storage_capacity_gb: storageCapacityGb,
    storage_type: form.storageType,
    gpu,
    screen_size: Number(form.screenSize),
  }
}

export function validateLaptopForm(form) {
  return validateLaptopFormExtended(form).errors
}

export function validateLaptopFormWithWarnings(form) {
  return validateLaptopFormExtended(form)
}

/**
 * @returns {Promise<{ mode: string, priceEur: number, priceInr: number, payload: object, demoNotice: string | null }>}
 */
export async function predictLaptopPrice(form, { mode = PREDICTION_MODE.API } = {}) {
  const payload = buildPredictionPayload(form)

  if (mode === PREDICTION_MODE.API && API_BASE) {
    const response = await fetch(`${API_BASE.replace(/\/$/, '')}/api/predict/laptop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || 'Prediction request failed.')
    }
    const data = await response.json()
    return {
      mode: PREDICTION_MODE.API,
      priceEur: data.price_eur ?? data.priceEur,
      priceInr: data.price_inr ?? data.priceInr,
      payload,
      demoNotice: null,
    }
  }

  throw new Error('API mode requires VITE_API_BASE_URL to be configured.')
}

/**
 * Batch prediction for multiple laptops (comparison feature)
 */
export async function predictBatchLaptops(forms) {
  const payloads = forms.map(buildPredictionPayload)

  if (!API_BASE) {
    throw new Error('API mode requires VITE_API_BASE_URL to be configured.')
  }

  const response = await fetch(`${API_BASE.replace(/\/$/, '')}/api/predict/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payloads),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Batch prediction request failed.')
  }

  return await response.json()
}

export function formatInr(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatEur(amount) {
  return new Intl.NumberFormat('en-DE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(amount)
}
