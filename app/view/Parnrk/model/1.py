from flask import Flask, request, session, jsonify, send_file
from flask_session import Session
import asyncio
import aiomysql
import logging
import winreg as reg
from redis import Redis
from werkzeug.security import generate_password_hash, check_password_hash
import random
import re
import tracemalloc
# flask交互的数据库导入
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
from PIL import Image, ImageDraw, ImageFont
import io
import random
import string
import base64

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class AsyncSQLAlchemyHelper:
    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = create_async_engine(
            self.database_url,
            echo=True,
            echo_pool='debug',
            pool_pre_ping=True,
            pool_size=20,  # 基础连接池大小
            max_overflow=10  # 超出基础大小时可创建的额外连接数
        )
        self.AsyncSession = sessionmaker(
            self.engine, expire_on_commit=True, class_=AsyncSession,
        )

    async def execute_single_query(self, query, params=None):
        async with self.AsyncSession() as session:
            try:
                print("Event loop is running:", asyncio.get_running_loop().is_running())
                result = await session.execute(text(query), params)
                await session.commit()  # 确保变更被提交
                return result.fetchone()
            except Exception as e:
                print(f"Error executing query: {e}")
                await session.rollback()  # 出错时回滚
                raise
            finally:
                print("Session is closing.")
                await self.engine.dispose()

    async def execute_multi_query(self, query, params=None):
        async with self.AsyncSession() as session:
            try:
                result = await session.execute(text(query), params)
                return result.fetchall()
            except Exception as e:
                print(f"Error executing query: {e}")
                await session.rollback()
                raise
            finally:
                print("Connection status after execute_multi_query:", session.is_active)
                await self.engine.dispose()

    async def execute_transaction(self, query, params=None):
        async with self.AsyncSession() as session:
            try:
                # 使用命名参数
                if params:
                    # 假设params是一个字典，键是SQL命名参数
                    result = await session.execute(text(query), params)
                else:
                    result = await session.execute(text(query))
                await session.commit()
                return result
            except Exception as e:
                print(e)
                await session.rollback()
                raise
            finally:
                print("Connection status after execute_multi_query:", session.is_active)
                await self.engine.dispose()


# 初始化异步SQLAlchemy帮助器
database_url = "mysql+aiomysql://root:lolpuuid450002!%40#@localhost:3306/parnrk"
lol2 = AsyncSQLAlchemyHelper(database_url)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KU0uCED8-SaMuDzHWGl5yir4lJfLTLrI'

app.config['SESSION_TYPE'] = 'redis'  # 指定 session 类型为 redis
app.config['SESSION_REDIS'] = Redis.from_url('redis://localhost:6379')  # 配置 redis 服务器地址

# 初始化 Flask-Session
Session(app)


# ====================
# 认证相关的路由
# ====================
@app.route('/can_login', methods=['GET'])
async def alter():
    query = "SELECT is_enabled,announcement from version where version = 0.6"
    try:
        result = await lol2.execute_single_query(query)
        if result[0] == 1:
            return jsonify({"message": result[0], "status": 200}), 200
        if result[0] != 1:
            return jsonify({"message": result[1], "status": 201}), 201
    except Exception as e:
        return jsonify({"message": str(e), "status": 500}), 500


@app.route('/register', methods=['POST'])
async def register_user():
    data = request.get_json()
    if data is None:
        return '数据不是JSON', 400

    lol2 = AsyncSQLAlchemyHelper(database_url)

    username = data.get('username')
    password = data.get('password')
    security_question = data.get('security_question')
    security_answer = data.get('security_answer')

    print(f'username: {username}, password: {password}')  # 打印请求的参数
    return await register(username, password, security_question, security_answer)


async def register(username, password, security_question, security_answer):
    # 检查用户名和密码是否符合要求
    if len(username) <= 7 or not re.search("[a-zA-Z]", username):
        return jsonify({"error": "用户名最少8位并且需要包含英文和数字", "status": 400}), 400
    if len(password) <= 7 or not re.search("[a-zA-Z]", password) or not re.search("[0-9]", password):
        return jsonify({"error": "密码最少8位数并且需要包含英文和数字", "status": 400}), 400

    hashed_password = generate_password_hash(password)

    # 检查用户名是否已存在
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = await lol2.execute_single_query(query)
    if result is not None:
        return jsonify({"error": "用户名已存在", "status": 400}), 400

    # 生成唯一的uid
    uid = random.randint(10000000, 99999999)
    query = f"SELECT * FROM users WHERE uid = {uid}"
    result = await lol2.execute_single_query(query)

    # 检查uid是否存在，直到生成不存在uid
    while result is not None:
        uid = random.randint(10000000, 99999999)
        query = f"SELECT * FROM users WHERE uid = {uid}"
        result = await lol2.execute_single_query(query)

    query = "INSERT INTO users (uid, username, password_hash, security_question, security_answer) VALUES (:uid, :username, :password_hash, :security_question, :security_answer)"
    params = {
        "uid": uid,
        "username": username,
        "password_hash": hashed_password,
        "security_question": security_question,
        "security_answer": security_answer
    }

    await lol2.execute_transaction(query, params)

    return jsonify({"message": f"注册成功,您的用户名为:{username}", "status": 200}), 200


@app.route('/user_info', methods=['GET'])
async def user_info():
    uid = session.get('user_id')
    if not uid:
        return '用户未登录', 401
    query = "SELECT username FROM users WHERE uid = :uid"
    params = {"uid": uid}
    result = await lol2.execute_single_query(query, params)
    username = result[0]
    if result:
        return jsonify({"message": "查询成功", "data": {"username": username, "uid": uid}, "status": 200}), 200
    else:
        return jsonify({"message": "未知错误", "status": 400}), 400


# 生成验证码二进制
def generate_captcha():
    # 生成随机验证码字符串
    letters = string.ascii_uppercase
    captcha_text = ''.join(random.choice(letters) for i in range(4))
    # 创建图像
    image = Image.new('RGB', (100, 50), color=(255, 255, 255))
    # 添加文字
    font = ImageFont.truetype("arial.ttf", 36)
    draw = ImageDraw.Draw(image)
    draw.text((10, 5), captcha_text, font=font, fill=(0, 0, 0))
    # 保存验证码值到会话
    session['captcha'] = captcha_text
    # 转换图像为二进制流
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


@app.route('/get_captcha')
def get_captcha():
    # 假设generate_captcha返回一个io.BytesIO对象
    captcha_io = generate_captcha()  # 获取验证码图像的二进制数据
    captcha_base64 = base64.b64encode(captcha_io.getvalue()).decode('utf-8')  # 将图像转换为Base64字符串
    return jsonify({'image': 'data:image/png;base64,' + captcha_base64, 'status': 200}), 200


@app.route('/login', methods=['POST'])
async def login():
    data = request.get_json()
    if data is None:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    username = data.get('username')
    password = data.get('password')
    user_captcha = data.get('captcha', None)

    # 检查登录失败次数
    failed_attempts = session.get('failed_attempts', 0)

    # 如果失败次数超过5次，需要检查验证码
    if failed_attempts >= 8:
        correct_captcha = session.get('captcha', '')
        if not user_captcha or user_captcha.lower() != correct_captcha.lower():
            return jsonify({"message": "需要验证码", "status": 400, "failed_attempts": session['failed_attempts']}), 400

            # 以下是原有的登录逻辑
    query = "SELECT password_hash, uid FROM users WHERE username = :username"
    params = {"username": username}
    result = await lol2.execute_single_query(query, params)
    if result is None:
        session['failed_attempts'] = failed_attempts + 1  # 增加失败次数
        return jsonify({"message": "用户名不存在", "status": 400, "failed_attempts": session['failed_attempts']}), 400

    stored_password_hash, uid = result
    if check_password_hash(stored_password_hash, password):
        session['user_id'] = uid
        session['failed_attempts'] = 0  # 重置失败次数

        return jsonify({"message": "登录成功", "status": 200}), 200
    else:
        session['failed_attempts'] = failed_attempts + 1  # 增加失败次数
        return jsonify({"message": "密码错误", "status": 400, "failed_attempts": session['failed_attempts']}), 400


@app.route('/reset_password', methods=['POST'])
async def reset_password():
    data = request.get_json()
    username = data.get('username')
    security_question = data.get('security_question')
    security_answer = data.get('security_answer')
    new_password = data.get('new_password')

    if len(new_password) <= 7 or not re.search("[a-zA-Z]", new_password) or not re.search("[0-9]", new_password):
        return jsonify({"message": "密码最少8位数并且需要包含英文和数字", "status": 400}), 400

    # 查询数据库以验证安全问题和答案
    query = "SELECT uid FROM users WHERE username = :username AND security_question =:security_question AND security_answer = :security_answer"
    params = {"username": username, "security_question": security_question, "security_answer": security_answer}
    result = await lol2.execute_single_query(query, params)

    if result:
        print('new_password')
        # 安全问题和答案匹配，更新密码
        new_password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = :new_password_hash WHERE username = :username"
        params = {"new_password_hash": new_password_hash, "username": username}  # 这里是参数的字典
        await lol2.execute_transaction(query, params)
        return jsonify({"message": "密码更改成功", "status": 200}), 200
    else:
        return jsonify({"message": "问题或者答案不对", "status": 401}), 401


# ====================
# 公告相关的路由  暂时不用
# ====================
@app.route('/message/get', methods=['GET'])
async def get_message():
    uid = session.get('user_id')
    if not uid:
        return '用户未登录', 401

    query = "SELECT message FROM message WHERE uid = :uid and new_message = 1"
    params = {"uid": uid}
    result = await lol2.execute_single_query(query, params)

    # 确保 result 以正确的格式处理
    messages = [row['message'] for row in result] if result else []
    return jsonify({"message": messages}), 200


# 确认公告下次不会再收到
@app.route('/message/confirm', methods=['GET'])
async def confirm_message():
    uid = session.get('user_id')
    if not uid:
        return '用户未登录', 401

    query = "UPDATE message SET new_message = 0 WHERE uid = :uid"
    params = {"uid": uid}
    await lol2.execute_transaction(query, params)

    return '确认成功', 200


# ====================
# 设置相关的路由
# ====================
@app.route('/settings/get', methods=['GET'])
async def get_setting():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录"}), 401

    query = f"SELECT game_events_settings, hud_settings, audio_settings,v2_game_events_settings FROM lol_settings WHERE uid = :uid"
    params = {"uid": uid}
    result = await lol2.execute_single_query(query, params)

    if result:
        settings = {
            "game_events_settings": result[0],
            "hud_settings": result[1],
            "audio_settings": result[2],
            "v2_game_events_settings": result[3]
        }

        return jsonify({"message": "成功获取", "data": settings, "status": 200}), 200
    else:
        return jsonify({"message": "设置未找到", "status": 404}), 404


@app.route('/settings/update', methods=['POST'])
async def update_setting():
    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    # 从 JSON 数据中获取各个设置项
    game_events_settings = data.get('game_events_settings')
    print(f'game_events_settings:{game_events_settings}')
    hud_settings = data.get('hud_settings')
    audio_settings = data.get('audio_settings')
    v2_game_events_settings = data.get('v2_game_events_settings')

    # 从会话中获取用户 ID
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    query = f"SELECT uid from lol_settings WHERE uid = :uid"
    params = {"uid": uid}
    result = await lol2.execute_single_query(query, params)
    if not result:
        query = (
            "INSERT INTO lol_settings (game_events_settings, hud_settings, audio_settings, v2_game_events_settings,uid) "
            "VALUES (:game_events_settings, :hud_settings, :audio_settings,:v2_game_events_settings, :uid)"
        )
        params = {
            "game_events_settings": game_events_settings,
            "hud_settings": hud_settings,
            "audio_settings": audio_settings,
            "v2_game_events_settings": v2_game_events_settings,
            "uid": uid
        }
        await lol2.execute_transaction(query, params)
    else:
        query = "UPDATE lol_settings SET game_events_settings = :game_events_settings, hud_settings = :hud_settings, audio_settings = :audio_settings, v2_game_events_settings = :v2_game_events_settings WHERE uid = :uid"
        params = {
            "game_events_settings": game_events_settings,
            "hud_settings": hud_settings,
            "audio_settings": audio_settings,
            "v2_game_events_settings": v2_game_events_settings,
            "uid": uid
        }
        print("Executing SQL Query:", query)
        print("With Parameters:", params)

    await lol2.execute_transaction(query, params)

    return jsonify({"message": "保存客户端设置成功", "status": 200}), 200


# ====================
# puuid 相关
# ====================
# 获取脚本 剧组 Ai 所有的puuid集合,用于主界面显示,可以直接点开证据的
@app.route('/puuid/getall', methods=['GET'])
async def get_all_puuid():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录"}), 401
    #
    query = "SELECT puuid,type,url from cheating_records "
    result = await lol2.execute_multi_query(query)


# 获取疑似剧组，按疑似度高低排序 这个是Parnrk查取疑似剧组
@app.route('/puuid/samecrew', methods=['GET'])
async def get_s():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录"}), 401

    puuid = data.get('game_events_settings')
    # cheating_records


# ====================
# 会否是完全类型剧组账号，是否可以解封
# ====================
@app.route('/puuid/typecheak', methods=['GET'])
async def cheak_puuid():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401
    # 先在客户端看有没有这个人,
    # 检查puuid是否存在剧组里，是剧组，是剧组的话是否是完全剧组类型，完全剧组类型不可解封。   偶尔剧组类型可解名单


# 交过保证金的转移表
@app.route('/puuid/promice', methods=['POST'])
async def baozheng_puuid():
    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    # 删除原有 crew 表,在新表插入 该puuid ，把旧的行提取过来 加一个缴纳时间，


# 用于删除误上名单
@app.route('/puuid/delete', methods=['Delete'])
async def delete_puuid():
    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    query = f"SELECT vip from users where uid = {uid}"
    result = lol2.execute_single_query()

    if not result:
        return jsonify({"message": "权限不足", "status": 402}), 402

    try:
        # 构造 SQL 语句
        query = "DELETE FROM users WHERE puuid = %s"
        # 执行事务
        await lol2.execute_transaction(query, (puuid,))
        return jsonify({"message": "删除成功"}), 200
    except Exception as e:
        # 如果出现错误，返回错误信息
        return jsonify({"message": "删除失败", "error": str(e)}), 500


# ====================
# passage通道
# ====================
# 通道 passage 查询数据库后 如果有 提交当前对局的 gameId和puuid
@app.route('/passage', methods=['POST'])
async def post_passage_puuid():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    gameId = data.get('gameId')
    puuid = data.get('puuid')
    if not gameId or not puuid:
        return jsonify({"message": "缺少gameId或puuid", "status": 200}), 200

    sub_type = data.get('sub_type')
    evidence_url = data.get('evidence_url')

    query = "INSERT INTO passage (gameId, puuid, sub_type, evidence_url) VALUES (:gameId, :puuid, :sub_type, :evidence_url)"
    await lol2.execute_transaction(query, {'gameId': gameId, 'puuid': puuid, 'sub_type': sub_type,
                                           'evidence_url': evidence_url})

    query = "SELECT * from passage where gameId =  :gameId and puuid = :puuid"
    pagrams = {'gameId': gameId, 'puuid': puuid}
    try:
        await lol2.execute_single_query(query, pagrams)
        return jsonify({"message": "上传成功", "status": 200}), 200
    except Exception as e:
        return jsonify({"message": "上传失败", "status": 400}), 400


# ====================
# passage通道
# ====================
# 通道 passage 获取是否有gameId的成员 ，获取它的puuid，和type  然后通过puuid API获得名字，
@app.route('/passage/<gameId>', methods=['GET'])
async def get_passage_info(gameId):
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    query = "SELECT puuid, sub_type,evidence_url FROM passage WHERE gameId = :gameId and gameId!=0"
    result = await lol2.execute_multi_query(query, {'gameId': gameId})

    # 检查查询结果
    if result:
        # 如果有结果，构建返回的 JSON 数据
        reports = [{"puuid": puuid, "sub_type": sub_type, "evidence_url": evidence_url} for
                   puuid, sub_type, evidence_url in result]
        return jsonify({"message": "同局对局有cheat_成员", "data": reports, "status": 200}), 200
    else:
        # 如果没有结果，返回相应消息
        return jsonify({"message": "没有找到与该 gameId 相关的信息", "status": 404}), 404


# ====================
# cheating_player
# ====================
# 提交puuid名单端点   #按名字列表提交 puuid 剧组，剧组类型，puuid所在大区, 保证只有自己能提交  where账号类型  = admin ，并且加一个字段，证据所在地址，上传到bilibili，蓝奏云之类
@app.route('/cheating/records', methods=['POST'])
async def post_puuid():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    # 权限查询
    sql = "SELECT admin from users where uid = :uid"
    param = {"uid": uid}
    respose = await lol2.execute_single_query(query, params)
    if respose != 1:
        return jsonify({"message": "权限不足", "status": 400}), 400

    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    puuid = data.get('puuid')
    new_evidence_url = data.get('new_evidence_url')
    new_cheat_type = data.get('new_cheat_type')
    new_sub_type = data.get('new_sub_type')
    evidence_url = data.get('evidence_url')

    query = """
        INSERT INTO cheating_records (puuid, evidence_url, cheat_type, sub_type,evidence_url)
        VALUES (:puuid, :evidence_url, :cheat_type, :sub_type,:evidence_url)
        ON DUPLICATE KEY UPDATE
        evidence_url = VALUES(evidence_url),
        cheat_type = VALUES(cheat_type),
        sub_type = VALUES(sub_type)
    """
    params = {
        'puuid': puuid,
        'evidence_url': new_evidence_url,
        'cheat_type': new_cheat_type,
        'sub_type': new_sub_type,
        'evidence_url': evidence_url
    }

    # 调用 execute_transaction 方法来执行更新
    await lol2.execute_transaction(query, params)

    sql = f"SELECT puuid, evidence_url, cheat_type, sub_type from cheating_records where puuid = :puuid"
    params = {
        'puuid': puuid,
    }
    result = await lol2.execute_single_query(query, params)
    if result:
        return jsonify({"message": result, "status": 200}), 200
    else:
        return jsonify({"message": "上传失败", "status": 400}), 400


# ====================
# cheating_player
# ====================
# 查看某puuid是否存在 存在的话是什么  用于查某人是否在名单里
@app.route('/cheating/records/<puuid>', methods=['GET'])
async def get_cheating_record(puuid):
    # 确认用户是否已经登录
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    # 构建SQL查询，获取除时间以外的所有字段
    query = """
        SELECT puuid, evidence_url, cheat_type, sub_type
        FROM cheating_records
        WHERE puuid = :puuid
    """
    params = {'puuid': puuid}

    # 执行查询
    result = await lol2.execute_single_query(query, params)
    if result:
        data = {
            "puuid": result[0],
            "evidence_url": result[1],
            "cheat_type": result[2],
            "sub_type": result[3]
        }
        return jsonify({"message": "成功", "data": data, "status": 200}), 200
    else:
        return jsonify({"message": "没有找到作弊记录", "status": 404}), 404


# 提交一组puuids，看看是否在名单里，用于房间查询，和进游戏后十人查询
@app.route('/cheating/records/puuids', methods=['POST'])
async def get_multiple_cheating_records():
    # 确认用户是否已经登录
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    # 获取请求中的puuids参数，应该是逗号分隔的字符串
    data = request.get_json()
    if not data or 'puuids' not in data:
        return jsonify({"message": "未提供puuids参数", "status": 400}), 400

    # 确保puuids是一个列表
    puuids_list = data['puuids']
    if not isinstance(puuids_list, list):
        return jsonify({"message": "puuids参数应该是一个列表", "status": 400}), 400

    query = """
          SELECT puuid, evidence_url, cheat_type, sub_type
          FROM cheating_records
          WHERE puuid IN (%s)
      """ % ','.join(['%s'] * len(puuids_list))  # 构造参数占位符

    # 执行查询
    results = await lol2.execute_multi_query(query, puuids_list)

    if results:
        # 将每个结果转换为字典
        records = [
            {
                "puuid": result[0],
                "evidence_url": result[1],
                "cheat_type": result[2],
                "sub_type": result[3]
            }
            for result in results
        ]
        return jsonify(records), 200
    else:
        return jsonify({"message": "没有找到作弊记录", "status": 404}), 404


# ====================
# 红色笔记 相关
# ====================
# 上传红色通缉人员
@app.route('/puuid/red', methods=['POST'])
async def post_red_puuid():
    data = request.get_json()
    if not data:
        return jsonify({"message": "数据不是JSON", "status": 400}), 400

    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    puuid = data.get('puuid')
    type_ = data.get('type')  # 'type' 是Python的保留字，所以这里使用 'type_' 作为变量名
    reason = data.get('reason')
    evidence_url = data.get('evidence_url')

    # 权限查询
    # sql = "SELECT admin from users where uid = :uid"
    # param = {"uid":uid}
    # respose = await lol2.execute_single_query(query, params)
    # if respose != 1:
    # return jsonify({"message": "权限不足", "status": 400}), 400

    query = """
            INSERT INTO wanted_red (puuid, type, reason, evidence_url) 
            VALUES (:puuid, :type, :reason, :evidence_url)
            ON DUPLICATE KEY UPDATE
            type = VALUES(type),
            reason = VALUES(reason),
            evidence_url = VALUES(evidence_url)
        """
    params = {"puuid": puuid, "type": type_, "reason": reason, "evidence_url": evidence_url}

    # 执行SQL语句
    await lol2.execute_transaction(query, params)
    # 反查确保成功
    verify_query = "SELECT * FROM wanted_red WHERE puuid = :puuid"
    verify_params = {"puuid": puuid}
    db_result = await lol2.execute_single_query(verify_query, verify_params)
    result_data = {
        "puuid": db_result[0],
        "type": db_result[1],
        "reason": db_result[2],
        "evidence_url": db_result[3]
    }

    # 验证结果
    if db_result is None or len(db_result) == 0:
        return jsonify({"message": "操作失败", "status": 400}), 400
    return jsonify({"message": "Operation successful", "status": 200, "data": result_data}), 200


# 红色笔记 举报相关
@app.route('/report/tracking', methods=['POST'])
async def red_note():
    # 确认用户是否已经登录
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    data = request.get_json()

    puuid = data.get('puuid')
    gameId = data.get('gameId')

    # 构建SQL查询，获取除时间以外的所有字段
    query = """
        SELECT report_count	
        FROM report_tracking
        WHERE puuid = :puuid and gameId = :gameId
    """
    params = {"puuid": puuid, "gameId": gameId}
    # 执行查询
    result = await lol2.execute_single_query(query, params)

    if not result:
        return jsonify({"message": "无记录", "status": 404}), 404

    report_count = result[0]

    if report_count <= 7:
        query = """
                UPDATE report_tracking SET report_count = report_count + 1 WHERE puuid = :puuid and gameId = :gameId
            """
        params
        await lol2.execute_transaction(query, params)
        return jsonify({"message": "举报次数更新", "report_count": report_count + 1}), 200
    else:
        return jsonify({"message": "被举报超过七次", "status": 404}), 404

#授权用户查询
@app.route('/authorization', methods=['POST'])
async def get_authorization():
    # 确认用户是否已经登录
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    data = request.get_json()
    puuid = data.get('puuid')

    #query = """SELECT puuid0,puuid1,puuid2,puuid3,puuid4 FROM users where uid = uid"""
    #result1 = await lol2.execute_single_query(query)
    #if result1:
        #return jsonify({"message": "白名单", "status": 200}), 200

    query = """
        SELECT puuid FROM user_authorization WHERE puuid = :puuid
    """
    params = {'puuid': puuid}

    # 执行查询
    result2 = await lol2.execute_single_query(query, params)
    if result2:
        return jsonify({"message": "成功","status": 200}), 200
    else:
        return jsonify({"message": "此puuid无授权", "status": 404}), 404

@app.route('/authorization/post', methods=['POST'])
async def post_authorization():
    uid = session.get('user_id')
    if not uid:
        return jsonify({"message": "用户未登录", "status": 401}), 401

    data = request.get_json()
    puuid = data.get('puuid')

    # 构建SQL查询，获取除时间以外的所有字段
    query = """
        INSERT INTO puuid_authorization (uid, puuid)
        VALUES (uid, puuid)
        ON DUPLICATE KEY UPDATE puuid = :puuid;
    """
    params = {"puuid": puuid}
    # 执行查询
    await lol2.execute_transaction(query, params)
    return jsonify({"message": "成功", "status": 200}), 200


# if __name__ == '__main__':
# app.run(host='0.0.0.0', port=5000, debug=True)
