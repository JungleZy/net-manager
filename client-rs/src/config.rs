use serde::{Deserialize, Serialize};
use std::{fs, path::PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub udp_host: String,
    pub udp_port: u16,
    pub tcp_port: u16,
    pub collect_interval: u64,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            udp_host: "<broadcast>".to_string(),
            udp_port: 12345,
            tcp_port: 12346,
            collect_interval: 10,
        }
    }
}

pub fn app_dir() -> PathBuf {
    let exe = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("."));
    exe.parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."))
}

pub fn state_file_path() -> PathBuf {
    app_dir().join("client_state.json")
}

pub fn load_config() -> Config {
    let mut cfg = Config::default();
    let p = state_file_path();
    if let Ok(s) = fs::read_to_string(&p) {
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(&s) {
            if let Some(u) = v.get("udp_port").and_then(|x| x.as_u64()) {
                cfg.udp_port = u as u16;
            }
            if let Some(t) = v.get("tcp_port").and_then(|x| x.as_u64()) {
                cfg.tcp_port = t as u16;
            }
            if let Some(c) = v.get("collect_interval").and_then(|x| x.as_u64()) {
                cfg.collect_interval = c;
            }
        }
    }
    cfg
}
