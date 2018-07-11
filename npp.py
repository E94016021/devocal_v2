import numpy as np


def left_pad(array, pad_length):
    if pad_length >= 0:
        return np.pad(array, (pad_length, 0), "constant", constant_values=(0, 0))
    elif pad_length < 0:
        return array[-pad_length:].copy()


def right_pad(array, pad_length):
    if pad_length >= 0:
        return np.pad(array, (0, pad_length), "constant", constant_values=(0, 0))
    elif pad_length < 0:
        return array[:pad_length]


def pad_the_same(a, b):
    pad_length = a.shape[0] - b.shape[0]
    if pad_length > 0:
        b = right_pad(b, pad_length)
    elif pad_length < 0:
        a = right_pad(a, -pad_length)

    return a, b


def right_shift(array, length):
    """
    :param array: origin signal
    :param length: shift length
    :return: shifted signal
    """

    buf = right_pad(array, -length)
    return left_pad(buf, length)


def left_shift(array, length):
    """
    :param array: origin signal
    :param length: shift length
    :return: shifted signal
    """
    buf = left_pad(array, -length)
    return right_pad(buf, length)


def convolve(kernel_array, array):
    """
    convolve
    :param kernel_array: kernel array
    :param array: array to convolve
    :return: left, right
    left is a array of result of convolve along left side
    left is a array of result of convolve along right side
    """

    print("start convolution\n")
    # 卷積
    convolved = np.convolve(kernel_array[::-1], array)
    print(convolved)

    # 往右shift的卷積
    right = convolved.copy()
    right = right[kernel_array.shape[0] - 1:]

    # 往左shift的卷積
    left = convolved.copy()
    left = left[:kernel_array.shape[0]][::-1]

    return left, right


def find_shift(kernel_array: np.ndarray, array: np.ndarray):
    # return int(-1728)

    # 卷積
    left, right = convolve(kernel_array, array)
    range = -1

    # 找到往右卷的最大值和位移
    r_max_idx = np.argmax(right[:range])
    r_max_value = right[:range].max()

    # 找到往左卷的最大值和位移
    l_max_idx = np.argmax(left[:range])
    l_max_value = left[:range].max()

    print("rMAX idx & value", r_max_idx, r_max_value)
    print("lMAX idx & value", l_max_idx, l_max_value)

    # return int(r_max_idx)
    # 看往左往右哪個大，return那個值
    # 往右是正數
    # 往左是負數
    if r_max_value > l_max_value:
        print("choose right")
        return int(r_max_idx)
    else:
        print("choose left")
        return int(-l_max_idx)


def auto_shift(kernel_array: np.ndarray, array: np.ndarray):
    shift = find_shift(kernel_array, array)
    a1 = right_shift(kernel_array, shift)
    print(shift)
    # print(find_shift(a1,a2))

    return a1


if __name__ == "__main__":
    a = np.zeros((5))

    a += 1

    a = left_pad(a, 2)

    a = right_pad(a, 3)

    b = np.array((1., 2., 3., 4., 5.))

    a1 = right_pad(a, 2)
    a2 = left_pad(a, 3)

    # print(b)
    # print(a1)
    # #
    # left,right = convolve(b,a1)
    #
    # print(left)
    # print(right)
    # print(np.convolve(a2,a1))

    # print(a2)
    # print(a1)
    #
    # a2 = auto_shift(a2, a1)
    # print(a2)
