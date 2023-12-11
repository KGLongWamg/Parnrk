# coding:utf-8
from PyQt5 import QtWidgets, uic
import sys
import os
import asyncio
from PyQt5.QtCore import Qt, QSize,QThread,pyqtSlot,pyqtSignal,QObject
from PyQt5.QtWidgets import QAction, QWidget, QVBoxLayout, QButtonGroup,QHBoxLayout,QGraphicsView,QCompleter,QGraphicsScene
from qfluentwidgets import (Action, DropDownPushButton, DropDownToolButton, PushButton, ToolButton, PrimaryPushButton,
                            HyperlinkButton, ComboBox, RadioButton, CheckBox, Slider, SwitchButton, EditableComboBox,
                            ToggleButton, RoundMenu, FluentIcon, SplitPushButton, SplitToolButton, PrimarySplitToolButton,
                            PrimarySplitPushButton, PrimaryDropDownPushButton, PrimaryToolButton, PrimaryDropDownToolButton,
                            ToggleToolButton, TransparentDropDownPushButton, TransparentPushButton, TransparentToggleToolButton,
                            TransparentTogglePushButton, TransparentDropDownToolButton, TransparentToolButton,
                            PillPushButton, PillToolButton,FlowLayout,SearchLineEdit)

from Parnrk.model.api_client_manager import APIClient
from Parnrk.utils.Singleton import wllp,Thread
from Parnrk import subscription

from .gallery_interface import GalleryInterface
from ..common.translator import Translator

from Parnrk import subscription

async def create_client():
    return APIClient("http://122.51.220.10:5000")

class Worker(QObject):
    finished = pyqtSignal()  # 如果需要，可以添加更多信号

    def run(self):
        # 为当前线程创建并设置新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 在新的事件循环中运行异步任务
        loop.run_until_complete(self.async_task())
        loop.close()

    async def async_task(self):
        asyncio.run_coroutine_threadsafe(wllp.get_instance(), loop=Thread)
        while True:
            future = asyncio.run_coroutine_threadsafe(subscription.GameSessionManager().control_event_1.wait(), loop=Thread)
            result = future.result()
            # 发出信号，例如更新UI等
            self.finished.emit()

class BasicInputInterface(GalleryInterface):
    """ Basic input interface """
    player_data_updated = pyqtSignal()

    def __init__(self, parent=None):

        translator = Translator()
        super().__init__(
            title="对局功能",
            subtitle='对局功能',
            parent=parent
        )
        self.setObjectName('basicInputInterface1')

        a =os.path.abspath(__file__)
        b =os.path.dirname(a)
        ui_path = os.path.join(b, "player_info.ui")
        self.record = uic.loadUi(ui_path)
        self.addExampleCard("对局战绩", self.record.record_module,"1",stretch=1) 

        for i in range(10):
            setattr(self, f'scene_info{i}', QGraphicsScene())
            setattr(self, f'scene_record{i}', QGraphicsScene())

        self.thread = QThread()
        self.worker = Worker()
        #self.player_data_updated.connect(self.update_player_stats)
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.player_data_updated)
        self.thread.started.connect(self.worker.run)

        self.thread.start()


    #这个用Qthread 设置 在这个线程中wait，等待另一边的查询
    def run(self):
        asyncio.run_coroutine_threadsafe(create_client(), loop=Thread)
        while True:
            future = asyncio.run_coroutine_threadsafe(control_event_1.wait(), loop=Thread)
            result = future.result()
            self.player_data_updated.emit()

    @pyqtSlot()
    def update_player_stats(self):
        # 清除旧的场景内容
        player_data = subscription.GameSessionManager._instance.player_data
        for i, (puuid, data) in enumerate(player_data.items()):
            self.scene_info[i].clear()
            self.scene_record[i].clear()
            print("进入了玩家信息")
            try:
                # data 是每个玩家的信息字典
                #profileicon_path = data['player_info']["profileicon_data"]
                displayName = data['player_info']["displayName"]
                puuid = data['player_info']["puuid"]
                current_tier = data['player_info']["current_tier"]
                division = data['player_info']["division"]
                current_lp = data['player_info']["current_lp"]
                info_view = self.get_view('info',5)
                scene_info = self.scene_info[i]
                tier_ico_path =f"Resources/tier_icons/{current_tier}.png"
            except Exception as e:
                print(f"An error occurred2: {e}")
            try:
                #name
                textItem = QGraphicsTextItem(displayName)
                textItem.setFont(QFont("Arial", 13, QFont.Bold))
                textItem.setDefaultTextColor(Qt.black)
                textItem.setPos(50, 9)  # 设置文本位置
                scene_info.addItem(textItem)

                #段位图片
                pixmap = QPixmap(tier_ico_path)
                pixmapItem = QGraphicsPixmapItem(pixmap)
                pixmapItem.setPos(43, 18)  # 设置图片位置
                scene_info.addItem(pixmapItem)

                #小段细节
                textItem = QGraphicsTextItem(displayName)
                textItem.setFont(QFont("Arial", 13, QFont.Bold))
                textItem.setDefaultTextColor(Qt.black)
                textItem.setPos(50, 9)  # 设置文本位置
                self.record.info[i].setScene(self.scene_info[i])

                setScene(self.scene_record[i])
            except Exception as e:
                print(f"An error occurred3: {e}")
            try:
                rank_historys = data['rank_history']
                champion_image_paths = []
                KDA_and_win = []
                if rank_historys is not None:
                    for rank_history in rank_historys:
                        participantIdentities = rank_history['participantIdentities']
                        gameCreationDate = rank_history['gameCreationDate']
                        gameDate = convert_time_to_string(gameCreationDate)
                        participants = rank_history['participants']
                        championId = participants['championId']
                        championId_str = str(championId)
                        championName = key_name_dict[championId_str]
                        champion_image_paths.append(f"Resources/champion_images/{championName}.png")
                        stats = participants['stats']
                        kills = stats['kills']
                        deaths = stats['deaths']
                        assists = stats['assists']
                        win = "胜利" if stats['win'] else "失败"
                        text_color = '#00CC00' if win == "胜利" else '#FF0000'
                        KDA_win = f"{kills}/{deaths}/{assists}\t{win} {gameDate}"
                        KDA_and_win.append({"text": KDA_win, "color": text_color})

                player_stats_instance.add_player_data(puuid, champion_image_paths,KDA_and_win)
                #
                self.display_images(self.scene_record[i],0, champion_image_paths, 1)
                self.display_images(self.scene_record[i],0, KDA_and_win, 2)

                self.record.record[i].setScene(self.scene_record[i])
            except Exception as e:
                print(f"An error occurred4: {e}")

        texts = []
        for i, (puuid, data) in enumerate(player_data.items()):
            if 'cheating_info' in data:
                cheating_info = data['cheating_info']
                evidence_url = cheating_info['evidence_url']
                sub_type = cheating_info['sub_type']

                text = f"剧组:{sub_type} 证据地址：{evidence_url}"
                texts.append(text)
                
        cheating_scene = QGraphicsScene()
        combined_text = "\t".join(texts)
        text_item = QGraphicsTextItem(combined_text)
        text_item.setPos(10, 10)  # 设置文本位置

        # 将文本项添加到场景
        cheating_scene.addItem(text_item)
        self.record.cheating.setScene(cheating_scene)
                
    #创建带序列scene
    def get_view(self,name,n):
        infos = []
        for i in range(n):  # 假设部件的名字是从 info0 到 info4
            info_name = f'{name}{i}'
            infos.append(getattr(self.record, info_name))

        return infos

    #用于战绩绘图
    def display_images(self,scene, contexts, a):
        image_size = 35
        space_between = 7
        start_y = 3
        start_x = 3

        if contexts:
            for i, context in enumerate(contexts):
                x = start_x
                y = start_y + i * (image_size + space_between)

                if a == 1:
                    image_file = context
                    pixmap = QPixmap(image_file)
                    pixmapItem = QGraphicsPixmapItem(pixmap)
                    pixmapItem.setPos(x, y)
                    scene.addItem(pixmapItem)
                    
                elif a == 2:
                    textItem = QGraphicsTextItem(context["text"])
                    textItem.setDefaultTextColor(QColor(context["color"]))
                    textItem.setFont(QFont("Arial", 12, QFont.Bold))
                    textItem.setPos(x, y)
                    scene.addItem(textItem)

