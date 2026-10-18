# RetainQ information-retention study

Anonymous, CPU only. Python 3.11+; about 262 MB download and 1.5 GB source-oracle memory limit. Official MovieLens data are downloaded directly and are not bundled.

```bash
python -m pip install -r requirements.txt
python verify.py results  # verify supplied evidence offline
python study.py --data-dir cache --output rerun_results  # fresh run; downloads official MovieLens
python verify.py rerun_results  # verify your independently generated results
```

Open `RetainQ_Final_Study.ipynb` for executed results or a portable rerun. `results/summary.json`, `results/SCIENTIFIC_SCOPE.json` and the CSV/PDF figures are the primary outputs. `theory.tex` contains proofs and precise modelling limits. The original theorem/compiler and frozen aggregates are preserved; no original producer code is imported.

The fixed-catalogue experiment constructs alternative movie choices around observed histories. It preserves ratings, timestamps, counts and ranks. It tests source feasibility, not the prevalence of counterfactual preferences. Its release model is one sealed cumulative horizon; prefix-release controls show the limit. No privacy guarantee or new strong-baseline physical performance win is claimed.

The configuration, search rule, benchmark caps and five timing repeats are fixed in `config.json`. Timing methods differ in output scope; CSVs state that scope. Specialized analytic baselines are included where applicable. No speedup is inferred for a method skipped by a declared cap.

MovieLens: F. Maxwell Harper and Joseph A. Konstan. 2015. *The MovieLens Datasets: History and Context*. ACM TiiS 5(4), Article 19. DOI: 10.1145/2827872. Dataset use remains subject to the official `ml-25m/README.txt` downloaded with the archive; no endorsement is implied.

Prior query-auditing/retention context: [Nabar et al.](https://cs.stanford.edu/people/kngk/papers/surveyQueryAuditingTechniquesDataPrivacy.pdf), [Lu and Miklau](https://people.cs.umass.edu/~miklau/assets/pubs/icde09/lu09auditing.pdf). General row-space auditing is established work; novelty rests with the original quota characterization/compiler and the specific supplementary certificates, not that general principle.
