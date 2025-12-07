use crate::{config, state, system};
use serde_json::json;
use std::time::Duration;
use tokio::{io::AsyncWriteExt, net::TcpStream, sync::mpsc};

pub struct TcpClient {
    server_ip: Option<String>,
    server_port: Option<u16>,
    client_id: String,
}

impl TcpClient {
    pub fn new() -> Self {
        Self {
            server_ip: None,
            server_port: None,
            client_id: state::get_or_create_client_id(),
        }
    }

    pub fn set_server(&mut self, ip: String, port: u16) {
        self.server_ip = Some(ip);
        self.server_port = Some(port);
    }

    pub async fn connect_and_run(&mut self) -> anyhow::Result<()> {
        let ip = self
            .server_ip
            .clone()
            .ok_or_else(|| anyhow::anyhow!("no server"))?;
        let port = self.server_port.ok_or_else(|| anyhow::anyhow!("no port"))?;
        let addr = format!("{}:{}", ip, port);
        let mut stream = TcpStream::connect(addr).await?;
        let _ = stream.set_nodelay(true);
        self.handshake(&mut stream).await?;
        let base_interval = config::load_config().collect_interval;
        let (tx, mut rx) = mpsc::channel::<Vec<u8>>(16);
        let mut writer = stream;
        let _writer_task = tokio::spawn(async move {
            loop {
                match rx.recv().await {
                    Some(buf) => {
                        let res = tokio::time::timeout(
                            Duration::from_secs(5),
                            send_framed(&mut writer, &buf),
                        )
                        .await;
                        match res {
                            Ok(Ok(_)) => {}
                            Ok(Err(_)) => {
                                break;
                            }
                            Err(_) => {
                                break;
                            }
                        }
                    }
                    None => break,
                }
            }
        });
        loop {
            let snap = system::collect_system_info(self.client_id.clone()).await;
            let t0 = std::time::Instant::now();
            let mut buf = Vec::with_capacity(4096);
            serde_json::to_writer(&mut buf, &snap)?;
            let _ = tx.try_send(buf);
            let collect_ms = t0.elapsed().as_millis() as u64;
            let cpu = snap.cpu_info.usage_percent;
            let mem = snap.memory_info.percentage;
            let mut interval = base_interval;
            if cpu > 80 || mem > 85 {
                interval = std::cmp::min(base_interval * 3, 60);
            }
            log::debug!("collect={}ms", collect_ms);
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
