import tempfile
from pathlib import Path
import shutil
from sync import sync, determine_actions


class TestE2E:

    @staticmethod
    def test_when_a_file_exists_in_the_source_but_not_the_destination():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a very useful file"
            (Path(source) / 'my-file').write_text(content)

            sync(source, dest)

            expected_path = Path(dest) /  'my-file'
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
            source_path = Path(source) / 'source-filename'
            old_dest_path = Path(dest) / 'dest-filename'
            expected_dest_path = Path(dest) / 'source-filename'
            source_path.write_text(content)
            old_dest_path.write_text(content)

            sync(source, dest)

            assert old_dest_path.exists() is False
            assert expected_dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)


class TestAction:

    @staticmethod
    def test_when_a_file_exists_in_the_source_but_not_the_destination():
        src_hashes = {'hash1': 'fn1'}
        dst_hashes = {}
        actions = list(determine_actions(src_hashes, dst_hashes, Path('/src'), Path('/dst')))
        assert actions == [('copy', Path('/src/fn1'), Path('/dst/fn1'))]

    @staticmethod
    def test_when_a_file_has_been_renamed_in_the_source():
        src_hashes = {'hash1': 'fn1'}
        dst_hashes = {'hash1': 'fn2'}
        actions = list(determine_actions(src_hashes, dst_hashes, Path('/src'), Path('/dst')))
        assert actions == [('move', Path('/dst/fn2'), Path('/dst/fn1'))]

