/**
 * CSV Data Service for Laptop Selection
 * Loads and parses laptop_select_list.csv for cascading dropdowns
 */

let csvData = null
let isLoaded = false

/**
 * Parse CSV text into array of objects
 */
function parseCSV(csvText) {
  const lines = csvText.trim().split('\n')
  if (lines.length === 0) return []

  const headers = lines[0].split(',').map(h => h.trim())
  const records = []

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',')
    if (values.length !== headers.length) continue

    const record = {}
    headers.forEach((header, index) => {
      let value = values[index]?.trim()
      
      // Convert numeric fields
      if (header === 'ram' || header === 'storage_capacity_gb' || header === 'screen_size') {
        value = value === '' || value === 'NaN' || value === 'undefined' ? null : parseFloat(value)
      }
      
      // Skip null/empty/invalid values
      if (value === '' || value === 'NaN' || value === 'undefined' || value === null) {
        return
      }
      
      record[header] = value
    })

    // Only add record if it has all required fields
    if (Object.keys(record).length === headers.length) {
      records.push(record)
    }
  }

  return records
}

/**
 * Load CSV data from public folder
 */
export async function loadCSVData() {
  if (isLoaded && csvData) return csvData

  try {
    const response = await fetch('/laptop_select_list.csv')
    if (!response.ok) {
      throw new Error(`Failed to load CSV: ${response.status}`)
    }
    const csvText = await response.text()
    csvData = parseCSV(csvText)
    isLoaded = true
    return csvData
  } catch (error) {
    console.error('Error loading CSV data:', error)
    csvData = []
    isLoaded = true
    return []
  }
}

/**
 * Get all data (cached)
 */
export function getCSVData() {
  return csvData || []
}

/**
 * Get unique brands from CSV
 */
export function getBrands() {
  if (!csvData || csvData.length === 0) return []
  const brands = new Set(csvData.map(r => r.brand))
  return Array.from(brands).sort()
}

/**
 * Get unique models for a given brand
 */
export function getModelsForBrand(brand) {
  if (!csvData || csvData.length === 0 || !brand) return []
  const models = new Set(csvData.filter(r => r.brand === brand).map(r => r.model))
  return Array.from(models).sort()
}

/**
 * Get unique CPUs from filtered records
 */
export function getCPUs(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const cpus = new Set(filteredRecords.map(r => r.cpu))
  return Array.from(cpus).sort()
}

/**
 * Get unique GPUs from filtered records
 */
export function getGPUs(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const gpus = new Set(filteredRecords.map(r => r.gpu))
  return Array.from(gpus).sort()
}

/**
 * Get unique RAM options from filtered records
 */
export function getRAMOptions(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const ramValues = new Set(filteredRecords.map(r => r.ram))
  return Array.from(ramValues).filter(r => r != null && !isNaN(r)).sort((a, b) => a - b)
}

/**
 * Get unique storage capacity options from filtered records
 */
export function getStorageCapacityOptions(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const capacities = new Set(filteredRecords.map(r => r.storage_capacity_gb))
  return Array.from(capacities).filter(c => c != null && !isNaN(c)).sort((a, b) => a - b)
}

/**
 * Get unique storage types from filtered records
 */
export function getStorageTypes(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const types = new Set(filteredRecords.map(r => r.storage_type))
  return Array.from(types).sort()
}

/**
 * Get unique screen sizes from filtered records
 */
export function getScreenSizes(filteredRecords) {
  if (!filteredRecords || filteredRecords.length === 0) return []
  const sizes = new Set(filteredRecords.map(r => r.screen_size))
  return Array.from(sizes).filter(s => s != null && !isNaN(s)).sort((a, b) => a - b)
}

/**
 * Filter records based on current selections (cascading)
 */
export function filterRecords(selections) {
  if (!csvData || csvData.length === 0) return []

  return csvData.filter(record => {
    if (selections.brand && record.brand !== selections.brand) return false
    if (selections.model && record.model !== selections.model) return false
    if (selections.cpu && record.cpu !== selections.cpu) return false
    if (selections.gpu && record.gpu !== selections.gpu) return false
    if (selections.ram != null && record.ram !== selections.ram) return false
    if (selections.storageCapacityGb != null && record.storage_capacity_gb !== selections.storageCapacityGb) return false
    if (selections.storageType && record.storage_type !== selections.storageType) return false
    if (selections.screenSize != null && record.screen_size !== selections.screenSize) return false
    return true
  })
}

/**
 * Verify that a complete combination exists in the CSV
 */
export function verifyCombinationExists(selections) {
  if (!csvData || csvData.length === 0) return false

  const requiredFields = ['brand', 'model', 'cpu', 'gpu', 'ram', 'storageCapacityGb', 'storageType', 'screenSize']
  
  // Check all required fields are present
  for (const field of requiredFields) {
    if (selections[field] == null || selections[field] === '') {
      return false
    }
  }

  // Search for matching record
  const match = csvData.find(record => {
    return (
      record.brand === selections.brand &&
      record.model === selections.model &&
      record.cpu === selections.cpu &&
      record.gpu === selections.gpu &&
      record.ram === selections.ram &&
      record.storage_capacity_gb === selections.storageCapacityGb &&
      record.storage_type === selections.storageType &&
      record.screen_size === selections.screenSize
    )
  })

  return match !== undefined
}

/**
 * Get available options for a field based on current selections
 */
export function getAvailableOptions(field, selections) {
  const filtered = filterRecords(selections)

  switch (field) {
    case 'brand':
      return getBrands()
    case 'model':
      return getModelsForBrand(selections.brand)
    case 'cpu':
      return getCPUs(filtered)
    case 'gpu':
      return getGPUs(filtered)
    case 'ram':
      return getRAMOptions(filtered)
    case 'storageCapacityGb':
      return getStorageCapacityOptions(filtered)
    case 'storageType':
      return getStorageTypes(filtered)
    case 'screenSize':
      return getScreenSizes(filtered)
    default:
      return []
  }
}

/**
 * Compute valid cascading options for an individual laptop form state
 * Enforces hierarchical dependency: Brand -> Model -> CPU -> GPU -> RAM -> Storage -> Storage Type -> Screen Size
 */
export function getLaptopCascadingOptions(laptop = {}) {
  const b = laptop.brand || ''
  const m = laptop.model || ''
  const c = laptop.cpu || ''
  const g = laptop.gpu || ''
  const r = laptop.ram != null && laptop.ram !== '' ? Number(laptop.ram) : null
  const sc = laptop.storageCapacityGb != null && laptop.storageCapacityGb !== '' ? Number(laptop.storageCapacityGb) : null
  const st = laptop.storageType || ''

  return {
    brands: getBrands(),
    models: b ? getModelsForBrand(b) : [],
    cpus: m ? getCPUs(filterRecords({ brand: b, model: m })) : [],
    gpus: c ? getGPUs(filterRecords({ brand: b, model: m, cpu: c })) : [],
    rams: g ? getRAMOptions(filterRecords({ brand: b, model: m, cpu: c, gpu: g })) : [],
    storageCapacities: r != null ? getStorageCapacityOptions(filterRecords({ brand: b, model: m, cpu: c, gpu: g, ram: r })) : [],
    storageTypes: sc != null ? getStorageTypes(filterRecords({ brand: b, model: m, cpu: c, gpu: g, ram: r, storageCapacityGb: sc })) : [],
    screenSizes: st ? getScreenSizes(filterRecords({ brand: b, model: m, cpu: c, gpu: g, ram: r, storageCapacityGb: sc, storageType: st })) : [],
  }
}

