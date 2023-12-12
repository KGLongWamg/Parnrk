from .model import lol_session_manager

# 用于查人信息
async def get_player_details(puuid = None):
    if puuid:
        displayName, profileIconId, puuid,privacy = await lol_session_manager.player_info_puuid(puuid)
        return displayName, profileIconId, puuid,privacy
    else:
        displayName, profileIconId, puuid,privacy = await lol_session_manager.player_info()
        return displayName, profileIconId, puuid,privacy

async def get_player_rank(puuid):
    current_tier, division, current_lp = await lol_session_manager.rank_date(puuid)
    return current_tier, division, current_lp

async def fetch_player_data(puuid):
    player_data = await lol_session_manager.get_player_info(puuid)
    # player_data = {
    #     "displayName": displayName,           # 玩家在游戏中显示的名字
    #     "puuid": puuid,                       # 玩家的唯一标识符
    #     "current_tier": current_tier,         # 玩家当前的段位
    #     "division": division,                 # 玩家在当前段位中的小段
    #     "current_lp": current_lp,             # 玩家在当前段位中的联赛积分
    # }
    
    return player_data

async def get_player_rank_history(puuid, a, b):
    #只有单双
    #participant_data = {"participants": participants[0], "participantIdentities": participantIdentities[0],"gameCreationDate": gameCreationDate}
    rank_history = await lol_session_manager.rank_history(puuid, a, b)
    return rank_history



