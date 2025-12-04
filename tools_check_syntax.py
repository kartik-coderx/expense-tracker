import py_compile, glob, sys
errors = []
for f in glob.glob('**/*.py', recursive=True):
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        errors.append((f, str(e)))
if errors:
    for f, e in errors:
        print('ERROR:', f)
        print(e)
    sys.exit(2)
print('ALL_OK')
