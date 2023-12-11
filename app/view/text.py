import sys
from PyQt5 import QtWidgets, uic


def main():
    app = QtWidgets.QApplication(sys.argv)
    # 从当前目录加载UI文件
    ui_path = 

    record_module_widget = main_window.findChild(QtWidgets.QWidget, 'record_module')
    record_module_widget.show()  # 确保 record_module 是可见的
    # 显示主窗口
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
