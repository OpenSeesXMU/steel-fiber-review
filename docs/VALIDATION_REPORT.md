# Validation report

Validation date: 2026-10-09. Platform: Windows x64. Existing research environment: Python 3.14.3 with exact versions in requirements.txt / requirements-optional.txt. No dependency download was needed.

## Data

The final database contains 61 rows and 107 columns. All 61 sample identifiers map to archived raw curves. All identifiers, input values and all 6,100 resampled force values in the rebuilt file agree exactly with the supplied processed database. Maximum absolute numeric difference: 0. The original workbook contains 62 nonblank parameter rows; yoo2017_S13_B.csv is explicitly excluded because it is absent from the supplied final database and no exact-name raw source exists. No substitute has been used. All numeric entries in the final database are present.

## Code execution

Executed tasks, each reporting success:

- `comparison`.
- `evaluate`.
- `hybrid`.
- `materials-demo`.
- `rebuild`.
- `rf`.
- `ultimate`.

Logs, run statuses, newly generated figures and outputs are in results/reproduced, separated by task. `materials-demo` is an analytical demonstration; successful Tcl generation does not validate an OpenSees execution. `comparison` is an analytical curve comparison rather than trained ML inference. No full OpenSees/MPI simulation, neural alternative, synthetic ablation or multi-output XGBoost alternative was run. No full-paper or figure-equivalence claim is made.

## Existing 90/10 evaluator

Training samples: 54; test samples: 7. Split random_state: 42. Peak MAE: 597.394109 N; peak MAPE: 251.258151%. These are results of the existing code, including the feature-index and pre-split-scaling issues. They are not asserted to match the submitted paper. The relatively large errors require author review before being used as supporting evidence. The selected example is `yoo2017_A_S30.csv` (original row 34, zero-based). All seven held-out curves and their predictions are exported in heldout_curve_predictions.csv.

## Source integrity and portability

364 copied source files match their recorded SHA-256 values. AST comparison confirms that all 15 portable legacy scripts have the same algorithmic syntax as their original source after normalizing only database/output locations and removing the added project-root definition. Original source code remains archived unchanged. New database-rebuild and review-runner utilities are explicitly documented.

All packaged Python files are syntax-checked. The final manifest records each file checksum and size. A dependency-free verification is also executed on the archive after extraction to a new directory. Those results are recorded in the accompanying local archive verification report. After running tasks on another computer, reproduced output checksums may change with the environment; verify the downloaded snapshot before generating new outputs.
