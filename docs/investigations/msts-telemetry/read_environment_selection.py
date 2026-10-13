"""Read-only native ENV selection inputs/result; never opens a game-supplied path."""
import argparse, datetime, hashlib, json
from pathlib import Path
from read_services import ServiceReader
from read_live import K

class SelectionReader(ServiceReader):
    def selection(self):
        route = self.u(0x7b8d3c)
        season, weather, editor = [self.u(a) for a in (0x79a3ac, 0x7be0d8, 0x7be0f8)]
        rows = []
        for s in range(4):
            for slot in range(3):
                offset = 0x70 + s * 12 + slot * 4
                pointer = self.u(route + offset)
                rows.append(dict(season=s, slot=slot, offset=offset, pointer=pointer,
                                 filename=self.wide(pointer) if pointer else None))
        selected = self.wide(0x7b8d48)
        if editor:
            expected = 'editor.env'
            chosen = None
        else:
            chosen = (season * 3 + (2 if weather == 1 else 1 if weather == 2 else 0)) if season < 4 else 3
            expected = rows[chosen]['filename']
        return dict(route=route, season_selector=season, weather_selector=weather,
                    editor_override_raw=editor, route_slots=rows,
                    selected_filename=selected, expected_filename=expected,
                    chosen_slot=chosen, selection_matches=selected == expected,
                    route_directory=self.wide(0x7b8310), env_directory=self.wide(0x7b74cc),
                    env_texture_directory=self.wide(0x7b76d4),
                    activity_header_weather=self.u(0x809810+0x30),
                    activity_header_season=self.u(0x809810+0x34),
                    inputs_stable=(route == self.u(0x7b8d3c) and
                        [season, weather, editor] == [self.u(a) for a in (0x79a3ac, 0x7be0d8, 0x7be0f8)]),
                    selected_filename_stable=selected == self.wide(0x7b8d48))

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
    r=SelectionReader(a.pid)
    try:
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,
                    sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),selection=r.selection())
        result.update(sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4))
        sources={}
        for name in ('read_environment_selection.py','read_services.py','read_live.py'):
            b=(root/name).read_bytes();(out/name).write_bytes(b);sources[name]=hashlib.sha256(b).hexdigest()
        result['sources']=sources
        (out/'selection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,indent=2))
    finally:K.CloseHandle(r.h)

if __name__=='__main__':main()
