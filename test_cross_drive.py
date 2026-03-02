import tempfile, os
from webpconvert import convert_folder

# create temporary directories on F: and C:
root_f = tempfile.mkdtemp(dir=r'F:\\')
# create a folder directly on C:\ that should always be writable
root_c = tempfile.mkdtemp(dir=r'C:\\')

# create dummy png inside root_c
png = os.path.join(root_c, 'test_0_0.png')
open(png, 'wb').close()

print('root_f', root_f)
print('root_c', root_c)
print('running convert_folder(root_c, root_f)')
zip_path = convert_folder(root_c, root_f, delete_source=False)
print('zip path returned', zip_path)
print('remaining files in root_c', os.listdir(root_c))
