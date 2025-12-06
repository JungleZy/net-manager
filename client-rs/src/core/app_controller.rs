use crate::{
    config,
    network::{tcp_client::TcpClient, udp_client},
};
use tokio::signal;

pub async fn run() -> anyhow::Result<()> {
    let cfg = config::load_config();
    let mut delay = std::time::Duration::from_secs(2);
    loop {
        let server = udp_client::discover_server_multicast()
            .await
            .or(udp_client::discover_server_broadcast().await);
        let (ip, port) = match server {
            Some((ip, p)) => (ip, p),
            None => ("127.0.0.1".to_string(), cfg.tcp_port),
        };
        let mut tcp = TcpClient::new();
        tcp.set_server(ip, port);
        tokio::select! {
            _ = signal::ctrl_c() => {
                log::info!("shutdown by ctrl-c");
                return Ok(())
            }
            res = tcp.connect_and_run() => {
                match res {
                    Ok(()) => return Ok(()),
                    Err(e) => {
                        log::warn!("connect failed: {}", e);
                        tokio::time::sleep(delay).await;
                        delay = std::cmp::min(delay * 2, std::time::Duration::from_secs(30));
                    }
                }
            }
        }
    }
}
