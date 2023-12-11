import json
import asyncio

from ..utils.utils import get_api
from ..utils.Singleton import wllp,Thread
#获取用户的输入设置，如键盘和鼠标配置
async def get_PutSettings():
    result = await (await wllp.get_instance()).request("get", "/lol-settings/v2/account/GamePreferences/input-settings")
    result = await result.json()
    return result

#获取用户的游戏设置，如图形和音效配置
async def get_GameSettings():
    result = await (await wllp.get_instance()).request("get", "/lol-game-settings/v1/game-settings")
    result = await result.json()
    return result

#获取用户的本地音频设置
async def get_AudioSettings():
    result = await (await wllp.get_instance()).request("get", "/lol-settings/v1/local/lol-audio")
    result = await result.json()
    return result


#获得界面设置
async def get_V2_GameSettings():
    result = await (await wllp.get_instance()).request("get", "/lol-settings/v2/account/GamePreferences/game-settings")
    result = await result.json()
    return result

#获得当前设置
async def settings_store():
    game_events_settings = json.dumps(await get_PutSettings())
    hud_settings =    json.dumps(await get_GameSettings())
    audio_settings = json.dumps(await get_AudioSettings())
    v2_game_events_settings =  json.dumps(await get_V2_GameSettings())
    
    return game_events_settings,hud_settings,audio_settings,v2_game_events_settings

#一键更改客户端设置
async def settings_change(game_events_settings, hud_settings, audio_settings,v2_game_events_settings):
    resepose1 = await (await wllp.get_instance()).request("patch", "/lol-settings/v2/account/GamePreferences/input-settings",
                       data=game_events_settings)
    
    resepose2 = await (await wllp.get_instance()).request("patch", "/lol-game-settings/v1/game-settings", data=hud_settings)
    resepose3 = await (await wllp.get_instance()).request("patch", "/lol-settings/v1/local/lol-audio", data=audio_settings)

    resepose3 = await (await wllp.get_instance()).request("patch", "/lol-settings/v2/account/GamePreferences/game-settings",data=v2_game_events_settings)


    






















