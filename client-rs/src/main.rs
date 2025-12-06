mod autostart;
mod config;
mod core;
mod network;
mod state;
mod system;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    env_logger::init();
    let cfg = config::load_config();
    let _ = state::load_state();
    if !cfg!(debug_assertions) {
        autostart::setup_autostart(&cfg);
    }
    core::app_controller::run().await
}
