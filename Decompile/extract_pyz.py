from PyInstaller.utils.cliutils import archive_viewer
import os
from pathlib import Path

magic = b"\x6f\x0d\x0d\x0a\0\0\0\0\0\0\0\0\0\0\0\0"
v = archive_viewer.ArchiveViewer("PYZ-00.pyz", False, False, False)
archive = v._open_toplevel_archive(v.filename)
archive_name = os.path.basename(v.filename)
v._show_archive_contents(archive_name, archive)

for name in archive.toc.keys():
    data = archive.extract(name, True)
    if data is None:
        print(f"Entry {name} has no associated data!")
        continue
    filename = f"x/{name.replace('.', '/')}.pyc"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "wb") as fp:
        fp.write(magic)
        fp.write(data)