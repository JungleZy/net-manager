import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    next_cmd,
    bulk_cmd,
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
import time

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
        "ifHCInOctets": "1.3.6.1.2.1.31.1.1.1.6",
        "ifHCOutOctets": "1.3.6.1.2.1.31.1.1.1.10",
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

    def __init__(self, traffic_cache=None):
        """初始化SNMP监控器"""
        # 创建MIB视图控制器
        self.mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(self.mib_builder)
        # 流量缓存引用，用于速率计算
        self._traffic_cache = traffic_cache or {}

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
        获取设备基本信息（参考 get_interface_info 的会话复用与健壮性）

        保持输入输出不变：
        - 成功连接时包含：description；其他字段按各自OID获取成功与否填充
        - 首次连接性检查失败则返回空字典
        """
        device_info: Dict[str, Any] = {}
        _start_ts = time.perf_counter()

        # 复用会话，统一关闭 dispatcher
        snmp_engine, transport_target, creds, _mode = await self._create_session(
            ip, version, **kwargs
        )

        try:
            # 连接性检查：仅拉取 sysDescr，失败则与原逻辑一致返回 {}
            try:
                error_indication, error_status, error_index, var_binds = await get_cmd(
                    snmp_engine,
                    creds,
                    transport_target,
                    ContextData(),
                    ObjectType(ObjectIdentity(self.OIDS["sysDescr"])),
                )
            except Exception as e:
                logger.error(f"设备 {ip} 连接性检查异常: {e}")
                return device_info

            if error_indication or error_status:
                # 与旧实现一致：首次请求失败直接返回空字典
                return device_info

            descr_val = var_binds[0][1] if var_binds else None
            device_info["description"] = str(descr_val) if descr_val else ""

            # 批量获取其余标量OID（若批量失败，回退到逐项GET）
            other_oids = [
                self.OIDS["sysName"],
                self.OIDS["sysLocation"],
                self.OIDS["sysUpTime"],
                self.OIDS["sysObjectID"],
                self.OIDS["ifNumber"],
            ]
            objects = [ObjectType(ObjectIdentity(o)) for o in other_oids]

            def _assign(key: str, val_obj: Any):
                # 保持与旧实现一致的类型与默认值
                if key == "if_count":
                    if val_obj is not None:
                        device_info["if_count"] = int(val_obj) if val_obj else 0
                else:
                    if val_obj is not None:
                        device_info[key] = str(val_obj) if val_obj else ""

            # 先尝试批量GET
            batch_ok = False
            try:
                error_indication, error_status, error_index, var_binds = await get_cmd(
                    snmp_engine,
                    creds,
                    transport_target,
                    ContextData(),
                    *objects,
                )
                if not error_indication and not error_status and var_binds:
                    # 按顺序映射到字段
                    values = [vb[1] for vb in var_binds]
                    # 兼容返回数量差异（尽量安全）
                    val_sysName = values[0] if len(values) > 0 else None
                    val_sysLocation = values[1] if len(values) > 1 else None
                    val_sysUpTime = values[2] if len(values) > 2 else None
                    val_sysObjectID = values[3] if len(values) > 3 else None
                    val_ifNumber = values[4] if len(values) > 4 else None

                    _assign("name", val_sysName)
                    _assign("location", val_sysLocation)
                    _assign("uptime", val_sysUpTime)
                    _assign("object_id", val_sysObjectID)
                    _assign("if_count", val_ifNumber)
                    batch_ok = True
            except Exception as e:
                logger.debug(f"批量获取设备信息失败，准备回退逐项GET: {e}")

            # 批量失败时逐项GET，保持与原实现相同的逐项成功/失败影响范围
            if not batch_ok:
                per_map = [
                    ("name", self.OIDS["sysName"]),
                    ("location", self.OIDS["sysLocation"]),
                    ("uptime", self.OIDS["sysUpTime"]),
                    ("object_id", self.OIDS["sysObjectID"]),
                    ("if_count", self.OIDS["ifNumber"]),
                ]
                for key, oid in per_map:
                    try:
                        error_indication, error_status, error_index, var_binds = (
                            await get_cmd(
                                snmp_engine,
                                creds,
                                transport_target,
                                ContextData(),
                                ObjectType(ObjectIdentity(oid)),
                            )
                        )
                        if not error_indication and not error_status and var_binds:
                            val_obj = var_binds[0][1]
                            _assign(key, val_obj)
                    except Exception:
                        # 单项失败与原实现一致：跳过该字段，不影响其他字段
                        pass

            return device_info
        finally:
            # 记录耗时并关闭 dispatcher
            try:
                elapsed_ms = int((time.perf_counter() - _start_ts) * 1000)
                status_text = "成功" if len(device_info) > 0 else "失败"
                logger.info(
                    f"{ip} 设备信息采集耗时 {elapsed_ms} ms，状态：{status_text}"
                )
            except Exception:
                pass
            try:
                snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                pass

    async def _create_session(
        self, ip: str, version: str, **kwargs
    ) -> Tuple[SnmpEngine, Any, Any, str]:
        """创建并返回可复用的 SNMP 会话 (engine, target, creds, mode)。
        mode: 'bulk' 用于 v2c/v3；'next' 用于 v1 或回退。
        """
        port = kwargs.get("port", 161)
        snmp_engine = SnmpEngine()
        transport_target = await UdpTransportTarget.create(
            (ip, port), timeout=2.0, retries=0
        )
        version_l = version.lower()
        if version_l == "v1":
            community = kwargs.get("community", "public")
            creds = CommunityData(community, mpModel=0)
            mode = "next"
        elif version_l in ("v2c", "2c"):
            community = kwargs.get("community", "public")
            creds = CommunityData(community)
            mode = "bulk"
        elif version_l == "v3":
            user = kwargs.get("user")
            auth_protocol = kwargs.get("auth_protocol", "md5").lower()
            auth_proto = (
                usmHMACSHAAuthProtocol
                if auth_protocol == "sha"
                else usmHMACMD5AuthProtocol
            )
            auth_key = kwargs.get("auth_key")
            priv_key = kwargs.get("priv_key")
            if priv_key and auth_key:
                creds = UsmUserData(
                    user,
                    authKey=auth_key,
                    authProtocol=auth_proto,
                    privKey=priv_key,
                    privProtocol=usmDESPrivProtocol,
                )
            elif auth_key:
                creds = UsmUserData(
                    user,
                    authKey=auth_key,
                    authProtocol=auth_proto,
                    privProtocol=usmNoPrivProtocol,
                )
            else:
                creds = UsmUserData(
                    user, authProtocol=usmNoAuthProtocol, privProtocol=usmNoPrivProtocol
                )
            mode = "bulk"
        else:
            raise ValueError(f"不支持的SNMP版本: {version}")
        return snmp_engine, transport_target, creds, mode

    async def _walk_columns_session(
        self,
        snmp_engine: SnmpEngine,
        transport_target: Any,
        creds: Any,
        mode: str,
        base_oids: List[str],
        **kwargs,
    ) -> Dict[str, Dict[int, Any]]:
        """一次遍历多列（同批 ObjectType），返回 {base_oid: {index: value}} 映射。
        - v1 使用 GETNEXT（next_cmd）
        - v2c/v3 使用 GETBULK（bulk_cmd）
        通过传入已创建的会话避免重复初始化。
        """
        results_by_oid: Dict[str, Dict[int, Any]] = {b: {} for b in base_oids}
        max_repetitions = int(kwargs.get("max_repetitions", 25))
        # 自适应：若 ifNumber 较小，则降低 max_repetitions，避免浪费
        if_count_hint = kwargs.get("_if_count_hint")
        if isinstance(if_count_hint, int) and if_count_hint > 0:
            max_repetitions = max(1, min(max_repetitions, if_count_hint))

        objects = [ObjectType(ObjectIdentity(b)) for b in base_oids]
        if mode == "bulk":
            cmd_iter = bulk_cmd(
                snmp_engine,
                creds,
                transport_target,
                ContextData(),
                0,
                max_repetitions,
                *objects,
            )
        else:
            cmd_iter = next_cmd(
                snmp_engine,
                creds,
                transport_target,
                ContextData(),
                *objects,
            )

        try:
            # 同时兼容返回异步迭代器或协程的两种实现
            if hasattr(cmd_iter, "__aiter__"):
                async for (
                    error_indication,
                    error_status,
                    error_index,
                    var_binds,
                ) in cmd_iter:
                    if error_indication:
                        logger.debug(f"遍历错误: {error_indication}")
                        break
                    if error_status:
                        logger.debug(f"遍历状态错误: {error_status}")
                        break
                    # 扁平列表，逐项按前缀归类
                    for var_bind in var_binds:
                        oid_obj = var_bind[0]
                        val_obj = var_bind[1]
                        oid_str = (
                            ".".join(str(x) for x in oid_obj.asTuple())
                            if hasattr(oid_obj, "asTuple")
                            else (
                                oid_obj.prettyPrint()
                                if hasattr(oid_obj, "prettyPrint")
                                else str(oid_obj)
                            )
                        )
                        for base_oid in base_oids:
                            if (
                                oid_str.startswith(base_oid + ".")
                                or oid_str == base_oid
                            ):
                                try:
                                    idx = int(oid_str.split(".")[-1])
                                except Exception:
                                    # 某些实现可能直接返回列根（无索引），跳过
                                    break
                                results_by_oid[base_oid][idx] = val_obj
                                break
                    # 如果不匹配任何列前缀，说明已越界（部分或全部列），继续让迭代自然结束
            else:
                # 某些版本返回协程：先消费首个响应，再按列推进继续拉取
                current_oids = list(base_oids)
                max_rounds = max(1, int(kwargs.get("_if_count_hint", 64))) * 2
                rounds = 0
                # 先处理首次 cmd_iter（避免未等待协程的警告）
                last_oid_by_base: Dict[str, Optional[str]] = {
                    b: None for b in base_oids
                }
                error_indication, error_status, error_index, var_binds = await cmd_iter
                if error_indication:
                    logger.debug(f"遍历错误: {error_indication}")
                elif error_status:
                    logger.debug(f"遍历状态错误: {error_status}")
                else:
                    progress = False
                    for var_bind in var_binds:
                        oid_obj = var_bind[0]
                        val_obj = var_bind[1]
                        oid_str = (
                            ".".join(str(x) for x in oid_obj.asTuple())
                            if hasattr(oid_obj, "asTuple")
                            else (
                                oid_obj.prettyPrint()
                                if hasattr(oid_obj, "prettyPrint")
                                else str(oid_obj)
                            )
                        )
                        for base_oid in base_oids:
                            if oid_str.startswith(base_oid + "."):
                                try:
                                    idx = int(oid_str.split(".")[-1])
                                except Exception:
                                    continue
                                results_by_oid[base_oid][idx] = val_obj
                                last_oid_by_base[base_oid] = oid_str
                                progress = True
                                break
                    if progress:
                        for i, b in enumerate(base_oids):
                            if last_oid_by_base[b]:
                                current_oids[i] = last_oid_by_base[b]
                # 继续追加循环，直到无进展或越界
                while rounds < max_rounds:
                    objects = [ObjectType(ObjectIdentity(o)) for o in current_oids]
                    if mode == "bulk":
                        cmd_iter_once = bulk_cmd(
                            snmp_engine,
                            creds,
                            transport_target,
                            ContextData(),
                            0,
                            max_repetitions,
                            *objects,
                        )
                    else:
                        cmd_iter_once = next_cmd(
                            snmp_engine,
                            creds,
                            transport_target,
                            ContextData(),
                            *objects,
                        )
                    error_indication, error_status, error_index, var_binds = (
                        await cmd_iter_once
                    )
                    if error_indication or error_status:
                        logger.debug(f"遍历错误: {error_indication or error_status}")
                        break
                    progress = False
                    last_oid_by_base = {b: None for b in base_oids}
                    for var_bind in var_binds:
                        oid_obj = var_bind[0]
                        val_obj = var_bind[1]
                        oid_str = (
                            ".".join(str(x) for x in oid_obj.asTuple())
                            if hasattr(oid_obj, "asTuple")
                            else (
                                oid_obj.prettyPrint()
                                if hasattr(oid_obj, "prettyPrint")
                                else str(oid_obj)
                            )
                        )
                        for base_oid in base_oids:
                            if oid_str.startswith(base_oid + "."):
                                try:
                                    idx = int(oid_str.split(".")[-1])
                                except Exception:
                                    continue
                                results_by_oid[base_oid][idx] = val_obj
                                last_oid_by_base[base_oid] = oid_str
                                progress = True
                                break
                    if not progress:
                        break
                    for i, b in enumerate(base_oids):
                        if last_oid_by_base[b]:
                            current_oids[i] = last_oid_by_base[b]
                    rounds += 1
            return results_by_oid
        except Exception as e:
            logger.error(f"多列遍历异常: {e}")
            return results_by_oid

    async def _walk_columns_session_batched(
        self,
        snmp_engine: SnmpEngine,
        transport_target: Any,
        creds: Any,
        mode: str,
        base_oids: List[str],
        batch_size: int,
        **kwargs,
    ) -> Dict[str, Dict[int, Any]]:
        """分批遍历多列，避免设备对大报文不友好时的失败或限速。
        - 将 base_oids 按批次切分，每批调用一次 _walk_columns_session
        - 合并所有批次的结果后返回
        """
        if batch_size <= 0:
            batch_size = len(base_oids)
        merged: Dict[str, Dict[int, Any]] = {b: {} for b in base_oids}
        for i in range(0, len(base_oids), batch_size):
            batch = base_oids[i : i + batch_size]
            part = await self._walk_columns_session(
                snmp_engine,
                transport_target,
                creds,
                mode,
                batch,
                **kwargs,
            )
            for b in batch:
                merged[b].update(part.get(b, {}))
        return merged

    async def _preflight_bulk_session(
        self,
        snmp_engine: SnmpEngine,
        transport_target: Any,
        creds: Any,
        base_oids: List[str],
        if_count: int,
    ) -> Tuple[bool, int, int]:
        """小批量GETBULK预探测：尝试较小的 max_repetitions，检测错误与响应行数。
        返回 (bulk_ok, recommended_rep, recommended_batch)。若 bulk 不可用，bulk_ok=False。
        recommended_rep 为建议的较小重复数（例如 5），用于敏感设备；recommended_batch 为建议的分批列数；无建议则为 0。
        根据 error_status（如 tooBig, noSuchName）调整策略。
        """
        try:
            small_rep = max(1, min(5, if_count))
            objects = [ObjectType(ObjectIdentity(b)) for b in base_oids]
            cmd_iter = bulk_cmd(
                snmp_engine,
                creds,
                transport_target,
                ContextData(),
                0,
                small_rep,
                *objects,
            )
            entries = 0
            # 兼容异步迭代器与协程
            if hasattr(cmd_iter, "__aiter__"):
                async for (
                    error_indication,
                    error_status,
                    error_index,
                    var_binds,
                ) in cmd_iter:
                    if error_indication or error_status:
                        status_str = (
                            (
                                error_status.prettyPrint()
                                if hasattr(error_status, "prettyPrint")
                                else str(error_status)
                            )
                            if error_status
                            else str(error_indication)
                        )
                        logger.debug(f"预探测错误: {status_str}")
                        return False, 0, 0
                    # 只评估首个批次响应
                    for vb in var_binds:
                        oid_str = (
                            vb[0].prettyPrint()
                            if hasattr(vb[0], "prettyPrint")
                            else str(vb[0])
                        )
                        # 统计匹配列的条目
                        for base in base_oids:
                            if oid_str.startswith(base + "."):
                                entries += 1
                                break
                    break
            else:
                error_indication, error_status, error_index, var_binds = await cmd_iter
                if error_indication or error_status:
                    status_str = (
                        (
                            error_status.prettyPrint()
                            if hasattr(error_status, "prettyPrint")
                            else str(error_status)
                        )
                        if error_status
                        else str(error_indication)
                    )
                    logger.debug(f"预探测错误: {status_str}")
                    return False, 0, 0
                for vb in var_binds:
                    oid_str = (
                        vb[0].prettyPrint()
                        if hasattr(vb[0], "prettyPrint")
                        else str(vb[0])
                    )
                    for base in base_oids:
                        if oid_str.startswith(base + "."):
                            entries += 1
                            break
            # 建议较小的重复数和批量
            if entries <= max(1, len(base_oids)):
                return True, small_rep, max(2, min(6, len(base_oids)))
            return True, 0, 0
        except Exception:
            logger.debug("预探测bulk失败", exc_info=True)
            return False, 0, 0

    async def get_interface_info(
        self, ip: str, version: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取接口信息（合并遍历 + 会话复用 + 自适应 max_repetitions）
        - 复用同一 SnmpEngine/TransportTarget/凭据
        - 将 6 列合并到一次 bulk/next 遍历，减少往返
        - 根据 ifNumber 调整 max_repetitions；必要时回退到 GETNEXT
        """
        interfaces: List[Dict[str, Any]] = []
        _start_ts = time.perf_counter()

        # 获取接口数量
        value, success = await self.get_data(
            ip, version, self.OIDS["ifNumber"], **kwargs
        )
        if not success:
            return interfaces
        if_count = int(value) if value else 0
        if if_count <= 0:
            return interfaces
        indices = list(range(1, if_count + 1))
        logger.info(f"{ip} 获取到 {if_count} 个接口索引: {indices}")

        # 常量映射
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
        admin_status_map = {1: "已启用", 2: "已禁用", 3: "测试中"}
        oper_status_map = {
            1: "运行中",
            2: "未运行",
            3: "测试中",
            4: "未知",
            5: "休眠",
            6: "不存在",
            7: "下层接口未运行",
        }

        base_oids = [
            self.OIDS["ifDescr"],
            self.OIDS["ifType"],
            self.OIDS["ifSpeed"],
            self.OIDS["ifPhysAddress"],
            self.OIDS["ifAdminStatus"],
            self.OIDS["ifOperStatus"],
            self.OIDS["ifInOctets"],
            self.OIDS["ifOutOctets"],
        ]

        # 会话复用
        snmp_engine, transport_target, creds, mode = await self._create_session(
            ip, version, **kwargs
        )

        # 自适应探测与缓存：优先使用用户传入；否则按profile缓存；再进行探测
        user_rep = kwargs.get("max_repetitions")
        if not hasattr(self, "_best_max_repetitions_cache"):
            self._best_max_repetitions_cache: Dict[str, int] = {}
        profile_key = self._profile_key(ip, version, **kwargs)
        if user_rep is not None:
            best_rep = int(user_rep)
        elif profile_key in self._best_max_repetitions_cache:
            best_rep = int(self._best_max_repetitions_cache[profile_key])
        else:
            best_rep = await self._probe_best_max_repetitions_session(
                snmp_engine,
                transport_target,
                creds,
                mode,
                self.OIDS["ifDescr"],
                if_count,
            )
            self._best_max_repetitions_cache[profile_key] = best_rep

        # 更精细预探测：首次小批量尝试，若失败则切换到GETNEXT；若返回很少建议保持小批量并分批
        batch_size = 0
        effective_rep = best_rep
        if mode == "bulk":
            bulk_ok, small_rep, recommended_batch = await self._preflight_bulk_session(
                snmp_engine, transport_target, creds, base_oids, if_count
            )
            if not bulk_ok:
                mode = "next"
                effective_rep = 1
            elif small_rep > 0:
                effective_rep = min(best_rep, small_rep)
                batch_size = recommended_batch  # 使用预探测建议的分批列数

        try:
            # 第一次尝试：bulk（若 v2c/v3）或 next（v1），使用自适应最佳/精细参数
            try:
                if batch_size and mode == "bulk":
                    results_by_oid = await self._walk_columns_session_batched(
                        snmp_engine,
                        transport_target,
                        creds,
                        mode,
                        base_oids,
                        batch_size,
                        _if_count_hint=if_count,
                        max_repetitions=effective_rep,
                    )
                else:
                    results_by_oid = await self._walk_columns_session(
                        snmp_engine,
                        transport_target,
                        creds,
                        mode,
                        base_oids,
                        _if_count_hint=if_count,
                        max_repetitions=effective_rep,
                    )
            except Exception:
                # 初次尝试异常，置空以触发后续回退检查
                logger.warning("列遍历初次尝试异常，将进行回退检查", exc_info=True)
                results_by_oid = {}

            # 若列数据明显不足且当前为 bulk，则回退到 next 再试一次（兼容部分设备）
            if mode == "bulk":
                total_items = sum(len(results_by_oid.get(b, {})) for b in base_oids)
                if total_items < len(base_oids) * max(1, min(if_count, 2)):
                    results_by_oid = await self._walk_columns_session_batched(
                        snmp_engine,
                        transport_target,
                        creds,
                        mode,
                        base_oids,
                        4,
                        _if_count_hint=if_count,
                        max_repetitions=min(effective_rep, best_rep),
                    )
                    total_items = sum(len(results_by_oid.get(b, {})) for b in base_oids)
                if total_items < len(base_oids) * max(1, min(if_count, 2)):
                    results_by_oid = await self._walk_columns_session_batched(
                        snmp_engine,
                        transport_target,
                        creds,
                        "next",
                        base_oids,
                        4,
                        _if_count_hint=if_count,
                        max_repetitions=1,
                    )

            # 组装
            descr_map = {
                i: results_by_oid.get(self.OIDS["ifDescr"], {}).get(i) for i in indices
            }
            type_map_res = {
                i: results_by_oid.get(self.OIDS["ifType"], {}).get(i) for i in indices
            }
            speed_map = {
                i: results_by_oid.get(self.OIDS["ifSpeed"], {}).get(i) for i in indices
            }
            phys_map = {
                i: results_by_oid.get(self.OIDS["ifPhysAddress"], {}).get(i)
                for i in indices
            }
            admin_map = {
                i: results_by_oid.get(self.OIDS["ifAdminStatus"], {}).get(i)
                for i in indices
            }
            oper_map = {
                i: results_by_oid.get(self.OIDS["ifOperStatus"], {}).get(i)
                for i in indices
            }
            in_octets_map = {
                i: results_by_oid.get(self.OIDS["ifInOctets"], {}).get(i)
                for i in indices
            }
            out_octets_map = {
                i: results_by_oid.get(self.OIDS["ifOutOctets"], {}).get(i)
                for i in indices
            }

            for idx in indices:
                interface: Dict[str, Any] = {"index": idx}

                d_val = descr_map.get(idx)
                if d_val is not None:
                    interface["description"] = str(d_val) if d_val else ""

                t_val = type_map_res.get(idx)
                if t_val is not None:
                    type_code = int(t_val) if t_val else 0
                    interface["type"] = type_code
                    interface["type_text"] = type_map.get(type_code, f"类型{type_code}")

                s_val = speed_map.get(idx)
                if s_val is not None:
                    speed_bps = int(s_val) if s_val else 0
                    interface["speed"] = speed_bps
                    if speed_bps == 0:
                        interface["speed_text"] = "-"
                    elif speed_bps >= 1_000_000_000:
                        interface["speed_text"] = (
                            f"{speed_bps / 1_000_000_000:.1f} Gbps"
                        )
                    elif speed_bps >= 1_000_000:
                        interface["speed_text"] = f"{speed_bps / 1_000_000:.0f} Mbps"
                    elif speed_bps >= 1_000:
                        interface["speed_text"] = f"{speed_bps / 1_000:.0f} Kbps"
                    else:
                        interface["speed_text"] = f"{speed_bps} bps"

                p_val = phys_map.get(idx)
                if p_val is not None:
                    try:
                        if hasattr(p_val, "prettyPrint"):
                            mac_bytes = bytes(p_val)
                        elif isinstance(p_val, bytes):
                            mac_bytes = p_val
                        elif isinstance(p_val, str):
                            mac_bytes = p_val.encode("latin-1")
                        else:
                            mac_bytes = bytes(str(p_val), "latin-1")
                        interface["address"] = (
                            ""
                            if len(mac_bytes) == 0
                            else ":".join(f"{b:02x}" for b in mac_bytes)
                        )
                    except Exception as e:
                        logger.debug(
                            f"转换物理地址失败: {e}, value type: {type(p_val)}, value: {repr(p_val)}"
                        )
                        interface["address"] = ""

                a_val = admin_map.get(idx)
                if a_val is not None:
                    admin_status_code = int(a_val) if a_val else 0
                    interface["admin_status"] = admin_status_code
                    interface["admin_status_text"] = admin_status_map.get(
                        admin_status_code, "未知"
                    )

                o_val = oper_map.get(idx)
                if o_val is not None:
                    oper_status_code = int(o_val) if o_val else 0
                    interface["oper_status"] = oper_status_code
                    interface["oper_status_text"] = oper_status_map.get(
                        oper_status_code, "未知"
                    )

                # 添加流量数据
                in_octets_val = in_octets_map.get(idx)
                out_octets_val = out_octets_map.get(idx)

                in_octets = int(in_octets_val) if in_octets_val is not None else 0
                out_octets = int(out_octets_val) if out_octets_val is not None else 0

                interface["in_octets"] = in_octets
                interface["out_octets"] = out_octets

                # 计算上传/下载速率 (bps)
                now = time.time()
                ip_cache = self._traffic_cache.get(ip)
                prev = ip_cache.get(idx) if ip_cache else None

                def _delta(curr: int, prev_val: int) -> int:
                    # 处理32位计数器回绕
                    if curr >= prev_val:
                        return curr - prev_val
                    return (curr + (1 << 32)) - prev_val

                upload_bps = 0.0
                download_bps = 0.0
                if prev and "timestamp" in prev and now > prev["timestamp"]:
                    dt = now - prev["timestamp"]
                    if dt > 0:
                        out_delta = _delta(out_octets, int(prev.get("out_octets", 0)))
                        in_delta = _delta(in_octets, int(prev.get("in_octets", 0)))
                        upload_bps = (out_delta * 8) / dt
                        download_bps = (in_delta * 8) / dt

                interface["upload_bps"] = int(round(upload_bps))
                interface["download_bps"] = int(round(download_bps))

                # 可读速率
                def _bps_readable(bps: float) -> str:
                    # 所有速率采用四舍五入后的整数显示
                    if bps >= 1_000_000_000:
                        return f"{int(round(bps/1_000_000_000))} Gbps"
                    if bps >= 1_000_000:
                        return f"{int(round(bps/1_000_000))} Mbps"
                    if bps >= 1_000:
                        return f"{int(round(bps/1_000))} Kbps"
                    return f"{int(round(bps))} bps"

                interface["upload_readable"] = _bps_readable(upload_bps)
                interface["download_readable"] = _bps_readable(download_bps)

                # 更新缓存
                if ip_cache is None:
                    self._traffic_cache[ip] = {}
                    ip_cache = self._traffic_cache[ip]
                ip_cache[idx] = {
                    "in_octets": float(in_octets),
                    "out_octets": float(out_octets),
                    "timestamp": now,
                }

                interfaces.append(interface)

            return interfaces
        finally:
            # 统一关闭 dispatcher

            try:
                elapsed_ms = int((time.perf_counter() - _start_ts) * 1000)
                status_text = "成功" if len(interfaces) > 0 else "失败"
                logger.info(
                    f"{ip} 接口信息采集耗时 {elapsed_ms} ms，状态：{status_text}"
                )
            except Exception:
                pass

            try:
                snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                pass

    async def get_interface_traffic(
        self, ip: str, version: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取接口流量统计信息（合并遍历 + 会话复用 + 自适应 + 分批）
        - 复用同一会话对象
        - 合并多列遍历减少往返
        - 小批量预探测与分批以兼容设备限制
        """
        traffic_stats: List[Dict[str, Any]] = []

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
        indices = list(range(1, if_count + 1))

        base_oids = [
            self.OIDS["ifDescr"],
            self.OIDS["ifInOctets"],
            self.OIDS["ifOutOctets"],
            self.OIDS["ifInDiscards"],
            self.OIDS["ifOutDiscards"],
            self.OIDS["ifInErrors"],
            self.OIDS["ifOutErrors"],
        ]

        # 会话复用
        snmp_engine, transport_target, creds, mode = await self._create_session(
            ip, version, **kwargs
        )

        # 自适应探测与缓存：沿用接口信息的策略
        user_rep = kwargs.get("max_repetitions")
        if not hasattr(self, "_best_max_repetitions_cache"):
            self._best_max_repetitions_cache: Dict[str, int] = {}
        profile_key = self._profile_key(ip, version, **kwargs)
        if user_rep is not None:
            best_rep = int(user_rep)
        elif profile_key in self._best_max_repetitions_cache:
            best_rep = int(self._best_max_repetitions_cache[profile_key])
        else:
            best_rep = await self._probe_best_max_repetitions_session(
                snmp_engine,
                transport_target,
                creds,
                mode,
                self.OIDS["ifDescr"],
                if_count,
            )
            self._best_max_repetitions_cache[profile_key] = best_rep

        # 更精细预探测
        batch_size = 0
        effective_rep = best_rep
        if mode == "bulk":
            bulk_ok, small_rep, recommended_batch = await self._preflight_bulk_session(
                snmp_engine, transport_target, creds, base_oids, if_count
            )
            if not bulk_ok:
                mode = "next"
                effective_rep = 1
            elif small_rep > 0:
                effective_rep = min(best_rep, small_rep)
                batch_size = recommended_batch  # 使用预探测建议的分批列数

        try:
            # 第一次尝试：bulk（若 v2c/v3）或 next（v1），使用自适应最佳/精细参数
            if batch_size and mode == "bulk":
                results_by_oid = await self._walk_columns_session_batched(
                    snmp_engine,
                    transport_target,
                    creds,
                    mode,
                    base_oids,
                    batch_size,
                    _if_count_hint=if_count,
                    max_repetitions=effective_rep,
                )
            else:
                results_by_oid = await self._walk_columns_session(
                    snmp_engine,
                    transport_target,
                    creds,
                    mode,
                    base_oids,
                    _if_count_hint=if_count,
                    max_repetitions=effective_rep,
                )
        except Exception:
            # 初次尝试异常，置空以触发后续回退检查
            logger.warning("列遍历初次尝试异常，将进行回退检查", exc_info=True)
            results_by_oid = {}

        # 若列数据明显不足且当前为 bulk，则回退到 next 再试一次（兼容部分设备）
        if mode == "bulk":
            total_items = sum(len(results_by_oid.get(b, {})) for b in base_oids)
            if total_items < len(base_oids) * max(1, min(if_count, 2)):
                results_by_oid = await self._walk_columns_session_batched(
                    snmp_engine,
                    transport_target,
                    creds,
                    mode,
                    base_oids,
                    4,
                    _if_count_hint=if_count,
                    max_repetitions=min(effective_rep, best_rep),
                )
                total_items = sum(len(results_by_oid.get(b, {})) for b in base_oids)
            if total_items < len(base_oids) * max(1, min(if_count, 2)):
                results_by_oid = await self._walk_columns_session_batched(
                    snmp_engine,
                    transport_target,
                    creds,
                    "next",
                    base_oids,
                    4,
                    _if_count_hint=if_count,
                    max_repetitions=1,
                )

        # 组装返回
        descr_map = {
            i: results_by_oid.get(self.OIDS["ifDescr"], {}).get(i) for i in indices
        }
        in_oct = {
            i: results_by_oid.get(self.OIDS["ifInOctets"], {}).get(i) for i in indices
        }
        out_oct = {
            i: results_by_oid.get(self.OIDS["ifOutOctets"], {}).get(i) for i in indices
        }
        in_disc = {
            i: results_by_oid.get(self.OIDS["ifInDiscards"], {}).get(i) for i in indices
        }
        out_disc = {
            i: results_by_oid.get(self.OIDS["ifOutDiscards"], {}).get(i)
            for i in indices
        }
        in_err = {
            i: results_by_oid.get(self.OIDS["ifInErrors"], {}).get(i) for i in indices
        }
        out_err = {
            i: results_by_oid.get(self.OIDS["ifOutErrors"], {}).get(i) for i in indices
        }

        for idx in indices:
            stats: Dict[str, Any] = {"index": idx}
            d = descr_map.get(idx)
            if d is not None:
                stats["description"] = str(d) if d else ""
            v = in_oct.get(idx)
            if v is not None:
                stats["in_octets"] = int(v) if v else 0
            v = out_oct.get(idx)
            if v is not None:
                stats["out_octets"] = int(v) if v else 0
            v = in_disc.get(idx)
            if v is not None:
                stats["in_discards"] = int(v) if v else 0
            v = out_disc.get(idx)
            if v is not None:
                stats["out_discards"] = int(v) if v else 0
            v = in_err.get(idx)
            if v is not None:
                stats["in_errors"] = int(v) if v else 0
            v = out_err.get(idx)
            if v is not None:
                stats["out_errors"] = int(v) if v else 0
            traffic_stats.append(stats)

        return traffic_stats

    async def _probe_best_max_repetitions_session(
        self,
        snmp_engine: SnmpEngine,
        transport_target: Any,
        creds: Any,
        mode: str,
        base_oid: str,
        if_count: int,
    ) -> int:
        """自适应探测设备最佳 max_repetitions。
        - 仅在 mode == 'bulk' 时生效；否则返回 1。
        - 通过一次 GETBULK（单列）首个响应批次的速度与条目数评估最佳值。
        - 选择吞吐量（条目/秒）最高的候选，失败则回退到 10 或 25。
        """
        if mode != "bulk":
            return 1
        candidates = []
        # 基于接口数量构造候选，避免超过 ifCount
        for v in (5, 10, 15, 25, 50):
            if v <= 0:
                continue
            candidates.append(min(v, max(1, if_count)))
        # 去重并排序（升序）
        candidates = sorted(set(candidates))

        best = None
        best_throughput = 0.0
        for rep in candidates:
            try:
                start = time.perf_counter()
                cmd_iter = bulk_cmd(
                    snmp_engine,
                    creds,
                    transport_target,
                    ContextData(),
                    0,
                    rep,
                    ObjectType(ObjectIdentity(base_oid)),
                )
                entries = 0
                error = False
                if hasattr(cmd_iter, "__aiter__"):
                    async for (
                        error_indication,
                        error_status,
                        error_index,
                        var_binds,
                    ) in cmd_iter:
                        if error_indication or error_status:
                            error = True
                            break
                        # 仅评估首个批次
                        for vb in var_binds:
                            oid_str = (
                                vb[0].prettyPrint()
                                if hasattr(vb[0], "prettyPrint")
                                else str(vb[0])
                            )
                            if oid_str.startswith(base_oid + "."):
                                entries += 1
                        break
                else:
                    error_indication, error_status, error_index, var_binds = (
                        await cmd_iter
                    )
                    if error_indication or error_status:
                        error = True
                    else:
                        for vb in var_binds:
                            oid_str = (
                                vb[0].prettyPrint()
                                if hasattr(vb[0], "prettyPrint")
                                else str(vb[0])
                            )
                            if oid_str.startswith(base_oid + "."):
                                entries += 1
                duration = max(1e-6, time.perf_counter() - start)
                if error:
                    continue
                throughput = entries / duration
                if throughput > best_throughput and entries > 0:
                    best_throughput = throughput
                    best = rep
            except Exception:
                continue
        if best is None:
            # 回退：优先 10，其次 25（并限定不超过 if_count）
            return min(max(1, if_count), 10 if if_count >= 10 else min(25, if_count))
        return best

    def _profile_key(self, ip: str, version: str, **kwargs) -> str:
        """生成设备/配置的profile key，用于缓存最佳max_repetitions。"""
        ident = kwargs.get("community") or kwargs.get("user") or ""
        return f"{version}:{ip}:{ident}"
