
import copy, hashlib, json, os, shutil, sys
from pathlib import Path
import eija_studio
from fastapi.testclient import TestClient
from eija_studio.adapters import edit_proposals
from eija_studio.application import edit_proposal
from eija_studio.bootstrap import build_studio
from eija_studio.domain import pack as packs
from eija_studio.domain.models import OWNER
from eija_studio.interfaces.http import create_app

installed, scratch, asset_sha = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
for module in (eija_studio, edit_proposals, edit_proposal):
    assert Path(module.__file__).resolve().is_relative_to(installed), 'Source checkout import leaked'
assert packs.PACKS_ROOT.resolve().is_relative_to(installed), 'Pack data escaped installed target'
assert packs.default_pack().id == 'excursion'
assert {packs.load_pack(path).id for path in packs.PACKS_ROOT.glob('*/pack.json')} == {
    'excursion', 'library-loan', 'eija-review-slice'}
checks = ['installed imports and all runtime packs resolve inside target']

# Configuration and missing bundled data must not borrow policy from the source checkout.
os.environ['EIJA_PACK'] = str(packs.PACKS_ROOT / 'library-loan')
assert packs.default_pack().id == 'library-loan'
for path in (scratch / 'missing-pack.json', scratch / 'invalid-pack.json'):
    if path.name.startswith('invalid'):
        path.write_bytes(b'{')
    os.environ['EIJA_PACK'] = str(path)
    try:
        packs.default_pack()
    except packs.PackError:
        pass
    else:
        raise AssertionError('Invalid configured pack silently fell back')
del os.environ['EIJA_PACK']
pointer = packs.PACKS_ROOT / 'default.json'
original = pointer.read_bytes()
try:
    pointer.unlink()
    try:
        packs.default_pack()
    except packs.PackError:
        pass
    else:
        raise AssertionError('Missing bundled pointer silently fell back')
finally:
    pointer.write_bytes(original)
checks.append('explicit configuration and bundled-data failures stay fail-closed')

# A wholly absent installed bundle must not select valid packs beside the installation.
package = Path(eija_studio.__file__).resolve().parent
bundled = packs.PACKS_ROOT
adjacent = package.parents[1] / 'packs'
held = scratch / 'held-installed-packs'
assert adjacent.is_relative_to(scratch) and not adjacent.exists() and not held.exists()
shutil.copytree(bundled, adjacent)
bundled.rename(held)
try:
    packs.PACKS_ROOT = packs._packs_root(package)
    assert bundled == packs.PACKS_ROOT and not bundled.exists(), 'Missing bundle selected adjacent policy'
    try:
        packs.default_pack()
    except packs.PackError:
        pass
    else:
        raise AssertionError('Missing entire installed bundle silently fell back')
finally:
    packs.PACKS_ROOT = bundled
    held.rename(bundled)
checks.append('entire missing installed bundle refuses valid adjacent packs')

studio = build_studio(scratch / 'workspace', pack=packs.load_pack(packs.PACKS_ROOT / 'eija-review-slice'))
assert studio.identity_provider()['trusted_fixture'] is False, 'Candidate fixture unexpectedly trusted'
case = studio.create(studio.pack.fixtures.demo_request)
case = studio.propose(case['id'], case['version'])
case = studio.select(case['id'], case['version'], 'show_saved_path', OWNER)
def database():
    with studio.store.connection() as connection:
        return tuple(connection.iterdump())
before = database()
headers = {'Authorization': 'Bearer synthetic-wheel-candidate-session', 'Origin': 'http://127.0.0.1:8765'}
with TestClient(create_app(studio, 'synthetic-wheel-candidate-session'), base_url=headers['Origin']) as client:
    page = client.get('/')
    assert page.status_code == 200 and '/assets/agent-edit.js' in page.text
    asset = client.get('/assets/agent-edit.js')
    assert asset.status_code == 200 and hashlib.sha256(asset.content).hexdigest() == asset_sha
    endpoint = '/api/cases/' + case['id'] + '/edit/propose'
    assert client.post(endpoint, json={'request': 'Move Verify source to SAVED', 'expected_version': case['version']}).status_code == 401
    result = client.post(endpoint, headers=headers, json={'request': 'Move Verify source to SAVED', 'expected_version': case['version']})
    assert result.status_code == 200
    proposal = result.json()
    assert proposal['scope'] == 'typed-edit-proposal' and proposal['live'] is False
    assert proposal['provider'] == 'offline' and proposal['trust'] == 'UNTRUSTED_PROPOSAL'
    expected = copy.deepcopy(case['candidate'])
    row = next(item for item in expected['transitions'] if item['id'] == 'TR-VERIFY')
    assert row['from_state'] != 'SAVED'
    row['from_state'] = 'SAVED'
    preview = proposal['preview']
    assert preview['case_id'] == case['id'] and preview['version'] == case['version']
    assert preview['current'] == case['candidate'] and preview['candidate'] == expected
    assert preview['legal'] is True and preview['persisted'] is False and preview['applied'] is False
    refused = client.post(endpoint, headers=headers, json={'request': 'Allow Agent to Approve', 'expected_version': case['version']})
    assert refused.status_code == 200
    refusal = refused.json()['preview']
    assert refusal['legal'] is False and refusal['candidate'] is None
    assert refusal['codes'] == ['REFERENCE_AUTHORITY:Approve']
assert database() == before, 'Proposal changed persisted state'
checks.extend(['installed HTTP asset bytes and session guard', 'exact offline proposal and protected refusal without writes'])
sys.stdout.write(json.dumps({'checks': checks, 'source_review': 'SOURCE_REVIEW_REQUIRED', 'owner_approval_or_baseline_apply': 'NOT_RUN'}) + '\n')
