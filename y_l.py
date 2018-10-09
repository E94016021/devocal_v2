import librosa
import librosa.display as d
import matplotlib.pyplot as plt

if __name__ == "__main__":
    mix_file = "test/6139_對摺/6139_對摺_40040745.mp3"
    bg_file = "test/6139_對摺/6139_對摺.mp3"

    # TODO: plt
    bg1, sr_bg = librosa.load(bg_file, sr=None)

    a = bg1.size / sr_bg
    mix1, sr_mix = librosa.load(mix_file, sr=None, duration=a)

    print(".")

    a1 = bg1.size // 10
    plt.figure()
    d.waveplot(mix1[:a1], sr=sr_mix)
    plt.title('mix')
    plt.figure()
    d.waveplot(bg1[:a1], sr=sr_bg)
    plt.title('bg')
    print(".")

    ###
