"""Run supported source scripts with local paths and separate review outputs."""
from pathlib import Path
import argparse, ast, builtins, contextlib, csv, hashlib, io, json, os, runpy, sys, traceback

ROOT = Path(__file__).resolve().parent
TASKS = {
    'rebuild': 'rebuild_database.py',
    'evaluate': 'train_and_evaluate.py',
    'rf': 'train_rf_model.py',
    'xgb': 'train_xgb_model.py',
    'ultimate': 'train_ultimate_model.py',
    'hybrid': 'train_hybrid_model.py',
    'comparison': 'triple_curve_compassion.py',
    'physical-straight': 'predict_curve.py',
    'physical-custom': 'predict_scifiber_curve.py',
    'four-features': 'extract_four_features.py',
    'materials-demo': 'batch_generate_materials.py',
    'synthetic-ablation': 'simulate.py',
    'nn': 'train_model.py',
    'nn-predict': 'predict_new_curve.py',
}

def verify():
    errors = []
    inventory = ROOT/'manifest_sha256.csv'
    if not inventory.exists():
        raise FileNotFoundError('manifest_sha256.csv has not been generated')
    with inventory.open(encoding='utf-8', newline='') as f:
        files = list(csv.DictReader(f))
    for row in files:
        p = (ROOT/row['path']).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            errors.append(f'Missing or unsafe path: {row["path"]}')
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            errors.append(f'Checksum differs: {row["path"]}')
    scripts = list((ROOT/'code').rglob('*.py')) + list((ROOT/'simulation').rglob('*.py')) + [Path(__file__)]
    for p in scripts:
        try:
            ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
        except SyntaxError as e:
            errors.append(f'Syntax error: {p.relative_to(ROOT)}: {e}')
    print(json.dumps({'inventoried_files': len(files), 'python_files_checked': len(scripts),
                      'errors': errors}, indent=2))
    return int(bool(errors))

def export_evaluation(state, np):
    from sklearn.model_selection import train_test_split
    df = state['df']
    train_idx, test_idx = train_test_split(np.arange(len(df)), test_size=0.10, random_state=42)
    with Path('split_assignment.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['sample_index', 'file_name', 'subset'])
        train_set = set(train_idx.tolist())
        w.writerows((i, df.iloc[i, 0], 'train' if i in train_set else 'test') for i in range(len(df)))
    with Path('heldout_curve_predictions.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['sample_index','file_name','slip_mm','actual_force_N','predicted_force_N'])
        for j, idx in enumerate(test_idx):
            for k, slip in enumerate(np.linspace(0,25,100)):
                w.writerow([int(idx), df.iloc[idx,0], float(slip), float(state['raw_Y_test'][j,k]),
                            float(state['Y_test_final'][j,k])])
    selected = int(state['sample_idx'])
    result = {'train_samples': len(train_idx), 'test_samples': len(test_idx), 'split_random_state':42,
              'example_plot_numpy_seed':42,'example_plot_sample_index': int(test_idx[selected]),
              'example_plot_file_name':str(df.iloc[test_idx[selected],0]),
              'peak_MAE_N':float(state['mae_peak']),'peak_MAPE_percent':float(state['mape_peak']),
              'note':'Results from the existing algorithm, including the issues documented in docs/KNOWN_ISSUES.md.'}
    Path('metrics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

def execute(task):
    work = ROOT/'results/reproduced'/task
    work.mkdir(parents=True, exist_ok=True)
    log = io.StringIO()
    initial = Path.cwd()
    old_input = builtins.input
    status = {'task':task, 'python':sys.version, 'success':False}
    try:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            os.chdir(work)
            if task == 'comparison':
                import shutil
                for name in ['wille2012_A_S.csv','yoo2017_S13_A_2.csv']:
                    shutil.copy2(ROOT/'data/reference_curves'/name, work/name)
            if task != 'rebuild':
                os.environ['MPLBACKEND'] = 'Agg'
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                import numpy as np
                if task == 'evaluate':
                    np.random.seed(42)  # Only controls the evaluator's random example plot.
                def save_displayed_figures(*args, **kwargs):
                    for number in plt.get_fignums():
                        plt.figure(number).savefig(work/f'displayed_figure_{number}.png', dpi=150, bbox_inches='tight')
                plt.show = save_displayed_figures
                builtins.input = lambda prompt='': ''
            state = runpy.run_path(str(ROOT/'code/portable'/TASKS[task]), run_name='__main__')
            if task == 'evaluate':
                export_evaluation(state,np)
            if task != 'rebuild':
                plt.close('all')
            status['success'] = True
    except Exception as e:
        status['error'] = f'{type(e).__name__}: {e}'
        log.write(traceback.format_exc())
    except SystemExit as e:
        status['success'] = e.code in (None,0)
        if not status['success']: status['error'] = f'SystemExit {e.code}'
    finally:
        os.chdir(initial)
        builtins.input = old_input
        (work/'run.log').write_text(log.getvalue(), encoding='utf-8')
        (work/'run_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
    print(f'Outputs: {work}')
    return 0 if status['success'] else 1

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', choices=['verify', *TASKS], default='verify')
    args = parser.parse_args()
    return verify() if args.task == 'verify' else execute(args.task)

if __name__ == '__main__':
    raise SystemExit(main())
