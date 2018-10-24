import csv
import numpy as np
import os


# data loader
class TableLoader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        time_header = ["year", "month", "day", "hour", "minute", "second"]

        csv_file_name = os.path.basename(self.csv_path)
        year = csv_file_name.split("_")[0][:4]
        month = csv_file_name.split("_")[0][4:6]
        day = csv_file_name.split("_")[0][6:8]
        hour = csv_file_name.split("_")[1]
        minute = csv_file_name.split("_")[2]
        second = csv_file_name.split("_")[3]
        time_in = [year, month, day, hour, minute, second]
        time_dict = dict(zip(time_header, time_in))
        self.csv_time = time_dict

        self.data = []
        with open(csv_path, 'r', encoding='utf8') as f:
            rows = csv.reader(f)
            for row in rows:
                self.data.append(row)

        self.header = self.data[0]
        print(self.header)
        self.data = self.data[1:]  # skip header

    def __getitem__(self, sid):

        song_info_header = ['clear', 'result_norm_ave', 'music_name', 'shift', 'volume_ratio', 'song_sr', 'bg_sr',
                            'result_sr', 'song_id', 'music_id', 'song_path', 'bg_path', 'result_path', 'song_duration',
                            'bg_duration', 'result_duration', 'error_text']
        try:
            for row_ in self.data:
                if row_[8] == str(sid):
                    return dict(zip(song_info_header, row_))

        except Exception as e_gi:
            print("from TableLoader.__getitem__ :", e_gi)
            # d['error'] = e_gi
            return None


if __name__ == "__main__":
    t = TableLoader("table/20181021_17_40_19_table.csv")
    k = t.data[10]
    a = t[47588273]

    print(".")

    with open("table/20181021_17_40_19_table.csv", newline="") as table:
        rows = csv.reader(table)
        header = ['clear', 'result_norm_ave', 'music_name', 'shift', 'volume_ratio', 'song_sr', 'bg_sr', 'result_sr',
                  'song_id', 'music_id', 'song_path', 'bg_path', 'result_path', 'song_duration', 'bg_duration',
                  'result_duration', 'error_text']

        for row in rows:
            if row[0] == "clear":
                i = 20
                continue
            # zip(header, row)
            a = dict(zip(header, row))
            print(a)

        print(".")
