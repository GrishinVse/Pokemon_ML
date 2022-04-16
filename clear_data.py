"""
Программа уменьшает размеры исходных изображений до размера target_size с помощью бибилиотеки OpenCV.
Также происходит конвертация всех используемых форматов в формат jpg
Используемые форматы: jpg jpeg png
"""
from importlib.resources import path
import os
import cv2
import time
import random

start_time = time.time()

main_dir = 'D:/CourseWork/project/dataset/'
target_dir = 'D:/CourseWork/project/clear_dataset/'
tagret_size = 200
max_number_of_pictures = 50

"""
main_dir - исходная директория
target_dir - конечная директория
P.S. пути абсолютны
tagret_size - ширина и высота исходного изображения
max_number_of_pictures - максимальное количество картинок в каждом классе
"""
def resize_clear(main_dir, target_dir, tagret_size, max_number_of_pictures):

    # Название исходной и конечных папок
    repl_old = main_dir.split('/')[-2]
    repl_new = target_dir.split('/')[-2]

    # Если директории конечной нет, то мы её создаем
    if not os.path.exists(target_dir):
        print("Создаем директорию : " + target_dir)
        os.mkdir(target_dir)

    dirs = os.listdir(main_dir)

    # Список всех исходных папок
    dirpath = [main_dir + dirname + '/' for dirname in dirs]

    for i in range(len(dirpath)):
        loc_dirpath = dirpath[i]
        
        target_dirpath = loc_dirpath.replace(repl_old, repl_new)
        
        # Проверка на существование директории
        if not os.path.exists(target_dirpath):
            os.mkdir(target_dirpath)

        # Печатаем папку в которой работаем
        print(loc_dirpath)

        # Выбор форматов файлов
        files = [file for file in os.listdir(loc_dirpath) if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"))]
        file_paths = [loc_dirpath + file for file in files]

        print("Кол-во файлов в категории = ", len(file_paths))
        if len(file_paths) <= max_number_of_pictures:
            final_file_paths = file_paths
        else:
            final_file_paths = random.sample(file_paths, max_number_of_pictures)

        for file_path in final_file_paths:
            #print(file_path.replace(repl_old, repl_new).replace(file_path.split(".")[1], "jpg"))
            #print(not file_path.endswith(".jpg"))
            #break
            # Читаем изображение
            src = cv2.imread(file_path)
            # Изменяем размер
            output = cv2.resize(src, (tagret_size, tagret_size))
            # Меняем формат всех изображений на JPG
            if not file_path.endswith(".jpg") :
                # Записываем в новую папку файл в формате JPG
                cv2.imwrite(file_path.replace(repl_old, repl_new).replace(file_path.split(".")[1], "jpg"), output, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            else:
                # Записываем в новую папку
                cv2.imwrite(file_path.replace(repl_old, repl_new), output)

resize_clear(main_dir, target_dir, tagret_size, max_number_of_pictures)

print("--- {} seconds ---".format(time.time() - start_time))