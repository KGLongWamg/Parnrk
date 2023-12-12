# coding:utf-8
from PyQt5 import QtWidgets, uic
import sys
import os
import asyncio
import json
from PyQt5.QtCore import Qt, QSize,QThread,pyqtSlot,pyqtSignal,QObject
from PyQt5.QtWidgets import QAction, QWidget, QVBoxLayout, QButtonGroup,QHBoxLayout,QGraphicsView,QCompleter,QGraphicsScene,QGraphicsTextItem,QGraphicsPixmapItem
from qfluentwidgets import (Action, DropDownPushButton, DropDownToolButton, PushButton, ToolButton, PrimaryPushButton,
                            HyperlinkButton, ComboBox, RadioButton, CheckBox, Slider, SwitchButton, EditableComboBox,
                            ToggleButton, RoundMenu, FluentIcon, SplitPushButton, SplitToolButton, PrimarySplitToolButton,
                            PrimarySplitPushButton, PrimaryDropDownPushButton, PrimaryToolButton, PrimaryDropDownToolButton,
                            ToggleToolButton, TransparentDropDownPushButton, TransparentPushButton, TransparentToggleToolButton,
                            TransparentTogglePushButton, TransparentDropDownToolButton, TransparentToolButton,
                            PillPushButton, PillToolButton,FlowLayout,SearchLineEdit)
from PyQt5.QtGui import QFont,QPixmap

from .Parnrk.model.api_client_manager import APIClient
from .Parnrk.utils.Singleton import wllp,Thread
from .Parnrk import subscription
from .Parnrk.utils.utils import get_versions,convert_time_to_string

from .gallery_interface import GalleryInterface
from ..common.translator import Translator

from .Parnrk import subscription

async def create_client():
    return APIClient("http://122.51.220.10:5000")



class Worker(QObject):
    finished = pyqtSignal()  # 如果需要，可以添加更多信号
    print("类创建了")
    def run(self):
        print("开始1")
        # 为当前线程创建并设置新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("开始2")
        # 在新的事件循环中运行异步任务
        loop.run_until_complete(self.async_task())
        loop.close()

    async def async_task(self):
        print("开始3")
        future = asyncio.run_coroutine_threadsafe(wllp.get_instance(), loop=Thread)
        result = future.result()
        print("开始4") 
        while True:
            subscription.GameSessionManager().control_event_1.clear()
            print("开始5")
            future = asyncio.run_coroutine_threadsafe(subscription.start_subscription(),loop=Thread)
            future = asyncio.run_coroutine_threadsafe(subscription.GameSessionManager().control_event_1.wait(), loop=Thread)

            print("开始6")
            result = future.result()
            print("开始7")
            # 发出信号，例如更新UI等
            self.finished.emit()
            print("开始8")

class PlayerStats:
    all_player_stats = []  # 类属性，用于存储所有玩家的统计数据
    def add_player_data(self, puuid, champion_image_paths,kda_and_win):
        player_data = {
            puuid: {
                "champion_image_paths":champion_image_paths,
                "kda_and_win": kda_and_win,
                "current_pages":0
            }
        }
        self.all_player_stats.append(player_data)
    def set_page(self, puuid, page):
        for player_data in self.all_player_stats:
            if puuid in player_data:
                player_data[puuid]["current_pages"] = page
                break  # 停止遍历，因为已经找到并修改了目标数据
    def stats_pages_restart(self):
        self.all_player_stats= []

player_stats_instance =  PlayerStats()
class BasicInputInterface(GalleryInterface):
    """ Basic input interface """

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
        file_path = os.path.join(b, 'Parnrk', 'champion_images', 'champion_key_name_dict.json')
        #file_path = '.Parnrk/champion_images/champion_key_name_dict.json'
        # 读取JSON文件并将其内容转换为Python字典
        with open(file_path, 'r', encoding='utf-8') as file:
            self.key_name_dict = json.load(file)

        ui_path = os.path.join(b, "player_info.ui")
        self.record = uic.loadUi(ui_path)
        self.addExampleCard("对局战绩", self.record.record_module,"1",stretch=1) 

        for i in range(10):
            setattr(self, f'scene_info{i}', QGraphicsScene())
            setattr(self, f'scene_record{i}', QGraphicsScene())

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.update_player_stats)
        self.thread.started.connect(self.worker.run)

        self.thread.start()

    @pyqtSlot()
    def update_player_stats(self):
        print("进入槽函数")
        # 清除旧的场景内容
        player_data = subscription.GameSessionManager._instance.player_data
        for i, (puuid, data) in enumerate(player_data.items()):
            getattr(self, f'scene_info{i}').clear()
            getattr(self, f'scene_record{i}').clear()

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
                scene_info = getattr(self, f'scene_info{i}')
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

                info = getattr(self.record, f'info{i}')
                info.setScene(scene_info)

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
                        championName = self.key_name_dict[championId_str]
                        champion_image_paths.append(f"Resources/champion_images/{championName}.png")
                        stats = participants['stats']
                        kills = stats['kills']
                        deaths = stats['deaths']
                        assists = stats['assists']
                        win = "胜利" if stats['win'] else "失败"
                        text_color = '#00CC00' if win == "胜利" else '#FF0000'
                        KDA_win = f"{kills}/{deaths}/{assists}\t{win} {gameDate}"
                        KDA_and_win.append({"text": KDA_win, "color": text_color})
            except Exception as e:
                print(f"An error occurred4: {e}")

            player_stats_instance.add_player_data(puuid, champion_image_paths,KDA_and_win)
            #
            self.display_images(getattr(self, f'scene_record{i}'),0, champion_image_paths, 1)
            self.display_images(getattr(self, f'scene_record{i}'),0, KDA_and_win, 2)

            record = getattr(self.record, f'record{i}')
            record.setScene(getattr(self, f'scene_record{i}'))


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
    def display_images(self, scene, page,contexts, a):
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

