import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity,
    get_cmd, UsmUserData, usmNoAuthProtocol, usmNoPrivProtocol, usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol, usmDESPrivProtocol
)
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi import builder, compiler, view
from typing import Dict, Any, Tuple, List, Optional
import logging

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
        'sysDescr': '1.3.6.1.2.1.1.1.0',
        'sysObjectID': '1.3.6.1.2.1.1.2.0',
        'sysUpTime': '1.3.6.1.2.1.1.3.0',
        'sysContact': '1.3.6.1.2.1.1.4.0',
        'sysName': '1.3.6.1.2.1.1.5.0',
        'sysLocation': '1.3.6.1.2.1.1.6.0',
        
        # 接口信息
        'ifNumber': '1.3.6.1.2.1.2.1.0',
        'ifTable': '1.3.6.1.2.1.2.2',
        'ifDescr': '1.3.6.1.2.1.2.2.1.2',
        'ifType': '1.3.6.1.2.1.2.2.1.3',
        'ifMtu': '1.3.6.1.2.1.2.2.1.4',
        'ifSpeed': '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress': '1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus': '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',
        'ifLastChange': '1.3.6.1.2.1.2.2.1.9',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
        'ifInUcastPkts': '1.3.6.1.2.1.2.2.1.11',
        'ifInNUcastPkts': '1.3.6.1.2.1.2.2.1.12',
        'ifInDiscards': '1.3.6.1.2.1.2.2.1.13',
        'ifInErrors': '1.3.6.1.2.1.2.2.1.14',
        'ifInUnknownProtos': '1.3.6.1.2.1.2.2.1.15',
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
        'ifOutUcastPkts': '1.3.6.1.2.1.2.2.1.17',
        'ifOutNUcastPkts': '1.3.6.1.2.1.2.2.1.18',
        'ifOutDiscards': '1.3.6.1.2.1.2.2.1.19',
        'ifOutErrors': '1.3.6.1.2.1.2.2.1.20',
        'ifOutQLen': '1.3.6.1.2.1.2.2.1.21',
        'ifSpecific': '1.3.6.1.2.1.2.2.1.22',
    }
    
    def __init__(self):
        """初始化SNMP监控器"""
        # 创建MIB视图控制器
        self.mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(self.mib_builder)
        
        # 编译MIB
        compiler.addMibCompiler(self.mib_builder, sources=['file:///usr/share/snmp/mibs', 'http://mibs.snmplabs.com/asn1/@mib@'])
        
    async def _get_snmp_v1(self, ip: str, community: str, oid: str, port: int = 161) -> Tuple[Any, bool]:
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
            transport_target = await UdpTransportTarget.create((ip, port))
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                CommunityData(community, mpModel=0),  # mpModel=0表示SNMPv1
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if error_indication:
                logger.error(f"SNMP v1错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v1错误状态: {error_status.prettyPrint()}")
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
    
    async def _get_snmp_v2c(self, ip: str, community: str, oid: str, port: int = 161) -> Tuple[Any, bool]:
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
            transport_target = await UdpTransportTarget.create((ip, port), timeout=2.0, retries=3)
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                CommunityData(community),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            if error_indication:
                logger.error(f"SNMP v2c错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v2c错误状态: {error_status.prettyPrint()}")
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
    
    async def _get_snmp_v3_noauth(self, ip: str, user: str, oid: str, port: int = 161) -> Tuple[Any, bool]:
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
            transport_target = await UdpTransportTarget.create((ip, port))
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(user, authProtocol=usmNoAuthProtocol, privProtocol=usmNoPrivProtocol),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if error_indication:
                logger.error(f"SNMP v3无认证错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3无认证错误状态: {error_status.prettyPrint()}")
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
    
    async def _get_snmp_v3_auth(self, ip: str, user: str, auth_key: str, oid: str, port: int = 161, auth_protocol: str = 'md5') -> Tuple[Any, bool]:
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
        # 根据参数选择认证协议
        if auth_protocol.lower() == 'sha':
            auth_proto = usmHMACSHAAuthProtocol
        else:
            auth_proto = usmHMACMD5AuthProtocol
            
        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create((ip, port))
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(user, authKey=auth_key, authProtocol=auth_proto, privProtocol=usmNoPrivProtocol),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if error_indication:
                logger.error(f"SNMP v3认证错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3认证错误状态: {error_status.prettyPrint()}")
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
    
    async def _get_snmp_v3_privacy(self, ip: str, user: str, auth_key: str, priv_key: str, oid: str, port: int = 161, auth_protocol: str = 'md5') -> Tuple[Any, bool]:
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
        # 根据参数选择认证协议
        if auth_protocol.lower() == 'sha':
            auth_proto = usmHMACSHAAuthProtocol
        else:
            auth_proto = usmHMACMD5AuthProtocol
            
        snmp_engine = SnmpEngine()
        try:
            transport_target = await UdpTransportTarget.create((ip, port))
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(user, authKey=auth_key, privKey=priv_key, authProtocol=auth_proto, privProtocol=usmDESPrivProtocol),
                transport_target,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if error_indication:
                logger.error(f"SNMP v3隐私错误: {error_indication}")
                return None, False
            elif error_status:
                logger.error(f"SNMP v3隐私错误状态: {error_status.prettyPrint()}")
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
    
    async def get_data(self, ip: str, version: str, oid: str, **kwargs) -> Tuple[Any, bool]:
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
        port = kwargs.get('port', 161)
        
        if version.lower() == 'v1':
            community = kwargs.get('community', 'public')
            return await self._get_snmp_v1(ip, community, oid, port)
        elif version.lower() == 'v2c':
            community = kwargs.get('community', 'public')
            return await self._get_snmp_v2c(ip, community, oid, port)
        elif version.lower() == 'v3':
            user = kwargs.get('user')
            if not user:
                logger.error("SNMP v3需要提供用户名")
                return None, False
                
            # 获取认证协议参数，默认为'md5'
            auth_protocol = kwargs.get('auth_protocol', 'md5')
            
            # 根据提供的参数确定安全级别
            auth_key = kwargs.get('auth_key')
            priv_key = kwargs.get('priv_key')
            
            if priv_key:
                # 隐私级别
                return await self._get_snmp_v3_privacy(ip, user, auth_key, priv_key, oid, port, auth_protocol)
            elif auth_key:
                # 认证级别
                return await self._get_snmp_v3_auth(ip, user, auth_key, oid, port, auth_protocol)
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
        
        # 获取系统描述
        value, success = await self.get_data(ip, version, self.OIDS['sysDescr'], **kwargs)
        if success:
            device_info['description'] = str(value) if value else ""
        
        # 获取系统名称
        value, success = await self.get_data(ip, version, self.OIDS['sysName'], **kwargs)
        if success:
            device_info['name'] = str(value) if value else ""
        
        # 获取系统位置
        value, success = await self.get_data(ip, version, self.OIDS['sysLocation'], **kwargs)
        if success:
            device_info['location'] = str(value) if value else ""
        
        # 获取系统运行时间
        value, success = await self.get_data(ip, version, self.OIDS['sysUpTime'], **kwargs)
        if success:
            device_info['uptime'] = str(value) if value else ""
            
        value, success = await self.get_data(ip, version, self.OIDS['sysObjectID'], **kwargs)
        if success:
            device_info['object_id'] = str(value) if value else ""
            
        return device_info
    
    async def get_interface_info(self, ip: str, version: str, **kwargs) -> List[Dict[str, Any]]:
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
        value, success = await self.get_data(ip, version, self.OIDS['ifNumber'], **kwargs)
        if not success:
            logger.error("无法获取接口数量")
            return interfaces
            
        if_count = int(value) if value else 0
        if if_count <= 0:
            return interfaces
            
        # 获取每个接口的信息
        for i in range(1, if_count + 1):
            interface = {'index': i}
            
            # 获取接口描述
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifDescr']}.{i}", **kwargs)
            if success:
                interface['description'] = str(value) if value else ""
            
            # 获取接口类型
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifType']}.{i}", **kwargs)
            if success:
                interface['type'] = int(value) if value else 0
            
            # 获取接口速度
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifSpeed']}.{i}", **kwargs)
            if success:
                interface['speed'] = int(value) if value else 0
            
            # 获取管理状态
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifAdminStatus']}.{i}", **kwargs)
            if success:
                interface['admin_status'] = int(value) if value else 0
            
            # 获取操作状态
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifOperStatus']}.{i}", **kwargs)
            if success:
                interface['oper_status'] = int(value) if value else 0
                
            interfaces.append(interface)
            
        return interfaces
    
    async def get_interface_traffic(self, ip: str, version: str, **kwargs) -> List[Dict[str, Any]]:
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
        value, success = await self.get_data(ip, version, self.OIDS['ifNumber'], **kwargs)
        if not success:
            logger.error("无法获取接口数量")
            return traffic_stats
            
        if_count = int(value) if value else 0
        if if_count <= 0:
            return traffic_stats
            
        # 获取每个接口的流量统计
        for i in range(1, if_count + 1):
            stats = {'index': i}
            
            # 获取接口描述
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifDescr']}.{i}", **kwargs)
            if success:
                stats['description'] = str(value) if value else ""
            
            # 获取接收字节数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifInOctets']}.{i}", **kwargs)
            if success:
                stats['in_octets'] = int(value) if value else 0
            
            # 获取发送字节数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifOutOctets']}.{i}", **kwargs)
            if success:
                stats['out_octets'] = int(value) if value else 0
                
            # 获取接收丢包数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifInDiscards']}.{i}", **kwargs)
            if success:
                stats['in_discards'] = int(value) if value else 0
                
            # 获取发送丢包数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifOutDiscards']}.{i}", **kwargs)
            if success:
                stats['out_discards'] = int(value) if value else 0
                
            # 获取接收错误数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifInErrors']}.{i}", **kwargs)
            if success:
                stats['in_errors'] = int(value) if value else 0
                
            # 获取发送错误数
            value, success = await self.get_data(ip, version, f"{self.OIDS['ifOutErrors']}.{i}", **kwargs)
            if success:
                stats['out_errors'] = int(value) if value else 0
                
            traffic_stats.append(stats)
            
        return traffic_stats

# 示例用法
if __name__ == "__main__":
    # 这里可以添加示例代码
    pass