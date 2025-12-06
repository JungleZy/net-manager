$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
Push-Location $proj
New-Item -ItemType Directory -Force -Path "$proj/dist" | Out-Null

Write-Host "Building Windows x64..."
cargo build --release
if (Test-Path "$proj/target/release/client-rs.exe") {
  Copy-Item "$proj/target/release/client-rs.exe" "$proj/dist/client-rs-windows-x64.exe" -Force
}

Write-Host "Building Linux x64 (musl)..."
try {
  $installed = & rustup target list --installed
  if ($installed -notmatch "x86_64-unknown-linux-musl") { & rustup target add x86_64-unknown-linux-musl }
  if (Get-Command musl-gcc -ErrorAction SilentlyContinue) {
    cargo build --release --target x86_64-unknown-linux-musl
    if (Test-Path "$proj/target/x86_64-unknown-linux-musl/release/client-rs") {
      Copy-Item "$proj/target/x86_64-unknown-linux-musl/release/client-rs" "$proj/dist/client-rs-linux-x64" -Force
    }
  } else { Write-Host "musl-gcc not found, skipping x86_64-unknown-linux-musl" }
} catch {}

Write-Host "Building Linux arm64 (musl)..."
try {
  $installed = & rustup target list --installed
  if ($installed -notmatch "aarch64-unknown-linux-musl") { & rustup target add aarch64-unknown-linux-musl }
  if (Get-Command aarch64-linux-musl-gcc -ErrorAction SilentlyContinue) {
    cargo build --release --target aarch64-unknown-linux-musl
    if (Test-Path "$proj/target/aarch64-unknown-linux-musl/release/client-rs") {
      Copy-Item "$proj/target/aarch64-unknown-linux-musl/release/client-rs" "$proj/dist/client-rs-linux-arm64" -Force
    }
  } else { Write-Host "aarch64-linux-musl-gcc not found, skipping aarch64-unknown-linux-musl" }
} catch {}

Write-Host "Artifacts in dist/"
Get-ChildItem "$proj/dist"
Pop-Location
