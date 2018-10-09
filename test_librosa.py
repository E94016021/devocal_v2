import librosa
import librosa.display as d
import matplotlib.pyplot as plt

if __name__ == "__main__":
    mix_file = "test/6139_對摺/6139_對摺_40040745.mp3"
    bg_file = "test/6139_對摺/6139_對摺.mp3"

    # TODO: plt
    mix1, sr_mix = librosa.load(mix_file, sr=None, duration=10)
    bg1, sr_bg = librosa.load(bg_file, sr=None, duration=10)
    print(".")

    plt.figure()
    d.waveplot(mix1, sr=sr_mix)
    plt.title('mix')
    plt.figure()
    d.waveplot(bg1, sr=sr_bg)
    plt.title('bg')
    print(".")

    ###
