import os
file_path = r'C:\Users\rayjo\AppData\Roaming\Python\Python312\site-packages\openbb_core\app\provider_interface.py'
with open(file_path, 'r', encoding='utf-8') as f: 
    text = f.read()

injection = '''
# --- DUMMY INJECTED TO PATCH OPENBB-EQUITY 1.6.1 VS OPENBB-CORE 1.6.7 ---
def __getattr__(name):
    if name.startswith('OBBject_'): return OBBject
    raise AttributeError(f'module {__name__} has no attribute {name}')
'''

if 'def __getattr__' not in text:
    with open(file_path, 'a', encoding='utf-8') as f: 
        f.write('\n' + injection)
    print('Patched successfully')
else:
    print('Already patched')
