"""Read-only checks of supplied evidence. Python standard library only."""
from pathlib import Path
import csv, hashlib, json
ROOT = Path(__file__).resolve().parents[1]
def read_csv(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def require(condition, message):
    if not condition:
        raise ValueError(message)
def distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j-1] + (x != y)))
        row = new
    return row[-1]
def scores(rows):
    result = []
    for transform in (str.split, list, lambda s: list(''.join(s.split()))):
        pairs = [(transform(r['reference']), transform(r['prediction'])) for r in rows]
        result.append(100 * sum(distance(a, b) for a,b in pairs) / sum(len(a) for a,b in pairs))
    return result

def main():
    paths = {
        'data/metadata/segments_metadata_v1_2_train_val_frozen.csv': '4911f46e0a8c3656089677b8899d8296b9e1528d8aa3633a64728eb645f28fab',
        'data/metadata/segments_metadata_v1_3_final_eval.csv': 'fd496632b179c97ab18189d0300b0fd84d1cda1d17a8071d4b3dc108b2ca1f70',
    }
    for path, expected in paths.items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, 'Frozen file changed: '+path)
    dev, combined = [read_csv(p) for p in paths]
    test = [r for r in combined if r['dataset_split'] == 'test']
    sets = [[r for r in dev if r['dataset_split'] == s] for s in ['train', 'validation']] + [test]
    require([len(s) for s in sets] == [1754,129,115], 'Unexpected partition counts')
    speakers = [set(r['speaker_group_id'] for r in s) for s in sets]
    require(all(not speakers[i] & speakers[j] for i in range(3) for j in range(i)), 'Speaker overlap')
    require(len({r['segment_id'] for r in combined}) == len(combined), 'Duplicate IDs')
    by_id = {r['segment_id']:r for r in combined}
    for r in dev:
        require(r['segment_id'] in by_id, 'Development segment missing')
        for k in ['dataset_split','speaker_group_id','duration_seconds']:
            require(r[k] == by_id[r['segment_id']][k], 'Development assignment/duration changed')
    changes = [r for r in dev if r['transcription'] != by_id[r['segment_id']]['transcription']]
    require(len(changes) == 19 and all(r['dataset_split']=='train' for r in changes), 'Unexpected transcript differences')
    print('PASS: frozen hashes, 1754/129/115 rows, disjoint speakers; 19 documented training-text differences.')
    for f in (ROOT/'notebooks').rglob('*.ipynb'):
        d = json.loads(f.read_text())
        require(d.get('nbformat') == 4 and isinstance(d.get('cells'),list), 'Invalid notebook: '+str(f))
    print('PASS: selected notebook JSON parses.')
    # Exact saved normalized references/hypotheses; no new text normalization.
    expected = {
        'mms_greedy_baseline': (66.98,21.96,21.55),
        'mms_half_bible_specaug': (70.75,18.97,15.91),
        'mms_full_specaug': (73.13,19.59,16.66),
        'fadhma_full': (74.48,22.73,19.85),
        'omni_full': (75.40,22.66,19.84),
    }
    ids = {r['segment_id'] for r in test}
    for model, target in expected.items():
        rows = read_csv('results/final_test_v1_3/'+model+'/predictions.csv')
        require(len(rows)==115 and {r['segment_id'] for r in rows}==ids, 'Prediction membership mismatch: '+model)
        require(all(r['reference']==by_id[r['segment_id']]['transcription'] for r in rows), 'Reference mismatch: '+model)
        got = scores(rows)
        require(all(abs(g-t)<0.006 for g,t in zip(got,target)), 'Metric mismatch: '+model)
        print(model+': '+', '.join(f'{s:.2f}%' for s in got)+' (WER, CER, CER without spaces)')
    rows = read_csv('results/mms_1b_tarifit_v1_2_specaug/validation_predictions.csv')
    got = scores(rows)
    require(abs(got[0]-85.9693877551)<1e-6 and abs(got[1]-43.2671436611)<1e-6, 'MMS validation mismatch')
    print('PASS: selected MMS validation checkpoint reproduces 85.97% WER / 43.27% CER.')
    print('Evidence checks passed. Audio, model loading, training and bootstrap reruns were not performed.')

if __name__ == '__main__':
    main()
