import pytest

import tempfile
import time
import os
import pytest
import pprint
import requests
import tarfile
import glob
import uuid

from datetime import datetime
from collections import namedtuple
from ae5_tools.api import AEUnexpectedResponseError

from .utils import _cmd, _compare_tarfiles, CMDException


@pytest.fixture(scope='module')
def project_list(user_session):
    return _cmd('project list --collaborators')


def test_project_info(project_list):
    for rec0 in project_list:
        id = rec0['id']
        pair = '{}/{}'.format(rec0['owner'], rec0['name'])
        rec1 = _cmd(f'project info {id}')
        rec2 = _cmd(f'project info {pair}')
        rec3 = _cmd(f'project info {pair}/{id}')
        assert all(rec0[k] == v for k, v in rec2.items()), pprint.pformat((rec0, rec2))
        assert all(rec1[k] == v for k, v in rec2.items()), pprint.pformat((rec1, rec2))
        assert rec2 == rec3


def test_project_info_errors(project_list):
    with pytest.raises(CMDException) as excinfo:
        _cmd('project info testproj1')
    assert 'Multiple projects' in str(excinfo.value)
    with pytest.raises(CMDException) as excinfo:
        _cmd('project info testproj4')
    assert 'No projects' in str(excinfo.value)


@pytest.fixture(scope='module')
def resource_profiles(user_session):
    return _cmd('resource-profile list')


def test_resource_profiles(resource_profiles):
    for rec in resource_profiles:
        rec2 = _cmd(f'resource-profile info {rec["name"]}')
        assert rec == rec2
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'resource-profile info *')
    assert 'Multiple resource profiles found' in str(excinfo.value)
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'resource-profile info abcdefg')
    assert 'No resource profiles found' in str(excinfo.value)


@pytest.fixture(scope='module')
def editors(user_session):
    return _cmd('editor list')


def test_editors(editors):
    for rec in editors:
        assert rec == _cmd(f'editor info {rec["id"]}')
    assert sum(rec['is_default'].lower() == 'true' for rec in editors) == 1
    assert set(rec['id'] for rec in editors).issuperset({'zeppelin', 'jupyterlab', 'notebook'})


def test_endpoints():
    slist = _cmd('endpoint list')
    for rec in slist:
        rec2 = _cmd(f'endpoint info {rec["id"]}')
        assert rec == rec2


def test_samples():
    slist = _cmd(f'sample list')
    assert sum(rec['is_default'].lower() == 'true' for rec in slist) == 1
    assert sum(rec['is_template'].lower() == 'true' for rec in slist) > 1
    for rec in slist:
        rec2 = _cmd(f'sample info "{rec["id"]}"')
        rec3 = _cmd(f'sample info "{rec["name"]}"')
        assert rec == rec2 and rec == rec3


def test_sample_clone():
    cname = 'nlp_api'
    pname = 'testclone'
    rrec1 = _cmd(f'sample clone {cname} --name {pname}')
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'sample clone {cname} --name {pname}')
    rrec2 = _cmd(f'sample clone {cname} --name {pname} --make-unique')
    rrec3 = _cmd(f'sample clone {cname}')
    _cmd(f'project delete {rrec1["id"]}')
    _cmd(f'project delete {rrec2["id"]}')
    _cmd(f'project delete {rrec3["id"]}')


@pytest.fixture(scope='module')
def cli_project(project_list):
    return next(rec for rec in project_list if rec['name'] == 'testproj3')


@pytest.fixture(scope='module')
def cli_revisions(cli_project):
    prec = cli_project
    revs = _cmd(f'project revision list {prec["id"]}')
    return prec, revs


@pytest.fixture(scope='module')
def downloaded_project(user_session, cli_revisions):
    prec, revs = cli_revisions
    with tempfile.TemporaryDirectory() as tempd:
        fname = _cmd(f'project download {prec["id"]}', table=False).strip()
        assert fname == prec['name'] + '.tar.gz'
        with tarfile.open(fname, 'r') as tf:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tf, path=tempd)
        dnames = glob.glob(os.path.join(tempd, '*', 'anaconda-project.yml'))
        assert len(dnames) == 1
        dname = os.path.dirname(dnames[0])
        yield fname, dname
    for r in _cmd('project list'):
        if r['name'].startswith('test_upload'):
            _cmd(f'project delete {r["id"]}')
    assert not any(r['name'].startswith('test_upload')
                   for r in _cmd('project list'))


def test_project_download(downloaded_project):
    pass


def test_project_upload(downloaded_project):
    fname, dname = downloaded_project
    _cmd(f'project upload {fname} --name test_upload1 --tag 1.2.3')
    rrec = _cmd(f'project revision list test_upload1')
    assert len(rrec) == 1
    rev = rrec[0]['name']
    fname2 = _cmd(f'project download test_upload1:{rev}', table=False).strip()
    assert fname2 == f'test_upload1-{rev}.tar.gz'
    assert os.path.exists(fname2)
    _compare_tarfiles(fname, fname2)
    if rev == '0.0.1':
        pytest.xfail("5.4.1 revision issue")
    assert rev == '1.2.3'


def test_project_upload_as_directory(downloaded_project):
    fname, dname = downloaded_project
    _cmd(f'project upload {dname} --name test_upload2 --tag 1.3.4')
    rrec = _cmd(f'project revision list test_upload2')
    assert len(rrec) == 1
    rev = rrec[0]['name']
    fname2 = _cmd(f'project download test_upload2:{rev}', table=False).strip()
    assert fname2 == f'test_upload2-{rev}.tar.gz'
    assert os.path.exists(fname2)
    if rev == '0.0.1':
        pytest.xfail("5.4.1 revision issue")
    assert rev == '1.2.3'


def test_project_revisions(cli_revisions):
    prec, revs = cli_revisions
    rev0 = _cmd(f'project revision info {prec["id"]}')
    assert revs[0] == rev0
    rev0 = _cmd(f'project revision info {prec["id"]}:latest')
    assert revs[0] == rev0
    for rev in revs:
        revN = _cmd(f'project revision info {prec["id"]}:{rev["id"]}')
        assert rev == revN


def test_project_revision_errors(cli_revisions):
    prec, revs = cli_revisions
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project revision info testproj1')
    assert 'Multiple projects' in str(excinfo.value)
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project revision info testproj4')
    assert 'No projects' in str(excinfo.value)
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project revision info {prec["id"]}:0.*')
    assert 'Multiple revisions' in str(excinfo.value)
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project revision info {prec["id"]}:a.b.c')
    assert 'No revisions' in str(excinfo.value)


def test_project_patch(cli_project, editors, resource_profiles):
    prec = cli_project
    old, new = {}, {}
    for what, wlist in (('resource-profile', (r['name'] for r in resource_profiles)),
                        ('editor', (e['id'] for e in editors))):
        old[what] = prec[what.replace('-', '_')]
        new[what] = next(v for v in wlist if v != old)
    prec2 = _cmd(f'project patch {prec["id"]} ' + ' '.join(f'--{k}={v}' for k, v in new.items()))
    assert {k: prec2[k.replace('-', '_')] for k in new} == new
    prec3 = _cmd(f'project patch {prec["id"]} ' + ' '.join(f'--{k}={v}' for k, v in old.items()))
    assert {k: prec3[k.replace('-', '_')] for k in old} == old


def test_project_collaborators(cli_project, project_list):
    prec = cli_project
    uname = next(rec['owner'] for rec in project_list if rec['owner'] != prec['owner'])
    id = prec['id']
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project collaborator info {id} {uname}')
    assert f'No collaborators found matching id={uname}' in str(excinfo.value)
    clist = _cmd(f'project collaborator add {id} {uname}')
    assert len(clist) == 1
    clist = _cmd(f'project collaborator add {id} everyone --group --read-only')
    assert len(clist) == 2
    assert all(c['id'] == uname and c['permission'] == 'rw' and c['type'] == 'user' or
               c['id'] == 'everyone' and c['permission'] == 'r' and c['type'] == 'group'
               for c in clist)
    clist = _cmd(f'project collaborator add {id} {uname} --read-only')
    assert len(clist) == 2
    assert all(c['id'] == uname and c['permission'] == 'r' and c['type'] == 'user' or
               c['id'] == 'everyone' and c['permission'] == 'r' and c['type'] == 'group'
               for c in clist)
    clist = _cmd(f'project collaborator remove {id} {uname} everyone')
    assert len(clist) == 0
    with pytest.raises(CMDException) as excinfo:
        clist = _cmd(f'project collaborator remove {id} {uname}')
    assert f'Collaborator(s) not found: {uname}' in str(excinfo.value)


def test_project_activity(cli_project):
    prec = cli_project
    activity = _cmd(f'project activity  {prec["id"]}')
    assert 1 <= len(activity) <= 10
    activity2 = _cmd(f'project activity --latest {prec["id"]}')
    assert activity[0] == activity2
    activity3 = _cmd(f'project activity --limit 1 {prec["id"]}')
    assert activity[0] == activity3[0]
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project activity --latest --all {prec["id"]}')
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project activity --limit 2 --all {prec["id"]}')
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project activity --latest --limit 2 {prec["id"]}')


@pytest.fixture(scope='module')
def cli_session(cli_project):
    prec = cli_project
    srec = _cmd(f'session start {prec["owner"]}/{prec["name"]}')
    srec2 = _cmd(f'session restart {srec["id"]} --wait')
    assert not any(r['id'] == srec['id'] for r in _cmd('session list'))
    yield prec, srec2
    _cmd(f'session stop {srec2["id"]}')
    assert not any(r['id'] == srec2['id'] for r in _cmd('session list'))


def test_session(cli_session):
    prec, srec = cli_session
    assert srec['owner'] == prec['owner'], srec
    assert srec['name'] == prec['name'], srec
    # Ensure that the session can be retrieved by its project ID as well
    srec2 = _cmd(f'session info {srec["owner"]}/*/{prec["id"]}')
    assert srec2['id'] == srec['id']
    endpoint = srec['id'].rsplit("-", 1)[-1]
    sdata = _cmd(f'call / --endpoint={endpoint}', table=False)
    assert 'Jupyter Notebook requires JavaScript.' in sdata, sdata


def test_project_sessions(cli_session):
    prec, srec = cli_session
    slist = _cmd(f'project sessions {prec["id"]}')
    assert len(slist) == 1 and slist[0]['id'] == srec['id']


def test_session_branches(cli_session):
    prec, srec = cli_session
    branches = _cmd(f'session branches {prec["id"]}')
    bdict = {r['branch']: r['sha1'] for r in branches}
    assert set(bdict) == {'local', 'origin/local', 'master'}, branches
    assert bdict['local'] == bdict['master'], branches


def test_session_before_changes(cli_session):
    prec, srec = cli_session
    changes1 = _cmd(f'session changes {prec["id"]}')
    assert changes1 == [], changes1
    changes2 = _cmd(f'session changes --master {prec["id"]}')
    assert changes2 == [], changes2


@pytest.fixture(scope='module')
def cli_deployment(cli_project):
    prec = cli_project
    dname = 'testdeploy'
    ename = 'testendpoint'
    drec = _cmd(f'project deploy {prec["owner"]}/{prec["name"]} --name {dname} --endpoint {ename} --command default --private')
    drec2 = _cmd(f'deployment restart {drec["id"]} --wait')
    assert not any(r['id'] == drec['id'] for r in _cmd('deployment list'))
    yield prec, drec2
    _cmd(f'deployment stop {drec2["id"]}')
    assert not any(r['id'] == drec2['id'] for r in _cmd('deployment list'))


def test_deploy(cli_deployment):
    prec, drec = cli_deployment
    assert drec['owner'] == prec['owner'], drec
    assert drec['project_name'] == prec['name'], drec
    for attempt in range(3):
        try:
            ldata = _cmd(f'call / --endpoint {drec["endpoint"]}', table=False)
            break
        except AEUnexpectedResponseError:
            time.sleep(attempt * 5)
            pass
    else:
        raise RuntimeError("Could not get the endpoint to respond")
    assert ldata.strip() == 'Hello Anaconda Enterprise!', ldata


def test_project_deployments(cli_deployment):
    prec, drec = cli_deployment
    dlist = _cmd(f'project deployments {prec["id"]}')
    assert len(dlist) == 1 and dlist[0]['id'] == drec['id']


def test_deploy_patch(cli_deployment):
    prec, drec = cli_deployment
    flag = '--private' if drec['public'].lower() == 'true' else '--public'
    drec2 = _cmd(f'deployment patch {flag} {drec["id"]}')
    assert drec2['public'] != drec['public']
    flag = '--private' if drec2['public'].lower() == 'true' else '--public'
    drec3 = _cmd(f'deployment patch {flag} {drec["id"]}')
    assert drec3['public'] == drec['public']


def test_deploy_token(user_session, cli_deployment):
    prec, drec = cli_deployment
    token = _cmd(f'deployment token {drec["id"]}', table=False).strip()
    resp = requests.get(f'https://{drec["endpoint"]}.' + user_session.hostname,
                        headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.text.strip() == 'Hello Anaconda Enterprise!', resp.text


def test_deploy_logs(cli_deployment):
    prec, drec = cli_deployment
    id = drec['id']
    app_prefix = 'anaconda-app-' + id.rsplit("-", 1)[-1] + '-'
    app_logs = _cmd(f'deployment logs {id}', table=False)
    event_logs = _cmd(f'deployment logs {id} --events', table=False)
    proxy_logs = _cmd(f'deployment logs {id} --proxy', table=False)
    assert 'The project is ready to run commands.' in app_logs
    assert app_prefix in event_logs, event_logs
    assert 'App Proxy is fully operational!' in proxy_logs, proxy_logs


def test_deploy_duplicate(cli_deployment):
    prec, drec = cli_deployment
    dname = drec['name'] + '-dup'
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project deploy {prec["id"]} --name {dname} --endpoint {drec["endpoint"]} --command default --private --wait')
    assert f'endpoint "{drec["endpoint"]}" is already in use' in str(excinfo.value)
    assert not any(r['name'] == dname for r in _cmd(f'deployment list'))


def test_deploy_collaborators(cli_deployment):
    uname = 'tooltest2'
    prec, drec = cli_deployment
    clist = _cmd(f'deployment collaborator list {drec["id"]}')
    assert len(clist) == 0
    clist = _cmd(f'deployment collaborator add {drec["id"]} {uname}')
    assert len(clist) == 1
    clist = _cmd(f'deployment collaborator add {drec["id"]} everyone --group')
    assert len(clist) == 2
    clist = _cmd(f'deployment collaborator add {drec["id"]} {uname}')
    assert len(clist) == 2
    assert all(c['id'] == uname and c['type'] == 'user' or
               c['id'] == 'everyone' and c['type'] == 'group'
               for c in clist)
    for crec in clist:
        crec2 = _cmd(f'deployment collaborator info {drec["id"]} {crec["id"]}')
        assert crec2['id'] == crec['id'] and crec2['type'] == crec['type']
    clist = _cmd(f'deployment collaborator remove {drec["id"]} {uname} everyone')
    assert len(clist) == 0
    with pytest.raises(CMDException) as excinfo:
        clist = _cmd(f'deployment collaborator remove {drec["id"]} {uname}')
    assert f'Collaborator(s) not found: {uname}' in str(excinfo.value)


def test_deploy_broken(cli_deployment):
    prec, drec = cli_deployment
    dname = drec['name'] + '-broken'
    with pytest.raises(CMDException) as excinfo:
        _cmd(f'project deploy {prec["id"]} --name {dname} --command broken --private --stop-on-error')
    assert 'Error completing deployment start: App failed to run' in str(excinfo.value)
    assert not any(r['name'] == dname for r in _cmd('deployment list'))


def test_k8s_node(user_session):
    nlist = _cmd('node list')
    for nrec in nlist:
        nrec2 = _cmd(f'node info {nrec["name"]}')
        assert nrec2['name'] == nrec['name']


def test_k8s_pod(user_session, cli_session, cli_deployment):
    _, srec = cli_session
    _, drec = cli_deployment
    plist = _cmd('pod list')
    assert any(prec['id'] == srec['id'] for prec in plist)
    assert any(prec['id'] == drec['id'] for prec in plist)
    for prec in plist:
        prec2 = _cmd(f'pod info {prec["id"]}')
        assert prec2['id'] == prec['id']
    srec2 = _cmd(f'session info {srec["id"]} --k8s')
    assert srec2['id'] == srec['id']
    drec2 = _cmd(f'deployment info {drec["id"]} --k8s')
    assert drec2['id'] == drec['id']


def test_job_run1(cli_project):
    prec = cli_project
    _cmd(f'job create {prec["id"]} --name testjob1 --command run --run --wait')
    jrecs = _cmd('job list')
    assert len(jrecs) == 1, jrecs
    rrecs = _cmd('run list')
    assert len(rrecs) == 1, rrecs
    ldata1 = _cmd(f'run log {rrecs[0]["id"]}', table=False)
    assert ldata1.strip().endswith('Hello Anaconda Enterprise!'), repr(ldata1)
    _cmd(f'job create {prec["id"]} --name testjob1 --make-unique --command run --run --wait')
    jrecs = _cmd('job list')
    assert len(jrecs) == 2, jrecs
    jrecs2 = _cmd(f'project jobs {prec["id"]}')
    assert {r['id']: r for r in jrecs} == {r['id']: r for r in jrecs2}
    rrecs = _cmd('run list')
    assert len(rrecs) == 2, rrecs
    rrecs2 = _cmd(f'project runs {prec["id"]}')
    assert {r['id']: r for r in rrecs} == {r['id']: r for r in rrecs2}
    for rrec in rrecs:
        _cmd(f'run delete {rrec["id"]}')
    for jrec in jrecs:
        _cmd(f'job delete {jrec["id"]}')
    assert not _cmd('job list')
    assert not _cmd('run list')


def test_job_run2(cli_project):
    prec = cli_project
    # Test cleanup mode and variables in jobs
    variables = {'INTEGRATION_TEST_KEY_1': 'value1', 'INTEGRATION_TEST_KEY_2': 'value2'}
    vars = ' '.join(f'--variable {k}={v}' for k, v in variables.items())
    _cmd(f'project run {prec["id"]} --command run_with_env_vars --name testjob2 {vars}')
    # The job record should have already been deleted
    assert not _cmd('job list')
    rrecs = _cmd('run list')
    assert len(rrecs) == 1, rrecs
    ldata2 = _cmd(f'run log {rrecs[0]["id"]}', table=False)
    # Confirm that the environment variables were passed through
    outvars = dict(line.strip().replace(' ', '').split(':', 1)
                   for line in ldata2.splitlines()
                   if line.startswith('INTEGRATION_TEST_KEY_'))
    assert variables == outvars, outvars
    _cmd(f'run delete {rrecs[0]["id"]}')
    assert not _cmd('run list')


def test_login_time(admin_session, user_session):
    # The current login time should be before the present
    now = datetime.utcnow()
    _cmd('project list')
    user_list = _cmd('user list')
    urec = next((r for r in user_list if r['username'] == user_session.username), None)
    assert urec is not None
    ltm1 = datetime.strptime(urec['lastLogin'], "%Y-%m-%d %H:%M:%S.%f")
    assert ltm1 < now
    # No more testing here, because we want to preserve the existing sessions
