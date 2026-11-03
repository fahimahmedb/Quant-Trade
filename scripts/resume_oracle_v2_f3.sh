#!/usr/bin/env bash
# Run as ubuntu in the already authenticated SSH session. Never print credentials.
set -euo pipefail
quant_target_sha=${1:?Exact qualified target SHA required}
quant_expected_sha=${2:-a67ffec48fff895d5edc42171855e2213e49cf0d}
quant_pr_number=${3:?Explicit code/canonical transport PR number required}
[[ "$quant_target_sha" =~ ^[0-9a-f]{40}$ ]] || exit 64
[[ "$quant_expected_sha" =~ ^[0-9a-f]{40}$ && "$quant_pr_number" =~ ^[0-9]+$ ]] || exit 64
quant_stage=$(mktemp -d)
trap 'rm -rf "$quant_stage"' EXIT

# All four exact-subject gates precede host/package/credential changes.
python3 - "$quant_target_sha" "$quant_stage" <<'PY'
import json,sys,urllib.request
from pathlib import Path
sha,stage=sys.argv[1:]
base='https://api.github.com/repos/fahimahmedb/Quant-Trade/'
def get(path):
    with urllib.request.urlopen(urllib.request.Request(base+path,headers={'User-Agent':'Quant-V2-F3-operator'}),timeout=30) as r:
        return json.load(r)
runs=get('actions/runs?head_sha='+sha+'&per_page=100')['workflow_runs']
required=['AI Working Method Gate','Canonical Code Qualification','Oracle V2 Core','SEC P0 pre-t0 gate']
selected={}
for name in required:
    matching=[r for r in runs if r['name']==name and r['head_sha']==sha and r['head_branch']=='code/canonical']
    if not matching or matching[0]['status']!='completed' or matching[0]['conclusion']!='success':
        raise SystemExit('BLOCK: exact required workflow not green: '+name)
    selected[name]=matching[0]['id']
Path(stage,'runs.json').write_text(json.dumps(selected))
url='https://raw.githubusercontent.com/fahimahmedb/Quant-Trade/'+sha+'/deploy/oracle_release_install.py'
with urllib.request.urlopen(url,timeout=30) as response: data=response.read(131073)
if len(data)>131072:raise SystemExit('BLOCK: installer size')
import hashlib
if hashlib.sha256(data).hexdigest()!='1c2f753b69e6b6a8bdc5af904f51bb894f7d31eb289e66003b677bb90b73fc7d':
    raise SystemExit('BLOCK: reviewed CP1 installer hash mismatch')
Path(stage,'installer.py').write_bytes(data)
print('EXACT_RELEASE_GATES=PASS')
PY

sudo -n true
# This installer creates an immutable candidate; it never stops/repoints a runtime.
sudo /usr/bin/python3.12 -B "$quant_stage/installer.py" \
  --sha "$quant_target_sha" --base /opt/quant-research/releases

if ! command -v gh >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y gh
fi
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  gh auth login --hostname github.com --git-protocol https --web --scopes repo
fi

# Convert the normal CLI login into a private service credential, without stdout.
quant_operator=$(id -un)
quant_input=$(sudo /usr/bin/python3.12 - "$quant_operator" "$quant_pr_number" <<'PY'
import json,os,pwd,subprocess,sys,tempfile,urllib.request
from datetime import datetime,timezone
user=sys.argv[1];pwd.getpwnam(user)
token=subprocess.check_output(['/usr/sbin/runuser','-u',user,'--','gh','auth','token','--hostname','github.com'],text=True,stderr=subprocess.DEVNULL).strip()
base='https://api.github.com/repos/fahimahmedb/Quant-Trade/'
def get(url):
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+token,'User-Agent':'Quant-V2-F3-operator'})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
actor=get('https://api.github.com/user')['login']
head=get(base+'git/ref/heads/code/canonical')['object']['sha']
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
values={'QUANT_REPOSITORY':'fahimahmedb/Quant-Trade','QUANT_CODEX_ISSUE_NUMBER':sys.argv[2],
    'QUANT_CODEX_TARGET_BRANCH':'code/canonical','QUANT_CODEX_EXPECTED_HEAD_SHA':head,
    'QUANT_CODEX_TASK_ID':'F3-ENGINEERING-'+stamp,
    'QUANT_CODEX_PROMPT':'Perform exactly one read-only engineering checkout-transport qualification for F3. The PR head is code/canonical and its base is project/canonical. Establish the supplied expected commit from the local PR Git objects before working; a merge checkout may contain it as a parent. If no remote exists, the repository URL is https://github.com/fahimahmedb/Quant-Trade.git; a missing origin alone is not a transport failure. Verify the canonical authority pair and run the existing focused host-wake/adapter tests. Do not create commits, branches, a PR or modify files. The durable output is your GitHub response and the existing published expected SHA. If verified and NO_CHANGE_REQUIRED, return the required result marker with that existing SHA. If blocked, report the actual failing transport command without a success marker. Keep the response concise. No audit, architecture, task expansion or scientific mutation.',
    'QUANT_GITHUB_TOKEN':token,'QUANT_GITHUB_ACTOR':actor,
    'QUANT_GPT_OSS_COMMAND':'AUTO_LOCAL_BACKEND'}
fd,path=tempfile.mkstemp(prefix='quant-f3-input-',suffix='.json',dir='/var/backups')
with os.fdopen(fd,'w') as stream:json.dump(values,stream)
os.chmod(path,0o600)
print(path)
PY
)

quant_v2_run=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["Oracle V2 Core"])' "$quant_stage/runs.json")
quant_sec_run=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["SEC P0 pre-t0 gate"])' "$quant_stage/runs.json")
cd "/opt/quant-research/releases/$quant_target_sha"
sudo /usr/bin/python3.12 -B -m deploy.oracle_v2_deploy \
  --action handoff --release "/opt/quant-research/releases/$quant_target_sha" \
  --expected-current-sha "$quant_expected_sha" \
  --v2-ci-run "$quant_v2_run" --sec-ci-run "$quant_sec_run" \
  --orchestration-config "$quant_input"
printf '%s\n' 'Handoff terminé. Conserver le chemin backup_directory. F3 attend les réveils naturels et la consommation du résultat Codex.'
