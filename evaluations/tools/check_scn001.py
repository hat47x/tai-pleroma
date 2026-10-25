#!/usr/bin/env python3
"""SCN-001 synthetic-fixture consistency probe, not a TAI runtime or semantic validator."""
import hashlib
import json
import sys
from pathlib import Path


def check(data):
    def ensure(test, message):
        if not test:
            raise ValueError(message)

    ensure(data.get('kind') == 'scn001-synthetic-trace/v0', 'unexpected fixture kind')
    observations = data['observations']
    ensure(len(observations) == 7, 'expected seven synthetic observations')
    by_id = {x['id']: x for x in observations}
    ensure(len(by_id) == 7, 'observation identity was reused')
    for item in observations:
        ensure(item['source'].startswith('synthetic://'), f"non-synthetic source: {item['id']}")
        ensure(item['revision'] and item['quote'], f"missing source/revision: {item['id']}")
        actual = hashlib.sha256(item['quote'].encode('utf-8')).hexdigest()
        ensure(actual == item['sha256'], f"quote hash mismatch: {item['id']}")
    ensure(by_id['O-05']['claim'] == 'not-found-in-reviewed-materials', 'O-05 scope lost')
    ensure(by_id['O-05']['inferred_absence'] is False, 'non-discovery became global absence')
    ensure(by_id['O-02']['quote'] == by_id['O-07']['quote'], 'expected a textual A→B→A return')
    ensure(by_id['O-02']['source'] != by_id['O-07']['source'], 'repeated text was conflated with source identity')
    ensure(by_id['O-02']['sha256'] == by_id['O-07']['sha256'], 'identical text has different digest')
    ensure(by_id['O-06']['quote'] != by_id['O-02']['quote'], 'middle version must differ')

    hypotheses = data['hypotheses']
    ensure({h['id'] for h in hypotheses} == {'H-01', 'H-02', 'H-03'}, 'missing hypotheses')
    for h in hypotheses:
        ensure(h['state'] == 'proposed', 'hypothesis incorrectly accepted')
        ensure(all(r in by_id for r in h['basis']), 'hypothesis has unknown source')
    ensure(data['conflict'] == {'evidence': ['O-02', 'O-03'], 'state': 'unresolved'},
           'source conflict suppressed or marked resolved')

    snapshots = data['snapshots']
    ensure([s['id'] for s in snapshots] == ['T0', 'T1', 'T2'], 'timeline changed')
    for i, s in enumerate(snapshots):
        expected = [f'O-{n:02d}' for n in range(1, 6 + i)]
        ensure(s['observation_ids'] == expected, f"non-append-only timeline: {s['id']}")
        draft = s['draft']
        ensure(draft['id'] == f'D-{i+1:02d}', 'draft identity lost')
        ensure(draft['state'] == 'draft' and draft['published'] is False, 'draft released or misrepresented')
        ensure('確認中' in draft['text'], 'uncertainty missing from draft')
        refs = draft['basis']
        expected_refs = [
            {'O-02', 'O-03'},
            {'O-02', 'O-03', 'O-06'},
            {'O-02', 'O-03', 'O-06', 'O-07'},
        ][i]
        ensure({ref['id'] for ref in refs} == expected_refs, 'draft evidence set does not match step')
        for ref in refs:
            ensure(ref['id'] in s['observation_ids'], 'draft references an unavailable version')
            ensure(ref['sha256'] == by_id[ref['id']]['sha256'], 'draft reference is stale')
        ensure(s['decision'] == {'status': 'undecided', 'authority': 'unknown'},
               'unaccepted meaning or authority was silently promoted')
        ensure(s['execution'] == 'not-performed', 'external effect inferred or performed')
    return ['source-fingerprints', 'conflict-and-hypotheses', 'three-snapshots',
            'draft-provenance', 'authority-boundary', 'return-without-reapproval']


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print('Usage: python3 evaluations/tools/check_scn001.py evaluations/fixtures/scn001-trace.json', file=sys.stderr)
        return 2
    try:
        checks = check(json.loads(Path(args[0]).read_text(encoding='utf-8')))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f'FAIL (synthetic consistency only): {error}', file=sys.stderr)
        return 1
    print(f'PASS (synthetic consistency only): {", ".join(checks)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
