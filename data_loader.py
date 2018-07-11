import csv
import os

from fac1728 import get_vocal_mp3


# data loader
class Loader:
    def __init__(self, csv_path, song_path, music_path):
        self.csv_path = csv_path
        self.song_path = song_path
        self.music_path = music_path
        self.lyric_path = music_path

        self.data = []
        with open(csv_path, 'r', encoding='utf8') as f:
            rows = csv.reader(f)

            for row in rows:
                self.data.append(row)

        self.header = self.data[0]
        self.data = self.data[1:]  # skip header

    def __getitem__(self, idx):
        try:
            d = {}
            d['song_id'] = self.data[idx][0]
            d['music_name'] = self.data[idx][1]
            d['music_id'] = self.data[idx][12]
            d['bg_path'] = os.path.join(self.music_path, d['music_id'] + "-" + d['music_name'],
                                        d['music_name'] + ".mp3")
            d['song_path'] = os.path.join(self.song_path, d['music_id'] + "-" + d['music_name'], d['song_id'] + ".mp3")
            d['lyric_path'] = os.path.join(self.music_path, d['music_id'] + "-" + d['music_name'],
                                           d['music_name'] + ".lyrc")
            f = open(d['lyric_path'], 'r', encoding="utf-8")
            lyric = f.readlines()
            d['lyric'] = lyric
        except Exception as e_gi:
            # print("from Loader.__getitem__ :", e_gi)
            d['error'] = e_gi
            return d
        return d


if __name__ == "__main__":

    # files location block ##################
    # female_ios.csv:   iOS裝置女生唱 照觀看次數排名
    # male_ios.csv:     iOS裝置男生唱 照觀看次數排名
    input_csv = "male_ios.csv"
    input_song_folder = "/home/slee/nas/music_grp/17sing/song"
    input_bg_folder = "/home/slee/nas/music_grp/17sing/final_music"

    output_csv = "file_table.csv"
    # TODO : ffmpeg need exist folder
    output_vocal_folder = "/home/slee/nas/music_grp/17sing/vocal"
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

        print("\nstart Loader")
        l = Loader(input_csv, input_song_folder, input_bg_folder)

        print("---Start ProcessPoolExecutor and check missing songs---")
        i = 0

        print("start for-loop and get_data")

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
                print("\nfor-loop", i + 1, "times")

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

                print("path done & start devocal")
                try:
                    card = get_vocal_mp3(d_mix_file, d_bg_file, d_lyric_file, d_out_file)

                    print("     " + mn + " done")
                    # 這裡不能插空白
                except Exception as e:
                    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
                    print(e)
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
                print("\n")
                continue
            except Exception as e:
                print("ERROR: for  data in l :", e)
