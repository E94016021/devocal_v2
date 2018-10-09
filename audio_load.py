import os

import audioread
import numpy as np
import scipy.signal
import resampy

import librosa.cache as cache
import librosa.util as util

# Resampling bandwidths as percentage of Nyquist
BW_BEST = resampy.filters.get_filter('kaiser_best')[2]
BW_FASTEST = resampy.filters.get_filter('kaiser_fast')[2]


def load(path, sr=22050, mono=True, offset=0.0, duration=None, dtype=np.float32, res_type='kaiser_best'):
    y = []
    with audioread.audio_open(os.path.realpath(path)) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels
        duration_1 = input_file.duration

        s_start = int(np.round(sr_native * offset)) * n_channels

        if duration is None:
            s_end = np.inf
        else:
            s_end = s_start + (int(np.round(sr_native * duration))
                               * n_channels)

        n = 0
        duration_2 = 0
        xxx = 0

        for frame in input_file:

            duration_2 = duration_2 + 1

            frame = util.buf_to_float(frame, dtype=dtype)
            n_prev = n
            n = n + len(frame)

            if n < s_start:
                # offset is after the current frame
                # keep reading
                continue

            if s_end < n_prev:
                # we're off the end.  stop reading
                break

            if s_end < n:
                # the end is in this frame.  crop.
                frame = frame[:(s_end - n_prev)]

            if n_prev <= s_start and s_start <= n:
                # beginning is in this frame
                frame = frame[(s_start - n_prev):]
                xxx = xxx + 1

            # tack on the current frame
            y.append(frame)

    if y:
        y1 = np.concatenate(y)
        print(".")

        if n_channels > 1:
            y1 = y1.reshape((-1, n_channels)).T
            if mono:
                y1 = to_mono(y1)

        if sr is not None:
            y1 = resample(y1, sr_native, sr, res_type=res_type)

        else:
            sr = sr_native

    # Final cleanup for dtype and contiguity
    y2 = np.ascontiguousarray(y1, dtype=dtype)

    return y2, sr


@cache(level=20)
def to_mono(y):
    # Validate the buffer.  Stereo is ok here.
    util.valid_audio(y, mono=False)

    if y.ndim > 1:
        y = np.mean(y, axis=0)

    return y


@cache(level=20)
def resample(y, orig_sr, target_sr, res_type='kaiser_best', fix=True, scale=False, **kwargs):
    # First, validate the audio buffer
    util.valid_audio(y, mono=False)

    if orig_sr == target_sr:
        return y

    ratio = float(target_sr) / orig_sr

    n_samples = int(np.ceil(y.shape[-1] * ratio))

    if res_type == 'scipy':
        y_hat = scipy.signal.resample(y, n_samples, axis=-1)
    else:
        y_hat = resampy.resample(y, orig_sr, target_sr, filter=res_type, axis=-1)

    if fix:
        y_hat = util.fix_length(y_hat, n_samples, **kwargs)

    if scale:
        y_hat /= np.sqrt(ratio)

    return np.ascontiguousarray(y_hat, dtype=y.dtype)
