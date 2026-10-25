"""Mutation-based negative probes, all synthetic and tool-local."""
import copy
import json
import pathlib
import unittest
from check_scn001 import check

FIXTURE = pathlib.Path(__file__).resolve().parents[1] / 'fixtures' / 'scn001-trace.json'


class SCN001Test(unittest.TestCase):
    def setUp(self):
        self.good = json.loads(FIXTURE.read_text(encoding='utf-8'))

    def reject(self, change):
        bad = copy.deepcopy(self.good)
        change(bad)
        with self.assertRaises(ValueError):
            check(bad)

    def test_reference_trace(self):
        self.assertTrue(check(self.good))

    def test_modified_quote_without_new_fingerprint(self):
        self.reject(lambda d: d['observations'][1].update(quote='書き換え'))

    def test_suppressed_conflict(self):
        self.reject(lambda d: d.update(conflict={'evidence': ['O-02'], 'state': 'resolved'}))

    def test_adopted_hypothesis(self):
        self.reject(lambda d: d['hypotheses'][0].update(state='accepted'))

    def test_unauthorized_publish(self):
        self.reject(lambda d: d['snapshots'][1]['draft'].update(published=True))

    def test_scope_limited_non_discovery_becomes_absence(self):
        self.reject(lambda d: d['observations'][4].update(inferred_absence=True))

    def test_history_dropped_on_update(self):
        self.reject(lambda d: d['snapshots'][2]['observation_ids'].remove('O-01'))

    def test_stale_provenance(self):
        self.reject(lambda d: d['snapshots'][2]['draft']['basis'][0].update(sha256='0' * 64))

    def test_previous_authority_resurrected_on_text_return(self):
        self.reject(lambda d: d['snapshots'][2].update(decision={'status': 'accepted', 'authority': 'previous'}))

    def test_returning_text_conflated_with_source(self):
        self.reject(lambda d: d['observations'][6].update(source=d['observations'][1]['source']))


if __name__ == '__main__':
    unittest.main()
