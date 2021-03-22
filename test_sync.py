import tempfile
from pathlib import Path
import shutil
from sync import FileSystem, sync


class TestE2E:
    @staticmethod
    def test_when_a_file_exists_in_the_source_but_not_the_destination():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a very useful file"
            (Path(source) / "my-file").write_text(content)

            sync(source, dest)

            expected_path = Path(dest) / "my-file"
            assert expected_path.exists()
            assert expected_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    @staticmethod
    def test_when_a_file_has_been_renamed_in_the_source():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that was renamed"
            source_path = Path(source) / "source-filename"
            old_dest_path = Path(dest) / "dest-filename"
            expected_dest_path = Path(dest) / "source-filename"
            source_path.write_text(content)
            old_dest_path.write_text(content)

            sync(source, dest)

            assert old_dest_path.exists() is False
            assert expected_dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)


class FakeFilesystem:
    def __init__(self, path_hashes):
        self.path_hashes = path_hashes
        self.actions = []

    def read(self, path):
        return self.path_hashes[path]

    def copy(self, src, dest):
        self.actions.append(('COPY', src, dest))

    def move(self, src, dest):
        self.actions.append(('MOVE', src, dest))

    def delete(self, dest):
        self.actions.append(('DELETE', dest))



def test_when_a_file_exists_in_the_source_but_not_the_destination():
    fakefs = FakeFilesystem({
        '/src': {"hash1": "fn1"},
        '/dst': {},
    })
    sync('/src', '/dst', filesystem=fakefs)
    assert fakefs.actions == [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]


def test_when_a_file_has_been_renamed_in_the_source():
    fakefs = FakeFilesystem({
        '/src': {"hash1": "fn1"},
        '/dst': {"hash1": "fn2"},
    })
    sync('/src', '/dst', filesystem=fakefs)
    assert fakefs.actions == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]
