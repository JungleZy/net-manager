export const formatOSInfo = (device) => {
  if (!device.os_name) return '未知'

  let osInfo = device.os_name
  if (device.os_version) {
    osInfo += ' ' + device.os_version
  }

  // 根据 machine_type 判断架构类型
  let architecture = device.os_architecture
  if (device.machine_type) {
    architecture += formatMachineType(device.machine_type)
  }

  if (architecture) {
    osInfo += ' (' + architecture + ')'
  }

  return osInfo
}
export const formatMachineType = (machineType) => {
  if (!machineType) return '未知'

  machineType = machineType.toLowerCase()
  if (machineType.includes('arm') || machineType.includes('aarch64')) {
    machineType = 'ARM'
  } else if (
    machineType.includes('x86') ||
    machineType.includes('amd64') ||
    machineType.includes('i386') ||
    machineType.includes('i686')
  ) {
    machineType = 'x86'
  } else {
    machineType = machineType
  }

  return machineType
}

/**
 * 根据设备描述智能推导设备类型
 * @param {string} description - 设备描述信息
 * @returns {string} 推导出的设备类型 (交换机/路由器/防火墙/服务器/打印机/电脑/笔记本/未知)
 */
export const deriveDeviceType = (description) => {
  if (!description) return '未知';

  // 统一转换为小写便于匹配
  const lowerDesc = description.toLowerCase();

  // 打印机识别
  if (lowerDesc.includes('printer') || lowerDesc.includes('laserjet') ||
    lowerDesc.includes('mfp') || lowerDesc.includes('officejet') ||
    lowerDesc.includes('deskjet') || lowerDesc.includes('打印机') ||
    lowerDesc.includes('epson') || lowerDesc.includes('canon') ||
    lowerDesc.includes('brother') || lowerDesc.includes('xerox') ||
    lowerDesc.includes('ricoh') || lowerDesc.includes('kyocera')) {
    return '打印机';
  }

  // 防火墙识别
  if (lowerDesc.includes('firewall') || lowerDesc.includes('防火墙') ||
    lowerDesc.includes('palo alto') || lowerDesc.includes('fortigate') ||
    lowerDesc.includes('checkpoint') || lowerDesc.includes('juniper srx') ||
    lowerDesc.includes('asa') || lowerDesc.includes('fortinet') ||
    lowerDesc.includes('ngfw') || lowerDesc.includes('utm')) {
    return '防火墙';
  }

  // 路由器识别
  if (lowerDesc.includes('router') || lowerDesc.includes('路由器') ||
    lowerDesc.includes('routing') || lowerDesc.includes('gateway') ||
    lowerDesc.includes('网关')) {
    return '路由器';
  }

  // 交换机识别
  if (lowerDesc.includes('switch') || lowerDesc.includes('交换机') ||
    lowerDesc.includes('catalyst') || lowerDesc.includes('nexus') ||
    lowerDesc.includes('procurve') || lowerDesc.includes('powerconnect') ||
    lowerDesc.includes('cloudengine') || lowerDesc.includes('ethernet switch')) {
    return '交换机';
  }

  // 服务器识别
  if (lowerDesc.includes('server') || lowerDesc.includes('服务器') ||
    lowerDesc.includes('poweredge') || lowerDesc.includes('proliant') ||
    lowerDesc.includes('thinksystem') || lowerDesc.includes('thinkserver') ||
    lowerDesc.includes('esxi') || lowerDesc.includes('vcenter') ||
    lowerDesc.includes('windows server') || lowerDesc.includes('linux server') ||
    lowerDesc.includes('centos') || lowerDesc.includes('ubuntu server') ||
    lowerDesc.includes('red hat')) {
    return '服务器';
  }

  // 笔记本识别
  if (lowerDesc.includes('laptop') || lowerDesc.includes('notebook') ||
    lowerDesc.includes('笔记本') || lowerDesc.includes('thinkpad') ||
    lowerDesc.includes('macbook') || lowerDesc.includes('latitude') ||
    lowerDesc.includes('elitebook') || lowerDesc.includes('pavilion')) {
    return '笔记本';
  }

  // PC识别
  if (lowerDesc.includes('desktop') || lowerDesc.includes('pc') ||
    lowerDesc.includes('台式机') || lowerDesc.includes('工作站') ||
    lowerDesc.includes('workstation') || lowerDesc.includes('optiplex') ||
    lowerDesc.includes('thinkcentre') || lowerDesc.includes('elitedesk') ||
    lowerDesc.includes('windows 10') || lowerDesc.includes('windows 11') ||
    lowerDesc.includes('imac')) {
    return '电脑';
  }

  // 根据常见厂商判断设备类型
  // 网络设备厂商
  if (description.includes('Cisco') || description.includes('Huawei') ||
    description.includes('H3C') || description.includes('Juniper') ||
    description.includes('Arista') || description.includes('华为') ||
    description.includes('思科') || description.includes('锐捷') ||
    description.includes('Ruijie')) {
    return '交换机'; // 默认为交换机
  }

  // 如果包含IP地址或MAC地址，可能是网络设备
  if (/\b(?:\d{1,3}\.){3}\d{1,3}\b/.test(description) ||
    /([0-9a-f]{2}[:-]){5}[0-9a-f]{2}/i.test(description)) {
    return '交换机';
  }

  // 默认返回未知类型
  return '未知';
};

/**
 * 根据设备描述智能推导设备名称
 * @param {string} description - 设备描述信息
 * @returns {string} 推导出的设备名称
 */
export const deriveDeviceName = (description) => {
  if (!description) return '';

  // 统一转换为小写便于匹配
  const lowerDesc = description.toLowerCase();

  // 华为设备识别 - 扩展更多型号
  if (description.includes('Huawei') || description.includes('华为')) {
    // 华为交换机型号识别 (S系列、CloudEngine系列等)
    const huaweiPatterns = [
      /s\d+-[a-z0-9]+/i,           // S系列如 S5720-28X-SI-AC, S5735-L24T4X-A1
      /cloudengine\s*\d+/i,        // CloudEngine系列
      /ce\d+-[a-z0-9]+/i          // CE系列
    ];

    for (const pattern of huaweiPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `华为${modelMatch[0]}交换机`;
      }
    }

    // 如果没有匹配到具体型号，则返回通用名称
    return '华为交换机';
  }

  // 思科设备识别 - 扩展更多型号
  if (description.includes('Cisco') || description.includes('思科')) {
    // 思科交换机型号识别 (Catalyst系列、Nexus系列等)
    const ciscoPatterns = [
      /catalyst\s*\d+[a-z0-9\-]*/i,  // Catalyst系列
      /nexus\s*\d+/i,                // Nexus系列
      /ws\-c\d+[a-z0-9\-]*/i         // WS-C系列
    ];

    for (const pattern of ciscoPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `思科${modelMatch[0]}交换机`;
      }
    }

    // 如果没有匹配到具体型号，则返回通用名称
    return '思科交换机';
  }

  // H3C设备识别 - 扩展更多型号
  if (description.includes('H3C')) {
    // H3C交换机型号识别 (S系列等)
    const h3cPatterns = [
      /s\d+[a-z0-9\-]*/i,            // S系列
      /h3c\s*[a-z0-9\-]+/i          // H3C+型号
    ];

    for (const pattern of h3cPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        // 清理匹配结果中的H3C前缀
        let modelName = modelMatch[0];
        if (modelName.toLowerCase().startsWith('h3c')) {
          modelName = modelName.substring(3).trim();
        }
        return modelName ? `H3C${modelName}交换机` : 'H3C交换机';
      }
    }

    // 如果没有匹配到具体型号，则返回通用名称
    return 'H3C交换机';
  }

  // 锐捷设备识别
  if (description.includes('Ruijie') || description.includes('锐捷')) {
    const ruijiePatterns = [
      /[a-z0-9]+\-?[a-z0-9]+/i      // 锐捷型号格式
    ];

    for (const pattern of ruijiePatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `锐捷${modelMatch[0]}交换机`;
      }
    }

    return '锐捷交换机';
  }

  // 戴尔设备识别
  if (description.includes('Dell') || description.includes('DELL') || description.includes('PowerConnect')) {
    const dellPatterns = [
      /powerconnect\s*\d+/i,         // PowerConnect系列
      /n\d+/i                        // N系列
    ];

    for (const pattern of dellPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `戴尔${modelMatch[0]}交换机`;
      }
    }

    return '戴尔交换机';
  }

  // Netgear设备识别
  if (description.includes('Netgear') || description.includes('NETGEAR')) {
    const netgearPatterns = [
      /gs\d+/i,                      // GS系列
      /gsm\d+/i,                     // GSM系列
      /fs\d+/i                       // FS系列
    ];

    for (const pattern of netgearPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `Netgear${modelMatch[0]}交换机`;
      }
    }

    return 'Netgear交换机';
  }

  // TP-LINK设备识别
  if (description.includes('TP-Link') || description.includes('TP_LINK') || description.includes('TPLINK')) {
    const tplinkPatterns = [
      /tl\-sg\d+/i,                  // TL-SG系列
      /tl\-sf\d+/i,                  // TL-SF系列
      /tl\-sh\d+/i                   // TL-SH系列
    ];

    for (const pattern of tplinkPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `TP-LINK${modelMatch[0]}交换机`;
      }
    }

    return 'TP-LINK交换机';
  }

  // Juniper设备识别
  if (description.includes('Juniper')) {
    const juniperPatterns = [
      /ex\d+/i,                      // EX系列交换机
      /qfx\d+/i,                     // QFX系列
      /srx\d+/i                      // SRX系列
    ];

    for (const pattern of juniperPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `Juniper${modelMatch[0]}交换机`;
      }
    }

    return 'Juniper交换机';
  }

  // Arista设备识别
  if (description.includes('Arista')) {
    const aristaPatterns = [
      /dcs\-?\d+[a-z]*/i             // DCS系列
    ];

    for (const pattern of aristaPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `Arista${modelMatch[0]}交换机`;
      }
    }

    return 'Arista交换机';
  }

  // HP设备识别（包括打印机、交换机等）
  if (description.includes('HP') || description.includes('惠普') || description.includes('Hewlett')) {
    // 首先检查是否是打印机
    if (lowerDesc.includes('laserjet') || lowerDesc.includes('printer') ||
      lowerDesc.includes('mfp') || lowerDesc.includes('officejet') ||
      lowerDesc.includes('deskjet') || lowerDesc.includes('打印机')) {

      // 尝试从PID字段提取型号
      const pidMatch = description.match(/PID:([^,]+)/i);
      if (pidMatch) {
        const model = pidMatch[1].trim();
        return model;
      }

      // 尝试匹配LaserJet等型号
      const printerPatterns = [
        /HP\s+LaserJet\s+[A-Z0-9\s]+/i,
        /HP\s+OfficeJet\s+[A-Z0-9\s]+/i,
        /HP\s+DeskJet\s+[A-Z0-9\s]+/i,
        /LaserJet\s+MFP\s+[A-Z0-9]+/i,
        /LaserJet\s+[A-Z0-9]+/i
      ];

      for (const pattern of printerPatterns) {
        const modelMatch = description.match(pattern);
        if (modelMatch) {
          return modelMatch[0].trim();
        }
      }

      return 'HP打印机';
    }

    // HP交换机识别
    const hpSwitchPatterns = [
      /procurve\s*\d+/i,             // ProCurve系列
      /\d+g\b/i,                     // 如2920G
      /aruba\s*\d+/i,                // Aruba系列
      /flexfabric\s*\d+/i            // FlexFabric系列
    ];

    for (const pattern of hpSwitchPatterns) {
      const modelMatch = description.match(pattern);
      if (modelMatch) {
        return `HP${modelMatch[0]}交换机`;
      }
    }

    return 'HP设备';
  }

  // 其他品牌设备
  if (description.includes('Switch') || description.includes('交换机') ||
    lowerDesc.includes('switch') || lowerDesc.includes('router') ||
    description.includes('路由器') || description.includes('Router')) {
    // 尝试提取品牌和型号
    const brandPatterns = [
      { pattern: /(HUAWEI|华为)/i, name: '华为' },
      { pattern: /(CISCO|思科)/i, name: '思科' },
      { pattern: /H3C/i, name: 'H3C' },
      { pattern: /(RUIJIE|锐捷)/i, name: '锐捷' },
      { pattern: /(TP\-LINK|TP_LINK|TPLINK)/i, name: 'TP-LINK' },
      { pattern: /(Dell|DELL|PowerConnect)/i, name: '戴尔' },
      { pattern: /(Netgear|NETGEAR)/i, name: 'Netgear' },
      { pattern: /Juniper/i, name: 'Juniper' },
      { pattern: /Arista/i, name: 'Arista' },
      { pattern: /(Extreme|EXTREME)/i, name: 'Extreme' },
      { pattern: /(Brocade|BROCADE)/i, name: 'Brocade' },
      { pattern: /(F5|F5 Networks)/i, name: 'F5' },
      { pattern: /(Palo Alto|PAN\-OS)/i, name: 'Palo Alto' }
    ];

    for (const brand of brandPatterns) {
      if (brand.pattern.test(description)) {
        const modelMatch = description.match(/([A-Z0-9\-]+[A-Z0-9\-]*)/i);
        return modelMatch ? `${brand.name}${modelMatch[1]}交换机` : `${brand.name}交换机`;
      }
    }

    return '交换机';
  }

  // 默认情况返回原始描述或空字符串
  return description || '';
}

