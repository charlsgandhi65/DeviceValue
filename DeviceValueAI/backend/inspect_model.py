import joblib

model = joblib.load('final_laptop_price_model.joblib')

print('Model type:', type(model))
print('Model name:', model.__class__.__name__)
print('\nPipeline steps:')
for name, step in model.named_steps.items():
    print(f'  {name}: {type(step).__name__}')

print('\nFeature names in:')
if hasattr(model, 'feature_names_in_'):
    print(model.feature_names_in_)
else:
    print('Not available')

print('\nNumber of features:')
if hasattr(model, 'n_features_in_'):
    print(model.n_features_in_)
else:
    print('N/A')

# Try to get the final estimator
final_estimator = model.named_steps.get('regressor') or model.named_steps.get('model') or model.named_steps.get('classifier')
if final_estimator:
    print('\nFinal estimator:', type(final_estimator).__name__)
