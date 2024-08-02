# 群管系统
import json
import logging
import asyncio
import websockets
import re
import colorlog
import os
import random
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from new_app.api import *
from new_app.config import owner_id


# 判断用户是否是QQ群群主
async def is_qq_owner(role):
    if role == "owner":
        return True
    else:
        return False


# 判断用户是否是QQ群管理员
async def is_qq_admin(role):
    if role == "admin":
        return True
    else:
        return False


async def handle_group_message(websocket, msg):
    try:
        # 读取消息信息
        user_id = msg["sender"]["user_id"]
        group_id = msg["group_id"]
        raw_message = msg["raw_message"]
        role = msg["sender"]["role"]

        # 全员禁言
        if "全员禁言" in raw_message:
            is_admin = await is_qq_admin(role)
            is_owner = await is_qq_owner(role)

            if (is_admin or is_owner) or (user_id in owner_id):
                await set_group_whole_ban(websocket, group_id, True)  # 全员禁言

        # 全员解禁
        if "全员解禁" in raw_message:
            is_admin = await is_qq_admin(role)
            is_owner = await is_qq_owner(role)

            if (is_admin or is_owner) or (user_id in owner_id):
                await set_group_whole_ban(websocket, group_id, False)  # 全员解禁

        # 踢人
        if (user_id in owner_id or role == "owner" or role == "admin") and (
            re.match(r"kick.*", raw_message)
            or re.match(r"t.*", raw_message)
            or re.match(r"踢.*", raw_message)
        ):
            # 初始化
            kick_qq = None

            # 遍历message列表，查找type为'at'的项并读取qq字段
            for i, item in enumerate(msg["message"]):
                if item["type"] == "at":
                    kick_qq = item["data"]["qq"]
                    break
            # 执行
            if kick_qq:
                await set_group_kick(websocket, group_id, kick_qq)

    except Exception as e:
        logging.error(f"处理群消息时出错: {e}")
