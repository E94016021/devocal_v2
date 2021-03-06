import librosa
import lyric_parser
from numpy import linalg
import numpy as np
import npp
from write_arr_mp3 import write_arr_mp3
import os
import datetime


"""
test devocal with void record bg
Conclusion:
        It works ! !
        (shift = 0)(void)
"""


def ms2sample(time_ms, sr=44100):
    time_sample = int(round(time_ms / 1000 * sr, 0))
    return time_sample


def mute_start(sig):
    sig[0:1000] = 0
    return sig


def compute_shift_vol(mix, bg, time):
    # TODO: to compute shift which is not -1728
    mix = mix[:time]
    bg = bg[:time]

    # compute shift
    fine_sample_shift = npp.find_shift(mix, bg)
    # fine_sample_shift = int(-1728)

    # compute volume
    a = linalg.norm(bg, ord=1)
    b = linalg.norm(mix, ord=1)

    vol_ratio = a / b

    # print("LA.norm(bg) =", a, "LA.norm(mix) =", b)
    # print("vol_ratio =", a / b)

    # vol_ratio = LA.norm(bg) / LA.norm(mix)
    if vol_ratio == np.nan:
        # useless
        # print("NAN error : set vol_ratio = 1")

        return fine_sample_shift, 1
    else:
        # print("     vol_ratio = ", vol_ratio)
        return fine_sample_shift, vol_ratio


def compute_vol_ratio_bgNorm(mix, bg, time):
    mix = mix[:time]
    bg = bg[:time]

    # Don't know why linalg.norm fail to 0.0 and nan (default:ord=2)

    # compute volume
    b = linalg.norm(bg, ord=1)
    m = linalg.norm(mix, ord=1)
    vol_ratio = b / m

    if vol_ratio == np.nan:
        # TODO: Don't know why nan not in ...
        # print("NAN error : set vol_ratio = 1")

        return 1, b
    else:
        return vol_ratio, b


def get_vocal_mp3_void(mix_file, bg_file, lyric_file, out_file="out.mp3"):
    # card_sample = ['clear', 'shift', 'volume_ratio',
    #                'song_sr', 'bg_sr', 'result_sr',
    #                'song_duration', 'bg_duration', 'result_duration', 'result_norm_ave',
    #                'error_text']
    card = [' ', ' ', ' ',
            ' ', ' ', ' ',
            ' ', ' ', ' ', ' ', ' ']

    # 讀audio檔
    bg, sr_bg = librosa.load(bg_file, sr=None)
    mix, sr_mix = librosa.load(mix_file, sr=None)

    # TODO: plt
    # import matplotlib.pyplot as plt
    # mix1, sr_mix = librosa.load(mix_file, sr=None, duration=10)
    # bg1, sr_bg = librosa.load(bg_file, sr=None, duration=10)
    # import librosa.display as d
    # import matplotlib.pyplot as plt
    # plt.figure()
    # d.waveplot(mix1, sr=sr_mix)
    # plt.title('mix')
    # plt.figure()
    # d.waveplot(bg1, sr=sr_bg)
    # plt.title('bg')
    # ###

    song_duration = len(mix)
    bg_duration = len(bg)

    if sr_mix != sr_bg:
        card = [0, ' ', ' ',
                sr_mix, sr_bg, ' ',
                song_duration, bg_duration, ' ', ' ', 'sr not match']

        # 輸出result with norm_value_fileName，回傳card
        fn = os.path.basename(out_file)
        fn = "sr_NOTmatch_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "error")
        fn = os.path.join(dn, fn)

        # Write null file with only filename
        result = np.array([])
        np.savetxt(fn, result)

        return card
    elif sr_mix == 44100:
        # shift = -1728
        shift = 0
    elif sr_mix == 22050:
        # shift = -1728 / 2
        shift = 0
    else:
        card = [0, ' ', ' ',
                sr_mix, sr_bg, ' ',
                song_duration, bg_duration, ' ', ' ', 'get_vocal error of if(sr_mix != sr_bg) function']

        # 輸出result with norm_value_fileName，回傳card
        fn = os.path.basename(out_file)
        fn = "sr_NOTmatch_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "error")
        fn = os.path.join(dn, fn)

        # Write null file with only filename
        result = np.array([])
        np.savetxt(fn, result)

        # Write null file with only filename
        result = np.array([])
        np.savetxt(fn, result)

        return card

    # sr is coming~
    sr = sr_mix
    sr_result = sr

    # get intro time
    l = lyric_parser.Lyric(lyric_file)
    time = l.get_time_before_vocal()

    if time < 1000:
        card[0] = 0
        card[10] = 'lyric might have wrong start (intro time < 1000)'

        # 輸出result with norm_value_fileName，回傳card
        fn = os.path.basename(out_file)
        fn = "lyric_wrongSTART_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "error")
        fn = os.path.join(dn, fn)

        # Write null file with only filename
        result = np.array([])
        np.savetxt(fn, result)

        return card

    # change ms 2 sample rate
    time = ms2sample(time - 1000, sr)
    time = time // 2

    # mute start to avoid blast sound
    mix = mute_start(mix)
    bg = mute_start(bg)

    # calculate volume rate
    vol, bg_norm = compute_vol_ratio_bgNorm(mix, bg, time)

    # some preprocessing and shift
    mix, bg = npp.pad_the_same(mix, bg)
    mix_shift = npp.right_shift(mix, shift)

    # devocal
    result = mix_shift[:song_duration] * vol - bg[:song_duration]
    # avoid lst blast （1728+1000）
    result = result[:len(result) - 3000]
    result_duration = len(result)

    # clear or not
    result_norm = linalg.norm(result[:time], ord=1)
    result_norm_ave = result_norm / time
    result_norm_ave = int(result_norm_ave * 10000000)

    if result_norm < bg_norm:

        fn = os.path.basename(out_file)
        fn = str(int(result_norm_ave)) + "_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "perfect")
        fn = os.path.join(dn, fn)

        # TODO : ouput result mp3
        write_arr_mp3(fn, result, sr)

        print(
            "   result_norm < bg_norm * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ! ! ! de success ! ! !",
            end=" ")
        print(datetime.datetime.now())
        card = [1, shift, vol,
                sr_mix, sr_bg, sr_result,
                song_duration, bg_duration, result_duration, result_norm_ave, ' ']
        return card
    else:
        # 輸出result with norm_value_fileName，回傳card
        fn = os.path.basename(out_file)
        fn = "norm_" + str(int(result_norm_ave)) + "_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "error")
        fn = os.path.join(dn, fn)

        # Write null file with only filename
        result = np.array([])
        np.savetxt(fn, result)

        # write_arr_mp3(fn, result, sr)
        print("   " + fn)

        print(
            "   result_norm > bg_norm - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ! ! ! de fail ! ! !",
            end=" ")
        print(datetime.datetime.now())
        card = [0, shift, vol,
                sr_mix, sr_bg, sr_result,
                song_duration, bg_duration, result_duration, result_norm_ave, 'de fail']
        return card


if __name__ == "__main__":
    # TODO: Test here.

    mix_folder = "/Users/LEE/nas/music_grp/17sing/v2/20206_星晴"
    d_bg_file = "/Users/LEE/PycharmProjects/devocal_v2/test/20206_星晴/20206_星晴_test.mp3"
    output_vocal_folder = "/Users/LEE/PycharmProjects/devocal_v2/test/20206_星晴/output"
    file_list = os.listdir(mix_folder)

    try:
        # get lyric path
        d_lyric_file = None

        for file in file_list:
            lyri_spliter = ".mp3"
            ll = file.split(lyri_spliter)
            if len(file.split(lyri_spliter)) == 1:
                d_lyric_file = os.path.join(mix_folder, file)
                break

        for file in file_list:
            card = ['.', '.', '.',
                    '.', '.', '.',
                    '.', '.', '.', '.',
                    '.']

            file_seg = file.split("_")
            file_len = len(file_seg)
            if file_len == 3:
                sid = file_seg[2].split(".mp3")[0]

                d_mix_file = os.path.join(mix_folder, file)

                song_spliter = "_" + sid
                m_name = file.split(song_spliter)[0] + file.split(song_spliter)[1]
                # d_bg_file = os.path.join(mix_folder, m_name)
                d_out_file = os.path.join(output_vocal_folder, file)

                try:
                    card = get_vocal_mp3_void(d_mix_file, d_bg_file, d_lyric_file, d_out_file)
                except Exception as e:
                    print(
                        "- - - - - - - - - - - - - - - - - - - - - - - -"
                        "- - - - - - - - - - - - - - - - - - - - - - - -", datetime.datetime.now())
                    print("ERROR : devocal_factory.get_voal_mp3() fail ")
                    print(e)
                    card[10] = e

                    #
                    ##
                    # start with write csv (not finish)

    except NotADirectoryError as nade:
        print("Input Song dir may have a wrong structure ! !")
        # print(nade)
        pass
    except Exception as e:
        print(e)

    print(".")
