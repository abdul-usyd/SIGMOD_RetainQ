#!/usr/bin/env python3
"""Run the anonymized CPU-only RetainQ information-retention study."""
from __future__ import annotations
import argparse, importlib.metadata, json, os, platform, sys, time, zipfile
from pathlib import Path
import numpy as np
from retainq_study import exact, experiments, source


def run(output,cache):
    if not __debug__:raise RuntimeError('Scientific verification must run without Python -O.')
    started=time.perf_counter();root=Path(__file__).resolve().parent
    config=json.loads((root/'config.json').read_text());out=Path(output)
    out.mkdir(parents=True,exist_ok=False)
    for name in ('tables','evidence','provenance'): (out/name).mkdir()
    archive=root/'v6_aggregates.zip';inputs=out/'inputs'
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            p=Path(member.filename)
            if p.is_absolute() or '..' in p.parts or member.is_dir():raise ValueError('unsafe input name')
        z.extractall(inputs)
    provenance=json.loads((inputs/'subset_provenance.json').read_text())
    for name,digest in provenance['selected_original_checksums'].items():
        assert source.digest(inputs/name)==digest
    bundles={c:{k:exact.read_bundle(inputs,c,k) for k in exact.KINDS} for c in exact.CASES}
    context={'run':out,'bundles':bundles,'checks':[],'analyses':{}}
    versions={p:importlib.metadata.version(p) for p in ('numpy','pandas','matplotlib','duckdb','nbformat')}
    exact.dump_json(out/'provenance/environment.json',{'python':platform.python_version(),
        'platform':platform.system()+' '+platform.machine(),'packages':versions,'cpu_only':True,
        'duckdb_threads':2,'seed':config['seed'],'memory_limit_for_source_oracles':'1500MB'})
    exact.dump_json(out/'provenance/configuration.json',config)
    print('1/7 Exact frozen-state and information audit',flush=True)
    exact.audit_representations(context)
    experiments.disclosure_profile(context)
    context['reconstruction']=exact.reconstruction_experiment(context)
    experiments.negative_reconstruction_controls(context)
    print('2/7 Verify fixed MovieLens catalogue and source archive',flush=True)
    data=source.obtain_data(cache)
    exact.dump_json(out/'provenance/source.json',data['provenance'])
    print('3/7 Independent full-source capture; verify M0 and M1 against frozen states',flush=True)
    captured,receipt=experiments.capture_cached(data,cache)
    experiments.verify_real_source(context,captured,receipt)
    # Preserve an independently reconstructed M0 reference table from fresh source.
    truth=captured['G5_H162541'];m0=context['analyses']['M0']
    for row in __import__('csv').DictReader((out/'tables/M0_reconstruction.csv').open()):
        metric=0 if row['metric']=='twice recorded rating' else 1
        assert int(row['reconstructed_from_graph_query_answers'])==truth[metric,int(row['group'])*10+int(row['rank_position'])-1]
    print('4/7 Fixed-catalogue source-feasible M1 kernel and independent edited-source oracle',flush=True)
    context['fixed_catalogue']=experiments.fixed_catalogue_experiment(context,data,captured,cache,config)
    print('5/7 Exhaustive small-box compiler and membership validation',flush=True)
    context['exhaustive']=experiments.exhaustive_geometry(context)
    print('6/7 Predeclared quota sensitivity and strong-baseline scalability',flush=True)
    experiments.policy_sensitivity(context);experiments.scalability(context,config)
    experiments.mutation_controls(context)
    print('7/7 Figures, scientific scope, checksums, and final evidence',flush=True)
    experiments.figures(context)
    exact.save_csv(out/'tables/checks.csv',context['checks'])
    scope={
        'supported':[
            'M0 permitted answers reconstruct every reachable cumulative rank metric; freshly validated against all 25M source rows.',
            'At the observed M1 answer vector, a fixed MovieLens catalogue permits 512 certified alternative histories spanning all nine year-metric kernel directions.',
            'Every one of 20 cumulative year-rank coordinates is nonunique across these compatible valid histories.',
            'Because feasible year differences span the complete kernel, at the observed joint answer vector a linear year statistic is uniquely determined over the fixed-catalogue source domain exactly when its coefficients belong to the authorised row space.',
            'Raw and pruned marginals distinguish all 512 histories; answer materialization and the forest retain one common state.',
            'The structural target-membership criterion and interval graph compiler agree with independent exact elimination on all enumerated small boxes.',
        ],
        'not_established':[
            'Differential privacy, anonymity, resistance to arbitrary auxiliary knowledge, or protection of every source history.',
            'Uniqueness or recovery of individual users, movie identities, or complete source records from M0 answers.',
            'An information advantage over storing all permitted answers: both have exactly the authorised row space.',
            'An end-to-end storage, ingestion, or query-latency win over the strongest physical baseline.',
            'An estimate of the frequency, probability, or human plausibility of constructed counterfactual preferences.',
            'Novelty of the general row-space query-auditing principle.',
            'Minimal bits among arbitrary encodings or feasible-domain-specific minimum state dimensions.',
        ],
        'modelling_limits':[
            'All authorised exact quota answers are assumed available; rate limits or different access controls alter the problem.',
            'The released object is one sealed cumulative horizon. Per-user answers, intermediate prefix releases, source logs, or other retained views may distinguish the histories; a prefix-release control explicitly demonstrates this limit.',
            'The catalogue is fixed. Alternative histories change selected movie choices while preserving observed ratings, timestamps, user counts, group membership, and ranking positions.',
            'Year compatibility is checked against timestamp year; exact cinema release dates are unavailable.',
            'MovieLens is public. Counterfactual source feasibility is a controlled benchmark property, not a claim of privacy for publicly known ratings.',
            'The nine-dimensional feasibility certificate concerns the year metric; rating values remain unchanged.',
            'Quota sensitivity is structural. Source-level feasible ambiguity is demonstrated for the M1 contract, not presumed for all swept contracts.',
            'Timings are one-machine observations with five repeats and explicit deterministic caps. Analytic baselines are included on their applicable families.',
        ],
    }
    exact.dump_json(out/'SCIENTIFIC_SCOPE.json',scope)
    assert all(row['passed'] for row in context['checks'])
    summary={'version':config['study_version'],'cpu_only':True,'all_checks_passed':True,
        'source':data['provenance'],'m0_reconstruction':context['reconstruction'],
        'fixed_catalogue_m1':context['fixed_catalogue'],'exhaustive_geometry':context['exhaustive'],
        'linear_disclosure_profiles':context['disclosure_profile'],
        'quota_sensitivity_contracts':len(context['sensitivity']),
        'scalability_measurements':sum(x['repetitions'] for x in context['scalability']),
        'checks':context['checks'],'actual_privacy_guarantee':False,
        'new_strong_baseline_systems_performance_advantage':False,
        'elapsed_seconds_diagnostic_only':time.perf_counter()-started}
    exact.dump_json(out/'summary.json',summary)
    hashes={p.relative_to(out).as_posix():source.digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    exact.dump_json(out/'CHECKSUMS.json',hashes)
    print(json.dumps({k:summary[k] for k in ('all_checks_passed','quota_sensitivity_contracts','scalability_measurements','elapsed_seconds_diagnostic_only')},indent=2),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='results',help='new output directory; refuses to overwrite')
    parser.add_argument('--data-dir',default='cache',help='cache for official MovieLens download; never distributed')
    args=parser.parse_args();run(Path(args.output),Path(args.data_dir))


if __name__=='__main__':main()
