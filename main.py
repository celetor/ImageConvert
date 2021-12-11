# -*- coding: utf-8 -*-
# from PyQt5.QtCore import pyqtSlot
# pyinstaller --add-data "resource;resource" -F -w -i resource/connect.ico  xx.py
import sys, os
from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets

from need.MainUI import Ui_MainWindow
from need.ImageConvert import ImageConvert


class WorkThread(QThread):
    trigger = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.info = ''

        self.ImageConvertObj = ImageConvert()
        self.file_path = ''
        self.flag = False

    def log(self, text):
        self.info = text

    def set_info(self, file_path, flag):
        self.file_path = file_path
        self.flag = flag

    def clear(self):
        self.info = ''
        self.ImageConvertObj.clear()

    def convert_all(self, path, check):
        if os.path.isfile(path):
            if path.rsplit(".", 1)[1].lower() in self.ImageConvertObj.ext:
                self.ImageConvertObj.convert(path, check, self.log)
                self.trigger.emit(self.info, 0)
        else:
            self.ImageConvertObj.find_all_image(path)
            for img in self.ImageConvertObj.image_list:
                self.ImageConvertObj.convert(img, check, self.log)
                self.trigger.emit(self.info, 0)

    def run(self):
        self.convert_all(self.file_path, self.flag)
        self.trigger.emit('*' * 52 + '任务完成' + '*' * 52, 1)


class AppMainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(AppMainWin, self).__init__(parent)
        self.setupUi(self)
        self.signal_connect_slot()

    def signal_connect_slot(self):
        self.pushButton.clicked.connect(self.on_select_clicked_function)
        self.pushButton_2.clicked.connect(self.on_run_clicked_function)
        self.pushButton_3.clicked.connect(self.on_clear_clicked_function)

        self.work_thread = WorkThread()
        self.work_thread.trigger.connect(self.show_log)

    def on_select_clicked_function(self):
        # https://www.jianshu.com/p/2f9f4d467fc2
        if self.checkBox_2.isChecked():
            file_name = QtWidgets.QFileDialog.getExistingDirectory(self, "选取图片文件夹", "./")
        else:
            file_type = "图片文件(*.jpg;*.jpeg;*.png;*.bmp;*.heic;*.webp);;所有文件(*)"
            file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(self, "选取图片", './', file_type)

        file_name = file_name.replace('/', '\\')
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
        self.textEdit.append(text)
        if number == 1:
            self.checkBox.setEnabled(True)
            self.checkBox_2.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)

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
    window = AppMainWin()  # 类名,注意要和自己定义的类名一致。
    # window.setWindowIcon(QIcon(get_resource_path('./resource/connect.ico')))
    window.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resource", "connect.ico")))
    window.show()
    sys.exit(app.exec_())
