export const MODEL_INFO = {
  name: 'Tuned Random Forest Regressor',
  maeEur: 227.78,
  rmseEur: 391.12,
  r2: 0.8085,
  datasetRecords: 3363,
  trainSplitPercent: 80,
  testSplitPercent: 20,
  testRecords: 673,
  targetCurrency: 'EUR',
}

export const METRIC_EXPLANATIONS = {
  mae: 'Mean Absolute Error (MAE) is the average absolute difference between predicted and actual prices on the test set. Lower is better.',
  rmse: 'Root Mean Squared Error (RMSE) penalizes larger errors more heavily than MAE. Lower is better.',
  r2: 'R² (coefficient of determination) measures how much of the price variance the model explains on the test set. It is not the same as prediction accuracy for a single device.',
  disclaimer:
    'These metrics were computed on a held-out test set (673 records). Individual predictions can differ significantly from actual market prices.',
}

/** Chart data derived only from documented evaluation results (error magnitudes in EUR). */
export const TEST_ERROR_CHART_DATA = [
  { metric: 'MAE', value: MODEL_INFO.maeEur, fill: '#3b82f6' },
  { metric: 'RMSE', value: MODEL_INFO.rmseEur, fill: '#8b5cf6' },
]

export const SPLIT_CHART_DATA = [
  { name: 'Training (80%)', value: MODEL_INFO.datasetRecords - MODEL_INFO.testRecords, fill: '#3b82f6' },
  { name: 'Test (20%)', value: MODEL_INFO.testRecords, fill: '#8b5cf6' },
]
