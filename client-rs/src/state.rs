use serde::{Deserialize, Serialize};
use std::{fs, path::PathBuf};
use uuid::Uuid;

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct State {
    pub client_id: Option<String>,
    pub udp_port: Option<u16>,
    pub tcp_port: Option<u16>,
    pub collect_interval: Option<u64>,
}

pub fn app_dir() -> PathBuf {
    let exe = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("."));
    exe.parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."))
}

fn state_path() -> PathBuf {
    app_dir().join("client_state.json")
}

pub fn load_state() -> State {
    let p = state_path();
    if let Ok(s) = fs::read_to_string(&p) {
        if let Ok(st) = serde_json::from_str::<State>(&s) {
            return st;
        }
    }
    let st = State::default();
    let _ = save_state(&st);
    st
}

pub fn save_state(st: &State) -> std::io::Result<()> {
    let p = state_path();
    if let Some(parent) = p.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let s = serde_json::to_string_pretty(st).unwrap_or_else(|_| "{}".to_string());
    fs::write(p, s)
}

pub fn get_or_create_client_id() -> String {
    let mut st = load_state();
    if let Some(id) = st.client_id.clone() {
        return id;
    }
    let id = Uuid::new_v4().to_string();
    st.client_id = Some(id.clone());
    let _ = save_state(&st);
    id
}
