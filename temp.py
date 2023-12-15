async def handle_room_session(self, data):
		try:
			result = data["data"]
			phase = result["timer"]["phase"]
			if phase == "GAME_STARTING":
				print("获得---------------",phase,type(result))
				await asyncio.sleep(5)
				print('走到这里')
				async with aiohttp.ClientSession() as session:
					print('走到这里了')
					#游戏进入后在本地的这个端口和路径就会生成这个json文件
					async with session.get("https://localhost:2999/liveclientdata/allgamedata", ssl=False) as response:
						print('走到这里了么')
						print(response.status)
						if response.status == 200:
							data = await response.json()
							allPlayers = data["allPlayers"]
							puuid_champion_mapping = {}   #十个puuid下面是英雄name
							print('开始循环10个英雄')
							for player in allPlayers:
								summoner_name = player["summonerName"]
								puuid = (await names_get_puuid(summoner_name)[0]["puuid"])
								champion_name = player["championName"]
								puuid_champion_mapping[puuid] = champion_name

							return summoner_champion_mapping
						else:
							print(f"yes,Error {response.status}: {await response.text()}")
							return None
				
				
				all_tasks = []
				for puuid in puuid_champion_mapping:
					self.player_data[puuid]['champion_name'] = champion_name
					all_tasks.append(self.fetch_player_data(puuid))
					
				await asyncio.gather(*all_tasks)

				#查询十个人战绩查询完成
			# 重置信息和作弊名单
			gameId = result["gameId"]
			print(gameId)
			if gameId in self.processed_sessions:
				return
			self.processed_sessions.add(gameId)  # 添加到processed_sessions = set() 防止重复查询

			self.gameId = gameId

			self.cheating_players = {}  # 用于得到通道非本队的名单
			self.player_data = {}

			myTeam = result["myTeam"]
			self.player_data = {player["puuid"]: {} for player in myTeam}

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
			
			#await self.post_allcrew_to_passage()
			#await asyncio.sleep(5)
			#await self.get_allcrew_from_passage(gameId)   留着以后白名单
			self.control_event_2.set()  #作弊信息收集结束

			self.control = 1
		except Exception as e:
			print(f"An error occurred: {e}")
			# Optionally, re-raise the exception if you want it to propagate.
			raise