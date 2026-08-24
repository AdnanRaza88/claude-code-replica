import base64, pathlib
parts = [pathlib.Path(f'src/orchestration/.rt_b64_{i}').read_text() for i in range(4)]
data = base64.b64decode(''.join(parts))
pathlib.Path('src/orchestration/runtime.py').write_bytes(data)
print('restored', len(data))
