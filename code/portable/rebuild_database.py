"""Rebuild the supplied database using the original interpolation rule and explicit paths."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

ROOT = Path(__file__).resolve().parents[2]

def main():
    parameters = pd.read_excel(ROOT / 'data/metadata/experiment.xlsx', header=1)
    parameters = parameters.dropna(subset=['file name'])
    with (ROOT/'data/metadata/source_index.csv').open(encoding='utf-8', newline='') as f:
        index = {row['file_name']: row for row in csv.DictReader(f)}
    samples = []
    excluded = []
    slip_grid = np.linspace(0, 25.0, 100)
    for _, row in parameters.iterrows():
        sample_name = str(row['file name']).strip()
        if sample_name not in index:
            excluded.append(sample_name)
            print(f'Excluded parameter record absent from the supplied final database: {sample_name}')
            continue
        item = index[sample_name]
        source = (ROOT / item['raw_curve_path']).resolve()
        if not source.is_relative_to(ROOT):
            raise ValueError(f'Source path leaves the package: {source}')
        if hashlib.sha256(source.read_bytes()).hexdigest() != item['raw_curve_sha256']:
            raise ValueError(f'Raw source checksum mismatch: {sample_name}')
        curve = pd.read_csv(source, header=None, names=['Slip', 'Force'])
        curve.loc[curve['Slip'] < 0, 'Slip'] = 0
        curve = curve.sort_values(by='Slip').drop_duplicates(subset='Slip').reset_index(drop=True)
        interpolation = interp1d(curve['Slip'].values, curve['Force'].values,
                                kind='linear', bounds_error=False, fill_value=(0, 0))
        force = interpolation(slip_grid)
        sample = row.to_dict()
        sample.update({f'Force_{i}': round(value, 2) for i, value in enumerate(force)})
        samples.append(sample)
    rebuilt = pd.DataFrame(samples)
    supplied = pd.read_csv(ROOT/'data/database/Final_AI_Dataset.csv')
    if list(rebuilt.columns) != list(supplied.columns):
        raise ValueError('Column order differs from the supplied database')
    if rebuilt['file name'].tolist() != supplied['file name'].tolist():
        raise ValueError('Sample order differs from the supplied database')
    expected = supplied.iloc[:, 1:].to_numpy(dtype=float)
    actual = rebuilt.iloc[:, 1:].to_numpy(dtype=float)
    difference = float(np.max(np.abs(expected - actual)))
    identical = bool(np.array_equal(expected, actual))
    rebuilt.to_csv('Final_AI_Dataset_rebuilt.csv', index=False)
    result = {'rows': len(rebuilt), 'columns': len(rebuilt.columns),
              'parameter_rows': len(parameters), 'excluded_parameter_records': excluded,
              'all_identifiers_and_numeric_values_identical': identical,
              'maximum_absolute_numeric_difference': difference}
    Path('rebuild_comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not identical:
        raise ValueError('Rebuilt values differ; see rebuild_comparison.json')

if __name__ == '__main__':
    main()
