#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
常驻进程管理处理器
"""

import json
import tornado.escape
from typing import Optional

from src.network.api.handlers.base_handler import BaseHandler
from src.core.logger import logger


class ResidentProcessListHandler(BaseHandler):
    """常驻进程列表处理器 - 获取所有常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def get(self):
        """
        获取所有常驻进程列表
        """
        try:
            processes = self.resident_process_manager.get_all_resident_processes()

            self.write(
                {
                    "status": "success",
                    "message": "获取常驻进程列表成功",
                    "data": processes,
                }
            )

        except Exception as e:
            logger.error(f"获取常驻进程列表失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class ResidentProcessCreateHandler(BaseHandler):
    """常驻进程创建处理器 - 新增常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def post(self):
        """
        创建新的常驻进程
        请求体: {"name": "进程名称"}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            name = data.get("name")
            if not name:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: name"})
                return

            # 类型检查
            if not isinstance(name, str):
                self.set_status(400)
                self.write({"status": "error", "message": "name必须是字符串"})
                return

            # 去除前后空格
            name = name.strip()
            if not name:
                self.set_status(400)
                self.write({"status": "error", "message": "name不能为空"})
                return

            # 导入模型
            from src.models.resident_process_info import ResidentProcessInfo

            # 创建ResidentProcessInfo对象
            process_info = ResidentProcessInfo(name=name)

            # 保存到数据库
            process_id = self.resident_process_manager.add_resident_process(
                process_info
            )

            self.write(
                {
                    "status": "success",
                    "message": "常驻进程添加成功",
                    "data": {"id": process_id, "name": name},
                }
            )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"创建常驻进程失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class ResidentProcessBatchCreateHandler(BaseHandler):
    """常驻进程批量创建处理器 - 批量新增常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def post(self):
        """
        批量创建常驻进程
        请求体: {"names": ["进程1", "进程2", "进程3"]}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            names = data.get("names")
            if not names:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: names"})
                return

            # 类型检查
            if not isinstance(names, list):
                self.set_status(400)
                self.write({"status": "error", "message": "names必须是数组"})
                return

            # 过滤和验证
            valid_names = []
            for name in names:
                if isinstance(name, str):
                    name = name.strip()
                    if name:
                        valid_names.append(name)

            if not valid_names:
                self.set_status(400)
                self.write({"status": "error", "message": "没有有效的进程名称"})
                return

            # 批量保存到数据库（自动去重并删除不在列表中的进程）
            result = self.resident_process_manager.batch_add_resident_processes(
                valid_names
            )

            # 构建响应消息
            message_parts = []
            if result["success_count"] > 0:
                message_parts.append(f"新增: {result['success_count']} 个")
            if result["skipped_count"] > 0:
                message_parts.append(f"已存在: {result['skipped_count']} 个")
            if result.get("deleted_count", 0) > 0:
                message_parts.append(f"删除: {result['deleted_count']} 个")
            if result["failed_count"] > 0:
                message_parts.append(f"失败: {result['failed_count']} 个")

            response_message = (
                "保存完成，" + "，".join(message_parts) if message_parts else "保存完成"
            )

            self.write(
                {
                    "status": "success",
                    "message": response_message,
                    "data": result,
                }
            )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"批量创建常驻进程失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class ResidentProcessDeleteHandler(BaseHandler):
    """常驻进程删除处理器 - 删除常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def post(self):
        """
        删除常驻进程
        请求体: {"id": 1} 或 {"name": "进程名称"}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 支持通过ID或名称删除
            process_id = data.get("id")
            name = data.get("name")

            if process_id is None and not name:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: id 或 name"})
                return

            # 优先使用ID删除
            if process_id is not None:
                # 类型检查和转换
                try:
                    process_id = int(process_id)
                except (ValueError, TypeError):
                    self.set_status(400)
                    self.write({"status": "error", "message": "id必须是整数"})
                    return

                # 删除常驻进程
                success = self.resident_process_manager.delete_resident_process(
                    process_id
                )

                if success:
                    self.write({"status": "success", "message": "常驻进程删除成功"})
                else:
                    self.set_status(404)
                    self.write(
                        {
                            "status": "error",
                            "message": f"未找到ID为 {process_id} 的常驻进程",
                        }
                    )
            else:
                # 使用名称删除
                name = name.strip()
                if not name:
                    self.set_status(400)
                    self.write({"status": "error", "message": "name不能为空"})
                    return

                success = self.resident_process_manager.delete_resident_process_by_name(
                    name
                )

                if success:
                    self.write({"status": "success", "message": "常驻进程删除成功"})
                else:
                    self.set_status(404)
                    self.write(
                        {"status": "error", "message": f"未找到名为 {name} 的常驻进程"}
                    )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"删除常驻进程失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class ResidentProcessClearHandler(BaseHandler):
    """常驻进程清空处理器 - 清空所有常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def post(self):
        """
        清空所有常驻进程
        """
        try:
            deleted_count = self.resident_process_manager.clear_all_resident_processes()

            self.write(
                {
                    "status": "success",
                    "message": f"清空成功，共删除 {deleted_count} 条记录",
                    "data": {"deleted_count": deleted_count},
                }
            )

        except Exception as e:
            logger.error(f"清空常驻进程失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class ResidentProcessGetHandler(BaseHandler):
    """常驻进程获取处理器 - 根据ID或名称获取单个常驻进程"""

    def initialize(self, resident_process_manager):
        self.resident_process_manager = resident_process_manager

    def get(self):
        """
        获取单个常驻进程信息
        查询参数: ?id=1 或 ?name=进程名称
        """
        try:
            # 获取查询参数
            process_id = self.get_argument("id", None)
            name = self.get_argument("name", None)

            if process_id is None and not name:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的参数: id 或 name"})
                return

            # 优先使用ID查询
            if process_id is not None:
                # 类型检查和转换
                try:
                    process_id = int(process_id)
                except (ValueError, TypeError):
                    self.set_status(400)
                    self.write({"status": "error", "message": "id必须是整数"})
                    return

                # 查询常驻进程
                process = self.resident_process_manager.get_resident_process_by_id(
                    process_id
                )

                if process:
                    self.write(
                        {
                            "status": "success",
                            "message": "获取常驻进程信息成功",
                            "data": process,
                        }
                    )
                else:
                    self.set_status(404)
                    self.write(
                        {
                            "status": "error",
                            "message": f"未找到ID为 {process_id} 的常驻进程",
                        }
                    )
            else:
                # 使用名称查询
                if not name:
                    self.set_status(400)
                    self.write({"status": "error", "message": "name不能为空"})
                    return

                name = name.strip()
                if not name:
                    self.set_status(400)
                    self.write({"status": "error", "message": "name不能为空"})
                    return

                process = self.resident_process_manager.get_resident_process_by_name(
                    name
                )

                if process:
                    self.write(
                        {
                            "status": "success",
                            "message": "获取常驻进程信息成功",
                            "data": process,
                        }
                    )
                else:
                    self.set_status(404)
                    self.write(
                        {"status": "error", "message": f"未找到名为 {name} 的常驻进程"}
                    )

        except Exception as e:
            logger.error(f"获取常驻进程信息失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})
