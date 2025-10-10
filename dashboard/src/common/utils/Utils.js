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