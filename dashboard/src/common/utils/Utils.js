export const formatOSInfo = (device) => {
  if (!device.os_name) return '未知'

  let osInfo = device.os_name
  if (device.os_version) {
    osInfo += ' ' + device.os_version
  }

  // 根据 machine_type 判断架构类型
  let architecture = device.os_architecture
  if (device.machine_type) {
    // 根据 machine_type 判断架构
    const machineType = device.machine_type.toLowerCase()
    if (machineType.includes('arm') || machineType.includes('aarch64')) {
      architecture += '-ARM'
    } else if (
      machineType.includes('x86') ||
      machineType.includes('amd64') ||
      machineType.includes('i386') ||
      machineType.includes('i686')
    ) {
      architecture += '-x86'
    } else {
      architecture = device.machine_type
    }
  }

  if (architecture) {
    osInfo += ' (' + architecture + ')'
  }

  return osInfo
}

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