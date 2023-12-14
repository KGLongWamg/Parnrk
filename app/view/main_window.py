# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen)
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .basic_input_interface import BasicInputInterface
from .icon_interface import IconInterface

from .setting_interface import SettingInterface

from ..common.config import SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.iconInterface = IconInterface(self)
        self.basicInputInterface = BasicInputInterface(self)

        self.settingInterface = SettingInterface(self)


        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.iconInterface, Icon.EMOJI_TAB_SYMBOLS, t.icons)
        #self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.basicInputInterface, FIF.CAFE,t.basicInput, pos)
 

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('uid', ':/gallery/images/shoko.png'),
            onClick=self.onSupport,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1300, 1080)
        self.setMinimumWidth(860)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('Parnrk -- Parnter Rank v0.7')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        w = MessageBox("欢迎使用Parnrk",
            '国服竞技环境变好从这里开始。如有侵权请联系B站KG龙王',
            self
        )
        w.yesButton.setText('不得不添加的按钮')
        w.cancelButton.setText('两个按钮一样的')
        if w.exec():
            pass
            #QDesktopServices.openUrl(QUrl(SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)
