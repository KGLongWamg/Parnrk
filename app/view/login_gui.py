import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from .uic_login import Ui_Form  # 导入生成的UI类
from .uic_register import Ui_Form as Ui_Form2
from PyQt5.QtCore import pyqtSignal,QThread

import asyncio
import io
from PIL import Image, ImageTk
import base64
from .Parnrk.model.api_client_manager import APIClient,base_url
from .Parnrk.utils.Singleton import Thread
import tempfile

from .main_window import MainWindow

#创建客户端
async def create_client():
    return APIClient("http://122.51.220.10:5000")
future = asyncio.run_coroutine_threadsafe(create_client(), loop=Thread)
client = future.result(timeout=2)

class FormManager(QtWidgets.QWidget):
    # 定义信号，用于切换登录和注册界面
    #show_login_form_signal = pyqtSignal()
    #show_register_form_signal = pyqtSignal()
    #show_main_form_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # 创建登录和注册界面的实例
        self.login_form = MyLoginForm()
        self.register_form = MyRegisterForm()
        #self.main_form = MainWindow()
        #self.main_form.hide()
        # 将信号连接到相应的槽函数

        self.login_form.show_register_form_signal.connect(self.show_register_form)
        self.register_form.show_login_form_signal.connect(self.show_login_form)
        #self.register_form.show_main_form_signal.connect(self.show_main_form)

        # 默认显示登录界面
        self.show_login_form()

    def show_login_form(self):
        # 显示登录界面并隐藏注册界面
        self.login_form.show()
        self.register_form.hide()

    def show_register_form(self):
        # 显示注册界面并隐藏登录界面
        self.register_form.show()
        self.login_form.hide()

class MyLoginForm(QtWidgets.QWidget, Ui_Form, Ui_Form2):
    show_register_form_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.login_button.clicked.connect(self.on_login_button_clicked)
        self.register_button.clicked.connect(self.show_register_form_signal.emit)

        self.session_cookie = client._instance.cookies
        if self.session_cookie:
            try:
                future = asyncio.run_coroutine_threadsafe(client.user_info(), loop=Thread)
                result = future.result(timeout=2)
                data = result.get("data")
                if data:
                    username = data["username"]
                    uid = data["uid"]
                    self.hide()
                    main_form = MainWindow()
                    main_form.username = username
                    main_form.uid = uid
            except Exception as e:
                QMessageBox.information(self, "登录过期", "登录信息过期，请重新登录")
    def on_login_button_clicked(self):
        username = self.uesrname_lineedit.text()
        password = self.password_lineedit.text()
        captcha = self.captcha_lineedit.text() or None

        future1 = asyncio.run_coroutine_threadsafe(APIClient(base_url).login(username, password, captcha), loop=Thread)
        response1 = future1.result(timeout=2)
        if response1.get('status') == 200:
            QMessageBox.information(self, "登录成功", "登录成功！")
            self.hide()
            main_form = MainWindow()
        else:
            failed_attempts = response1.get('failed_attempts')
            if failed_attempts >= 8:
                future2 = asyncio.run_coroutine_threadsafe(APIClient(base_url).get_captcha(), loop=Thread)
                response2 = future2.result(timeout=2)
                response_data = response2['image']
                base64_data = response_data.split(',')[1]
                image_data = base64.b64decode(base64_data)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
                    temp_image_file.write(image_data)
                    temp_image_path = temp_image_file.name

                pixmap = QPixmap(temp_image_path)
                captcha_Label.setPixmap(pixmap)
            print(response1)
            QMessageBox.information(self, "info", response1.get('message'))

class MyRegisterForm(QtWidgets.QWidget, Ui_Form2):
    show_login_form_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.register_button.clicked.connect(self.on_register_button_clicked)
        self.login_button.clicked.connect(self.show_login_form_signal.emit)

    def on_register_button_clicked(self):
        username = self.uesrname_lineedit.text()
        password = self.password_lineedit.text()
        verify_password = self.verify_password_lineedit.text()
        security_question = self.security_question_lineedit.text()
        security_answer = self.security_answer_lineedit.text()
        if password != verify_password:
            QMessageBox.warning(self, "密码不匹配", "两次输入的密码不相同，请重新输入。")
        future = asyncio.run_coroutine_threadsafe(APIClient(base_url).register(username, password, security_question, security_answer), loop=Thread)
        response = future.result(timeout=2)
        if response.get('status') == 200:
            QMessageBox.information(self, "注册成功", "您已成功注册。")
            self.show_login_form_signal.emit()
        else:
            QMessageBox.warning(self, "注册失败", response.get('message'))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form_manager = FormManager()
    sys.exit(app.exec_())