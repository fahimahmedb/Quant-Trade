import subprocess

import pytest

from research.research_os.github_state import GitHubStateStore,Snapshot,StateConflict,PREFIX


@pytest.fixture
def local_store(tmp_path):
    remote=tmp_path/'remote.git'
    subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
    store=GitHubStateStore(cache=tmp_path/'cache.git',repository='fixture/only',branch='vertical-fixture')
    store.remote=str(remote)
    tree=store._git('mktree',data=b'').decode().strip()
    env={'GIT_AUTHOR_NAME':'Fixture','GIT_AUTHOR_EMAIL':'fixture@localhost',
         'GIT_COMMITTER_NAME':'Fixture','GIT_COMMITTER_EMAIL':'fixture@localhost'}
    head=store._git('commit-tree',tree,data=b'synthetic initial state\n',env=env).decode().strip()
    store._git('push',store.remote,head+':'+store.ref)
    return store,Snapshot(head,tmp_path,{})


def remote_head(store):
    return subprocess.check_output(['git','--git-dir='+store.remote,'rev-parse',store.ref],text=True).strip()


@pytest.mark.parametrize('suffix',['tasks//task.json','tasks/./task.json','tasks/task.json/','tasks/'])
def test_noncanonical_path_cannot_acknowledge_an_ignored_write(local_store,suffix):
    store,snapshot=local_store
    with pytest.raises(ValueError):
        store.commit(snapshot,{PREFIX+suffix:{'synthetic':True}},message='synthetic malformed path')
    assert remote_head(store)==snapshot.head


def test_valid_json_write_binds_ack_to_actual_git_blob(local_store):
    store,snapshot=local_store;path=PREFIX+'tasks/task.json'
    head=store.commit(snapshot,{path:{'synthetic':True}},create_only=[path],message='synthetic valid write')
    assert remote_head(store)==head
    assert store._git('rev-parse',head+'^').decode().strip()==snapshot.head
    assert b'"synthetic": true' in store._git('show',head+':'+path)


def test_stale_blob_refuses_before_mutating_remote(local_store):
    store,snapshot=local_store;path=PREFIX+'tasks/task.json'
    with pytest.raises(StateConflict):
        store.commit(snapshot,{path:{'synthetic':True}},expected_blobs={path:'a'*40},message='synthetic stale proof')
    assert remote_head(store)==snapshot.head
