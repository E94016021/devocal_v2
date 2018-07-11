import numpy as np
import subprocess as sp
import os
import librosa


def write_arr_mp3(file_name='mp3.mp3', array: np.ndarray = [], sr=44100):
    print("write_mp3_start")
    try:

        # TODO: stereo to mono ?
        # sr = str(sr / 2)
        array1 = array.tobytes()
        command = ['ffmpeg',
                   '-y',  # (optional) means overwrite the output file if it already exists
                   '-f', 'f32le',  # float 32 little endian
                   '-acodec', 'pcm_f32le',
                   '-ar', str(sr),  # sr eat str, bytes or os.PathLike object, not float

                   # 22050-ac2; 44100-ac1？？

                   '-ac', '1',  # stereo (set to '1' for mono)
                   '-i', '-',  # means that the input will arrive from the pipe
                   '-vn',  # means "don't expect any video input"
                   # '-acodec', "libfdk_aac",  # output audio codec
                   #            '-b', "3000k",  # output bitrate (=quality). Here, 3000kb/second
                   file_name
                   ]

        # pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE)
        pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

        pipe.stdin.write(array1)

        pipe.stdout.close()
        pipe.stdin.close()
        pipe.stderr.close()
    except Exception as e:
        print(e)

    '''

    array1 = array.tobytes()
    command = ['ffmpeg',
               '-y',
               '-i', '-',
               '-vn',
               '-acodec', "libmp3lame",
               '-q:a', '0',
               file_name
               ]

    pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    pipe.stdin.write(array1)

    
    array = array.tobytes()
    command = ['ffmpeg',
               '-y',  # (optional) means overwrite the output file if it already exists
               '-f', 'f32le',  # float 32 little endian
               '-acodec', 'pcm_f32le',
               '-ar', '44100',  # ouput will have 44100 Hz
               '-ac', '2',  # stereo (set to '1' for mono)
               '-i', '-',
               #        '-vn', # means "don't expect any video input"
               #        '-acodec', "libfdk_aac" # output audio codec
               #        '-b', "3000k", # output bitrate (=quality). Here, 3000kb/second
               file_name
               ]
    pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    pipe.stdin.write(array)
    '''


if __name__ == '__main__':
    file_name = "out.mp3"
    file = "./17sing/final_music/52899-算什麼男人/算什麼男人.mp3"
    music_array, sr = librosa.load(file, sr=None)
    write_arr_mp3(file_name, music_array, sr)
