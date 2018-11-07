from table_loader import TableLoader
import os

if __name__ == "__main__":
    song_info_header = ['clear', 'result_norm_ave', 'music_name', 'shift', 'volume_ratio', 'song_sr', 'bg_sr',
                        'result_sr', 'song_id', 'music_id', 'song_path', 'bg_path', 'result_path', 'song_duration',
                        'bg_duration', 'result_duration', 'error_text']

    table_dir = "./table"
    a = os.listdir(table_dir)
    list.sort(a)

    t_ = 0

    for file in a:
        t = TableLoader(os.path.join(table_dir, file))
        zzz = len(t)
        t_ = t_ + zzz
        print(file, "- len :", zzz)

    print("total :", t_)
    print(".")

    t = TableLoader()
