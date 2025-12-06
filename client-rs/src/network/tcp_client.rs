use tokio::{net::TcpStream, io::AsyncWriteExt};
use serde_json::json;
use std::time::Duration;
use crate::{state, system, config};

pub struct TcpClient {
    server_ip: Option<String>,
    server_port: Option<u16>,
    client_id: String,
}

impl TcpClient {
    pub fn new() -> Self { Self { server_ip: None, server_port: None, client_id: state::get_or_create_client_id() } }

    pub fn set_server(&mut self, ip: String, port: u16) { self.server_ip = Some(ip); self.server_port = Some(port); }

    pub async fn connect_and_run(&mut self) -> anyhow::Result<()> {
        let ip = self.server_ip.clone().ok_or_else(|| anyhow::anyhow!("no server"))?;
        let port = self.server_port.ok_or_else(|| anyhow::anyhow!("no port"))?;
        let addr = format!("{}:{}", ip, port);
        let mut stream = TcpStream::connect(addr).await?;
        self.handshake(&mut stream).await?;
        let interval = config::load_config().collect_interval;
        loop {
            let snap = system::collect_system_info(self.client_id.clone()).await;
            let msg = serde_json::to_string(&snap)?;
            send_framed(&mut stream, msg.as_bytes()).await?;
            tokio::time::sleep(Duration::from_secs(interval)).await;
        }
    }

    async fn handshake(&self, stream: &mut TcpStream) -> anyhow::Result<()> {
        let payload = json!({"type":"handshake","client_id": self.client_id, "timestamp": chrono::Utc::now().to_rfc3339()});
        let s = payload.to_string();
        send_framed(stream, s.as_bytes()).await?;
        Ok(())
    }
}

async fn send_framed(stream: &mut TcpStream, payload: &[u8]) -> anyhow::Result<()> {
    let len = (payload.len() as u32).to_be_bytes();
    stream.write_all(&len).await?;
    stream.write_all(payload).await?;
    Ok(())
}
