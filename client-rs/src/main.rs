mod config;
mod state;
mod system;
mod network;
mod core;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    env_logger::init();
    core::app_controller::run().await
}
