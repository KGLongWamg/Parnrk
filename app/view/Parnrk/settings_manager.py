import asyncio
import json

from .utils.Singleton import wllp,Thread
from .model.api_client_manager import APIClient
from .model.lol_setting_manager  import settings_store,settings_change

client =None
async def create_client():
    return APIClient('http://122.51.220.10:5000') 

future = asyncio.run_coroutine_threadsafe(create_client(), loop=Thread)
client = future.result(timeout=2)

async def get_settings_store():
    #获取当前客户端设置
    game_events_settings,hud_settings,audio_settings,v2_game_events_settings = await settings_store()
    #储存在云服务器
    resepose = await client.update_settings(game_events_settings, hud_settings, audio_settings,v2_game_events_settings)
    if resepose.get("status") == 200:
        return True

async def post_settings_change():
    #获取云服务器设置
    result = await client.get_settings()
    if result.get("status") == 200:
        data = result["data"]
        game_events_settings = data["game_events_settings"]
        hud_settings = data["hud_settings"]
        audio_settings = data["audio_settings"]
        v2_game_events_settings = data["v2_game_events_settings"]
        game_events_settings = json.loads(game_events_settings)

        hud_settings = json.loads(hud_settings)

        audio_settings = json.loads(audio_settings)
        v2_game_events_settings = json.loads(v2_game_events_settings)
        #更改当前客户端设置
        await settings_change(game_events_settings, hud_settings, audio_settings,v2_game_events_settings)
        return True


















