const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health`)
    if (!response.ok) {
      throw new Error('Backend health check failed')
    }
    return await response.json()
  } catch (error) {
    throw new Error(error.message || 'Unable to connect to backend')
  }
}

export async function estimateResaleValue(laptopSpecs) {
  const response = await fetch(`${API_BASE}/api/resale/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(laptopSpecs),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || 'Resale estimation request failed.')
  }

  return await response.json()
}

export function formatInr(amount) {
  if (amount == null || isNaN(amount)) return '₹0'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}
