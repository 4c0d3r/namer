import os
import json
from sys import stdout
from types import SimpleNamespace
from distutils.file_util import copy_file
import subprocess
from typing import Tuple
import unittest
from pathlib import Path

def getResolution(file: str) -> int:
    """
    Gets the vertical resolution of an mp4 file.  For example, 720, 1080, 2160...
    """
    print("resolution stream of file {}".format(file))

    process = subprocess.Popen(['ffprobe',  
                                    '-v',
                                    'error',
                                    '-select_streams',
                                    'v:0',
                                    '-show_entries',
                                    'stream=height',
                                    '-of',
                                    'csv=p=0',
                                    file],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
    success = process.wait() == 0
    output = process.stdout.read()
    error_msg = process.stderr.read()
    if not success:
        print("Error gettng resolution of file {}".format(file))
        print("{}".format(error_msg))
    process.stdout.close()
    process.stderr.close()
    print("output {}".format(output))
    return int(output)

def getAudioStreamForLang(input: str, language: str) -> int:
    """
    given an mp4 input file and a desired language will return the stream position of that language in the mp4.
    if the language is None, or the stream is not found, or the desired stream is the only default stream, None is returned.
    """
    # audio_streams_str = os.popen('ffprobe -show_streams -select_streams a -of json -i "{}"'.format(input)).read().strip()

    # print("Target for audio: {}".format(input))

    process = subprocess.Popen(['ffprobe',  
                                    '-show_streams',
                                    '-select_streams',
                                    'a',
                                    '-of',
                                    'json',
                                    '-i',
                                    input],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
    success = process.wait() == 0                       
    audio_streams_str = process.stdout.read()
    audio_streams_err = process.stderr.read()
    if not success:
        print("Error gettng audio streams of file {}".format(input))
        print("{}".format(audio_streams_err))
    process.stdout.close()
    process.stderr.close()

    print("Target for audio: {}".format(input))

    audio_streams = json.loads(audio_streams_str, object_hook=lambda d: SimpleNamespace(**d))
    lang_stream=None
    needs_updated=False
    if language:
        test_lang = language.lower()[0:3]
        if audio_streams != None and  hasattr(audio_streams, 'stream'):
            for audio_stream in audio_streams.streams:
                default = audio_stream.disposition.default == 1
                lang = audio_stream.tags.language
                if lang == test_lang:
                    lang_stream = audio_stream.index - 1
                    if default == False:
                        needs_updated = True
                elif default == True:
                    needs_updated = True
            if needs_updated and lang_stream:
                return lang_stream
    return None

def copyAndUpdateAudioStreamIfNeeded(input: str, output: str, language: str) -> bool:
    """
    Returns true if the file had to be edited to have a default audio stream equal to the desired language,
    mostly a concern for apple players (Quicktime/Apple TV/etc.)

    Copies, and potentially updates the default audio stream of a video file.
    """
    # split=os.path.splitext(input)    
    # if split[1] == ".mkv":
    #     newinput = split[0]+".mp4"
    #     process = subprocess.Popen(['ffmpeg',  
    #                                 '-i',
    #                                 '{}'.format(input), #input file

    #                                 # -c:v libx264 -crf 19 -preset slow -c:a aac -strict experimental -b:a 192k -ac 2
    #                                 '-c:v',
    #                                 'libx264',
    #                                 '-crf',
    #                                 '19',
    #                                 '-c:a',
    #                                 'aac',
    #                                 '-b:a',
    #                                 '128k',
    #                                 '-tag:v',
    #                                 'hvc1',
    #                                 '{}'.format(newinput)],
    #                                 stdout=subprocess.PIPE,
    #                                 stderr=subprocess.PIPE,
    #                                 universal_newlines=True)
    #     output = process.stdout.read()
    #     error_msg = process.stderr.read()
    #     success = process.wait() == 0
    #     if success:
    #         input=newinput

    stream = getAudioStreamForLang(input, language)
    if stream != None:
        newinput = None
        if input == output:
            newinput = os.path.join(Path(input).parent.absolute(), "temp_"+os.path.basename(input))
            os.rename(input, newinput)
            input = newinput
        print("Attempt to alter default audio stream of {}".format(input))    
        process = subprocess.Popen(['ffmpeg',  
                                    '-i',
                                    '{}'.format(input), #input file
                                    '-map',
                                    '0', #copy all stream
                                    '-disposition:a',
                                    'none', #mark all audio streams as not default
                                    '-disposition:a:{}'.format(stream), #mark this audio stream as default
                                    'default',
                                    '-c',
                                    'copy', #don't reencode anything.
                                    '{}'.format(output)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
        output = process.stdout.read()
        error_msg = process.stderr.read()
        success = process.wait() == 0
        if not success:
            print("Could not update audio stream for {}".format(input))
            print("{}".format(error_msg))
        process.stdout.close()
        process.stderr.close()
        print('Return code: '.format(process.returncode))
        if newinput != None:
            os.remove(newinput)
        return success
    else:
        return copy_file(input, output)[1]


class UnitTestAsTheDefaultExecution(unittest.TestCase):
    """
    Always test first.
    """

    current=os.path.dirname(os.path.abspath(__file__))


    def test_get_resolution(self):
        file = os.path.join(os.path.join(self.current, "test"), "Site.22.01.01.painful.pun.XXX.720p.xpost.mp4")
        res = getResolution(file)
        self.assertEqual(res, 240)

    def test_get_audio_stream(self):
        file = os.path.join(os.path.join(self.current, "test"), "Site.22.01.01.painful.pun.XXX.720p.xpost.mp4")
        id = getAudioStreamForLang(file, "und")
        self.assertEqual(id, None)
        id = getAudioStreamForLang(file, "eng")
        self.assertEqual(id, None)

if __name__ == '__main__':
    unittest.main()