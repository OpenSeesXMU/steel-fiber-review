# Steel fiber pull-out database and research code

Data and code collected for review of **ML-Driven Material Design and Multiscale Analysis of Large-Scale RC Structures: A Performance-Based UHPC Local Enhancement Approach**, based on Sensi924. Version: v1.0.0. Prepared: 2026-10-09.

This package contains the supplied 61-sample database, digitized source curves, parameter workbook, original scripts, portable script copies, supporting mesh/model files and archived result figures. **Read docs/KNOWN_ISSUES.md before interpreting or publishing results.** The available code has scientific and manuscript-consistency issues; a successful script run is not evidence of complete reproduction of the published method or hospital case study.

## Files

- `data/database/Final_AI_Dataset.csv`: 61 samples, 107 columns (identifier, 6 inputs, 100 force points); 31 hooked and 30 straight fibers.
- `data/metadata/`: original Excel parameter table, full field dictionary, slip grid and exact raw-file mapping with checksums.
- `data/raw_curves/`: unchanged curves from both source locations. Duplicate source copies are retained with their origin identified.
- `data/reference_curves/`: curves used by the literature-comparison script.
- `data/additional_parameter_curves/`: additional digitized curves with incomplete metadata.
- `code/original/`: unmodified scripts for provenance; local paths may not work on another computer.
- `code/portable/`: adaptations restricted to paths/output handling.
- `simulation/original_model/`: available original Tcl scripts, meshes and geometry/material generators; correspondence to the manuscript case is unconfirmed.
- `results/archived/`: existing figures/outputs; no claim of figure-to-manuscript correspondence.
- `results/reproduced/`: results generated while validating this package, with task logs.
- `docs/`: scope, sources, environment, changes and known issues.
- `manifest_sha256.csv`: checksum/size inventory. `source_manifest.csv`: provenance for unchanged copied files.

## How the database and outputs were produced

The following notes describe the supplied files and executable scripts. They explain the available workflow; the confirmed scope of reproduction is recorded in `docs/VALIDATION_REPORT.md`.

1. **Pair each experimental curve with its material parameters.** The raw CSV files contain slip–force coordinates from published pull-out studies. `experiment.xlsx` associates a curve filename with fiber type, diameter, tensile strength, embedment length, matrix strength and inclination angle. `source_index.csv` identifies the exact archived file for each sample, including files stored under different directories or with repeated `.csv` extensions.

   > Note: One complete curve is one sample. The 100 force values along that curve are its output coordinates, not 100 independent experiments. The original digitization software and extraction protocol were not recorded in the supplied files.

2. **Convert curves of different lengths into a common output format.** The procedure in `data_fusion.py` cleans and orders the slip coordinates, then linearly interpolates each curve onto 100 points from 0 to 25 mm. The six input parameters and `Force_0` through `Force_99` are combined into one database row. The review utility `rebuild_database.py` repeats this procedure using the explicit source mapping and compares its output with the supplied database.

   > Note: A zero assigned outside the measured slip range is a preprocessing fill value. It does not establish that a zero force was measured at that location. The supplied database contains 61 curves; the unmatched parameter record is described below.

3. **Train the curve-profile and force-anchor models.** In `train_and_evaluate.py`, the six inputs are augmented by expressions intended to represent contact area, the square root of matrix strength and a bond-capacity indicator. The script scales the inputs and force coordinates, reserves 10% of the samples for testing, and trains a 300-tree random forest to predict the scaled curve. Two XGBoost regressors predict peak force and the mean of the last five force coordinates. The curve is converted back to force units, scaled to the predicted peak, adjusted over its final 20% toward the residual anchor, and clipped to nonnegative force. The runner exports the existing predictions, split assignments and peak-error metrics.

   > Note: This describes the current implementation. Its matrix-strength index selects the angle column, and scaling is fitted before the test split. Both behaviors are retained and documented in `docs/KNOWN_ISSUES.md`. Other model scripts implement alternative settings, including an 80/20 split.

4. **Generate the supporting comparisons and material demonstrations.** `triple_curve_compassion.py` plots literature curves beside an analytical straight-fiber curve; its nominal peak is calculated as `pi * diameter * embedment_length * tau_max`, giving about 31.8 N for its configured parameters. `batch_generate_materials.py` generates illustrative curves, extracts four backbone points, converts slip to strain and force to stress using its configured length and fiber area, and writes Pinching4 material definitions. Available geometry scripts associate generated fibers with concrete mesh nodes.

   > Note: The approximately 31.8 N comparison curve and material-generator demonstrations do not call the database-trained predictor. The archived geometry/model files have not been established as the complete NSM/DDM/FMC hospital workflow described in the manuscript.

5. **Assemble and check this review package.** Relevant data, scripts, mesh inputs and existing outputs were copied from the workspace and the original model directory referenced by the training script. Original copies retain their bytes; portable copies locate the database relative to the package. The runner stores fresh outputs separately from archived results. Database reconstruction, supported script runs, source checksums and Python syntax were checked before creating the ZIP archive. The extracted archive was also verified, and its database-rebuild and 90/10-evaluation tasks were run from the new location.

   > Note: `results/archived` contains pre-existing artifacts; `results/reproduced` contains outputs generated while checking this package. Their separation allows a reviewer to trace which results were actually regenerated.

## Installation

Use Python 3.14.3 and create your own environment. The exact core package versions below were available in the local validation environment; installation on another platform is not tested.

```console
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS instead:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install `requirements-optional.txt` only for the archived CatBoost/PyTorch model variants. The default evaluator does not require them.

## Review commands

Run from the package directory, or invoke run_review.py by its full path:

```console
python run_review.py --task verify
python run_review.py --task rebuild
python run_review.py --task evaluate
python run_review.py --task rf
python run_review.py --task ultimate
python run_review.py --task comparison
```

`verify` checks the file inventory and Python syntax without third-party dependencies. `rebuild` uses the unchanged Excel table plus source_index.csv to reconstruct and compare the complete processed database without overwriting it. `evaluate` runs the existing 90/10 RF+XGBoost script unchanged numerically, including the issues recorded in KNOWN_ISSUES.md. Its example plot is selected with NumPy seed 42; the training split remains random_state=42. The runner saves logs, held-out sample IDs, existing predictions, metrics and figures to separate task directories. `rf` and `ultimate` are the supplied 80/20 alternatives. `comparison` is the **analytical** reference comparison, not database-trained ML inference.

Additional supported tasks: `xgb`, `hybrid` (CatBoost needed), `physical-straight`, `physical-custom`, `four-features`, `materials-demo`, `synthetic-ablation`, `nn`, `nn-predict`. Tasks containing `physical`, `demo` or `synthetic` generate illustrative analytical/synthetic results and must not be presented as experimental-database-trained predictions. See `python run_review.py --help`.

## Database preparation rule

The original data_fusion.py reads experiment.xlsx using header row 2, clips negative slip to zero, sorts by slip, removes repeated slip points, linearly interpolates onto 100 equally spaced points from 0 to 25 mm, assigns zero outside the observed range and rounds force to two decimals. source_index.csv resolves filename/directory discrepancies explicitly without changing the original workbook or raw files. The workbook contains 62 nonblank parameter records; yoo2017_S13_B.csv is absent from the supplied final database and has no exact-name raw source in the collected files. It is explicitly excluded and listed in rebuild_comparison.json; it is not substituted by the differently named yoo2017_S13_BA.csv. This is a reconstruction of the existing procedure; it does not validate the physical treatment of tails or duplicates.

## Scope and availability

See docs/MANUSCRIPT_SCOPE.md and docs/VALIDATION_REPORT.md. The model meshes found via the original script path are supplementary source material. Full hospital-scale NSM/DDM/FMC code, earthquake excitation and complete analysis outputs have not been identified. No trained checkpoints or unverified original environment information have been invented. Preserve this version when responding to reviewers; document later scientific corrections in a new version.

## Reuse

The author has not specified an open-source or dataset reuse license. No license is assigned by this packaging step. A GitHub publication decision, author-selected reuse terms and literature-data attribution should be made separately. This folder is local; no upload has been performed.
