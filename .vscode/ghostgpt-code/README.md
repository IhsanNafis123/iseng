# GhostGPT Code — Ekstensi VS Code

Generate kode lengkap dengan GhostGPT.io dan aplikasikan langsung di VS Code.

## Perintah

| Perintah | Keterangan |
|----------|------------|
| `GhostGPT: Set API Key` | Simpan API Key GhostGPT (dapatkan di ghostgpt.io) |
| `GhostGPT: Generate Code` | Deskripsi kode yang diinginkan, hasil disimpan sebagai file dan dibuka di editor |
| `GhostGPT: Chat` | Obrolan singkat dengan GhostGPT, hasil ditampilkan di Output panel |

## Cara pakai

1. Install ekstensi ini di VS Code (atau buka folder `.vscode/ghostgpt-code` sebagai ekstensi development).
2. Buka Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → `GhostGPT: Set API Key`, masukkan kunci API Anda.
3. Buka Command Palette → `GhostGPT: Generate Code`, ketik deskripsi kode.
4. Hasil kode disimpan di folder `generated_code` dan langsung dibuka di editor.

## Konfigurasi

- `ghostgpt-code.apiKey` — API Key GhostGPT
- `ghostgpt-code.baseUrl` — `https://api.ghostgpt.io/v1`
- `ghostgpt-code.model` — `ghostgpt`
- `ghostgpt-code.temperature` — `0.7`

## Catatan

API GhostGPT berbayar (ada trial kecil untuk pelanggan chat berbayar). Web chat gratis tersedia di ghostgpt.io tanpa telepon/kartu.
