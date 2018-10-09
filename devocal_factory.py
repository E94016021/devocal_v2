import csv
import os
import librosa

from fac1728 import get_vocal_mp3

if __name__ == "__main__":

    # test librosa.load
    m, s = librosa.load('/Users/LEE/PycharmProjects/devocal_v2/test/64335_擊敗人/64335_擊敗人_42412744.mp3', sr=None)
    filename = librosa.util.example_audio_file()
    y, sr = librosa.load(filename)
    ###################

    input_song_folder = "/home/slee/nas/music_grp/17sing/v2"
    input_song_folder = "./test"
    output_csv = "male_table.csv"
    # TODO : ffmpeg need exist folder
    output_vocal_folder = "/home/slee/nas/music_grp/17sing/v2_vocal"
    output_vocal_folder = "./vocal"
    output_file_type = ".mp3"
    #########################################

    with open(output_csv, 'w', newline='', encoding='utf8') as t:
        # 定義欄位
        fieldnames = ['clear', 'result_norm_ave', 'music_name', 'shift', 'volume_ratio',
                      'song_sr', 'bg_sr', 'result_sr',
                      'song_id', 'music_id',
                      'song_path', 'bg_path', 'result_path', 'song_duration', 'bg_duration', 'result_duration',
                      'error_text']
        # card_sample = ['clear', 'shift', 'volume_ratio',
        #         'song_sr', 'bg_sr', 'result_sr',
        #         'song_duration', 'bg_duration', 'result_duration', 'result_norm_ave', 'error_text']

        # 將 dictionary 寫入 CSV 檔
        writer = csv.DictWriter(t, fieldnames=fieldnames)

        # 寫入第一列的欄位名稱
        writer.writeheader()

        # print("\nstart Loader")
        # l = Loader(input_csv, input_song_folder, input_bg_folder)
        # cnt = len(l.data)
        dir_list = os.listdir(input_song_folder)
        for music_dir in dir_list:
            try:
                mid, music_name = music_dir.split("_")[0], music_dir.split("_")[1]
                file_list = os.listdir(os.path.join(input_song_folder, music_dir))

                # get lyric path
                d_lyric_file = None
                for file in file_list:
                    lyri_spliter = ".mp3"
                    ll = file.split(lyri_spliter)
                    if len(file.split(lyri_spliter)) == 1:
                        d_lyric_file = os.path.join(input_song_folder, music_dir, file)
                        break

                for file in file_list:

                    # lyri_spliter = ".mp3"
                    # ll = file.split(lyri_spliter)
                    # if len(file.split(lyri_spliter)) == 1:
                    #     d_lyric_file = os.path.join(input_song_folder, music_dir, file)

                    file_seg = file.split("_")
                    file_len = len(file_seg)
                    if file_len == 3:
                        sid = file_seg[2].split(".mp3")[0]
                        d_mix_file = os.path.join(input_song_folder, music_dir, file)

                        song_spliter = "_" + sid
                        m_name = file.split(song_spliter)[0] + file.split(song_spliter)[1]
                        d_bg_file = os.path.join(input_song_folder, music_dir, m_name)
                        d_out_file = os.path.join(output_vocal_folder, file)

                        card = get_vocal_mp3(d_mix_file, d_bg_file, d_lyric_file, d_out_file)
                        print(".")

                print(".")

            except NotADirectoryError as nade:
                # print(nade)
                pass

        print(".")

        # print("---Start ProcessPoolExecutor and check missing songs---")
        i = 0

        # print("start for-loop and get_data")

        for data in l:
            table = [' ', ' ', ' ', ' ', ' ',
                     ' ', ' ', ' ',
                     ' ', ' ',
                     ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            card = ['.', '.', '.',
                    '.', '.', '.',
                    '.', '.', '.', '.',
                    '.']
            try:
                # print("\nfor-loop", i + 1, "times")

                lp = data['lyric_path']

                mp = l.music_path
                mn, mi = data['music_name'], data['music_id']

                sp = l.song_path
                sn, si = data['music_name'], data['song_id']

                d_mix_file = os.path.join(sp, mi + "-" + sn, si + ".mp3")
                d_bg_file = os.path.join(mp, mi + "-" + mn, mn + ".mp3")
                d_lyric_file = lp

                # TODO: ouput mp3 or wav
                d_out_file = os.path.join(output_vocal_folder,
                                          mi + "_" + mn + "_" + si + output_file_type)

                # print("path done & start devocal")
                try:
                    card = get_vocal_mp3(d_mix_file, d_bg_file, d_lyric_file, d_out_file)

                    # print("     " + mn + " done")
                    # 這裡不能插空白
                except Exception as e:
                    # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
                    # print(e)
                    card[10] = e

                # TODO : write csv

                try:
                    card[10] = data['error']
                except Exception:
                    pass

                table = [card[0], card[9], mn, card[1], card[2],
                         card[3], card[4], card[5],
                         si, mi,
                         d_mix_file, d_bg_file, d_out_file,
                         card[6], card[7], card[8], card[10]]

                list_dict = {key: value for key, value in zip(fieldnames, table)}
                writer.writerow(list_dict)
                t.flush()

                i += 1
                # print("\n")
                continue
            except Exception as e:
                # print("ERROR: for  data in l :", e)
                if i == cnt + 1 or i == cnt - 1 or i == cnt:
                    break
