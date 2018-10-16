import csv
import os
import datetime

from fac1728 import get_vocal_mp3
import audio_load as al
from data_loader import Loader

if __name__ == "__main__":

    # input_song_folder = "/home/slee/nas/music_grp/17sing/v2"
    input_song_folder = "/mnt/nas/music_grp/17sing/v2"
    time_s = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    # time_s = datetime.datetime.now()
    table_dir_name = "./table"
    output_csv = table_dir_name+"/" + time_s + "_table.csv"
    # output_vocal_folder = "/home/slee/nas/music_grp/17sing/v2_vocal"
    output_vocal_folder = "/mnt/nas/music_grp/17sing/v2_vocal"
    output_file_type = ".mp3"
    #########################################
    if not os.path.exists(table_dir_name):
        os.makedirs(table_dir_name)
        print("Create output_csv folder")

    if not os.path.exists(output_vocal_folder):
        os.makedirs(output_vocal_folder)
        print("Create output_csv folder")

    # ffmpeg NEED exist folder
    perfect_output_dir = os.path.join(output_vocal_folder, "perfect")
    error_output_dir = os.path.join(output_vocal_folder, "error")
    if not os.path.exists(perfect_output_dir):
        os.makedirs(perfect_output_dir)
        print("Create perfect folder")
    if not os.path.exists(error_output_dir):
        os.makedirs(error_output_dir)
        print("Create error folder")

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
        # Write cnt initial = 0 .
        write_cnt = 0
        #
        # print("\nstart Loader")
        # l = Loader(input_csv, input_song_folder, input_bg_folder)
        # cnt = len(l.data)

        # TODO: 1. Exist skip system 2. Write to csv
        # Preprocess sorting dir to newer m_id first .
        d_list = os.listdir(input_song_folder)
        el_list = []
        for el in d_list:
            el = el.split("_")
            try:
                el[0] = int(el[0])
                el_list.append(el)
            except Exception as e:
                # Dir which not match the format
                pass

        el_list = sorted(el_list, key=lambda x: x[0], reverse=True)
        dir_list = []
        for el in el_list:
            d_n = str(el[0]) + "_" + el[1]
            dir_list.append(d_n)

        # buile exist files table
        exist_sid_list = []
        for root, dirs, files_ in os.walk(output_vocal_folder):
            for d in dirs:

                if d == "perfect":
                    for root_, dirs_, files in os.walk(os.path.join(root, d)):
                        for f in files:
                            try:
                                sid = f.split("_")[3].split(".mp3")[0]
                                exist_sid_list.append(sid)
                            except IndexError as ide:
                                pass
                elif d == "error":
                    for root_, dirs_, files in os.walk(os.path.join(root, d)):
                        for f in files:
                            try:
                                # TODO: write only file_name with empty file.txt
                                sid = f.split("_")[4].split(".mp3")[0]
                                exist_sid_list.append(sid)
                            except IndexError as ide:
                                pass
                elif len(exist_sid_list) == 0:
                    print("Output file's dir may have wrong structure ! !")
                    print("- Check exist de_files fail")
                    raise Exception

        exist_sid_list.sort()
        print("* Finish checking exist de_files. count =", len(exist_sid_list))

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
                    # Initial state of table and card
                    table = [' ', ' ', ' ', ' ', ' ',
                             ' ', ' ', ' ',
                             ' ', ' ',
                             ' ', ' ', ' ', ' ', ' ', ' ', ' ']
                    card = ['.', '.', '.',
                            '.', '.', '.',
                            '.', '.', '.', '.',
                            '.']

                    # lyri_spliter = ".mp3"
                    # ll = file.split(lyri_spliter)
                    # if len(file.split(lyri_spliter)) == 1:
                    #     d_lyric_file = os.path.join(input_song_folder, music_dir, file)

                    file_seg = file.split("_")
                    file_len = len(file_seg)
                    if file_len == 3:
                        sid = file_seg[2].split(".mp3")[0]
                        if sid in exist_sid_list:
                            print("* sid:", sid, "exist!!")
                        else:
                            d_mix_file = os.path.join(input_song_folder, music_dir, file)

                            song_spliter = "_" + sid
                            m_name = file.split(song_spliter)[0] + file.split(song_spliter)[1]
                            d_bg_file = os.path.join(input_song_folder, music_dir, m_name)
                            d_out_file = os.path.join(output_vocal_folder, file)

                            try:
                                card = get_vocal_mp3(d_mix_file, d_bg_file, d_lyric_file, d_out_file)
                                if card[0] == 1:
                                    write_cnt= write_cnt+1
                                # print(d_mix_file, ":", card[10])
                                # print(".")
                            except Exception as e:
                                print(
                                    "- - - - - - - - - - - - - - - - - - - - - - - -"
                                    "- - - - - - - - - - - - - - - - - - - - - - - -")
                                print("ERROR : devocal_factory.get_voal_mp3() fail")
                                print(e)
                                card[10] = e

                            #
                            ##
                            # start with write csv (not finish)

                            table = [card[0], card[9], music_name, card[1], card[2],
                                     card[3], card[4], card[5],
                                     sid, mid,
                                     d_mix_file, d_bg_file, d_out_file,
                                     card[6], card[7], card[8], card[10]]

                            list_dict = {key: value for key, value in zip(fieldnames, table)}
                            writer.writerow(list_dict)
                            t.flush()




            except NotADirectoryError as nade:
                print("Input Song dir may have a wrong structure ! !")
                # print(nade)
                pass

            if datetime.datetime.now().second == 0:
                print("\n\n" + str(datetime.datetime.now()))
                print("Now de_perfect with", write_cnt, "files\n\n")
            ###
            ##
            #

print(".")

# # print("---Start ProcessPoolExecutor and check missing songs---")
# i = 0
#
# # print("start for-loop and get_data")
#
# for data in l:
#     table = [' ', ' ', ' ', ' ', ' ',
#              ' ', ' ', ' ',
#              ' ', ' ',
#              ' ', ' ', ' ', ' ', ' ', ' ', ' ']
#     card = ['.', '.', '.',
#             '.', '.', '.',
#             '.', '.', '.', '.',
#             '.']
#     try:
#         # print("\nfor-loop", i + 1, "times")
#
#         lp = data['lyric_path']
#
#         mp = l.music_path
#         mn, mi = data['music_name'], data['music_id']
#
#         sp = l.song_path
#         sn, si = data['music_name'], data['song_id']
#
#         d_mix_file = os.path.join(sp, mi + "-" + sn, si + ".mp3")
#         d_bg_file = os.path.join(mp, mi + "-" + mn, mn + ".mp3")
#         d_lyric_file = lp
#
#         # TODO: ouput mp3 or wav
#         d_out_file = os.path.join(output_vocal_folder,
#                                   mi + "_" + mn + "_" + si + output_file_type)
#
#         # print("path done & start devocal")
#         try:
#             card = get_vocal_mp3(d_mix_file, d_bg_file, d_lyric_file, d_out_file)
#
#             # print("     " + mn + " done")
#             # 這裡不能插空白
#         except Exception as e:
#             # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
#             # print(e)
#             card[10] = e
#
#         # TODO : write csv
#
# try:
#     card[10] = data['error']
# except Exception:
#     pass
#
# table = [card[0], card[9], mn, card[1], card[2],
#          card[3], card[4], card[5],
#          si, mi,
#          d_mix_file, d_bg_file, d_out_file,
#          card[6], card[7], card[8], card[10]]
#
# list_dict = {key: value for key, value in zip(fieldnames, table)}
# writer.writerow(list_dict)
# t.flush()
#
# i += 1
# # print("\n")
# continue
#     except Exception as e:
#         # print("ERROR: for  data in l :", e)
#         if i == cnt + 1 or i == cnt - 1 or i == cnt:
#             break
