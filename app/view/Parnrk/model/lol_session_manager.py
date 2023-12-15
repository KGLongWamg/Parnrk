import asyncio
import json

from tenacity import retry, stop_after_attempt, wait_fixed

from ..utils.Singleton import wllp
from ..utils.utils import get_versions

# 玩家个人信息 包括头像ID 名字 puuid
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def player_info():
    summoner = await(await ((await wllp.get_instance()).request("GET", "/lol-summoner/v1/current-summoner"))).json()

    # 获取字典的所有内容
    puuid = summoner["puuid"]  # puuid
    accountId = summoner["accountId"]  # 账户ID
    summonerId = summoner["summonerId"]  # summoner ID

    displayName = summoner["displayName"]  # 名字

    profileIconId = summoner["profileIconId"]  # 头像ID
    privacy = summoner["privacy"]

    return displayName, profileIconId, puuid,privacy

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def player_info_puuid(puuid):
    summoner = await (
        await ((await wllp.get_instance()).request("GET", f"/lol-summoner/v2/summoners/puuid/{puuid}"))).json()

    profileIconId = summoner["profileIconId"]
    displayName = summoner["displayName"]
    puuid = summoner["puuid"]

    privacy = summoner["privacy"]
    #PRIVATE  PUBLIC
    return displayName, profileIconId, puuid,privacy


# 查列表名字的个人信息
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def names_get_puuid(data1):
    # data1 = ["忍着胜","重谱旧曲"]
    data1=[data1]
    summoner_datas = await (
        await ((await wllp.get_instance()).request("POST", "/lol-summoner/v2/summoners/names", data=data1))).json()

    return summoner_datas  # 两个player_info字典

# 查房间里的信息    里面还有 ban的过程 和秒退时间 最后更新 以及对面的情况
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def room_session():
    result = await (await ((await wllp.get_instance()).request("GET", "/lol-champ-select/v1/session"))).json()
    gameId = result["gameId"]
    myTeam = result["myTeam"]
    puuids =[]
    player_details =[]

    for player in myTeam:
        player_info = {
            "assignedPosition": player["assignedPosition"],
            "cellId": player["cellId"],
            "championId": player["championId"],
            "championPickIntent": player["championPickIntent"],
            "nameVisibilityType": player["nameVisibilityType"],
            "obfuscatedPuuid": player["obfuscatedPuuid"],
            "obfuscatedSummonerId": player["obfuscatedSummonerId"],
            "puuid": player["puuid"],
            "selectedSkinId": player["selectedSkinId"],
            "spell1Id": player["spell1Id"],
            "spell2Id": player["spell2Id"],
            "summonerId": player["summonerId"],
            "team": player["team"],
            "wardSkinId": player["wardSkinId"]
        }
        player_details.append(player_info)
        puuids.append(player["puuid"])

    return puuids

# 战绩
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def rank_history(puuid, a, b):
    session_data = await (await ((await wllp.get_instance()).request("GET",f"/lol-match-history/v1/products/lol/{puuid}/matches?begIndex={a}&endIndex={b}"))).json()
    # accountId= games["accountId"]   这个暂时不需要

    player_infos =[]
    if session_data.get("games"):
        games = session_data["games"]["games"]

        if games:
            for game in games:
                queueId = game["queueId"]
                if queueId == 420:
                    # gameId=game["gameId"]   暂时没有意义

                    gameCreationDate = game["gameCreationDate"]
                    participants = game["participants"]  # 获得KDA  和英雄ID  以及team
                    participantIdentities = game["participantIdentities"]  # 获得查询的这个人的信息 主要用于显示 summonerName

                    participant_data = {"participants": participants[0], "participantIdentities": participantIdentities[0],"gameCreationDate": gameCreationDate}

                    player_infos.append(participant_data)
                else:
                    continue
        return player_infos

# 用于房间信息的 player
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_player_info(puuid):

    displayName, profileIconId, puuid,privacy = await player_info_puuid(puuid)
    current_rank_data = await rank_date(puuid)

    if current_rank_data is not None:
        # 获得 段位 小段 点数
        current_tier, division, current_lp = current_rank_data
    else:
        current_tier = division = current_lp = "没有段位"

    player_data = {
        #"profileicon_data": profileicon_url,
        "displayName": displayName,
        "puuid": puuid,
        "current_tier": current_tier,
        "division": division,
        "current_lp": current_lp,
    }
    print(player_data)
    return player_data

# 通过PUUid查当前的单双rank分数
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def rank_date(puuid):
    session_data = await (
        await (await wllp.get_instance()).request("GET", f"/lol-ranked/v1/ranked-stats/{puuid}")).json()
    if "queues" in session_data:
        queues = session_data["queues"]
        for queue in queues:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                current_tier = queue["tier"]
                division = queue["division"]
                current_lp = queue["leaguePoints"]
                return current_tier, division, current_lp
    else:
        return None








