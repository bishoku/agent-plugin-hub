#!/usr/bin/env python3
"""Unpack into a new directory, preserving all safe members for subsequent edits."""
import argparse
from pathlib import Path, PurePosixPath
import stat
import zipfile


def unpack(source, destination):
    destination=Path(destination)
    if destination.exists(): raise ValueError('destination already exists; choose a new directory')
    with zipfile.ZipFile(source) as archive:
        infos=archive.infolist(); names=set()
        if sum(i.file_size for i in infos)>100*1024*1024: raise ValueError('archive exceeds 100 MiB unpacked limit')
        for entry in infos:
            name=entry.filename; path=PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or not path.parts: raise ValueError(f'unsafe archive path: {name}')
            if path.as_posix() in names: raise ValueError(f'duplicate archive path: {name}')
            if stat.S_ISLNK(entry.external_attr >> 16): raise ValueError('archive symlinks are unsupported')
            names.add(path.as_posix())
        if not {'workspace.json','diagram.json'} <= names: raise ValueError('missing workspace.json or diagram.json')
        files = {PurePosixPath(i.filename).as_posix() for i in infos if not i.is_dir()}
        for name in names:
            if any(parent.as_posix() in files for parent in PurePosixPath(name).parents):
                raise ValueError('archive file/directory path conflict')
        destination.mkdir(parents=True)
        for entry in infos:
            path=destination/entry.filename
            if entry.is_dir(): path.mkdir(parents=True,exist_ok=True)
            else:
                path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(archive.read(entry))
    return len(infos)


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('project'); parser.add_argument('destination'); args=parser.parse_args()
    try: print(f'Unpacked {unpack(args.project,args.destination)} entries into {Path(args.destination).resolve()}')
    except (OSError,ValueError,zipfile.BadZipFile) as exc: parser.exit(1,f'ERROR: {exc}\n')

if __name__=='__main__': main()
