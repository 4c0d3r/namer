import os
import unittest
from unittest import mock
import tempfile
from distutils.dir_util import copy_tree
from namer_metadataapi import match, main
from namer_types import Performer
from namer_file_parser import parse_file_name

current=os.path.dirname(os.path.abspath(__file__))

def readfile(file: str) -> str: 
    if os.path.isfile(file):
        text_file = open(file, "r")
        data = text_file.read()
        text_file.close()
        return data
    return None

class UnitTestAsTheDefaultExecution(unittest.TestCase):
    """
    Always test first.
    """

    def prepare_workdir():
        current=os.path.dirname(os.path.abspath(__file__))
        test_fixture="test"
        tmpdir = tempfile.TemporaryDirectory()
        test_root = os.path.join(tmpdir.name,test_fixture)
        copy_tree(os.path.join(current, test_fixture), tmpdir.name)
        return tmpdir

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_parse_response_metadataapi_net_dorcel(self, mock_response):
        mock_response.return_value = readfile(os.path.join(current, "test","DorcelClub - 2021-12-23 - Aya.Benetti.Megane.Lopez.And.Bella.Tina.json"))
        name = parse_file_name('DorcelClub - 2021-12-23 - Aya.Benetti.Megane.Lopez.And.Bella.Tina.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 1)  
        result = results[0]
        info = result.looked_up  
        self.assertEqual(info.name, "Peeping Tom")
        self.assertEqual(info.date, "2021-12-23")
        self.assertEqual(info.site, "Dorcel Club")
        self.assertRegex(info.description, r'kissing in a parking lot')
        self.assertEqual(info.source_url, "https://dorcelclub.com/en/scene/85289/peeping-tom")
        self.assertEqual(info.poster_url, "https://thumb.metadataapi.net/unsafe/1000x1500/smart/filters:sharpen():upscale():watermark(https%3A%2F%2Fcdn.metadataapi.net%2Fsites%2F15%2Fe1%2Fac%2Fe028ae39fdc24d6d0fed4ecf14e53ae%2Flogo%2Fdorcelclub-logo.png,-10,-10,25)/https%3A%2F%2Fcdn.metadataapi.net%2Fscene%2F6e%2Fca%2F89%2F05343d45d85ef2d480ed63f6311d229%2Fbackground%2Fbg-dorcel-club-peeping-tom.jpg")
        expected = []
        expected.append(Performer("Ryan Benetti", None))
        expected.append(Performer("Aya Benetti","Female"))
        expected.append(Performer("Bella Tina","Female"))     
        expected.append(Performer("Megane Lopez","Female"))     
        self.assertListEqual(info.performers, expected)


    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_metadataapi_net(self, mock_response):
        mock_response.return_value = readfile(os.path.join(current,"test","response.json"))
        name = parse_file_name('EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertTrue(result.datematch)
        self.assertTrue(result.sitematch)
        self.assertGreaterEqual(result.name_match, 90.0)
        info = results[0].looked_up
        self.assertEqual(info.name, "Carmela Clutch: Fabulous Anal 3-Way!")
        self.assertEqual(info.date, "2022-01-03")
        self.assertEqual(info.site, "Evil Angel")
        self.assertRegex(info.description, r'brunette Carmela Clutch positions her big, juicy')
        self.assertEqual(info.source_url, "https://evilangel.com/en/video/Carmela-Clutch-Fabulous-Anal-3-Way/198543")
        self.assertEqual(info.poster_url, "https://thumb.metadataapi.net/unsafe/1000x1500/smart/filters:sharpen():upscale()/https%3A%2F%2Fcdn.metadataapi.net%2Fscene%2Fe6%2Fb9%2F5b%2F066589730107dcfd6b656a398a584b5%2Fbackground%2Fbg-evil-angel-carmela-clutch-fabulous-anal-3-way.jpg")
        expected = []
        expected.append(Performer("Carmela Clutch", "Female"))
        expected.append(Performer("Francesca Le","Female"))
        expected.append(Performer("Mark Wood","Male"))     
        self.assertListEqual(info.performers, expected)

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_full_metadataapi_net(self, mock_response):
        mock_response.return_value = readfile(os.path.join(current,"test","full.json"))
        name = parse_file_name('EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertTrue(result.datematch)
        self.assertTrue(result.sitematch)
        self.assertGreaterEqual(result.name_match, 90.0)
        info = results[0].looked_up
        self.assertEqual(info.name, "Carmela Clutch: Fabulous Anal 3-Way!")
        self.assertEqual(info.date, "2022-01-03")
        self.assertEqual(info.site, "Evil Angel")
        self.assertRegex(info.description, r'brunette Carmela Clutch positions her big, juicy')
        self.assertEqual(info.source_url, "https://evilangel.com/en/video/Carmela-Clutch-Fabulous-Anal-3-Way/198543")
        self.assertRegexpMatches(info.poster_url, "https://thumb.metadataapi.net/unsafe/1000x1500/smart/.*%2Fbackground%2Fbg-evil-angel-carmela-clutch-fabulous-anal-3-way.jpg")
        expected = []
        expected.append(Performer("Carmela Clutch", "Female"))
        expected.append(Performer("Francesca Le","Female"))
        expected.append(Performer("Mark Wood","Male"))     
        self.assertListEqual(info.performers, expected)

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_metadataapi_net_no_data(self, mock_response):
        mock_response.return_value = '{}'
        name = parse_file_name('EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 0)

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_metadataapi_net_no_message(self, mock_response):
        mock_response.return_value = ''
        name = parse_file_name('EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 0)

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_metadataapi_net_none_message(self, mock_response):
        mock_response.return_value = None
        name = parse_file_name('EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4')
        results = match(name, "your_porndb_authkey")
        self.assertEqual(len(results), 0)             

    @mock.patch("namer_metadataapi.__get_response_json_object")
    def test_call_main(self, mock_response):
        mock_response.return_value = readfile(os.path.join("test","response.json"))
        main(['-f','EvilAngel.22.01.03.Carmela.Clutch.Fabulous.Anal.3-Way.XXX.mp4','-t','your_porndb_authkey','-q'])
        # verify we got here.
        
if __name__ == '__main__':
    unittest.main()