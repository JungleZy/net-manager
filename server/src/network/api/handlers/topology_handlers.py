#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑图管理处理器
"""

import json
import tornado.escape
from typing import Optional

from src.network.api.handlers.base_handler import BaseHandler
from src.core.logger import logger


class TopologyCreateHandler(BaseHandler):
    """拓扑图创建处理器 - 新增拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def post(self):
        """
        创建新的拓扑图
        请求体: {"content": "拓扑图JSON内容"}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            content = data.get("content")
            if content is None:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: content"})
                return

            # 类型检查和验证
            if not isinstance(content, str):
                # 如果content是字典或列表，转换为JSON字符串
                try:
                    content = json.dumps(content, ensure_ascii=False)
                except (TypeError, ValueError) as e:
                    self.set_status(400)
                    self.write(
                        {"status": "error", "message": f"content字段格式无效: {str(e)}"}
                    )
                    return

            # 验证content是有效的JSON字符串
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                self.set_status(400)
                self.write(
                    {
                        "status": "error",
                        "message": f"content必须是有效的JSON字符串: {str(e)}",
                    }
                )
                return

            # 导入模型
            from src.models.topology_info import TopologyInfo

            # 创建TopologyInfo对象
            topology_info = TopologyInfo(content=content)

            # 保存到数据库
            topology_id = self.topology_manager.save_topology(topology_info)

            self.write(
                {
                    "status": "success",
                    "message": "拓扑图创建成功",
                    "data": {"id": topology_id},
                }
            )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"创建拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class TopologyUpdateHandler(BaseHandler):
    """拓扑图更新处理器 - 修改拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def post(self):
        """
        更新拓扑图内容
        请求体: {"id": 1, "content": "新的拓扑图JSON内容"}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            topology_id = data.get("id")
            content = data.get("content")

            if topology_id is None:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: id"})
                return

            if content is None:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: content"})
                return

            # 类型检查和转换
            try:
                topology_id = int(topology_id)
            except (ValueError, TypeError):
                self.set_status(400)
                self.write({"status": "error", "message": "id必须是整数"})
                return

            if not isinstance(content, str):
                # 如果content是字典或列表，转换为JSON字符串
                try:
                    content = json.dumps(content, ensure_ascii=False)
                except (TypeError, ValueError) as e:
                    self.set_status(400)
                    self.write(
                        {"status": "error", "message": f"content字段格式无效: {str(e)}"}
                    )
                    return

            # 验证content是有效的JSON字符串
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                self.set_status(400)
                self.write(
                    {
                        "status": "error",
                        "message": f"content必须是有效的JSON字符串: {str(e)}",
                    }
                )
                return

            # 更新拓扑图
            success = self.topology_manager.update_topology(topology_id, content)

            if success:
                self.write({"status": "success", "message": "拓扑图更新成功"})
            else:
                self.set_status(404)
                self.write(
                    {"status": "error", "message": f"未找到ID为 {topology_id} 的拓扑图"}
                )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"更新拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class TopologyDeleteHandler(BaseHandler):
    """拓扑图删除处理器 - 删除拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def post(self):
        """
        删除拓扑图
        请求体: {"id": 1}
        """
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            topology_id = data.get("id")
            if topology_id is None:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: id"})
                return

            # 类型检查和转换
            try:
                topology_id = int(topology_id)
            except (ValueError, TypeError):
                self.set_status(400)
                self.write({"status": "error", "message": "id必须是整数"})
                return

            # 删除拓扑图
            success = self.topology_manager.delete_topology(topology_id)

            if success:
                self.write({"status": "success", "message": "拓扑图删除成功"})
            else:
                self.set_status(404)
                self.write(
                    {"status": "error", "message": f"未找到ID为 {topology_id} 的拓扑图"}
                )

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            logger.error(f"删除拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class TopologiesHandler(BaseHandler):
    """拓扑图列表处理器 - 获取所有拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def get(self):
        """
        获取所有拓扑图
        返回按创建时间降序排列的所有拓扑图列表，如果没有数据则返回空列表
        """
        try:
            topologies = self.topology_manager.get_all_topologies()

            # 处理返回数据：将content字段解析为JSON对象
            processed_topologies = []
            for topology in topologies:
                try:
                    # 尝试将content解析为JSON对象
                    content_obj = json.loads(topology["content"])
                    processed_topology = {
                        "id": topology["id"],
                        "content": content_obj,  # 解析后的JSON对象
                        "created_at": topology["created_at"],
                    }
                except json.JSONDecodeError:
                    # 如果解析失败，保持原始字符串
                    processed_topology = {
                        "id": topology["id"],
                        "content": topology["content"],
                        "created_at": topology["created_at"],
                    }
                processed_topologies.append(processed_topology)

            self.write(
                {
                    "status": "success",
                    "data": processed_topologies,
                    "count": len(processed_topologies),
                }
            )

        except Exception as e:
            logger.error(f"查询所有拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class TopologyLatestHandler(BaseHandler):
    """最新拓扑图处理器 - 获取最新的拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def get(self):
        """
        获取最新的拓扑图
        返回创建时间最新的拓扑图，如果没有数据则返回空拓扑结构
        """
        try:
            topology = self.topology_manager.get_latest_topology()

            if topology:
                try:
                    # 尝试将content解析为JSON对象
                    content_obj = json.loads(topology["content"])
                    processed_topology = {
                        "id": topology["id"],
                        "content": content_obj,
                        "created_at": topology["created_at"],
                    }
                except json.JSONDecodeError:
                    # 如果解析失败，保持原始字符串
                    processed_topology = {
                        "id": topology["id"],
                        "content": topology["content"],
                        "created_at": topology["created_at"],
                    }

                self.write({"status": "success", "data": processed_topology})
            else:
                # 没有数据时返回空的拓扑结构，而不是404错误
                empty_topology = {
                    "id": None,
                    "content": {"nodes": [], "edges": []},
                    "created_at": None,
                }
                self.write({"status": "success", "data": empty_topology})

        except Exception as e:
            logger.error(f"查询最新拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class TopologyHandler(BaseHandler):
    """单个拓扑图处理器 - 根据ID获取拓扑图"""

    def initialize(self, topology_manager):
        self.topology_manager = topology_manager

    def get(self, topology_id: str):
        """
        根据ID获取拓扑图
        路径参数: topology_id
        如果未找到则返回空拓扑结构
        """
        try:
            # 类型检查和转换
            try:
                topology_id_int = int(topology_id)
            except (ValueError, TypeError):
                self.set_status(400)
                self.write({"status": "error", "message": "id必须是整数"})
                return

            topology = self.topology_manager.get_topology_by_id(topology_id_int)

            if topology:
                try:
                    # 尝试将content解析为JSON对象
                    content_obj = json.loads(topology["content"])
                    processed_topology = {
                        "id": topology["id"],
                        "content": content_obj,
                        "created_at": topology["created_at"],
                    }
                except json.JSONDecodeError:
                    # 如果解析失败，保持原始字符串
                    processed_topology = {
                        "id": topology["id"],
                        "content": topology["content"],
                        "created_at": topology["created_at"],
                    }

                self.write({"status": "success", "data": processed_topology})
            else:
                # 未找到时返回空拓扑结构
                empty_topology = {
                    "id": None,
                    "content": {"nodes": [], "edges": []},
                    "created_at": None,
                }
                self.write({"status": "success", "data": empty_topology})

        except Exception as e:
            logger.error(f"查询拓扑图失败: {str(e)}", exc_info=True)
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})
