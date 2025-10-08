from typing import Dict, List, Tuple, Any
import re
from pysnmp.smi import builder, view, compiler
from pysnmp.smi.rfc1902 import ObjectIdentity
import logging

# 配置日志
logger = logging.getLogger(__name__)

class OIDClassifier:
    """
    OID分类器，用于智能识别和分类OID
    """
    
    # OID分类映射
    OID_CATEGORIES = {
        'system': [
            '1.3.6.1.2.1.1',  # system
        ],
        'interfaces': [
            '1.3.6.1.2.1.2',  # interfaces
            '1.3.6.1.2.1.31', # ifXTable
        ],
        'ip': [
            '1.3.6.1.2.1.4',  # ip
        ],
        'icmp': [
            '1.3.6.1.2.1.5',  # icmp
        ],
        'tcp': [
            '1.3.6.1.2.1.6',  # tcp
        ],
        'udp': [
            '1.3.6.1.2.1.7',  # udp
        ],
        'snmp': [
            '1.3.6.1.2.1.11', # snmp
        ],
        'cpu': [
            '1.3.6.1.4.1.9.9.109',  # Cisco CPU
            '1.3.6.1.4.1.2011.11',   # UCD-SNMP-MIB CPU
            '1.3.6.1.4.1.2011.6.3.4',   # HUAWEI-SNMP-MIB CPU
        ],
        'memory': [
            '1.3.6.1.4.1.9.9.48',   # Cisco Memory
            '1.3.6.1.4.1.2021.4',   # UCD-SNMP-MIB Memory
            '1.3.6.1.4.1.2011.6.3.5',   # HUAWEI-SNMP-MIB Memory
        ],
        'disk': [
            '1.3.6.1.4.1.2021.9',   # UCD-SNMP-MIB Disk
        ]
    }
    
    # 常用OID名称映射
    OID_NAMES = {
        # System OIDs
        '1.3.6.1.2.1.1.1.0': 'sysDescr',
        '1.3.6.1.2.1.1.2.0': 'sysObjectID',
        '1.3.6.1.2.1.1.3.0': 'sysUpTime',
        '1.3.6.1.2.1.1.4.0': 'sysContact',
        '1.3.6.1.2.1.1.5.0': 'sysName',
        '1.3.6.1.2.1.1.6.0': 'sysLocation',
        
        # Interface OIDs
        '1.3.6.1.2.1.2.1.0': 'ifNumber',
        '1.3.6.1.2.1.2.2.1.1': 'ifIndex',
        '1.3.6.1.2.1.2.2.1.2': 'ifDescr',
        '1.3.6.1.2.1.2.2.1.3': 'ifType',
        '1.3.6.1.2.1.2.2.1.4': 'ifMtu',
        '1.3.6.1.2.1.2.2.1.5': 'ifSpeed',
        '1.3.6.1.2.1.2.2.1.6': 'ifPhysAddress',
        '1.3.6.1.2.1.2.2.1.7': 'ifAdminStatus',
        '1.3.6.1.2.1.2.2.1.8': 'ifOperStatus',
        '1.3.6.1.2.1.2.2.1.10': 'ifInOctets',
        '1.3.6.1.2.1.2.2.1.11': 'ifInUcastPkts',
        '1.3.6.1.2.1.2.2.1.12': 'ifInNUcastPkts',
        '1.3.6.1.2.1.2.2.1.13': 'ifInDiscards',
        '1.3.6.1.2.1.2.2.1.14': 'ifInErrors',
        '1.3.6.1.2.1.2.2.1.16': 'ifOutOctets',
        '1.3.6.1.2.1.2.2.1.17': 'ifOutUcastPkts',
        '1.3.6.1.2.1.2.2.1.18': 'ifOutNUcastPkts',
        '1.3.6.1.2.1.2.2.1.19': 'ifOutDiscards',
        '1.3.6.1.2.1.2.2.1.20': 'ifOutErrors',
        
        # CPU OIDs (common ones)
        '1.3.6.1.4.1.9.9.109.1.1.1.1.7': 'cpmCPUTotal5minRev',
        '1.3.6.1.4.1.2021.11.9.0': 'ssCpuUser',
        '1.3.6.1.4.1.2021.11.10.0': 'ssCpuSystem',
        '1.3.6.1.4.1.2021.11.11.0': 'ssCpuIdle',
        '1.3.6.1.4.1.2011.6.3.4.1.1': 'hwCpuDevDuty',  # 华为CPU使用率
        
        # Memory OIDs (common ones)
        '1.3.6.1.4.1.9.9.48.1.1.1.5': 'ciscoMemoryPoolUsed',
        '1.3.6.1.4.1.9.9.48.1.1.1.6': 'ciscoMemoryPoolFree',
        '1.3.6.1.4.1.2021.4.5.0': 'memTotalReal',
        '1.3.6.1.4.1.2021.4.6.0': 'memAvailReal',
        '1.3.6.1.4.1.2021.4.11.0': 'memTotalSwap',
        '1.3.6.1.4.1.2021.4.12.0': 'memAvailSwap',
        '1.3.6.1.4.1.2011.6.3.5.1.1.2': 'hwMemoryDevFree',  # 华为内存空闲
        '1.3.6.1.4.1.2011.6.3.5.1.1.3': 'hwMemoryDevSize',   # 华为内存总量
    }
    
    def __init__(self):
        """初始化OID分类器"""
        self.mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(self.mib_builder)
        
        # 尝试编译一些常用的MIB
        try:
            compiler.addMibCompiler(self.mib_builder, sources=['file:///usr/share/snmp/mibs', 'http://mibs.snmplabs.com/asn1/@mib@'])
        except Exception as e:
            logger.warning(f"无法加载MIB文件: {e}")
    
    def classify_oid(self, oid: str) -> str:
        """
        根据OID分类映射对OID进行分类
        
        Args:
            oid: 要分类的OID
            
        Returns:
            OID的分类名称
        """
        for category, oid_prefixes in self.OID_CATEGORIES.items():
            for prefix in oid_prefixes:
                if oid.startswith(prefix):
                    return category
        return 'unknown'
    
    def get_oid_name(self, oid: str) -> str:
        """
        获取OID的名称
        
        Args:
            oid: OID字符串
            
        Returns:
            OID的名称，如果未找到则返回原始OID
        """
        # 首先尝试从预定义映射中查找
        if oid in self.OID_NAMES:
            return self.OID_NAMES[oid]
        
        # 尝试使用MIB解析
        try:
            object_identity = ObjectIdentity(oid)
            object_identity.resolveWithMib(self.mib_view_controller)
            return str(object_identity.getMibSymbol()[1])
        except Exception as e:
            logger.debug(f"无法解析OID {oid}: {e}")
            return oid
    
    def parse_oid_value(self, oid: str, value: Any) -> Dict[str, Any]:
        """
        解析OID值，根据OID类型进行适当的格式化
        
        Args:
            oid: OID字符串
            value: OID的值
            
        Returns:
            包含解析后信息的字典
        """
        result = {
            'oid': oid,
            'name': self.get_oid_name(oid),
            'category': self.classify_oid(oid),
            'raw_value': value,
            'formatted_value': str(value),
            'value_type': type(value).__name__
        }
        
        # 根据OID类型进行特殊处理
        if 'ifSpeed' in oid and value:
            # 接口速度转换为Mbps
            try:
                speed_bps = int(value)
                speed_mbps = speed_bps / 1000000
                result['formatted_value'] = f"{speed_mbps} Mbps"
            except (ValueError, TypeError):
                pass
        elif 'Octets' in self.get_oid_name(oid) and value:
            # 流量数据转换为更可读的格式
            try:
                bytes_value = int(value)
                if bytes_value >= 1024 * 1024 * 1024:  # GB
                    result['formatted_value'] = f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"
                elif bytes_value >= 1024 * 1024:  # MB
                    result['formatted_value'] = f"{bytes_value / (1024 * 1024):.2f} MB"
                elif bytes_value >= 1024:  # KB
                    result['formatted_value'] = f"{bytes_value / 1024:.2f} KB"
                else:  # B
                    result['formatted_value'] = f"{bytes_value} B"
            except (ValueError, TypeError):
                pass
        elif 'PhysAddress' in oid and value:
            # 物理地址格式化为MAC地址
            try:
                if isinstance(value, str):
                    # 尝试将字符串转换为MAC地址格式
                    mac = ':'.join([f'{ord(c):02x}' for c in value])
                    result['formatted_value'] = mac.upper()
                elif hasattr(value, 'asNumbers'):
                    # SNMP OctetString类型
                    numbers = value.asNumbers()
                    mac = ':'.join([f'{n:02x}' for n in numbers])
                    result['formatted_value'] = mac.upper()
            except Exception as e:
                logger.debug(f"无法格式化MAC地址: {e}")
        
        return result
    
    def identify_device_type(self, sys_object_id: str) -> str:
        """
        根据sysObjectID识别设备类型
        
        Args:
            sys_object_id: sysObjectID OID值
            
        Returns:
            设备类型字符串
        """
        # 企业OID前缀
        enterprise_oids = {
            '1.3.6.1.4.1.9': 'Cisco',
            '1.3.6.1.4.1.1991': 'Brocade',
            '1.3.6.1.4.1.25506': 'H3C',
            '1.3.6.1.4.1.2011': 'Huawei',
            '1.3.6.1.4.1.1916': 'Extreme',
            '1.3.6.1.4.1.2272': 'Nortel',
            '1.3.6.1.4.1.311': 'Microsoft',
            '1.3.6.1.4.1.318': 'APC',
            '1.3.6.1.4.1.11': 'HP',
        }
        
        for oid_prefix, vendor in enterprise_oids.items():
            if sys_object_id.startswith(oid_prefix):
                return vendor
                
        return 'Unknown'
    
    def get_recommended_oids(self, device_type: str = 'generic') -> List[str]:
        """
        根据设备类型获取推荐监控的OID列表
        
        Args:
            device_type: 设备类型
            
        Returns:
            推荐的OID列表
        """
        # 基础OID（所有设备都应该支持）
        base_oids = [
        ]
        
        # 根据设备类型添加特定OID
        if device_type.lower() == 'cisco':
            base_oids.extend([
                '1.3.6.1.4.1.9.9.109.1.1.1.1.7',  # CPU使用率
                '1.3.6.1.4.1.9.9.48.1.1.1.5',     # 内存使用
            ])
        elif device_type.lower() == 'huawei':
            # 华为设备使用华为特定OID
            base_oids.extend([
                '1.3.6.1.4.1.2011.6.3.4.1.1',  # 华为CPU使用率
                '1.3.6.1.4.1.2011.6.3.5.1.1.2', # 华为内存使用
                '1.3.6.1.4.1.2011.6.3.5.1.1.3', # 华为内存总量
            ])
        elif device_type.lower() == 'generic':
            # 通用设备使用标准OID
            base_oids.extend([
                '1.3.6.1.4.1.2021.11.9.0',  # CPU用户态
                '1.3.6.1.4.1.2021.11.10.0', # CPU系统态
                '1.3.6.1.4.1.2021.11.11.0', # CPU空闲
                '1.3.6.1.4.1.2021.4.6.0',   # 可用内存
                '1.3.6.1.4.1.2021.4.5.0',   # 总内存
            ])
            
        return base_oids

# 示例用法
if __name__ == "__main__":
    # 这里可以添加示例代码
    pass