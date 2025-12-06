use crate::config;
use if_addrs::get_if_addrs;
use serde_json::json;
use socket2::{Domain, Socket, Type};
use std::net::ToSocketAddrs;
use std::net::{Ipv4Addr, SocketAddrV4};
use tokio::net::UdpSocket;

pub async fn discover_server_multicast() -> Option<(String, u16)> {
    let group = Ipv4Addr::new(239, 255, 1, 1);
    let port = 37020;
    let any = Ipv4Addr::UNSPECIFIED;
    let sock = Socket::new(Domain::IPV4, Type::DGRAM, None).ok()?;
    let addr = SocketAddrV4::new(any, port);
    let _ = sock.set_reuse_address(true);
    let _ = sock.bind(&addr.into());
    let _ = sock.join_multicast_v4(&group, &Ipv4Addr::UNSPECIFIED);
    let std_sock: std::net::UdpSocket = sock.into();
    let _ = std_sock.set_nonblocking(true);
    let socket = UdpSocket::from_std(std_sock).ok()?;
    let q = "DISCOVER|ANY";
    let _ = socket.send_to(q.as_bytes(), (group, port)).await.ok()?;
    let mut buf = [0u8; 1024];
    if let Ok((n, from)) = socket.recv_from(&mut buf).await {
        if n > 0 {
            if let Ok(v) = String::from_utf8(buf[..n].to_vec()) {
                if let Ok(j) = serde_json::from_str::<serde_json::Value>(&v) {
                    if j.get("type").and_then(|x| x.as_str()) == Some("discovery_response") {
                        if let Some(p) = j.get("tcp_port").and_then(|x| x.as_u64()) {
                            return Some((from.ip().to_string(), p as u16));
                        }
                    }
                }
            }
        }
    }
    None
}

pub async fn discover_server_broadcast() -> Option<(String, u16)> {
    let cfg = config::load_config();
    let sock = Socket::new(Domain::IPV4, Type::DGRAM, None).ok()?;
    let _ = sock.set_broadcast(true);
    let std_sock: std::net::UdpSocket = sock.into();
    let _ = std_sock.set_nonblocking(true);
    let socket = UdpSocket::from_std(std_sock).ok()?;
    let msg = json!({"type":"discovery","timestamp": chrono::Utc::now().to_rfc3339()}).to_string();

    let mut targets: Vec<std::net::SocketAddr> = Vec::new();
    // 处理占位符 "<broadcast>"，统一为 255.255.255.255
    let host = if cfg.udp_host.trim() == "<broadcast>" {
        "255.255.255.255".to_string()
    } else {
        cfg.udp_host.clone()
    };
    // 主广播地址
    if let Ok(mut addrs) = (host.as_str(), cfg.udp_port).to_socket_addrs() {
        if let Some(a) = addrs.next() {
            targets.push(a);
        }
    }
    // 按网卡收集 IPv4 广播地址，兼容 Windows/Linux
    if let Ok(ifaces) = get_if_addrs() {
        for iface in ifaces {
            if iface.is_loopback() {
                continue;
            }
            if is_virtual_iface(&iface.name) {
                continue;
            }
            match iface.addr {
                if_addrs::IfAddr::V4(v4) => {
                    if let Some(bv4) = v4.broadcast {
                        targets.push(std::net::SocketAddr::V4(std::net::SocketAddrV4::new(
                            bv4,
                            cfg.udp_port,
                        )));
                    } else {
                        let ip = v4.ip;
                        let mask = v4.netmask;
                        let bcast = std::net::Ipv4Addr::from(u32::from(ip) | !u32::from(mask));
                        targets.push(std::net::SocketAddr::V4(std::net::SocketAddrV4::new(
                            bcast,
                            cfg.udp_port,
                        )));
                    }
                }
                _ => {}
            }
        }
    }
    // 去重
    targets.sort_unstable();
    targets.dedup();
    // 发送到每个目标
    for t in targets.iter() {
        let _ = socket.send_to(msg.as_bytes(), *t).await.ok();
    }
    let mut buf = [0u8; 1024];
    // 设置超时，避免长期阻塞
    if let Ok(Ok((n, from))) = tokio::time::timeout(
        std::time::Duration::from_millis(800),
        socket.recv_from(&mut buf),
    )
    .await
    {
        if n > 0 {
            if let Ok(v) = String::from_utf8(buf[..n].to_vec()) {
                if let Ok(j) = serde_json::from_str::<serde_json::Value>(&v) {
                    if j.get("type").and_then(|x| x.as_str()) == Some("discovery_response") {
                        if let Some(p) = j.get("tcp_port").and_then(|x| x.as_u64()) {
                            return Some((from.ip().to_string(), p as u16));
                        }
                    }
                }
            }
        }
    }
    None
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
