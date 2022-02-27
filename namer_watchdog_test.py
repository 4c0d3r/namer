"""
Test namer_watchdog.py
"""
import datetime
import os
from pathlib import Path
import time
import unittest
from unittest.mock import patch
import logging
import tempfile
from freezegun import freeze_time
from mutagen.mp4 import MP4
from namer_mutagen_test import validate_mp4_tags
from namer_test import new_ea, prepare
from namer_types import NamerConfig, default_config
from namer_watchdog import create_watcher, done_copying, retry_failed

def make_locations(tempdir: Path) -> NamerConfig:
    """
    Make temp testing dirs.
    """
    config = default_config()
    config.watch_dir = tempdir / 'watch'
    config.watch_dir.mkdir()
    config.work_dir = tempdir / 'work'
    config.work_dir.mkdir()
    config.dest_dir = tempdir / 'dest'
    config.dest_dir.mkdir()
    config.failed_dir = tempdir / 'failed'
    config.failed_dir.mkdir()
    return config

def wait_until_processed(config: NamerConfig):
    """
    Waits until all files have been moved out of watch/working dirs.
    """
    while len(list(config.watch_dir.iterdir())) > 0 or len(list(config.work_dir.iterdir())) > 0:
        time.sleep(.2)

class UnitTestAsTheDefaultExecution(unittest.TestCase):
    """
    Always test first.
    """

    def test_done_copying_non_existant_file(self):
        """
        Test negatives.
        """
        non_path = Path("should_not_exist")
        self.assertFalse(done_copying(non_path))
        self.assertFalse(done_copying(None))


    @patch('namer_metadataapi.__get_response_json_object')
    @patch('namer.get_poster')
    def test_handler_collisions_success(self, mock_poster, mock_response):
        """
        Test the handle function works for a directory.
        """
        with tempfile.TemporaryDirectory(prefix="test") as tmpdir:
            tempdir = Path(tmpdir)
            config = make_locations(tempdir)
            config.prefer_dir_name_if_available=True
            config.write_namer_log = True
            config.min_file_size = 0
            watcher = create_watcher(config)
            watcher.start()
            targets = [new_ea(config.watch_dir),new_ea(config.watch_dir,use_dir=False)]
            prepare(targets, mock_poster, mock_response)
            wait_until_processed(config)
            watcher.stop()
            self.assertFalse(targets[0].file.exists())
            self.assertEqual(len(list(config.work_dir.iterdir())),0)
            outputfile = ( config.dest_dir / 'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!' /
                'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!.mp4')
            output = MP4(outputfile)
            self.assertEqual(output.get('\xa9nam'), ['Carmela Clutch: Fabulous Anal 3-Way!'])

            outputfile2 = ( config.dest_dir / 'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!' /
                'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!(1).mp4')
            output2 = MP4(outputfile2)
            self.assertEqual(output2.get('\xa9nam'), ['Carmela Clutch: Fabulous Anal 3-Way!'])



    @patch('namer_metadataapi.__get_response_json_object')
    @patch('namer.get_poster')
    def test_eventlisterner_success(self, mock_poster, mock_response):
        """
        Test the handle function works for a directory.
        """
        with tempfile.TemporaryDirectory(prefix="test") as tmpdir:
            tempdir = Path(tmpdir)
            config = make_locations(tempdir)
            config.prefer_dir_name_if_available=True
            config.min_file_size=0
            config.write_namer_log = True
            config.min_file_size = 0
            watcher = create_watcher(config)
            watcher.start()
            targets = [
                new_ea(config.watch_dir)
            ]
            prepare(targets, mock_poster, mock_response)
            wait_until_processed(config)
            watcher.stop()
            self.assertFalse(targets[0].file.exists())
            self.assertEqual(len(list(config.work_dir.iterdir())),0)
            outputfile = ( config.dest_dir / 'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!' /
                'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!.mp4')
            output = MP4(outputfile)
            self.assertEqual(output.get('\xa9nam'), ['Carmela Clutch: Fabulous Anal 3-Way!'])


    @patch('namer_metadataapi.__get_response_json_object')
    @patch('namer.get_poster')
    def test_handler_deeply_nested_success(self, mock_poster, mock_response):
        """
        Test the handle function works for a directory.
        """
        with tempfile.TemporaryDirectory(prefix="test") as tmpdir:
            tempdir = Path(tmpdir)
            config = make_locations(tempdir)
            config.prefer_dir_name_if_available = False
            config.write_namer_log = True
            config.min_file_size = 0
            watcher = create_watcher(config)
            watcher.start()
            targets = [
                new_ea(config.watch_dir / "deeper" / "and_deeper", use_dir=False),
                new_ea(config.watch_dir,post_stem="number2", use_dir=False)
            ]
            prepare(targets, mock_poster, mock_response)
            wait_until_processed(config)
            watcher.stop()
            self.assertFalse(targets[0].file.exists())
            self.assertEqual(len(list(config.work_dir.iterdir())),0)
            outputfile = ( config.dest_dir / 'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!' /
                'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!.mp4')
            validate_mp4_tags(self, outputfile)
            self.assertTrue((outputfile.parent / (outputfile.stem + "_namer.log")).exists())
            outputfile2 = ( config.dest_dir / 'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!' /
                'EvilAngel - 2022-01-03 - Carmela Clutch Fabulous Anal 3-Way!(1).mp4')
            validate_mp4_tags(self, outputfile2)


    @patch('namer_metadataapi.__get_response_json_object')
    @patch('namer.get_poster')
    def test_handler_failure(self, mock_poster, mock_response):
        """
        Test the handle function works for a directory.
        """
        with tempfile.TemporaryDirectory(prefix="test") as tmpdir:
            tempdir = Path(tmpdir)
            config = make_locations(tempdir)
            config.prefer_dir_name_if_available = False
            config.write_namer_log = True
            config.min_file_size = 0
            watcher = create_watcher(config)
            os.environ.update([('BUILD_DATE','date'),('GIT_HASH','hash')])
            watcher.start()
            targets = [
                new_ea(config.watch_dir, use_dir=False, match=False),
            ]
            prepare(targets, mock_poster, mock_response)
            wait_until_processed(config)
            watcher.stop()
            self.assertFalse(targets[0].file.exists())
            relative = targets[0].file.relative_to(config.watch_dir)
            work_file = config.work_dir / relative
            self.assertFalse(work_file.exists())
            failed_file = config.failed_dir /relative
            self.assertTrue(failed_file.exists() and failed_file.is_file())
            retry_failed(config)
            self.assertEqual(len(list(config.failed_dir.iterdir())), 0)
            self.assertGreater(len(list(config.watch_dir.iterdir())), 0)


    def test_manual_tick(self):
        """
        see it work.
        """
        config = default_config()
        hour = int(config.retry_time.split(":", maxsplit=1)[0].lstrip('0'))
        minstr = config.retry_time.split(":")[1].lstrip('0')
        minute = 0 if len(minstr) == 0 else int(minstr)
        today = datetime.datetime.today()
        before_retry = today.replace(hour=hour, minute=minute) - datetime.timedelta(seconds=3)
        with freeze_time(before_retry) as frozen_datetime:
            self.assertEqual(frozen_datetime(), before_retry)

            frozen_datetime.tick()
            before_retry += datetime.timedelta(seconds=1)
            self.assertEqual(frozen_datetime(),before_retry)

            frozen_datetime.tick(delta=datetime.timedelta(seconds=10))
            before_retry += datetime.timedelta(seconds=10)
            self.assertEqual(frozen_datetime(), before_retry)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
