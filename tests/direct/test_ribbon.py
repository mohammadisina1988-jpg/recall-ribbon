import ast
import copy
import hashlib
import itertools
import json
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
REPO = 'mohammadisina1988-jpg/recall-ribbon'
EXPECTED = json.loads((ROOT / 'config/expected.json').read_text())
BODY = {name: (ROOT / 'notices' / (name + '.json')).read_bytes() for name in EXPECTED}


def source(name, body=None):
    return 'https://raw.githubusercontent.com/' + REPO + '/' + 'a' * 40 + '/notices/' + name + '.json', hashlib.sha256(BODY[name] if body is None else body).hexdigest()


def report(name):
    out = copy.deepcopy(EXPECTED[name])
    if out['decision'] == 'ACTIVE':
        out['exception_mode'] = 'RANGES' if out['exceptions'] else 'NONE'
        if not out['exceptions']:
            out.pop('exceptions')
    else:
        out.pop('spans'); out.pop('exceptions')
    out['quote'] = json.loads(BODY[name])['text'].split('. ')[1] + '.'
    return out


def mock(vm, name, leader=None, own=None, body=None):
    vm.clear_mocks()
    vm.mock_web(re.escape(source(name)[0]), {'status': 200, 'body': BODY[name] if body is None else body})
    vm.mock_llm(r'.*RIBBON-LEADER.*', json.dumps(report(name) if leader is None else leader))
    vm.mock_llm(r'.*RIBBON-VALIDATOR.*', json.dumps(report(name) if own is None else own))


@pytest.fixture
def ribbon(direct_deploy):
    return direct_deploy(str(ROOT / 'contracts/recall_ribbon.py'), REPO, 'Northforge', 'NF-20')


def ingest(c, vm, name):
    mock(vm, name)
    c.ingest_notice(*source(name))


def test_exemption_boundaries_and_partial_lot(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt')
    assert ribbon.inspect_lot(100, 199)['known_affected'] == 90
    assert ribbon.inspect_lot(140, 149)['status'] == 'NO_LISTED_MATCH'
    assert ribbon.inspect_lot(139, 150)['known_affected'] == 2
    assert ribbon.inspect_lot(90, 109)['status'] == 'KNOWN_PARTIAL'
    assert ribbon.inspect_lot(100, 139)['status'] == 'KNOWN_FULL'
    assert direct_vm.run_validator() is True


def test_overlay_provenance_and_no_double_count(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt'); ingest(ribbon, direct_vm, 'overlap')
    assert ribbon.get_state()['segments'] == [
        {'start': 100, 'end': 139, 'notices': ['N-A']},
        {'start': 150, 'end': 179, 'notices': ['N-A']},
        {'start': 180, 'end': 199, 'notices': ['N-A', 'N-B']},
        {'start': 200, 'end': 219, 'notices': ['N-B']},
    ]
    assert ribbon.inspect_lot(100, 219)['known_affected'] == 110
    assert ribbon.inspect_lot(175, 185)['known_affected'] == 11
    assert direct_vm.run_validator() is True


def test_negative_decision_preserves_index(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt')
    before = ribbon.get_state()['segments']
    ingest(ribbon, direct_vm, 'foreign')
    assert ribbon.get_state()['segments'] == before
    assert ribbon.get_state()['notices'][-1]['scope']['decision'] == 'IGNORE'
    assert direct_vm.run_validator() is True


def test_unknown_blocks_unqualified_no_match(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt'); ingest(ribbon, direct_vm, 'unresolved')
    assert ribbon.inspect_lot(300, 305)['status'] == 'REVIEW'
    assert ribbon.inspect_lot(100, 110)['status'] == 'REVIEW'
    assert ribbon.inspect_lot(100, 110)['known_affected'] == 11
    assert ribbon.inspect_lot(300, 305)['unresolved'] == ['N-D']
    assert direct_vm.run_validator() is True


@pytest.mark.parametrize('field,value', [('spans', [[100, 198]]), ('exceptions', [[141, 149]]), ('exception_mode', 'NONE')])
def test_validator_checks_every_consequential_boundary(ribbon, direct_vm, field, value):
    ingest(ribbon, direct_vm, 'exempt')
    own = report('exempt'); own[field] = value
    if field == 'exception_mode': own.pop('exceptions')
    mock(direct_vm, 'exempt', own=own)
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('name', ['foreign', 'unresolved'])
def test_validator_independently_checks_negative_and_unknown(ribbon, direct_vm, name):
    ingest(ribbon, direct_vm, name)
    own = report(name); own.update(decision='ACTIVE', spans=[[1, 999]], exception_mode='NONE')
    mock(direct_vm, name, own=own)
    assert direct_vm.run_validator() is False


def test_validator_refetches_source(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt')
    mock(direct_vm, 'exempt', body=BODY['exempt'] + b' ')
    assert direct_vm.run_validator() is False


@pytest.mark.parametrize('kind', ['bool', 'float', 'reverse', 'zero', 'overflow', 'missing-decision', 'missing-exception-mode', 'missing-spans', 'missing-exceptions', 'outside-exemption', 'unanchored-quote', 'empty-quote', 'contradiction'])
def test_malformed_response_cannot_mutate_index(ribbon, direct_vm, kind):
    bad = report('exempt')
    if kind == 'bool': bad['spans'][0][0] = True
    if kind == 'float': bad['spans'][0][0] = 100.5
    if kind == 'reverse': bad['spans'] = [[199, 100]]
    if kind == 'zero': bad['spans'] = [[0, 199]]
    if kind == 'overflow': bad['spans'] = [[100, 1000000]]
    if kind == 'missing-decision': bad.pop('decision')
    if kind == 'missing-exception-mode': bad.pop('exception_mode')
    if kind == 'missing-spans': bad.pop('spans')
    if kind == 'missing-exceptions': bad.pop('exceptions')
    if kind == 'outside-exemption': bad['exceptions'] = [[200, 201]]
    if kind == 'unanchored-quote': bad['quote'] = 'Invented recall notice wording'
    if kind == 'empty-quote': bad['quote'] = ''
    if kind == 'contradiction': bad['exception_mode'] = 'NONE'
    mock(direct_vm, 'exempt', leader=bad)
    with direct_vm.expect_revert(): ribbon.ingest_notice(*source('exempt'))
    assert ribbon.get_state()['notices'] == [] and ribbon.get_state()['segments'] == []


def test_source_replay_and_notice_id_collision(ribbon, direct_vm):
    ingest(ribbon, direct_vm, 'exempt')
    with direct_vm.expect_revert('already indexed'): ribbon.ingest_notice(*source('exempt'))
    changed = json.loads(BODY['exempt']); changed['text'] += ' Additional publication metadata.'
    body = json.dumps(changed).encode()
    mock(direct_vm, 'exempt', body=body)
    with direct_vm.expect_revert('ID already indexed'): ribbon.ingest_notice(*source('exempt', body))
    assert len(ribbon.get_state()['notices']) == 1


@pytest.mark.parametrize('url', ['https://raw.githubusercontent.com/' + REPO + '/main/notices/exempt.json', 'https://example.com/exempt.json', 'https://raw.githubusercontent.com/other/recall-ribbon/' + 'a' * 40 + '/notices/exempt.json'])
def test_source_scope_is_fixed(ribbon, direct_vm, url):
    with direct_vm.expect_revert('Commit-pinned'): ribbon.ingest_notice(url, 'a' * 64)


@pytest.mark.parametrize('start,end', [(0, 10), (20, 10), (1, 1000000)])
def test_invalid_lot(ribbon, direct_vm, start, end):
    with direct_vm.expect_revert('Invalid serial lot'): ribbon.inspect_lot(start, end)


def test_any_caller_can_index_but_cannot_override_scope(ribbon, direct_vm, direct_bob):
    direct_vm.sender = direct_bob
    ingest(ribbon, direct_vm, 'overlap')
    assert ribbon.inspect_lot(180, 219)['status'] == 'KNOWN_FULL'


def pure_functions():
    tree = ast.parse((ROOT / 'contracts/recall_ribbon.py').read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'ranges', 'subtract', 'overlay', 'inspect'}]
    def fail(message): raise ValueError(message)
    namespace = {'fail': fail, 're': re}
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<pure contract algorithms>', 'exec'), namespace)
    return namespace


def test_canonical_ranges_merge_semantically_identical_encodings():
    p = pure_functions()
    assert p['ranges']([['5', '8'], [1, 3], [3, 4], [5, 8]]) == [[1, 8]]


def test_independent_pointwise_oracle_exhaustive():
    p = pure_functions()
    intervals = [[a, b] for a in range(1, 7) for b in range(a, 7)]
    checked = 0
    for a, b in itertools.product(intervals, repeat=2):
        # Each notice either has no exemption or exempts its first serial.
        for exempt_a, exempt_b in itertools.product([False, True], repeat=2):
            notices = [{'document': {'id': name}, 'scope': {'decision': 'ACTIVE', 'spans': [span], 'exceptions': [[span[0], span[0]]] if excluded else []}} for name, span, excluded in [('A', a, exempt_a), ('B', b, exempt_b)]]
            segments = p['overlay'](notices)
            previous = None
            for segment in segments:
                assert segment['start'] <= segment['end']
                if previous:
                    assert previous['end'] < segment['start']
                    assert previous['end'] + 1 != segment['start'] or previous['notices'] != segment['notices']
                previous = segment
            for serial in range(1, 7):
                wanted = [n['document']['id'] for n in notices if any(l <= serial <= r for l, r in n['scope']['spans']) and not any(l <= serial <= r for l, r in n['scope']['exceptions'])]
                got = [x['notices'] for x in segments if x['start'] <= serial <= x['end']]
                assert got == ([wanted] if wanted else [])
            assert p['inspect'](segments, [], 1, 6)['known_affected'] == sum(any(x['start'] <= serial <= x['end'] for x in segments) for serial in range(1, 7))
            checked += 1
    assert checked == 1764
