# -*- coding: utf-8 -*-
"""
Программа извлекает ключевые кадры из видеофайла и добавляет их в отдельную папку
"""
from importlib.resources import path
import os
from cv2 import cv2
import operator
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.signal import argrelextrema

"""Cглажевает данные, используя окно требуемого размера.

Этот метод основан на свертывании масштабированного окна с сигналом.
Сигнал готовится введением отраженных копий сигнала
(с размером окна) на обоих концах, чтобы минимизировать переходные части
в начале и конце выходного сигнала.

input:
    x: входной сигнал
    window_len: размеры масштабируемого окна
    window: тип окна 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
        плоское окно будет производить сглаживание скользящей средней.
output:
    сглаженный сигнал
"""
def smooth(x, window_len=13, window="hanning"):

    print(len(x), window_len)

    s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

    if window == "flat":  # скользящее среднее
        w = np.ones(window_len, "d")
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode="same")
    return y[window_len - 1 : -window_len + 1]


class Frame:
    """Класс для сохранения информации о кадре видео"""

    def __init__(self, id, diff):
        self.id = id
        self.diff = diff

    def __lt__(self, other):
        if self.id == other.id:
            return self.id < other.id
        return self.id < other.id

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.id == other.id and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == "__main__":
    print(sys.executable)

    # Установка фиксированных пороговых критериев
    USE_TOP_ORDER = False
    # Установка критериев локальных максимумов
    USE_LOCAL_MAXIMA = True
    # Количество лучших отсортированных кадров
    NUM_TOP_FRAMES = 30

    # Видео путь к исходному файлу
    videospath = "videos"
    videoname = "S1-E1.mp4"
    # Директория для хранения обработанных кадров
    dir = "D:\CourseWork\project\extract_result"
    res_path = dir + "\\" + videoname.split('.')[0] + "\\"
    if not os.path.exists(res_path):
        print("create directory : " + res_path)
        os.mkdir(res_path)


    # Размер окна сглаживания
    # Если ставить больше то будет меньше кадров и больше точность разделения на ключевые кадры
    len_window = int(100)

    print("target video : " + videospath + '\\'+ videoname)
    print("frame save directory: " + dir)
    
    # Путь к ролику для загрузки в библиотеку
    path_to_video = str(videospath + '\\'+ videoname)

    # Загружаем видео и вычисляем разницу между кадрами
    cap = cv2.VideoCapture(path_to_video)
    curr_frame = None
    prev_frame = None
    frame_diffs = []
    frames = []
    success, frame = cap.read()
    i = 0
    while success:
        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        if (curr_frame is not None and prev_frame is not None):
            diff = cv2.absdiff(curr_frame, prev_frame)
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            frames.append(frame)
        prev_frame = curr_frame
        i = i + 1
        success, frame = cap.read()
    cap.release()

    # Вычисление ключевых кадров
    keyframe_id_set = set()
    if USE_TOP_ORDER:
        # Отсортировать список по убыванию
        frames.sort(key=operator.attrgetter("diff"), reverse=True)
        for keyframe in frames[:NUM_TOP_FRAMES]:
            keyframe_id_set.add(keyframe.id)
    if USE_LOCAL_MAXIMA:
        print("Using Local Maxima")
        diff_array = np.array(frame_diffs)
        sm_diff_array = smooth(diff_array, len_window)
        frame_indexes = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]
        for i in frame_indexes:
            keyframe_id_set.add(frames[i - 1].id)

        # Создаем и сохраняем stem график в папку
        plt.figure(figsize=(40, 20))
        plt.locator_params(nbins=100)
        plt.stem(sm_diff_array)
        plt.savefig(res_path + "plot.png")

    # Сохраняем все ключевые кадры как изображение
    cap = cv2.VideoCapture(path_to_video)
    curr_frame = None
    keyframes = []
    success, frame = cap.read()
    idx = 0
    while success:
        if idx in keyframe_id_set:
            name = "keyframe_" + str(idx) + ".png"
            path_to_img = res_path + name            
            if not cv2.imwrite(path_to_img, frame):
                raise Exception("Could not write image")

            keyframe_id_set.remove(idx)
        idx = idx + 1
        success, frame = cap.read()
    cap.release()