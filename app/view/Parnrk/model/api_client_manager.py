import aiohttp
import asyncio
import json
import winreg as reg

from tenacity import retry, stop_after_attempt, wait_fixed

class APIClient:
    _instance = None  # Class level instance variable

    def __new__(cls, base_url):
        if cls._instance is None:
            cls._instance = super(APIClient, cls).__new__(cls)
            # 这里的初始化只会执行一次
            cls._instance.base_url = base_url
            cls._instance.session = aiohttp.ClientSession()
            try:
                saved_cookies = cls._instance.get_reg('session')  # 修正这行代码
                if saved_cookies:
                    # 如果有保存的cookie，将它加入到会话的cookie jar中
                    cls._instance.session.cookie_jar.update_cookies({'session': saved_cookies})
                cls._instance.cookies = saved_cookies
            except Exception as e:  # 捕获任何异常
                print(f"Failed to read cookies from registry: {e}")
                # 如果需要，您可以在这里设置cls._instance.cookies为None或者其他默认值
                
                cls._instance.cookies = None
    
        return cls._instance
    
    def set_reg(self,name, value):
        try:
            reg_key_path = "Software\\Parnrk"
            registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, reg_key_path)  # 确保键存在，如果不存在，将创建它
            reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, value)
            reg.CloseKey(registry_key)
            return True
        except Exception as e:  # 更广泛的异常捕获
            print(f"Failed to write to registry: {e}")  # 打印错误信息
            return False
            
    def get_reg(self, name):
        try:
            # 尝试打开注册表项
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\\Parnrk", 0, reg.KEY_READ)
            value, regtype = reg.QueryValueEx(registry_key, name)
            reg.CloseKey(registry_key)
            return value
        except FileNotFoundError:
            # 如果键不存在，则尝试创建键
            try:
                registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, "Software\\Parnrk")
                reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, "")  # 设置空字符串为默认值
                reg.CloseKey(registry_key)
                return ""
            except Exception as e:
                print(f"Failed to create registry key 'Software\\Parnrk': {e}")
                return None
        except Exception as e:
            print(f"Failed to read from registry: {e}")
            return None
    

    async def close(self):
        await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_data(self, path):
        async with self.session.get(f'{self.base_url}{path}') as response:
            try:
                return await response.json()
            except ValueError:
                # 如果无法解析为JSON，返回文本内容
                return await response.text()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def send_post(self, path, data):
        async with self.session.post(f'{self.base_url}{path}', json=data) as response:
            try:
                return await response.json()
            except ValueError:
                # 如果无法解析为JSON，返回文本内容
                return await response.text()

    async def can_login(self):
        return await self.get_data('/can_login')

    #注册
    async def register(self, username, password, security_question, security_answer):
        data = {
            "username": username,
            "password": password,
            "security_question": security_question,
            "security_answer": security_answer
        }
        return (await self.send_post('/register', data))

    #重置密码
    async def reset_password(self, username, security_question, security_answer, new_password):
        data = {
            "username": username,
            "security_question": security_question,
            "security_answer": security_answer,
            "new_password": new_password
        }
        return await self.send_post('/reset_password', data)

    #登录  如果成功读取cookie并保存在环境变量  因为这个本身没有cookie，所以不使用cookie
    async def login(self, username, password, captcha):
        data = {"username": username, "password": password ,"captcha": captcha}
        async with self.session.post(f'{self.base_url}/login', json=data) as response:
            if response.status == 200:
                #cookies = self._instance.session.cookie_jar.filter_cookies(self.base_url)
                #session_cookie = cookies.get('session')
                #print(f"response.headers:{session_cookie}")
                if 'Set-Cookie' in response.headers:
                    session_cookie_str = response.headers['Set-Cookie']

                    print("Original Set-Cookie Header:", session_cookie_str)

                    # 从 Set-Cookie 字符串中提取 session 的值

                    for cookie_part in session_cookie_str.split(';'):

                        if cookie_part.strip().startswith('session='):

                            session_cookie = cookie_part.split('=', 1)[1].strip()

                            break
                if session_cookie:
          
                    self._instance.cookies = session_cookie 
                    self._instance.session.cookie_jar.update_cookies({'session': session_cookie})
                    # 调用 set_reg 并返回它的返回值
                    result = self.set_reg('session', session_cookie)
                    return {"message": "登录成功", "status": 200} if result else{"message": "保存cookie失败", "status": 400}
            return await response.json() 

    async def user_info(self):
        return await self.get_data('/user_info')

    #获取新公告内容，
    async def get_new_messages(self):
        return await self.get_data('/message/get')

    #确认公告内容，让下次不再出现
    async def confirm_messages(self):
        return await self.get_data('/message/confirm')

    #获取存储设置
    async def get_settings(self):
        return await self.get_data('/settings/get')

    #上传三个设置
    async def update_settings(self, game_events_settings, hud_settings, audio_settings,v2_game_events_settings):
        settings = {
            'game_events_settings': game_events_settings,
            'hud_settings': hud_settings,
            'audio_settings': audio_settings,
            'v2_game_events_settings':v2_game_events_settings
        }
        return await self.send_post('/settings/update', settings)

    #次端点用于提交一个puuid 管理员使用 ，后续要对此api使用加验证         未确认
    async def update_cheating_record(self, puuid, new_evidence_url, new_cheat_type, new_sub_type):
        data = {
            "puuid": puuid,
            "new_evidence_url": new_evidence_url,
            "new_cheat_type": new_cheat_type,
            "new_sub_type": new_sub_type
        }
        return await self.send_post('/cheating/records', data)
       #new_sub_type 'hack': ['脚本', 'AI', '透视'] 'teamplay': ['演员', '导演', '导演/演员'],
       # "new_cheat_type": 外挂  /  剧组,

    # 从puuid表中查询某个puuid，用于查询某人是什么类型
    async def get_cheating_record_by_puuid(self, puuid):
        return await self.get_data(f'/cheating/records/{puuid}')

    async def post_red(self, puuid, type_, reason, evidence_url):
        data = {
            "puuid": puuid,
            "type": type_,
            "reason": reason,
            "evidence_url": evidence_url
        }
        return await self.send_post('/puuid/red', data)

    #这个是笔记人员端点  逻辑是从笔记搜索puuid，然后当前大区看是否有该人，然后遍历gameId进行举报，这里gameId打乱顺序
    async def report_tracking(self, puuid,gameId):
        data = {
            "puuid": puuid,
            "gameId": gameId,
        }
        return await self.send_post('/report/tracking', data)

    #上传信息到 奇怪的通道
    async def post_passage(self, gameId, puuid, sub_type,evidence_url):

        data = {
            "gameId": gameId,
            "puuid": puuid,
            "sub_type":sub_type,
            "evidence_url": evidence_url
        }
        return await self.send_post('/passage', data)

    async def get_passage(self, gameId):
        return await self.get_data(f'/passage/{gameId}')

    async def get_captcha(self):
        return await self.get_data('/get_captcha')

    async def authorization(self,puuid):
        data = {"puuid": puuid}
        return await self.send_post('/authorization',data)

    async def add_authorization(self,puuid):
        data = {"puuid": puuid}
        return await self.send_post('/authorization/post',data)

base_url = "http://122.51.220.10:5000"


































