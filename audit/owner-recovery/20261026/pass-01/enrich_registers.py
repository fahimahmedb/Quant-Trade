from catalog import *
from collections import Counter
refs=loadrefs(); can=refs['builder/convergence-wave2-canonical-20261021']
def readcsv(name): return list(csv.DictReader((ROOT/'reports'/name).open()))
branches=readcsv('05_BRANCH_AND_RAIL_LEDGER.csv')
spec={
'blue/master-v2-2026-09-20':('Default GitHub / routing historique','DEFAULT_ROUTING_BRANCH; NOT_CURRENT_INTEGRATED_PRODUCT_PROOF','UNKNOWN','UNKNOWN'),
'builder/convergence-wave2-canonical-20261021':('Convergence cumulative Wave2 C2','QUALIFIED_CANDIDATE; FORMAL_OWNER_SEAL_NOT_FOUND','CUMULATIVE_EXACT_HEAD_PASS_39882531103; MEGA_E_GATE_FAIL_39882531036','REFERENCE_CANDIDATE_ONLY'),
'builder/convergence-cp069-wave2-base-20261021':('Premier rail cumulatif fondé sur CP069','SUPERSEDED_BASE_ATTEMPT','UNKNOWN_FOR_EXACT_HEAD','REPLACED_BY_CP079_BASE; NOT_ALL_SOURCE_HEADS_ANCESTORS'),
'builder/convergence-cp079-wave2-base-20261021':('Base immuable réparée Wave2','IMMUTABLE_BASE_USED_BY_W2_AND_V3','BASE_QUALIFICATION_REFERENCES; NOT_REFETCHED_CI_IN_THIS_PASS','EXACT_ANCESTOR_OF_W2'),
'builder/wave2-convergence2-foreman-20261021':('Préparation de convergence, conflits et ordre des ports','DOCUMENTARY_FOREMAN_NOT_PRODUCT_BUILD','NOT_A_PRODUCT_QUALIFICATION','BRANCH_DOCS; DOWNSTREAM_CONVERGENCE_HAS_PORTS'),
'builder/wave2-seal-preflight-20261021':('Qualification exacte des bases cumulatives','QUALIFICATION_TOOLING_HISTORICAL','EXACT_BASE_TARGET_RECORDED; NOT_HEAD_PRODUCT_QUALIFICATION','BASE_PREFLIGHT_REUSED; NOT_PRODUCT_TRUNK'),
'builder/convergence2-multisource-pinned-b5ba7541':('Pin MultiSource avant mises à jour tardives','HISTORICAL_PIN_SUPERSEDED_BY_BBDEA_IN_W2','UNKNOWN_FOR_FINAL_HEAD','W2_MERGED_LATER_MS_HEAD'),
'builder/mega-a-research-intelligence-20261021':('Recherche pré-outcome : mémoire, identité, choix des actions','PORT_PRESENT_IN_W2; PRODUCTION_USE_NOT_PROVEN','EXACT_HEAD_SEC_ONLY; NOT_RI_QUALIFICATION','RESEARCH_INTELLIGENCE_BLOB_BYTE_EQUAL'),
'builder/mega-b-discovery-engine-20261021':('Discovery : contrat Candidate commun et handoff Factory','ADAPTED_PORT_PRESENT_IN_W2','EXACT_HEAD_MEGA_B_PASS_39656474279','ADAPTED_FILES_DIFFER; CUMULATIVE_SEAM_TESTED'),
'builder/mega-c0-scientific-adjudication-20261021':('Arbitrage scientifique C0 et indépendance sémantique','OLDER_KERNEL_PORTED; LATE_REPAIR_NOT_PORTED','EXACT_HEAD_C0_PASS_39662900753; SEC_GATE_FAIL','OLDER_3f0e1b7_KERNEL_IN_W2; LATEST_d19b867_NOT_BYTE_EQUAL'),
'builder/mega-d0-economic-lifecycle-20261021':('Lifecycle économique pré-outcome D0','KERNEL_PRESERVED_AND_ADAPTED_IN_W2','EXACT_HEAD_D0_PASS_39623992108; SEC_GATE_FAIL','KERNEL_BYTE_EQUAL; CANONICAL_ADAPTER_REBINDS_BASE'),
'builder/mega-e-autonomous-runtime-20261021':('Runtime autonome, reprise, reçus et outbox','CODE_PRESENT_IN_W2; DEPLOYMENT_NOT_PROVEN','EXACT_SOURCE_HEAD_PASS_39637373986; W2_SEPARATE_GATE_FAIL','ORACLE_WORKER_BYTE_EQUAL; CUMULATIVE_RUNTIME_TESTS_PASS'),
'builder/multi-source-ideation-intake-20261021':('MultiSource V1/V2 : politiques passives et admission','MERGED_IN_W2; V3_EXISTS_OFF_CANDIDATE','W2_EXACT_HEAD_MS_QUALIFICATION_PASS','CORE_FILE_BYTE_EQUAL; GIT_MERGE_0722dc4'),
'builder/multi-source-outcome-firewall-repair-20261021':('Réparation firewall du MultiSource historique','HISTORICAL_REPAIR_SCOPE','UNKNOWN_FOR_EXACT_HEAD','TARGET_CONTENT_REQUIRES_TARGETED_REPLAY'),
'builder/multi-source-ideation-intake-v3-20261026':('Admission V3 durable, bornée, idempotente et hostile','QUALIFIED_ON_BRANCH; NOT_IN_W2_OR_RUNTIME','EXACT_HEAD_V3_PASS_40249296902','NOT_INTEGRATED; BASE_2b99_NOT_W2_HEAD'),
'builder/giga-f-idea-federation-autonomous-feed-20261023':('Fédération et flux borné, dénominateur/exposition upstream','IMPLEMENTED_QUALIFIED_ON_BRANCH; FEED_DISABLED','EXACT_HEAD_GIGA_F_PASS_40054403097','3_COMMITS_AFTER_W2; NOT_IN_W2_Q_OR_RUNTIME'),
'builder/giga-q-final-whole-system-hardening-20261023':('Durcissement transversal et rejeu du corpus hostile','IMPLEMENTED_REPAIRS; NOT_QUALIFIED; BLOCKERS_REMAIN','EXACT_HEAD_FAIL_40054895425; HISTORICAL_V_FAIL','3_COMMITS_AFTER_W2; NOT_INTEGRATED'),
'codex/horizontal-completeness-prewave2-20261021':('H phase A : couverture avant Wave2','BOUNDED_LOCAL_QUALIFICATION; PHASE_B_NOT_STARTED','LOCAL_LOGS; NO_EXACT_HEAD_HOSTED_CI_FOUND','SEPARATE_RAIL; REPLAY_REQUIRED_ON_CONVERGED_TARGET'),
'codex/horizontal-completeness-convergence1-20261021':('H sur Convergence1 : modules, seams et L001','BOUNDED_LOCAL_QUALIFICATION; L001_OPEN','LOCAL_LOGS; NO_EXACT_HEAD_HOSTED_CI_FOUND','SEPARATE_RAIL; Q_PARTIAL_REPAIRS_OVERLAP'),
'codex/vertical-depth-prewave2-20261021':('V : attaques, réparations et correction des faux CP de profondeur','OWNER_STOPPED_CP046; 47_SUBSTANTIVE_ENTRIES; PHASE_A_INCOMPLETE','QUALIFIED_SOURCE_e98a1b2; 83_SOURCE_HASHES_334_LOG_HASHES_VERIFIED; NO_HEAD_HOSTED_CI','SEPARATE_RAIL; Q_RETAINS_OLDER_92c4ee0_CORPUS'),
'builder/oracle-v2-core-20261020':('Runtime Git durable Oracle V2 et activité production','RECENT_DURABLE_WAKE; NOOP_FRONTIER_EXHAUSTED','POSTBOOT_AND_NATIVE_GITHUB_PROOFS; LATEST_WAKE_2026_10_26_005015Z','RUNTIME_STATE_RAIL; RELEASE_a67ffec_NOT_W2'),
'builder/oracle-economic-loop-recovery-20261019':('Oracle V1 et workers multi-étapes','HISTORICAL_RUNTIME_SUPERSEDED_BY_V2_TIMER','DOCUMENTARY_REAL_WAKES_AND_TASKS','V1_CODE_HISTORY_REUSED; NOT_CURRENT_TIMER'),
'builder/oracle-v2-live-lab-bridge-20261020':('Projection Oracle vers Live Lab','BOUND_REAL_EVENTS_PROOF; CURRENT_HOST_NOT_OBSERVED','SAVED_SSE_AND_REDUCER_PROOFS','CONTRACT_PROJECTION; NOT_RESEARCH_OWNER'),
'builder/live-lab-oracle-canonical-20261020':('Interface Live Lab / Oracle','BRANCH_LOCAL_UX_AND_CONNECTION_PROOFS','SAVED_BROWSER_SSE_AND_PRODUCTION_ARTIFACTS; FRESH_REMOTE_PROBE_NOT_PERFORMED','SOME_CONTENT_IN_W2; FULL_TREE_EQUIVALENCE_PENDING'),
'builder/live-lab-oracle-integration-20261020':('Intégration projection et identité Live Lab','HISTORICAL_INTEGRATION_RAIL','SAVED_PROOFS; EXACT_HEAD_CI_NOT_FETCHED','SUBSEQUENT_LIVE_LAB_CANONICAL_RAIL'),
'research/economic-test-form144-supply-20261017':('Protocole, admission et tentative économique Form144','EXECUTED_SOURCE_ACQUISITION; PARK_DATA_HTTP403','ACTUAL_RUN_39032686104_FAILURE_BEFORE_OUTCOME; FROZEN_RESULT_EXISTS','UNIQUE_EXPERIMENT_ARTIFACTS_NOT_IN_RUNTIME_OR_W2'),
'builder/econ-test-flow-ust-auction-20261019':('Validation puis protocole figé Treasury 10Y','FROZEN_PROTOCOL; DECLARED_AUTHORIZATION; EXECUTION_NOT_FOUND','DOCUMENTARY_CHECKPOINTS; NOT_ECONOMIC_EXECUTION_PROOF','PROTOCOL_INHERITED_BY_RUNTIME_AND_W2; NO_EXECUTION_DESCENDANT_FOUND'),
'research/duebill-source-readiness-20261017':('Qualification des données Due Bill / when-issued','PARK_DATA_REPRODUCIBLE_PAIR_HISTORY_MISSING','SOURCE_READINESS_ARTIFACT; NO_OUTCOME_EXECUTION','BRANCH_LOCAL_ASSESSMENT_NOT_IN_RUNTIME_OR_W2'),
'research/close-auction-source-readiness-20261017':('Qualification des sources enchère de clôture','BRANCH_EXISTS; EXACT_ASSESSMENT_PATH_STILL_TO_RECONSTRUCT','NOT_YET_SEMANTICALLY_REVIEWED','UNKNOWN'),
'research/edge-lab-continuous':('Discovery historique et expériences à faible coût','DURABLE_RESULTS_PARKS_AND_ONE_PROMOTED_VX_EXPRESSION; NO_CURRENT_WORKER_PROOF','REAL_RESULT_AND_RECEIPT_ARTIFACTS; NOT_ALL_RUNS_REAUDITED','PARTIAL_HISTORY_COPIED; DIVERGENT_LATER_RESEARCH_REMAINS'),
'research/legacy-economic-reconciliation-20261015':('Réconciliation historique et mémoire négative','20_RECONCILIATION_RECORDS; EXPLICIT_GAPS','RECORD_EXISTENCE_ONLY; NOT_PRIMARY_PROOF_OF_ALL_RESULTS','PINNED_IMPORT_USED_BY_RUNTIME'),
'audit/forensic-checkpoint-20261019':('Audit historique des rails','HISTORICAL_AUDIT_LEAD_ONLY','NOT_PRODUCT_QUALIFICATION','SOURCE_FOR_LEADS_NOT_CURRENT_TRUTH'),
'builder/research-os-autonomous-loop-20261015':('Producteurs et validations du premier loop','HISTORICAL_LOOP_WITH_REAL_TASKS','DURABLE_TASK_HYPOTHESIS_ASSESSMENT_ARTIFACTS','ANCESTRAL_RESEARCH_STATE; SUPERSEDED_RUNTIME'),
'builder/research-os-econ-readiness-activation-20261017':('Activation contrôlée de readiness sur état autonome','HISTORICAL_ACTIVATION; NOT_GLOBAL_ECONOMIC_AUTHORITY','COMMIT_e980d201_AND_BRANCH_INPUTS','ANCESTRAL_TO_FORM144_AND_ORACLE_STATE'),
'builder/w1-scientific-memory-depth-20261021':('W1 Scientific Memory','FUNCTIONAL_PORT_PRESENT_IN_W2','BRANCH_QUALIFICATION_NOT_INDEPENDENTLY_REFETCHED','CUMULATIVE_SCIENTIFIC_MEMORY_CODE_AND_TESTS_PRESENT'),
'builder/w1-data-evidence-sec-depth-20261021':('W1 données, PIT, evidence, SEC','FUNCTIONAL_PORT_PRESENT_IN_W2','BRANCH_QUALIFICATION_NOT_INDEPENDENTLY_REFETCHED','CUMULATIVE_DATA_CODE_AND_TESTS_PRESENT'),
'builder/w1-factory-experiment-depth-20261021':('W1 Factory/Freeze/Trial/Experiment','FUNCTIONAL_PORT_PRESENT_IN_W2','BRANCH_QUALIFICATION_NOT_INDEPENDENTLY_REFETCHED','CUMULATIVE_EXPERIMENT_CODE_AND_TESTS_PRESENT'),
'builder/w1-economic-portfolio-depth-20261021':('W1 Economic Identity / Portfolio','FUNCTIONAL_PORT_PRESENT_IN_W2','BRANCH_QUALIFICATION_NOT_INDEPENDENTLY_REFETCHED','CUMULATIVE_ECONOMIC_CODE_AND_TESTS_PRESENT'),
}
for r in branches:
    x=spec.get(r['BRANCH'])
    if x:
        r.update(MISSION=x[0],CURRENT_STATUS=x[1],QUALIFIED=x[2],INTEGRATED=x[3],SUPERSEDED='YES_AS_BASE' if 'SUPERSEDED_BASE' in x[1] else 'SCOPE_DEPENDENT; see status',UNIQUE_UNINTEGRATED_WORK=x[3],RELEVANCE_TODAY='CURRENT_RECONCILIATION_OR_REUSABLE_SCOPED_VALUE',EVIDENCE_CLASS='FACT_PROVEN_GIT_AND_CITED_ARTIFACTS; STATUS_SCOPED')
        r['AUDIT_REVIEW_STATUS']='SCOPED_REVIEW_COMPLETE' if 'NOT_YET' not in x[2] else 'PARTIAL_REVIEW'
    else:r['AUDIT_REVIEW_STATUS']='GIT_CENSUS_ONLY; SEMANTIC_REVIEW_PENDING'
csvout('05_BRANCH_AND_RAIL_LEDGER.csv',branches)

cp=readcsv('04_CP_MASTER_INDEX.csv'); cm=json.loads((ROOT/'evidence/all_commits.json').read_text());bysha={x['sha']:x for x in cm}
for r in cp:
    sha=r['COMMIT_SHA'];changes=git('diff-tree','--no-commit-id','--name-only','-r',sha,check=False).decode().splitlines() if sha!='UNKNOWN' else []
    code=[p for p in changes if pathlib.Path(p).suffix in ['.py','.js','.mjs','.ts','.sh'] and '/tests/' not in p and not pathlib.Path(p).name.startswith('test_')]
    r['WAS_CODE_CHANGED']='YES_IN_ARTIFACT_INTRODUCTION_COMMIT' if code else 'NO_IN_ARTIFACT_INTRODUCTION_COMMIT; CP repair may be earlier'
    r['ONLY_DOCUMENTATION']='YES_INTRODUCTION_COMMIT' if changes and all(pathlib.Path(p).suffix in ['.md','.txt'] for p in changes) else 'NO_OR_MIXED'
    r['EVIDENCE_RECORD_KIND']='CHECKPOINT_ARTIFACT_VERSION'
    r['AUDIT_REVIEW_STATUS']='PENDING_SEMANTIC_AUDIT'
    if r['PATH'].startswith('VERTICAL_CP'):
        # Only the version actually at the frozen V tip is current disposition.
        b=git('rev-parse',refs['codex/vertical-depth-prewave2-20261021']+':'+r['PATH'],check=False).decode().strip()
        if b==r['BLOB_SHA']:
            r['AUDIT_REVIEW_STATUS']='CURRENT_LABEL_DISPOSITION_VERIFIED_IN_HASH_BOUND_QUALIFICATION'
            r['EVIDENCE_CLASS']='FACT_PROVEN_CURRENT_LABEL_DISPOSITION; REPAIR_ITEM_INDEPENDENCE_NOT_CLAIMED'
            n=int(re.search(r'\d+',r['CP_ID']).group())
            r['DEFECT_FOUND']='NO_DEFECT; PROCESS_DEATH_PROOF' if n==39 else ('YES_ENUMERATED_REPAIR_GROUP' if n<=46 or n==61 else 'NO_ACCEPTED_NEW_DEFECT_FROM_THIS_LABEL')
            r['DEFECT_REPAIRED']='YES_SCOPED_IN_VERIFIED_SOURCE_AND_LOGS' if n<=46 and n!=39 or n==61 else 'NO_NEW_REPAIR_CLAIM'
            r['LATER_INVALIDATED']='YES_DEPTH_LABEL_REJECTED' if n in list(range(47,61))+list(range(62,101)) else 'NO_CURRENT_SCOPE_RETRACTION_FOUND'
    r['INTRODUCTION_CHANGED_PATHS']=';'.join(changes)
    r['CODE_CHANGE_SCOPE_NOTE']='Introducer commit is not automatically the executable commit qualified by this checkpoint.'
# Preserve explicit checkpoint labels in commit subjects even without a named CP file.
bound={(r['COMMIT_SHA'],r['CP_ID']) for r in cp}
for c in cm:
    tokens=list(dict.fromkeys(x.upper() for x in re.findall(r'(?<![A-Z0-9])CP[_-]?\d+[A-Z]?(?![0-9])',c['subject'],re.I)))
    for token in tokens:
        if (c['sha'],token) in bound:continue
        r={k:'UNKNOWN' for k in cp[0]}
        r.update(RAIL='COMMIT_LABEL_SCOPE_UNRESOLVED',CP_ID=token,DATE=c['commit_time'],COMMIT_SHA=c['sha'],PARENT=c['parents'],MISSION=c['subject'],WHAT_WAS_TESTED='NOT_INFERRED_FROM_COMMIT_SUBJECT',WHAT_WAS_FOUND='SUBJECT_LABEL_ONLY; source artifacts/rail binding pending',CLASSIFICATION='UNKNOWN',EVIDENCE_CLASS='FACT_PROVEN_LABEL_EXISTS; FUNCTIONAL_INTERPRETATION_UNKNOWN',PATH='NOT_FOUND_BOUND_CP_ARTIFACT_IN_THIS_PASS',BLOB_SHA='N/A',BOUND_SHAS=c['sha'],EVIDENCE='https://github.com/fahimahmedb/Quant-Trade/commit/'+c['sha'],EVIDENCE_RECORD_KIND='COMMIT_LABEL_NOT_YET_BOUND_TO_RAIL',AUDIT_REVIEW_STATUS='PENDING_RAIL_BINDING_AND_SEMANTIC_AUDIT',CODE_CHANGE_SCOPE_NOTE='A subject mentioning CP is not proof that CP passed; may refer to target, stop or rejected label.')
        cp.append(r)
csvout('04_CP_MASTER_INDEX.csv',cp)
stats=dict(branches_discovered=len(branches),branches_scoped_reviewed=sum(x['AUDIT_REVIEW_STATUS']=='SCOPED_REVIEW_COMPLETE' for x in branches),branches_partial=sum(x['AUDIT_REVIEW_STATUS']=='PARTIAL_REVIEW' for x in branches),cp_records=len(cp),cp_current_label_dispositions_verified=sum(x['AUDIT_REVIEW_STATUS'].startswith('CURRENT_LABEL') for x in cp),cp_artifact_versions=sum(x['EVIDENCE_RECORD_KIND']=='CHECKPOINT_ARTIFACT_VERSION' for x in cp),commit_label_records=sum(x['EVIDENCE_RECORD_KIND']!='CHECKPOINT_ARTIFACT_VERSION' for x in cp),cp_unique_scope_warning='CP record count includes versions and unbound subject references; not independent or completed checkpoints.',branches_pending=[x['BRANCH'] for x in branches if x['AUDIT_REVIEW_STATUS']!='SCOPED_REVIEW_COMPLETE'])
dump('review_coverage_stats.json',stats);print(json.dumps({k:v for k,v in stats.items() if k!='branches_pending'},indent=2))
