import hashlib
import os
import shutil
from pathlib import Path

class FileSystem:

    def read(self, path):
        return read_paths_and_hashes(path)

    def copy(self, source, dest):
        shutil.copyfile(source, dest)

    def move(self, source, dest):
        shutil.move(source, dest)

    def delete(self, dest):
        os.remove(dest)


def sync(source, dest, filesystem=FileSystem()):
    source_hashes = filesystem.read(source)
    dest_hashes = filesystem.read(dest)

    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source) / filename
            destpath = Path(dest) / filename
            filesystem.copy(sourcepath, destpath)

        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest) / dest_hashes[sha]
            newdestpath = Path(dest) / filename
            filesystem.move(olddestpath, newdestpath)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(dest / filename)



BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes
