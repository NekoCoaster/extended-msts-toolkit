"""Read the physical-object list independently of connected train chains."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
from read_live import Reader, K


class PhysicalRegistryReader(Reader):
    def physical_registry(self):
        manager = self.u(0x7bdecc)
        table = self.u(0x828108)
        root = self.u(manager + 0x18)
        header = self.read(root, 8)
        node = self.u(root)
        seen, rows = set(), []
        while node != root:
            if not node or node in seen or len(seen) >= 4096:
                raise ValueError('Physical registry null/cycle/bound')
            seen.add(node)
            raw = self.read(node, 12)
            nxt, prev, index = self.unpack(node, 'III')
            if index >= 100000:
                raise ValueError('Object table index bound')
            obj = self.u(table + index * 8)
            class_index = self.u(obj)
            if class_index >= 100000:
                raise ValueError('Class table index bound')
            cls = self.u(table + class_index * 8)
            slot = self.u(cls + 0x64 + 0x14 * 4)
            if slot >= 1024:
                raise ValueError('Method slot bound')
            method = self.u(cls + 0x1064 + slot * 4)
            # Exact constant-return methods verified by pass218. Never invoke them.
            signatures = {
                0x5f15ac: (0x4000e, bytes.fromhex('558bec51894dfcb80e0004008be55dc3')),
                0x63465b: (0x4000d, bytes.fromhex('558bec51894dfcb80d0004008be55dc3')),
            }
            kind = None
            if method in signatures:
                value, signature = signatures[method]
                if self.read(method, len(signature)) != signature:
                    raise ValueError('Class-method bytes changed')
                kind = value
            row = dict(node=node, table_index=index, address=obj, class_index=class_index,
                       class_object=cls, method=method, native_kind=kind)
            if kind in (0x4000d, 0x4000e):
                row.update(object_id=self.u(obj + 0x50), owner=self.u(obj + 0x98),
                           physics=self.car(obj))
            row['stable'] = (raw == self.read(node, 12) and
                             obj == self.u(table + index * 8) and
                             class_index == self.u(obj) and
                             cls == self.u(table + class_index * 8) and
                             slot == self.u(cls + 0xb4) and
                             method == self.u(cls + 0x1064 + slot * 4))
            row['reciprocal_list_links'] = self.u(nxt + 4) == node and self.u(prev) == node
            rows.append(row)
            node = nxt
        trains = self.trains()
        connected = {c['address'] for t in trains for c in t['cars']}
        physical = {x['address'] for x in rows if x['native_kind'] in (0x4000d, 0x4000e)}
        return dict(manager=manager, table=table, root=root, objects=rows,
                    roots_stable=(manager == self.u(0x7bdecc) and table == self.u(0x828108)
                                  and root == self.u(manager + 0x18) and header == self.read(root, 8)),
                    physical_not_in_train_chains=sorted(physical-connected),
                    train_cars_not_in_physical_list=sorted(connected-physical),
                    trains=[dict(address=t['address'], id=t['id'], is_player=t['is_player'],
                                 cars=[c['address'] for c in t['cars']]) for t in trains])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--name', required=True)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..'):
        p.error('Invalid capture name')
    root = Path(__file__).resolve().parent
    out = root / 'captures' / a.name
    out.mkdir(exist_ok=False)
    r = PhysicalRegistryReader(a.pid)
    try:
        result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      sha256=r.sha, sim_time=r.f(0x80acd4), paused=r.u(0x7be0f4))
        result['registry'] = r.physical_registry()
        result['sim_time_after'] = r.f(0x80acd4)
        result['sources'] = {}
        for name in ('read_live.py', 'read_physical_registry.py'):
            data = (root/name).read_bytes()
            (out/name).write_bytes(data)
            result['sources'][name] = hashlib.sha256(data).hexdigest()
        (out/'registry.json').write_text(json.dumps(result, indent=2))
        reg = result['registry']
        print(json.dumps(dict(output=str(out), count=len(reg['objects']),
              roots_stable=reg['roots_stable'], unstable=sum(not x['stable'] for x in reg['objects']),
              broken_links=sum(not x['reciprocal_list_links'] for x in reg['objects']),
              outside=reg['physical_not_in_train_chains'], missing=reg['train_cars_not_in_physical_list'])))
    finally:
        K.CloseHandle(r.h)
