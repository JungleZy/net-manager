import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    UsmUserData,
    usmNoAuthProtocol,
    usmNoPrivProtocol,
    usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol,
    usmDESPrivProtocol,
)
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi import builder, compiler, view
from typing import Dict, Any, Tuple, List, Optional
import logging
import binascii

# 配置日志
logger = logging.getLogger(__name__)


class SNMPMonitor:
    """
    SNMP监控类，支持SNMP v1、v2c、v3版本
    支持v3的三种安全级别：privacy、authentication、noauthentication
    具备智能OID分类和识别功能
    可获取设备信息、CPU占用率、内存占用率、网口上传下载流量等信息
    """

    # 常用MIB OID定义
    OIDS = {
        # 系统信息
        "sysDescr": "1.3.6.1.2.1.1.1.0",
        "sysObjectID": "1.3.6.1.2.1.1.2.0",
        "sysUpTime": "1.3.6.1.2.1.1.3.0",
        "sysContact": "1.3.6.1.2.1.1.4.0",
        "sysName": "1.3.6.1.2.1.1.5.0",
        "sysLocation": "1.3.6.1.2.1.1.6.0",
        # 接口信息
        "ifNumber": "1.3.6.1.2.1.2.1.0",
        "ifTable": "1.3.6.1.2.1.2.2",
        "ifDescr": "1.3.6.1.2.1.2.2.1.2",  # 描述接口的字符串，应该包含制造商、产品名和接口软硬件的版本。
        "ifType": "1.3.6.1.2.1.2.2.1.3",  # 接口类型。ifType的额外值必须通过因特网地址分配组织（IANA）升级IANAifType原文约定的语义的方式分配。 以太类型接口转成集群口后，ifType显示other(1)。
        "ifMtu": "1.3.6.1.2.1.2.2.1.4",  # 最大传输单元。接口上可以传送的最大报文的大小，单位是octet。对于传输网络数据报的接口，这是接口可以传输的最大数据报的大小。 二层口ifMtu显示jumboframe。jumboframe可以通过命令jumboframe enable [ value ]配置。
        "ifSpeed": "1.3.6.1.2.1.2.2.1.5",  # 估计的接口当前带宽，单位是bit/s。对于带宽无法改变或者无法准确估计的接口，该项为额定带宽值。 如果接口的带宽比该表项的值大，则该表项的值是其最大值（4,294,967,295），并且ifHighSpeed的值是接口的速率。对于没有速率概念的子层接口，该表项的值为零。
        "ifPhysAddress": "1.3.6.1.2.1.2.2.1.6",  # 接口的协议子层对应的接口地址，如对于802.x的接口，该项一般为MAC地址。接口的media-specific MIB必须定义位和字节的顺序和该表项的值的格式。 对于没有这种地址的接口（如串口），则该表项的值是一个表示零长度的八位字节串（octet string）。
        "ifAdminStatus": "1.3.6.1.2.1.2.2.1.7",
        "ifOperStatus": "1.3.6.1.2.1.2.2.1.8",
        "ifLastChange": "1.3.6.1.2.1.2.2.1.9",
        "ifInOctets": "1.3.6.1.2.1.2.2.1.10",
        "ifInUcastPkts": "1.3.6.1.2.1.2.2.1.11",
        "ifInNUcastPkts": "1.3.6.1.2.1.2.2.1.12",
        "ifInDiscards": "1.3.6.1.2.1.2.2.1.13",
        "ifInErrors": "1.3.6.1.2.1.2.2.1.14",
        "ifInUnknownProtos": "1.3.6.1.2.1.2.2.1.15",
        "ifOutOctets": "1.3.6.1.2.1.2.2.1.16",
        "ifOutUcastPkts": "1.3.6.1.2.1.2.2.1.17",
        "ifOutNUcastPkts": "1.3.6.1.2.1.2.2.1.18",
        "ifOutDiscards": "1.3.6.1.2.1.2.2.1.19",
        "ifOutErrors": "1.3.6.1.2.1.2.2.1.20",
        "ifOutQLen": "1.3.6.1.2.1.2.2.1.21",
        "ifSpecific": "1.3.6.1.2.1.2.2.1.22",
    }

    def __init__(self):
        """初始化SNMP监控器"""
        # 创建MIB视图控制器
        self.mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(self.mib_builder)

        # 编译MIB
        compiler.addMibCompiler(
            self.mib_builder,
            sources=[
                "file:///usr/share/snmp/mibs",
                "http://mibs.snmplabs.com/asn1/@mib@",
            ],
        )

    async def _get_snmp_v1(
        self, ip: str, community: str, oid: str, port: int = 161
    ) -> Tuple[Any, bool]:
        """
        使用SNMP v1获取数据

        Args:
            ip: 设备IP地址
            community: 社区字符串
            oid: OID
            port: 端口号，默认161

        Returns:
            (值, 是否成功)
        """
        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create(
                (ip, port), timeout=2.0, retries=0
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                CommunityData(community, mpModel=0),  # mpModel=0表示SNMPv1
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                logger.error(f"SNMP v1错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v1错误状态: {str(error_status)}")
                return None, False
            else:
                for var_bind in var_binds:
                    return var_bind[1], True

        except Exception as e:
            logger.error(f"SNMP v1异常: {str(e)}")
            return None, False
        finally:
            # 确保关闭引擎
            snmp_engine.transportDispatcher.closeDispatcher()

        return None, False

    async def _get_snmp_v2c(
        self, ip: str, community: str, oid: str, port: int = 161
    ) -> Tuple[Any, bool]:
        """
        使用SNMP v2c获取数据

        Args:
            ip: 设备IP地址
            community: 社区字符串
            oid: OID
            port: 端口号，默认161

        Returns:
            (值, 是否成功)
        """
        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create(
                (ip, port), timeout=2.0, retries=0
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                CommunityData(community),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )
            if error_indication:
                logger.debug(f"SNMP v2c错误: ip: {ip}, {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v2c错误状态: {str(error_status)}")
                return None, False
            else:
                for var_bind in var_binds:
                    return var_bind[1], True

        except Exception as e:
            logger.error(f"SNMP v2c异常: {str(e)}")
            return None, False
        finally:
            # 确保关闭引擎
            snmp_engine.transportDispatcher.closeDispatcher()

        return None, False

    async def _get_snmp_v3_noauth(
        self, ip: str, user: str, oid: str, port: int = 161
    ) -> Tuple[Any, bool]:
        """
        使用SNMP v3无认证模式获取数据

        Args:
            ip: 设备IP地址
            user: 用户名
            oid: OID
            port: 端口号，默认161

        Returns:
            (值, 是否成功)
        """
        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create(
                (ip, port), timeout=2.0, retries=0
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(
                    user, authProtocol=usmNoAuthProtocol, privProtocol=usmNoPrivProtocol
                ),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                logger.error(f"SNMP v3无认证错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3无认证错误状态: {str(error_status)}")
                return None, False
            else:
                for var_bind in var_binds:
                    return var_bind[1], True

        except Exception as e:
            logger.error(f"SNMP v3无认证异常: {str(e)}")
            return None, False
        finally:
            # 确保关闭引擎
            snmp_engine.transportDispatcher.closeDispatcher()

        return None, False

    async def _get_snmp_v3_auth(
        self,
        ip: str,
        user: str,
        auth_key: Optional[str],
        oid: str,
        port: int = 161,
        auth_protocol: str = "md5",
    ) -> Tuple[Any, bool]:
        """
        使用SNMP v3认证模式获取数据

        Args:
            ip: 设备IP地址
            user: 用户名
            auth_key: 认证密钥
            oid: OID
            port: 端口号，默认161
            auth_protocol: 认证协议，'md5' 或 'sha'，默认为 'md5'

        Returns:
            (值, 是否成功)
        """
        # 验证auth_key参数
        if not auth_key:
            logger.error("SNMP v3认证模式需要提供认证密钥")
            return None, False

        # 根据参数选择认证协议
        if auth_protocol.lower() == "sha":
            auth_proto = usmHMACSHAAuthProtocol
        else:
            auth_proto = usmHMACMD5AuthProtocol

        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create(
                (ip, port), timeout=2.0, retries=0
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(
                    user,
                    authKey=auth_key,
                    authProtocol=auth_proto,
                    privProtocol=usmNoPrivProtocol,
                ),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                logger.error(f"SNMP v3认证错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3认证错误状态: {str(error_status)}")
                return None, False
            else:
                for var_bind in var_binds:
                    return var_bind[1], True

        except Exception as e:
            logger.error(f"SNMP v3认证异常: {str(e)}")
            return None, False
        finally:
            # 确保关闭引擎
            snmp_engine.transportDispatcher.closeDispatcher()

        return None, False

    async def _get_snmp_v3_privacy(
        self,
        ip: str,
        user: str,
        auth_key: Optional[str],
        priv_key: Optional[str],
        oid: str,
        port: int = 161,
        auth_protocol: str = "md5",
    ) -> Tuple[Any, bool]:
        """
        使用SNMP v3隐私模式获取数据

        Args:
            ip: 设备IP地址
            user: 用户名
            auth_key: 认证密钥
            priv_key: 加密密钥
            oid: OID
            port: 端口号，默认161
            auth_protocol: 认证协议，'md5' 或 'sha'，默认为 'md5'

        Returns:
            (值, 是否成功)
        """
        # 验证必需参数
        if not auth_key:
            logger.error("SNMP v3隐私模式需要提供认证密钥")
            return None, False
        if not priv_key:
            logger.error("SNMP v3隐私模式需要提供加密密钥")
            return None, False

        # 根据参数选择认证协议
        if auth_protocol.lower() == "sha":
            auth_proto = usmHMACSHAAuthProtocol
        else:
            auth_proto = usmHMACMD5AuthProtocol

        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create(
                (ip, port), timeout=2.0, retries=0
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(
                    user,
                    authKey=auth_key,
                    privKey=priv_key,
                    authProtocol=auth_proto,
                    privProtocol=usmDESPrivProtocol,
                ),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                logger.error(f"SNMP v3隐私错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3隐私错误状态: {str(error_status)}")
                return None, False
            else:
                for var_bind in var_binds:
                    return var_bind[1], True

        except Exception as e:
            logger.error(f"SNMP v3隐私异常: {str(e)}")
            return None, False
        finally:
            # 确保关闭引擎
            snmp_engine.transportDispatcher.closeDispatcher()

        return None, False

    async def get_data(
        self, ip: str, version: str, oid: str, **kwargs
    ) -> Tuple[Any, bool]:
        """
        根据指定的SNMP版本获取数据

        Args:
            ip: 设备IP地址
            version: SNMP版本 ('v1', 'v2c', 'v3')
            oid: OID
            **kwargs: 其他参数
                对于v1/v2c: community
                对于v3: user, auth_key(可选), priv_key(可选), auth_protocol(可选，默认'md5')

        Returns:
            (值, 是否成功)
        """
        port = kwargs.get("port", 161)
        if version.lower() == "v1":
            community = kwargs.get("community", "public")
            return await self._get_snmp_v1(ip, community, oid, port)
        elif version.lower() == "v2c" or version.lower() == "2c":
            community = kwargs.get("community", "public")
            return await self._get_snmp_v2c(ip, community, oid, port)
        elif version.lower() == "v3":
            user = kwargs.get("user")
            if not user:
                logger.error("SNMP v3需要提供用户名")
                return None, False

            # 获取认证协议参数，默认为'md5'
            auth_protocol = kwargs.get("auth_protocol", "md5")

            # 根据提供的参数确定安全级别
            auth_key = kwargs.get("auth_key")
            priv_key = kwargs.get("priv_key")

            if priv_key and auth_key:
                # 隐私级别（需要同时提供认证密钥和加密密钥）
                return await self._get_snmp_v3_privacy(
                    ip, user, auth_key, priv_key, oid, port, auth_protocol
                )
            elif auth_key:
                # 认证级别（只需要认证密钥）
                return await self._get_snmp_v3_auth(
                    ip, user, auth_key, oid, port, auth_protocol
                )
            else:
                # 无认证级别
                return await self._get_snmp_v3_noauth(ip, user, oid, port)
        else:
            logger.error(f"不支持的SNMP版本: {version}")
            return None, False

    async def get_device_info(self, ip: str, version: str, **kwargs) -> Dict[str, Any]:
        """
        获取设备基本信息

        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数

        Returns:
            包含设备信息的字典
        """
        device_info = {}

        # 获取系统描述（作为连通性测试）
        value, success = await self.get_data(
            ip, version, self.OIDS["sysDescr"], **kwargs
        )
        if not success:
            # 第一次请求失败，设备不可达，直接返回空字典，避免后续无效请求
            return device_info

        device_info["description"] = str(value) if value else ""

        # 获取系统名称
        value, success = await self.get_data(
            ip, version, self.OIDS["sysName"], **kwargs
        )
        if success:
            device_info["name"] = str(value) if value else ""

        # 获取系统位置
        value, success = await self.get_data(
            ip, version, self.OIDS["sysLocation"], **kwargs
        )
        if success:
            device_info["location"] = str(value) if value else ""

        # 获取系统运行时间
        value, success = await self.get_data(
            ip, version, self.OIDS["sysUpTime"], **kwargs
        )
        if success:
            device_info["uptime"] = str(value) if value else ""

        value, success = await self.get_data(
            ip, version, self.OIDS["sysObjectID"], **kwargs
        )
        if success:
            device_info["object_id"] = str(value) if value else ""

        # 获取端口数量
        value, success = await self.get_data(
            ip, version, self.OIDS["ifNumber"], **kwargs
        )
        if success:
            device_info["if_count"] = int(value) if value else 0

        return device_info

    async def get_interface_info(
        self, ip: str, version: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取接口信息

        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数

        Returns:
            包含接口信息的列表
        """
        interfaces = []

        # 获取接口数量
        value, success = await self.get_data(
            ip, version, self.OIDS["ifNumber"], **kwargs
        )
        if not success:
            return interfaces
        if_count = int(value) if value else 0
        if if_count <= 0:
            return interfaces

        # 获取每个接口的信息
        for i in range(1, if_count + 1):
            interface: Dict[str, Any] = {"index": i}

            # 获取接口描述
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifDescr']}.{i}", **kwargs
            )
            if success:
                interface["description"] = str(value) if value else ""

            # 获取接口类型
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifType']}.{i}", **kwargs
            )
            if success:
                type_code = int(value) if value else 0
                interface["type"] = type_code
                # 转换为中文类型描述（基于IANAifType）
                type_map = {
                    1: "其他",
                    6: "以太网",
                    23: "PPP",
                    24: "环回接口",
                    37: "ATM",
                    53: "VLAN",
                    131: "隧道接口",
                    135: "二层VLAN",
                    136: "三层VLAN",
                    161: "IEEE 802.11无线",
                    117: "千兆以太网",
                    244: "聚合接口",
                }
                interface["type_text"] = type_map.get(type_code, f"类型{type_code}")

            # 获取接口速度（单位：bps）
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifSpeed']}.{i}", **kwargs
            )
            if success:
                speed_bps = int(value) if value else 0
                interface["speed"] = speed_bps
                # 格式化为易读的速度描述
                if speed_bps == 0:
                    interface["speed_text"] = "-"
                elif speed_bps >= 1000000000:  # >= 1 Gbps
                    speed_gbps = speed_bps / 1000000000
                    interface["speed_text"] = f"{speed_gbps:.1f} Gbps"
                elif speed_bps >= 1000000:  # >= 1 Mbps
                    speed_mbps = speed_bps / 1000000
                    interface["speed_text"] = f"{speed_mbps:.0f} Mbps"
                elif speed_bps >= 1000:  # >= 1 Kbps
                    speed_kbps = speed_bps / 1000
                    interface["speed_text"] = f"{speed_kbps:.0f} Kbps"
                else:
                    interface["speed_text"] = f"{speed_bps} bps"

            # 获取接口物理地址(对于802.x接口为MAC地址,对于串口等为空)
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifPhysAddress']}.{i}", **kwargs
            )
            if success and value:
                try:
                    # 将OctetString转换为bytes
                    if hasattr(value, "prettyPrint"):
                        # pysnmp的OctetString对象
                        mac_bytes = bytes(value)
                    elif isinstance(value, bytes):
                        mac_bytes = value
                    elif isinstance(value, str):
                        # 如果已经是字符串,尝试转换为bytes
                        mac_bytes = value.encode("latin-1")
                    else:
                        mac_bytes = bytes(str(value), "latin-1")

                    # 零长度的八位字节串表示没有物理地址(如串口、loopback等)
                    if len(mac_bytes) == 0:
                        interface["address"] = ""
                    # 6字节表示以太网MAC地址(802.x)
                    elif len(mac_bytes) == 6:
                        interface["address"] = ":".join(f"{b:02x}" for b in mac_bytes)
                    # 其他长度的物理地址
                    else:
                        interface["address"] = ":".join(f"{b:02x}" for b in mac_bytes)
                except Exception as e:
                    logger.debug(
                        f"转换物理地址失败: {e}, value type: {type(value)}, value: {repr(value)}"
                    )
                    interface["address"] = ""
            else:
                # 空值表示没有物理地址
                interface["address"] = ""

            # 获取管理状态 (1=up, 2=down, 3=testing)
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifAdminStatus']}.{i}", **kwargs
            )
            if success:
                admin_status_code = int(value) if value else 0
                interface["admin_status"] = admin_status_code
                # 转换为中文状态描述
                admin_status_map = {1: "已启用", 2: "已禁用", 3: "测试中"}
                interface["admin_status_text"] = admin_status_map.get(
                    admin_status_code, "未知"
                )

            # 获取操作状态 (1=up, 2=down, 3=testing, 4=unknown, 5=dormant, 6=notPresent, 7=lowerLayerDown)
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifOperStatus']}.{i}", **kwargs
            )
            if success:
                oper_status_code = int(value) if value else 0
                interface["oper_status"] = oper_status_code
                # 转换为中文状态描述
                oper_status_map = {
                    1: "运行中",
                    2: "未运行",
                    3: "测试中",
                    4: "未知",
                    5: "休眠",
                    6: "不存在",
                    7: "下层接口未运行",
                }
                interface["oper_status_text"] = oper_status_map.get(
                    oper_status_code, "未知"
                )

            # 获取接收字节数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifInOctets']}.{i}", **kwargs
            # )
            # if success:
            #     interface["in_octets"] = int(value) if value else 0

            # 获取发送字节数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifOutOctets']}.{i}", **kwargs
            # )
            # if success:
            #     interface["out_octets"] = int(value) if value else 0

            # 获取接收丢包数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifInDiscards']}.{i}", **kwargs
            # )
            # if success:
            #     interface["in_discards"] = int(value) if value else 0

            # 获取发送丢包数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifOutDiscards']}.{i}", **kwargs
            # )
            # if success:
            #     interface["out_discards"] = int(value) if value else 0

            # 获取接收错误数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifInErrors']}.{i}", **kwargs
            # )
            # if success:
            #     interface["in_errors"] = int(value) if value else 0

            # 获取发送错误数
            # value, success = await self.get_data(
            #     ip, version, f"{self.OIDS['ifOutErrors']}.{i}", **kwargs
            # )
            # if success:
            #     interface["out_errors"] = int(value) if value else 0

            interfaces.append(interface)

        return interfaces

    async def get_interface_traffic(
        self, ip: str, version: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取接口流量统计信息

        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数

        Returns:
            包含接口流量信息的列表
        """
        traffic_stats = []

        # 获取接口数量
        value, success = await self.get_data(
            ip, version, self.OIDS["ifNumber"], **kwargs
        )
        if not success:
            logger.error("无法获取接口数量")
            return traffic_stats

        if_count = int(value) if value else 0
        if if_count <= 0:
            return traffic_stats

        # 获取每个接口的流量统计
        for i in range(1, if_count + 1):
            stats: Dict[str, Any] = {"index": i}

            # 获取接口描述
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifDescr']}.{i}", **kwargs
            )
            if success:
                stats["description"] = str(value) if value else ""

            # 获取接收字节数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifInOctets']}.{i}", **kwargs
            )
            if success:
                stats["in_octets"] = int(value) if value else 0

            # 获取发送字节数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifOutOctets']}.{i}", **kwargs
            )
            if success:
                stats["out_octets"] = int(value) if value else 0

            # 获取接收丢包数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifInDiscards']}.{i}", **kwargs
            )
            if success:
                stats["in_discards"] = int(value) if value else 0

            # 获取发送丢包数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifOutDiscards']}.{i}", **kwargs
            )
            if success:
                stats["out_discards"] = int(value) if value else 0

            # 获取接收错误数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifInErrors']}.{i}", **kwargs
            )
            if success:
                stats["in_errors"] = int(value) if value else 0

            # 获取发送错误数
            value, success = await self.get_data(
                ip, version, f"{self.OIDS['ifOutErrors']}.{i}", **kwargs
            )
            if success:
                stats["out_errors"] = int(value) if value else 0

            traffic_stats.append(stats)

        return traffic_stats
