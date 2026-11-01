import { getCSVData, filterRecords } from './csvDataService'

/**
 * Validation service using CSV data from laptop_select_list.csv
 * All options and validations are derived from the CSV dataset
 */

export function getModelsForBrand(brand) {
  const csvData = getCSVData()
  if (!brand || csvData.length === 0) return []
  const models = new Set(csvData.filter(r => r.brand === brand).map(r => r.model))
  return Array.from(models).sort()
}

/**
 * @returns {{ errors: Record<string, string>, warnings: Record<string, string> }}
 */
export function validateLaptopFormExtended(form) {
  const errors = {}
  const warnings = {}

  // Basic required field validation
  if (!form.brand) errors.brand = 'Please select a brand.'
  if (!form.model.trim()) errors.model = 'Laptop model is required.'
  if (!form.cpu) errors.cpu = 'CPU / processor is required.'
  if (!form.ram) errors.ram = 'Please select RAM capacity.'
  if (!form.storageCapacityGb) errors.storageCapacityGb = 'Please select storage capacity.'
  if (!form.storageType) errors.storageType = 'Please select storage type.'
  if (!form.gpu) errors.gpu = 'GPU selection is required.'
  if (!form.screenSize) errors.screenSize = 'Please select screen size.'

  // If there are basic errors, return early
  if (Object.keys(errors).length > 0) {
    return { errors, warnings }
  }

  // Validate that the combination exists in CSV
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

  const matchingRecords = filterRecords(selections)

  if (matchingRecords.length === 0) {
    errors.form = 'This hardware combination does not exist in the dataset. Please select compatible options.'
  }

  return { errors, warnings }
}
