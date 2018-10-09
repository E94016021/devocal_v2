import librosa
import lyric_parser
# import matplotlib.pyplot as plt
from numpy import linalg as LA
# import numpy as np
import numpy as np
import npp
from write_arr_mp3 import write_arr_mp3
import os


def gg(fn):
    print(fn)


def ms2sample(time_ms, sr=44100):
    time_sample = int(round(time_ms / 1000 * sr, 0))
    return time_sample


def mute_start(sig):
    sig[0:1000] = 0
    return sig


def compute_t_v(mix, bg, time):
    mix = mix[:time]
    bg = bg[:time]

    # compute shift
    fine_sample_shift = npp.find_shift(mix, bg)
    # fine_sample_shift = int(-1728)

    # compute volume
    a = LA.norm(bg)
    b = LA.norm(mix)

    vol_ratio = a / b

    # print("LA.norm(bg) =", a, "LA.norm(mix) =", b)
    # print("vol_ratio =", a / b)

    # vol_ratio = LA.norm(bg) / LA.norm(mix)
    if vol_ratio == np.nan:
        # print("NAN error : set vol_ratio = 1")

        return fine_sample_shift, 1
    else:
        # print("     vol_ratio = ", vol_ratio)
        return fine_sample_shift, vol_ratio


def compute_vol_ratio_bgNorm(mix, bg, time):
    mix = mix[:time]
    bg = bg[:time]

    # compute volume
    a = LA.norm(bg)
    b = LA.norm(mix)

    vol_ratio = a / b

    # print("LA.norm(bg) =", a, "LA.norm(mix) =", b)
    # print("vol_ratio =", a / b)

    # vol_ratio = LA.norm(bg) / LA.norm(mix)
    if vol_ratio == np.nan:
        # print("NAN error : set vol_ratio = 1")

        return 1, a
    else:
        # print("     vol_ratio = ", vol_ratio)
        return vol_ratio, a


def get_vocal_mp3(mix_file, bg_file, lyric_file, out_file="out.mp3"):
    # print("-----deal with ---", bg_file, "---")
    card_sample = ['clear', 'shift', 'volume_ratio',
                   'song_sr', 'bg_sr', 'result_sr',
                   'song_duration', 'bg_duration', 'result_duration', 'result_norm_ave',
                   'error_text']
    card = [' ', ' ', ' ',
            ' ', ' ', ' ',
            ' ', ' ', ' ', ' ', ' ']

    # 讀audio檔
    mix, sr_mix = librosa.load(mix_file, sr=None)
    bg, sr_bg = librosa.load(bg_file, sr=None)

    # # TODO: plt
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
        # print("sr_mix, sr_bg = ", sr_mix, ",", sr_bg,
        #       "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - sr not match")
        card = [0, ' ', ' ',
                sr_mix, sr_bg, ' ',
                song_duration, bg_duration, ' ', ' ', 'sr not match']
        return card
    elif sr_mix == 44100:
        shift = -1728
    elif sr_mix == 22050:
        shift = -1728 / 2
    else:
        # print("- - - - - - get_vocal error of if function - - - - - - - ")
        # print("sr_mix =", sr_mix,end='  ')
        # print("sr_bg =", sr_bg)
        card = [0, ' ', ' ',
                sr_mix, sr_bg, ' ',
                song_duration, bg_duration, ' ', ' ', 'get_vocal error of if function']
        return card

    # sr來囉
    sr = sr_mix
    sr_result = sr

    # 取得前奏的時間
    l = lyric_parser.Lyric(lyric_file)
    time = l.get_time_before_vocal()

    if time < 1000:
        card[0] = 0
        card[10] = 'lyric might have wrong start'
        # print(
        #     "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - lyric might have wrong start")
        return card

    # 單位變換，從ms換成sample
    time = ms2sample(time - 1000, sr)
    time = time // 2

    # 前處理
    mix = mute_start(mix)
    bg = mute_start(bg)

    # 計算音量比例
    vol, bg_norm = compute_vol_ratio_bgNorm(mix, bg, time)
    # print("shift = ", shift)
    # print("vol =", vol)

    # 前處理
    mix, bg = npp.pad_the_same(mix, bg)
    mix_shift = npp.right_shift(mix, shift)

    # 訊號相減，只留有人聲的長度
    result = mix_shift[:song_duration] * vol - bg[:song_duration]
    # 防尾段爆音（1728+1000）
    result = result[:len(result) - 3000]
    result_duration = len(result)

    # clear or not
    result_norm = LA.norm(result[:time])
    result_norm_ave = result_norm / time

    # print("result_norm, bg_norm, time =", result_norm, ",", bg_norm, ",", time)
    # print("result_norm_ave =", result_norm_ave, end='   ')
    result_norm_ave = int(result_norm_ave * 10000000)
    # print("result_norm_ave in 10^7 =", result_norm_ave)

    if result_norm < bg_norm:
        # print("out_file, result, sr = ", out_file, ",", result, ",", sr)

        fn = os.path.basename(out_file)
        fn = str(int(result_norm_ave)) + "_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "perfect")
        fn = os.path.join(dn, fn)

        # TODO : 輸出 result mp3
        # write_arr_mp3(fn, result, sr)
        gg(fn)

        print(
            "   result_norm < bg_norm * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * ! ! ! de success ! ! !")
        card = [1, shift, vol,
                sr_mix, sr_bg, sr_result,
                song_duration, bg_duration, result_duration, result_norm_ave, ' ']
        return card
    else:
        # 輸出result with norm_value_fileName，回傳card
        # TODO : 暫時不輸出檔案
        fn = os.path.basename(out_file)
        fn = "norm_" + str(int(result_norm_ave)) + "_" + fn
        dn = os.path.dirname(out_file)
        dn = os.path.join(dn, "error")
        fn = os.path.join(dn, fn)
        # TODO : output file
        # write_arr_mp3(fn, result, sr)
        # print(
        #     "   result_norm > bg_norm - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ! ! ! de fail ! ! !")
        card = [0, shift, vol,
                sr_mix, sr_bg, sr_result,
                song_duration, bg_duration, result_duration, result_norm_ave, 'de fail']
        return card

    # if __name__ == "__main__":
    #     get_vocal_mp3("./17sing/song/52899-算什麼男人/76363.mp3",
    #               "./17sing/final_music/52899-算什麼男人/算什麼男人.mp3",
    #               "./17sing/final_music/52899-算什麼男人/算什麼男人.lyrc",
    #               "./17sing/result/52899-算什麼男人/76363.mp3")

    '''
    - - first iter    
    [0. 0. 0. ... 0. 0. 0.]
    rMAX idx & value 16 1.1026217
    lMAX idx & value 864 1.8426653
    choose left
    LA.norm(bg) = 2.926685 LA.norm(mix) = 1.3986075
    vol_ratio = 2.0925708
         vol_ratio =  2.0925708
    shift =  -864
    vol = 2.0925708


    '''
