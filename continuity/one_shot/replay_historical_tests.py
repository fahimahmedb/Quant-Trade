"""Replay preserved tests ONLY against immutable CP06; never current qualification."""
import os,subprocess,tarfile,tempfile,io
SHA='3be85e3314aa70d2fecfd1b145c3aaa9ab5df199'
with tempfile.TemporaryDirectory(prefix='oneshot-historical-replay-') as d:
    archive=subprocess.check_output(['git','archive',SHA])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf: tf.extractall(d,filter='data')
    print('REPLAY_ONLY_SHA='+SHA,flush=True)
    env={**os.environ,'PYTHONPATH':d+'/src:'+d,'PYTHONDONTWRITEBYTECODE':'1'}
    subprocess.run(['python3','-m','unittest','-v','tests.test_verified_continuity_admission_identity','tests.test_verified_continuation_contract','tests.test_verified_continuity_renewal'],cwd=d,env=env,check=True)
