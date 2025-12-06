use crate::config::Config;
#[cfg(target_os = "linux")]
use std::fs;
#[cfg(target_os = "linux")]
use std::io::Write;
use std::path::PathBuf;

pub fn setup_autostart(cfg: &Config) {
    if !cfg.autostart {
        return;
    }
    #[cfg(windows)]
    {
        use winreg::enums::HKEY_CURRENT_USER;
        use winreg::RegKey;
        let exe = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("client-rs.exe"));
        let val = format!("\"{}\"", exe.display());
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        let path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
        if let Ok((key, _)) = hkcu.create_subkey(path) {
            let _ = key.set_value("NetManagerClient", &val);
        }
    }
    #[cfg(target_os = "linux")]
    {
        let exe = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("client-rs"));
        let conf_home = std::env::var("XDG_CONFIG_HOME")
            .ok()
            .map(PathBuf::from)
            .unwrap_or_else(|| {
                std::env::var("HOME")
                    .ok()
                    .map(PathBuf::from)
                    .unwrap_or_else(|| PathBuf::from("."))
                    .join(".config")
            });
        let dir = conf_home.join("autostart");
        let _ = fs::create_dir_all(&dir);
        let file = dir.join("net-manager-client.desktop");
        let content = format!(
            "[Desktop Entry]\nType=Application\nName=Net Manager Client\nExec=\"{}\"\nTerminal=false\nX-GNOME-Autostart-enabled=true\n",
            exe.display()
        );
        write_if_changed(file, content);
    }
    // macOS not supported: client only targets Windows/Linux
}

#[cfg(target_os = "linux")]
fn write_if_changed(path: PathBuf, content: String) {
    match fs::read(&path) {
        Ok(existing) => {
            if existing == content.as_bytes() {
                return;
            }
        }
        Err(_) => {}
    }
    if let Ok(mut f) = fs::File::create(&path) {
        let _ = f.write_all(content.as_bytes());
    }
}
