use if_addrs::get_if_addrs;
use once_cell::sync::Lazy;
use serde::Serialize;
use std::sync::Mutex;
use std::{collections::HashMap, time::Instant};
use sysinfo::{Disks, Networks, System};

static SYS: Lazy<Mutex<System>> = Lazy::new(|| Mutex::new(System::new_all()));
static NETS: Lazy<Mutex<Networks>> = Lazy::new(|| Mutex::new(Networks::new_with_refreshed_list()));

#[derive(Serialize, Clone)]
pub struct ServiceInfo {
    pub protocol: String,
    pub local_address: String,
    pub status: String,
    pub pid: Option<i32>,
    pub process_name: Option<String>,
}

#[derive(Serialize, Clone)]
pub struct ProcessInfo {
    pub pid: i32,
    pub name: String,
    pub cpu_percent: f32,
    pub memory_percent: f32,
    pub status: String,
}

#[derive(Serialize, Clone)]
pub struct InterfaceInfo {
    pub name: String,
    pub ip_address: String,
    pub mac_address: String,
    pub gateway: String,
    pub netmask: String,
    pub upload_rate: u64,
    pub download_rate: u64,
}

#[derive(Serialize, Clone)]
pub struct CpuInfo {
    pub cores: usize,
    pub usage_percent: u32,
    pub per_cpu_percent: Vec<u32>,
    pub current_frequency: Option<f32>,
    pub max_frequency: Option<f32>,
}

#[derive(Serialize, Clone)]
pub struct MemoryInfo {
    pub total: u64,
    pub available: u64,
    pub used: u64,
    pub percentage: u32,
}

#[derive(Serialize, Clone)]
pub struct DiskPartition {
    pub device: String,
    pub mountpoint: String,
    pub file_system: String,
    pub total: u64,
    pub used: u64,
    pub free: u64,
    pub percentage: u32,
}

#[derive(Serialize, Clone)]
pub struct DiskInfo {
    pub partitions: Vec<DiskPartition>,
    pub total: u64,
    pub used: u64,
    pub free: u64,
    pub percentage: u32,
}

#[derive(Serialize, Clone)]
pub struct SystemSnapshot {
    pub client_id: String,
    pub hostname: String,
    pub os_name: String,
    pub os_version: String,
    pub os_architecture: String,
    pub machine_type: String,
    pub services: Vec<ServiceInfo>,
    pub processes: Vec<ProcessInfo>,
    pub networks: Vec<InterfaceInfo>,
    pub cpu_info: CpuInfo,
    pub memory_info: MemoryInfo,
    pub disk_info: DiskInfo,
    pub timestamp: String,
}

// 全局网络速率缓存：记录上次采集的字节数与时间戳
static NET_CACHE: Lazy<Mutex<HashMap<String, (u64, u64, Instant)>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

pub async fn collect_system_info(client_id: String) -> SystemSnapshot {
    let mut sys = SYS.lock().unwrap();
    sys.refresh_cpu_usage();
    sys.refresh_memory();

    let hostname = System::host_name().unwrap_or_else(|| "unknown".to_string());
    let os_name = System::name().unwrap_or_else(|| std::env::consts::OS.to_string());
    let os_version = System::os_version().unwrap_or_else(|| "unknown".to_string());
    let os_architecture = std::env::consts::ARCH.to_string();
    let machine_type = arch_to_machine_type(std::env::consts::ARCH);

    sys.refresh_cpu_usage();
    let cpu_usage = {
        let v = sys.global_cpu_usage();
        let v = v.floor() as u32;
        v.min(100)
    };
    let per_cpu = sys
        .cpus()
        .iter()
        .map(|c| {
            let v = c.cpu_usage();
            let v = v.floor() as u32;
            v.min(100)
        })
        .collect::<Vec<_>>();
    let cpu_freq = sys.cpus().get(0).map(|c| c.frequency() as f32);
    let cpu_info = CpuInfo {
        cores: sys.cpus().len(),
        usage_percent: cpu_usage,
        per_cpu_percent: per_cpu,
        current_frequency: cpu_freq,
        max_frequency: None,
    };

    let mem_total = sys.total_memory();
    let mem_used = sys.used_memory();
    let mem_available = sys.available_memory();
    let mem_percent = if mem_total > 0 {
        let v = (mem_used as f32 / mem_total as f32) * 100.0;
        let v = v.floor() as u32;
        v.min(100)
    } else {
        0
    };
    let memory_info = MemoryInfo {
        total: mem_total,
        available: mem_available,
        used: mem_used,
        percentage: mem_percent,
    };

    let mut partitions = Vec::new();
    let mut total_disk = 0u64;
    let mut used_disk = 0u64;
    let disks = Disks::new_with_refreshed_list();
    for d in disks.list() {
        let total = d.total_space();
        let avail = d.available_space();
        let used = total.saturating_sub(avail);
        let pct = if total > 0 {
            let v = (used as f32 / total as f32) * 100.0;
            let v = v.floor() as u32;
            v.min(100)
        } else {
            0
        };
        partitions.push(DiskPartition {
            device: d.name().to_string_lossy().into(),
            mountpoint: d.mount_point().to_string_lossy().into(),
            file_system: d.file_system().to_string_lossy().into(),
            total,
            used,
            free: avail,
            percentage: pct,
        });
        total_disk = total_disk.saturating_add(total);
        used_disk = used_disk.saturating_add(used);
    }
    let disk_pct = if total_disk > 0 {
        let v = (used_disk as f32 / total_disk as f32) * 100.0;
        let v = v.floor() as u32;
        v.min(100)
    } else {
        0
    };
    let disk_info = DiskInfo {
        partitions,
        total: total_disk,
        used: used_disk,
        free: total_disk.saturating_sub(used_disk),
        percentage: disk_pct,
    };

    let mut procs = sys
        .processes()
        .values()
        .map(|p| ProcessInfo {
            pid: p.pid().as_u32() as i32,
            name: p.name().to_string_lossy().into(),
            cpu_percent: p.cpu_usage(),
            memory_percent: 0.0,
            status: format!("{:?}", p.status()),
        })
        .collect::<Vec<_>>();
    procs.sort_by(|a, b| {
        b.cpu_percent
            .partial_cmp(&a.cpu_percent)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    // 不限制进程数量，返回全部进程

    drop(sys);
    let networks = collect_interfaces().await;

    SystemSnapshot {
        client_id,
        hostname,
        os_name,
        os_version,
        os_architecture,
        machine_type,
        services: Vec::new(),
        processes: procs,
        networks,
        cpu_info,
        memory_info,
        disk_info,
        timestamp: chrono::Utc::now().to_rfc3339(),
    }
}

async fn collect_interfaces() -> Vec<InterfaceInfo> {
    let mut nets = NETS.lock().unwrap();
    nets.refresh(true);

    let mut res = Vec::new();
    if let Ok(addrs) = get_if_addrs() {
        for iface in addrs {
            if iface.is_loopback() {
                continue;
            }
            let ip_v4 = match iface.ip() {
                std::net::IpAddr::V4(v4) => v4,
                _ => continue,
            };
            let ip = ip_v4.to_string();
            let name = iface.name.clone();
            if is_virtual_iface(&name) {
                continue;
            }

            // 计算速率：基于 sysinfo 的累计字节数与缓存差分
            let (upload_rate, download_rate) = {
                let entry = nets
                    .list()
                    .iter()
                    .find(|(n_name, _)| n_name.as_str() == name.as_str())
                    .or_else(|| {
                        nets.list().iter().find(|(n_name, _)| {
                            n_name.to_lowercase().contains(&name.to_lowercase())
                        })
                    });
                if let Some((_, n)) = entry {
                    let tx = n.total_transmitted();
                    let rx = n.total_received();
                    let mut cache = NET_CACHE.lock().unwrap();
                    let now = Instant::now();
                    if let Some((prev_tx, prev_rx, prev_t)) = cache.get(&name).cloned() {
                        let dt = now.duration_since(prev_t).as_secs_f64();
                        if dt < 0.5 {
                            cache.insert(name.clone(), (tx, rx, now));
                            (0, 0)
                        } else {
                            let up_bps = (tx.saturating_sub(prev_tx)) as f64 / dt;
                            let down_bps = (rx.saturating_sub(prev_rx)) as f64 / dt;
                            let up_kbps = (up_bps / 1024.0).floor() as u64;
                            let down_kbps = (down_bps / 1024.0).floor() as u64;
                            cache.insert(name.clone(), (tx, rx, now));
                            (up_kbps, down_kbps)
                        }
                    } else {
                        cache.insert(name.clone(), (tx, rx, now));
                        (0, 0)
                    }
                } else {
                    (0, 0)
                }
            };

            let netmask = match iface.addr {
                if_addrs::IfAddr::V4(v4) => v4.netmask.to_string(),
                _ => String::new(),
            };

            let mac_address = get_mac_address(&name, &ip);

            // 获取默认网关（按平台分别处理）
            let gateway = get_default_gateway_for_ip(&ip);

            res.push(InterfaceInfo {
                name,
                ip_address: ip,
                mac_address,
                gateway,
                netmask,
                upload_rate,
                download_rate,
            });
        }
    }
    res
}

fn is_virtual_iface(name: &str) -> bool {
    let n = name.to_lowercase();
    let patterns = [
        "veth", "docker", "br-", "vmware", "vbox", "hyper-v", "wsl", "tun", "tap",
    ];
    if n.starts_with('{') && n.ends_with('}') {
        return true;
    }
    patterns.iter().any(|p| n.contains(p))
}

// 按平台获取 MAC 地址
fn get_mac_address(iface_name: &str, ip: &str) -> String {
    #[cfg(target_os = "linux")]
    {
        let p = format!("/sys/class/net/{}/address", iface_name);
        if let Ok(s) = std::fs::read_to_string(&p) {
            return s.trim().to_string();
        }
        return String::new();
    }
    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        // 先尝试通过 IP 精确匹配接口别名，再获取 MAC
        if let Ok(alias_out) = Command::new("powershell").args([
            "-Command",
            &format!(
                "(Get-NetIPConfiguration | Where-Object {{ $_.IPv4Address.IPAddress -eq '{}' }} | Select-Object -First 1 -ExpandProperty InterfaceAlias)"
                , ip)
        ]).output() {
            let alias = String::from_utf8_lossy(&alias_out.stdout).trim().to_string();
            if !alias.is_empty() {
                if let Ok(mac_out) = Command::new("powershell").args([
                    "-Command",
                    &format!(
                        "(Get-NetAdapter -Name '{}' | Select-Object -First 1 -ExpandProperty MacAddress)"
                        , alias)
                ]).output() {
                    let mac = String::from_utf8_lossy(&mac_out.stdout).trim().to_string();
                    if !mac.is_empty() {
                        return mac.replace("-", ":");
                    }
                }
            }
        }
        // 回退：按名称粗略解析 ipconfig 输出
        if let Ok(o) = Command::new("ipconfig").arg("/all").output() {
            let text = String::from_utf8_lossy(&o.stdout);
            let mut current_block = String::new();
            let mut blocks = Vec::new();
            for line in text.lines() {
                if line.trim().ends_with(":") {
                    if !current_block.is_empty() {
                        blocks.push(current_block.clone());
                    }
                    current_block.clear();
                }
                current_block.push_str(line);
                current_block.push('\n');
            }
            blocks.push(current_block);
            for b in blocks {
                if b.to_lowercase().contains(&iface_name.to_lowercase()) || b.contains(ip) {
                    for l in b.lines() {
                        let ll = l.to_lowercase();
                        if ll.contains("physical address") || ll.contains("物理地址") {
                            if let Some(pos) = l.find(":") {
                                return l[pos + 1..].trim().replace("-", ":");
                            }
                        }
                    }
                }
            }
        }
        String::new()
    }
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let out = Command::new("ifconfig").arg(iface_name).output();
        if let Ok(o) = out {
            let text = String::from_utf8_lossy(&o.stdout);
            for l in text.lines() {
                if l.trim().starts_with("ether ") {
                    return l.trim()[6..].trim().to_string();
                }
            }
        }
        String::new()
    }
}

// 按平台解析默认网关，并仅在与传入 IP 匹配的接口返回
fn get_default_gateway_for_ip(_ip: &str) -> String {
    #[cfg(target_os = "linux")]
    {
        // 解析 /proc/net/route 获取十六进制网关，按小端转换
        if let Ok(s) = std::fs::read_to_string("/proc/net/route") {
            for line in s.lines().skip(1) {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 3 && parts[1] == "00000000" {
                    // 默认路由
                    let gw_hex = parts[2];
                    if let Some(gw) = hex_to_ip_le(gw_hex) {
                        return gw;
                    }
                }
            }
        }
        String::new()
    }
    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        // 使用 PowerShell 读取默认网关
        let out = Command::new("powershell").args(["-Command","Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -First 1 -ExpandProperty NextHop"]).output();
        if let Ok(o) = out {
            let gw = String::from_utf8_lossy(&o.stdout).trim().to_string();
            if gw.contains('.') {
                return gw;
            }
        }
        String::new()
    }
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let out = Command::new("route")
            .args(["-n", "get", "default"])
            .output();
        if let Ok(o) = out {
            let text = String::from_utf8_lossy(&o.stdout);
            for l in text.lines() {
                if l.trim().starts_with("gateway:") {
                    return l.split(':').nth(1).unwrap_or("").trim().to_string();
                }
            }
        }
        String::new()
    }
}

// Linux: 将小端十六进制 IP 转为点分十进制
#[cfg(target_os = "linux")]
fn hex_to_ip_le(hex_ip: &str) -> Option<String> {
    if hex_ip.len() != 8 {
        return None;
    }
    let bytes = (0..4)
        .map(|i| u8::from_str_radix(&hex_ip[i * 2..i * 2 + 2], 16).ok())
        .collect::<Option<Vec<_>>>()?;
    Some(format!(
        "{}.{}.{}.{}",
        bytes[3], bytes[2], bytes[1], bytes[0]
    ))
}
fn arch_to_machine_type(arch: &str) -> String {
    match arch {
        "x86_64" => "x64".to_string(),
        "x86" | "i686" => "x86".to_string(),
        "aarch64" => "arm64".to_string(),
        "arm" | "armv7" | "armv6" => "arm".to_string(),
        other => other.to_string(),
    }
}
