"""Survey five traced manager lists without assigning vehicle layouts to objects."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from read_live import Reader, K


def survey(r):
    manager, table = r.u(0x7bdecc), r.u(0x828108)
    if not manager:
        return dict(available=False, reason='manager_null', manager=0, lists=None)
    result = dict(available=True, manager=manager, table=table, lists=[])
    for offset in (0, 8, 0x10, 0x18, 0x20):
        sentinel = r.u(manager + offset)
        count = r.u(manager + offset + 4)
        header = r.read(sentinel, 8)
        node = r.u(sentinel)
        seen, objects = set(), []
        while node != sentinel:
            if not node or node in seen or len(seen) >= 16384:
                raise ValueError('Manager list null/cycle/research bound')
            seen.add(node)
            raw = r.read(node, 12)
            nxt, prev, index = r.unpack(node, 'III')
            if index >= 100000: raise ValueError('Object table index bound')
            obj = r.u(table + index * 8)
            # Only the class table index is decoded, not a vehicle ID or physics fields.
            class_index = r.u(obj)
            objects.append(dict(node=node, table_index=index, address=obj,
                class_index=class_index,
                stable=(raw == r.read(node, 12) and obj == r.u(table + index*8)
                        and class_index == r.u(obj)),
                reciprocal_links=r.u(nxt+4) == node and r.u(prev) == node))
            node = nxt
        result['lists'].append(dict(offset=offset, root=sentinel, stored_count=count,
            stored_count_after=r.u(manager+offset+4), objects=objects,
            root_stable=sentinel == r.u(manager+offset) and header == r.read(sentinel, 8)))
    result['roots_stable'] = manager == r.u(0x7bdecc) and table == r.u(0x828108)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--name', required=True)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..'): p.error('Invalid capture name')
    root = Path(__file__).resolve().parent
    out = root/'captures'/a.name
    out.mkdir(exist_ok=False)
    r = Reader(a.pid)
    try:
        data = dict(pid=a.pid, sha256=r.sha, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    sim_time=r.f(0x80acd4), paused=r.u(0x7be0f4), player=r.u(0x7c2ac0))
        try: data['survey'] = survey(r)
        except (OSError, ValueError) as exc: data['error'] = str(exc)
        data['sim_time_after'] = r.f(0x80acd4)
        data['sources'] = {}
        for name in ('read_manager_lists.py', 'read_live.py'):
            raw = (root/name).read_bytes()
            (out/name).write_bytes(raw)
            data['sources'][name] = hashlib.sha256(raw).hexdigest()
        (out/'manager.json').write_text(json.dumps(data, indent=2))
        print(json.dumps(dict(output=str(out), error=data.get('error'),
                             available=data.get('survey', {}).get('available'))))
    finally:
        K.CloseHandle(r.h)
