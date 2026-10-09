# Portability changes

All unmodified source scripts are retained under code/original. Adapted copies are under code/portable.

- batch_generate_materials.py: material output path redirected to the current run directory.
- batch_generate_materials.py: added project-root path definition; no numerical or data-path change.
- extract_four_features.py: added project-root path definition; no numerical or data-path change.
- generate_single_fiber.py: added project-root path definition; no numerical or data-path change.
- predict_curve.py: added project-root path definition; no numerical or data-path change.
- predict_scifiber_curve.py: added project-root path definition; no numerical or data-path change.
- train_and_evaluate.py: added project-root path definition; replaced database path.
- predict_new_curve.py: added project-root path definition; replaced database path.
- train_hybrid_model.py: added project-root path definition; replaced database path.
- train_model.py: added project-root path definition; replaced database path.
- train_rf_model.py: added project-root path definition; replaced database path.
- train_ultimate_model.py: added project-root path definition; replaced database path.
- train_xgb_model.py: added project-root path definition; replaced database path.
- predict_fiber3_advanced.py: added project-root path definition; no numerical or data-path change.
- simulate.py: added project-root path definition; no numerical or data-path change.
- triple_curve_compassion.py: added project-root path definition; no numerical or data-path change.

The review runner uses a separate output directory, selects a noninteractive plotting backend, saves figures when the original script only displays them, and intercepts the final press-Enter prompt. For the 90/10 evaluator it fixes NumPy seed 42 so the randomly selected example figure is repeatable, and exports arrays already produced by the original algorithm. Scientific feature selection, scaling, training splits, model settings and physical formulae are unchanged. Database rebuilding is a new utility using the original interpolation/rounding procedure and an explicit file mapping; it writes a new file and compares with the supplied database.
