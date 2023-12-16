import json
import asyncio
import logging
import aiohttp 
import threading
import re

from .utils.Singleton import wllp
from .model.api_client_manager import APIClient
from . import summoner_data_fetcher

from .model.lol_session_manager import names_get_puuid

async def default_message_handler(data):
	#print(data['eventType'] + ' ' + data['uri'])
	pass


#an event message handler takes data (which is the content of the message)
async def printing_listener(data):
	#let's just print everything we receive into this handler
	#print(json.dumps(data, indent=4, sort_keys=True))
	pass

#游戏自动接受类
class AutoGameSessionController:
	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(AutoGameSessionController, cls).__new__(cls)
			# 初始化实例变量
			cls._instance.auto_accept_control = 0
			cls._instance.initialized = True
		return cls._instance

	@classmethod
	def reset_instance(cls):
		"""重置单例实例"""
		if cls._instance is not None:
			cls._instance = None

	async def accept_game_automatically(self,data):
		if self.auto_accept_contorl == 1:
			# 检查data是否存在且其中有"data"键
			if data and "data" in data:
				inner_data = data["data"]
				# 检查inner_data是否存在且其中有"state"键
				if inner_data and "state" in inner_data:
					state = inner_data.get("state")
					if state == "InProgress":
						await (await wllp.get_instance()).request("POST", "/lol-matchmaking/v1/ready-check/accept",
																  data={})

#这个修改为，只查询隐私设置是公开的，和使用Parnrk的人的战绩
class GameSessionManager:
	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(GameSessionManager, cls).__new__(cls)
		return cls._instance

	def __init__(self):
		if not hasattr(self, 'initialized'):
			self.client = APIClient('http://122.51.220.10:5000')  # 初始化和API交互的客户端

			self.player_data = {}  # 使用字典来存储玩家信息和排名历史 以及是否是作弊玩家
			self.cheating_players = {}  # 存储作弊玩家信息

			self.processed_sessions = set()  # 放gameId 防止重复查询当前

			self.initialized = True
			self.gameId = None					#从程序启动开始，这个软件会遇到很多新的gameID

			self._control = 0   #用于触发信号

			self.control_event_1 = asyncio.Event()
			self.control_event_2 = asyncio.Event()
			self.control_event_3 = asyncio.Event()

	@property
	def control(self):
		return self._control

	@control.setter
	def control(self, value):
		self._control = value


	async def handle_room_session(self, data):

		try:

			task = asyncio.current_task()
			print(f"当前任务: {task}")
			task_repr = str(task)


    # 使用正则表达式提取任务编号

			result = data["data"]
			phase = result["timer"]["phase"]
			if phase == "GAME_STARTING":
				match = re.search(r'Task-(\d+)', task_repr)
				match_int=int(match.group(1))
				print('match is ',match_int)
				if match_int%2==0:
					return 

				print('开始等待======================')
				await asyncio.sleep(20)

				async with aiohttp.ClientSession() as session:

					#游戏进入后在本地的这个端口和路径就会生成这个json文件
					async with session.get("https://localhost:2999/liveclientdata/allgamedata", ssl=False) as response:

						if response.status == 200:
							data = await response.json()
							allPlayers = data["allPlayers"]
							puuid_champion_mapping = {}   #十个puuid下面是英雄name

							all_tasks=[]
							for player in allPlayers:
								summoner_name = player["summonerName"]
								puuid_result = await names_get_puuid(summoner_name)
								puuid = puuid_result[0]["puuid"]
								#print('puuid is ',puuid)	
								champion_name = player["championName"]
								print('game start 英雄名字:',champion_name)
								if puuid in self.player_data:
									print('本来有champion_name')
									self.player_data[puuid]['champion_name'] = champion_name
								else:
									print('没有champion_name')
									self.player_data[puuid]={}
									self.player_data[puuid]['champion_name'] = champion_name
								print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
								for key, value in self.player_data.items():
									print(key)
								print('添加到puuid的set成功',champion_name)
								all_tasks.append(self.fetch_player_data(puuid))


								
							await asyncio.gather(*all_tasks)
							self.control_event_1.set()

						else:
							print(f"yes,Error {response.status}: {await response.text()}")
							return None
				



				#查询十个人战绩查询完成
			# 重置信息和作弊名单

			
			gameId = result["gameId"]
			print(gameId)
			current_thread = threading.current_thread()
			print('当前的线程iD====================',current_thread.ident)
			if gameId in self.processed_sessions:
				return
			
			print('==========================================================================================不然图标了手动停止【======================')
			self.processed_sessions.add(gameId)  # 添加到processed_sessions = set() 防止重复查询
			self.gameId = gameId
			print('I am already here')
			print('=============================================')
			print('=============================================')
			print('=============================================')
			self.cheating_players = {}  # 用于得到通道非本队的名单
			self.player_data = {}

			myTeam = result["myTeam"]
			self.player_data = {player["puuid"]: {} for player in myTeam}

			length = len(self.player_data)

			print(f"字典长度: {length}")
			print('first_time -----------player_data')

			for key, value in self.player_data.items():
				print(key, value)
			print('first_time -----------player_data')
			tasks = []
			for player in myTeam:	
				puuid = player["puuid"]
				print(puuid)
				# 创建协程对象，并加入到任务列表中
				tasks.append(self.fetch_player_data(puuid))

			# 并发执行所有任务
			print("准备执行任务1")
			await asyncio.gather(*tasks)
			print("任务完毕1")
			self.control_event_1.set()  #玩家信息收集结束
			print('==========================================================================================手动停止')
			#return
			#await self.post_allcrew_to_passage()
			#await asyncio.sleep(5)
			#await self.get_allcrew_from_passage(gameId)  # 留着以后白名单
			#self.control_event_2.set()  #作弊信息收集结束

			self.control = 1
		except Exception as e:
			print(f"An error occurred: {e}")
			# Optionally, re-raise the exception if you want it to propagate.
			raise

	
	


	
	async def fetch_player_data(self, puuid):
		# 并发获取玩家信息和排名历史
		try:
			player_info_task = summoner_data_fetcher.fetch_player_data(puuid)
			#这里查询puuid是否可用，是否在某个数据库，或者是否公开隐私设置，或者是否
			displayName, profileIconId, puuid, privacy = await summoner_data_fetcher.get_player_details(puuid)
			rank_history_task = summoner_data_fetcher.get_player_rank_history(puuid, 0, 50)

			#后面再加入授权过的puuid账号，先测试能跑起来
			#authorization = await authorization(puuid)
			if privacy == "PUBLIC": #or authorization:
				player_info, rank_history = await asyncio.gather(player_info_task, rank_history_task)
			else:
				player_info = await summoner_data_fetcher.fetch_player_data(puuid)
				rank_history =None
				print(player_info['displayName'],' 不让看战绩')
			print('player_info')
			print(player_info)
			if puuid not in self.player_data:
				self.player_data[puuid] = {}
				print('出问题了')
			# 将获取到的信息存储在字典中
			self.player_data[puuid]['player_info'] = player_info     #玩家上方框信息
			self.player_data[puuid]['rank_history'] = rank_history   #玩家下方框信息

		except Exception as e:
			print(f"奇怪的错误{e}")

	#这里改动为 白名单上传暂停，下个版本改，  先改为查询自己家的作弊成员，匿名显示
	async def post_allcrew_to_passage(self):
		puuids_list = list(self.player_data.keys())
		for puuid in puuids_list:
			response = await self.client.get_cheating_record_by_puuid(puuid)
			if response.get("status") == 200:
				data = response["data"]
				evidence_url = data['evidence_url']
				cheat_type = data['cheat_type']
				sub_type = data['sub_type']
				if 'cheating_info' not in self.player_data[puuid]:
					self.player_data[puuid]['cheating_info'] = {}
				# 更新作弊信息
				self.player_data[puuid]['cheating_info']['evidence_url'] = evidence_url
				self.player_data[puuid]['cheating_info']['cheat_type'] = cheat_type
				self.player_data[puuid]['cheating_info']['sub_type'] = sub_type

				print(f"{self.gameId}, {puuid}, {sub_type},{evidence_url}")
				#try:
					#result = await self.client.post_passage(self.gameId, puuid, sub_type,evidence_url)  # 上传到数据库
				#except Exception as e:
					#print(f"在这里发生错误: {e}")
				print("完成代码")   #测试是否成功完成
	#获取通道白名单
	async def get_allcrew_from_passage(self, gameId):
		response = await self.client.get_passage(gameId)
		if response.get("status") == 200:
			try:
				data = response["data"]
				for item in data:
					puuid = item['puuid']
					if puuid in self.player_data:
						continue
					sub_type = item['sub_type']
					evidence_url = item['evidence_url']
					# 更新作弊玩家信息
					self.cheating_players[puuid] = {
						'sub_type': sub_type,
						'evidence_url': evidence_url
					}
			except Exception as e:
				print(f"在处时发生错误: {e}")
			print("通道代码完成") 


async def start_subscription():
	wllp_get_instance = await wllp.get_instance()
	all_events_subscription = await wllp_get_instance.subscribe('OnJsonApiEvent',default_handler=default_message_handler)

	wllp_get_instance.subscription_filter_endpoint(all_events_subscription, '/lol-matchmaking/v1/ready-check', handler=AutoGameSessionController().accept_game_automatically)
	print('before /lol-champ-select/v1/session, handler=GameSessionManager().handle_room_session')
	wllp_get_instance.subscription_filter_endpoint(all_events_subscription, '/lol-champ-select/v1/session', handler=GameSessionManager().handle_room_session)
	print('after /lol-champ-select/v1/session, handler=GameSessionManager().handle_room_session')
	while True:
		await asyncio.sleep(10)

if __name__ == '__main__':
	try:
		asyncio.run(start_subscription())
	except KeyboardInterrupt:
		asyncio.run(wllp.close())




















