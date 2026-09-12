"""Build the native x86 DLL with an explicit TCC 0.9.27 Windows x86 path."""
from pathlib import Path
import sys,subprocess,hashlib,json
root=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python runtime/build.py C:/Tools/tcc/tcc.exe')
subprocess.run([sys.argv[1],'-shared','-o',str(root/'DINPUT.dll'),str(root/'loader.c'),'-ladvapi32','-luser32'],check=True)
subprocess.run([sys.executable,str(root/'fix-exports.py'),str(root/'DINPUT.dll')],check=True)
generated=root/'DINPUT.def'
if generated.exists():generated.unlink()
(root/'integrity.json').write_text(json.dumps({'DINPUT.dll':hashlib.sha256((root/'DINPUT.dll').read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
print('Built native DLL and refreshed installation integrity hash.')
