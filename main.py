# -*- coding: utf-8 -*-
# from PyQt5.QtCore import pyqtSlot
# pyinstaller --add-data "resource;resource" -F -w -i resource/connect.ico  demo2.py

import sys
from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets

import os
from io import BytesIO

from PIL import Image
import pyheifx as pyheif
import whatimage

from need.sel import Ui_MainWindow


class ImageConvert():
    def __init__(self):
        self.ext = ['jpg', 'jpeg', 'png', 'bmp', 'heic', 'webp']
        self.image_list = []
        self.count = 0

    def _mkdir(self, path):
        _path = os.path.normpath(path)
        if not os.path.exists(_path):
            os.makedirs(_path)
        return _path

    def _find_image(self, sub_url):
        for dir_sub in os.listdir(sub_url):
            dir_sub = os.path.join(sub_url, dir_sub)
            if os.path.isfile(dir_sub):
                if dir_sub.rsplit(".", 1)[1].lower() in self.ext:
                    self.image_list.append(dir_sub)
            else:
                self._find_image(dir_sub)

    def find_all_image(self, sub_url):
        self.image_list = []
        self._find_image(sub_url)

    def convert(self, filepath, check, printf):
        with open(filepath, 'rb') as f:
            bytes_io = f.read()

        if check:
            new_path = filepath.rsplit(".", 1)[0] + '.jpg'
        else:
            father_path, file_name = os.path.split(filepath)
            save_dir = os.path.join(father_path, 'convert')
            self._mkdir(save_dir)
            new_path = os.path.join(save_dir, file_name.rsplit(".", 1)[0] + '.jpg')

        try:
            fmt = whatimage.identify_image(bytes_io)
            if fmt == 'jpeg':
                printf(f'{filepath}\t{fmt}图片跳过')
            elif fmt in ['bmp', 'png', 'webp']:
                if check:
                    os.remove(filepath)
                self.count += 1
                pi = Image.open(BytesIO(bytes_io))
                exif_data = pi.info.get('exif')
                exif_data = b'' if exif_data is None else exif_data
                pi = pi.convert("RGB")
                pi.save(new_path, format="jpeg", quality=100, exif=exif_data)
                printf(f'{self.count}\t{filepath}\t->\t{fmt} {new_path}')
            elif fmt in ['heic']:
                if check:
                    os.remove(filepath)
                self.count += 1
                heif_file = pyheif.read(bytes_io)
                exif_data = b''
                for metadata in heif_file.metadata:
                    if str(metadata['type']).lower() == 'exif':
                        exif_data = metadata['data']
                        break
                pi = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                # http://cn.voidcc.com/question/p-qzogslmj-ve.html
                pi.save(new_path, format="jpeg", quality=100, exif=exif_data)
                printf(f'{self.count}\t{filepath}\t->\t{fmt} {new_path}')
            else:
                printf(f'{filepath}\t{fmt}无法转换跳过')
        except Exception as e:
            printf(f'报错: {e}')

    def convert_all(self, file_path, flag, printf=print):
        if os.path.isfile(file_path):
            if file_path.rsplit(".", 1)[1].lower() in self.ext:
                self.convert(file_path, flag, printf)
        else:
            self.find_all_image(file_path)
            for img in self.image_list:
                self.convert(img, flag, printf)

    def clear(self):
        self.image_list = []
        self.count = 0


class work_thread(QThread):  # 线程2
    trigger = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.info = []

        self.ImageConvertObj = ImageConvert()
        self.file_path = ''
        self.flag = False

    def log(self, text):
        self.info.append(str(text))

    def set_info(self, file_path, flag):
        self.file_path = file_path
        self.flag = flag

    def clear(self):
        self.info = []
        self.ImageConvertObj.clear()

    def convert_all(self, path, check):
        if os.path.isfile(path):
            if path.rsplit(".", 1)[1].lower() in self.ImageConvertObj.ext:
                self.ImageConvertObj.convert(path, check, self.log)
                self.trigger.emit(self.info[-1], 0)
        else:
            self.ImageConvertObj.find_all_image(path)
            for img in self.ImageConvertObj.image_list:
                self.ImageConvertObj.convert(img, check, self.log)
                self.trigger.emit(self.info[-1], 0)

    def run(self):
        self.convert_all(self.file_path, self.flag)
        self.trigger.emit('', 1)


class AppMainWin(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(AppMainWin, self).__init__(parent)
        self.setupUi(self)
        self.signal_connect_slot()

    def signal_connect_slot(self):
        self.pushButton.clicked.connect(self.on_select_clicked_function)
        self.pushButton_2.clicked.connect(self.on_run_clicked_function)
        self.pushButton_3.clicked.connect(self.on_clear_clicked_function)

        self.work_thread = work_thread()
        self.work_thread.trigger.connect(self.show_log)

    def on_select_clicked_function(self):
        # https://www.jianshu.com/p/2f9f4d467fc2
        if self.checkBox_2.isChecked():
            file_name = QtWidgets.QFileDialog.getExistingDirectory(self, "选取图片文件夹", "./")
        else:
            file_type = "图片文件(*.jpg;*.jpeg;*.png;*.bmp;*.heic;*.webp);;所有文件(*)"
            file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(self, "选取图片", './', file_type)

        self.lineEdit.setText(file_name)
        # path = self.lineEdit.text()  # 文件路径

    def on_run_clicked_function(self):
        self.checkBox.setEnabled(False)
        self.checkBox_2.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        # 路径
        path = self.lineEdit.text()
        # 是否覆盖原图
        check = self.checkBox.isChecked()

        self.work_thread.set_info(path, check)
        self.work_thread.start()

    def show_log(self, text, number):
        if number == 1:
            self.checkBox.setEnabled(True)
            self.checkBox_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
        else:
            self.textEdit.append(text)

    def on_clear_clicked_function(self):
        self.work_thread.clear()
        self.textEdit.setText('')


# pyinstaller在onefile模式下对资源路径的定位
def get_resource_path(relative_path):  # 利用此函数实现资源路径的定位
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS  # 获取临时资源
    else:
        base_path = os.path.abspath(".")  # 获取当前路径
    return os.path.join(base_path, relative_path)  # 绝对路径


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWin()  ## 类名,注意要和自己定义的类名一致。
    #window.setWindowIcon(QIcon(get_resource_path('./resource/connect.ico')))
    window.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resource", "connect.ico")))  
    window.show()
    sys.exit(app.exec_())
