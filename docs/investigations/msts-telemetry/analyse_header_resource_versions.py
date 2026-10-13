"""Compare explicitly retained header resource lists with live loaded sources."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
stored=json.loads((root/'save-header-lists.json').read_text())
live=json.loads((root/'captures/header-resource-versions-paused-01/versions.json').read_text())
comparisons=[]
for token,kind in [('0x404c9','path'),('0x404c8','consist'),('0x404cb','service')]:
    expected=[(e['name'],e['word']) for b in stored['blocks'] if b['token']==token for e in b['entries']]
    # This fixture uses exactly equal names; native string comparison case rules remain untraced.
    actual=list(dict.fromkeys((s[kind+'_name'],s[kind+'_word']) for s in live['services'] if s['eligible']))
    comparisons.append(dict(kind=kind,stored=expected,live=actual,equal=expected==actual))
expected=[(e['name'],e['word']) for b in stored['blocks'] if b['token']=='0x404ca' for e in b['entries']]
actual=[(live['traffic_name'],live['traffic_word'])]
comparisons.append(dict(kind='traffic',stored=expected,live=actual,equal=expected==actual))
result=dict(comparisons=comparisons,all_equal=all(x['equal'] for x in comparisons),
            distinct_pairs=sum(len(x['stored']) for x in comparisons),
            limitations='Retained installed ASV compared to paused loaded metadata, not a newly written save or a round trip. This exact-name fixture does not establish native case normalization, deduplication of conflicting words, or producer semantics.')
(root/'header-resource-comparison.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result['all_equal']
