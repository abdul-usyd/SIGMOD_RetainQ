#!/usr/bin/env python3
"""Offline verification of the final evidence and exact reconstruction witnesses."""
import argparse, json
from pathlib import Path
from fractions import Fraction
import numpy as np
from retainq_study import exact,source


def verify(root):
    if not __debug__:raise RuntimeError('Verification must run without Python -O.')
    root=Path(root);hashes=json.loads((root/'CHECKSUMS.json').read_text())
    for name,expected in hashes.items():
        assert source.digest(root/name)==expected,name
    summary=json.loads((root/'summary.json').read_text());assert summary['all_checks_passed']
    data=json.loads((root/'evidence/M0_independent_decoder.json').read_text())
    inverse=[[Fraction(x) for x in row] for row in data['exact_decoder']]
    positions=[tuple(p) for p in data['target_positions']]
    matrix=[[exact.policy_row(q,10)[g*10+r-1] for g,r in positions] for q in data['queries']]
    assert exact.invert_exact(matrix)==inverse
    D=np.array(json.loads((root/'evidence/feasible_year_kernel_basis.json').read_text())['basis'],dtype=np.int64)
    A=np.array([exact.policy_row((q,10-q),10) for q in range(11)],dtype=np.int64)
    assert exact.ExactSpan(D.tolist()).rank==9 and not np.any(D@A.T)
    import csv
    worlds=list(csv.DictReader((root/'tables/fixed_catalogue_worlds.csv').open()))
    assert len(worlds)==512 and all(r['all_22_answers_equal_from_direct_source_selection']=='True' for r in worlds)
    print(f'PASS: {len(hashes)} file hashes, exact M0 decoder, rank-nine M1 kernel, and 512 world certificates.')
    print('Source-level revalidation: run study.py with the official MovieLens archive; raw data are intentionally not bundled.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('results',nargs='?',default='results')
    verify(p.parse_args().results)
