"""Summarize retained snapshots without treating bounded chains as full queues."""
import collections, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parent
out=[]
for name in ['audio-streams-paused-01','audio-streams-paused-02']:
    path=root/'captures'/name/'streams.json';data=json.loads(path.read_text())['snapshot'];rows=data['streams']
    complete=[r for r in rows if not r.get('error') and r.get('queue_complete',True)]
    checks=['stable_state','stable_definition','stable_queue_links','stable_owner']
    active=[r for r in rows if r.get('native_bit2_predicate')]
    out.append(dict(capture=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        time=data['context']['time'],time_after=data['time_after'],paused=data['paused_after'],
        receiver_count=len(data['context']['receivers']),stream_count=len(rows),
        list_stable=data['context']['stable_list'],errors=[dict(label=r['label'],index=r['index'],error=r['error']) for r in rows if 'error' in r],
        completed_queues=len(complete),completed_queue_nodes=sum(len(r['queue_nodes']) for r in complete),
        incomplete_queues=[dict(label=r['label'],index=r['index'],observed_nodes=len(r['queue_nodes']),stop=r['queue_traversal_stop']) for r in rows if 'queue_traversal_stop' in r],
        stability_counts={k:dict(collections.Counter(str(r.get(k,'unavailable')) for r in rows)) for k in checks},
        lock_pairs=dict(collections.Counter(str((r.get('lock_before'),r.get('lock_after'))) for r in rows)),
        native_bit2_count=len(active),native_bit2_with_buffer=sum(bool(r.get('buffer_interface')) for r in active),
        native_bit2_without_buffer=sum(not r.get('buffer_interface') for r in active),
        all_buffer_interfaces=sum(bool(r.get('buffer_interface')) for r in rows),
        all_spatial_interfaces=sum(bool(r.get('spatial_interface')) for r in rows),
        player_associated_streams=sum(any(a['is_player'] for a in r['associations']) for r in rows),
        ai_associated_streams=sum(any(not a['is_player'] for a in r['associations']) for r in rows),
        trigger_counts=sorted(set(r.get('trigger_count') for r in rows if 'trigger_count' in r))))
result=dict(captures=out,limitations='Native flag is not measured audibility. Bounded linked records are not a complete queue count; no time duration/backlog or sample identity inferred. Two paused snapshots do not prove stable lifetime or AI coverage.')
(root/'audio-streams-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
