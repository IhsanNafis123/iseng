# iseng

Proyek contoh untuk menghubungkan (pasangkan) **GhostGPT.io** versi gratis, dilengkapi chatbot dan ekstensi VS Code.

- `GHOSTGPT.md` — panduan langkah demi langkah daftar dan menghubungkan GhostGPT.io (gratis, tanpa telepon/kartu).
- `codebot.py` — chatbot CLI Python dengan generate kode lengkap dan simpan ke file (`/code`, `/files`, `/open`).
- `chatbot.py` — chatbot CLI Python umum (riwayat percakapan, streaming, perintah `/help`).
- `ghostgpt.py` — klien Python (OpenAI-kompatibel) untuk API GhostGPT.
- `ghostgpt_client.py` — contoh klien Python sederhana (API mentah).
- `.env.example` — template konfigurasi kunci API GhostGPT.
- `requirements.txt` — dependensi Python.
- `.vscode/ghostgpt-code/` — ekstensi VS Code untuk generate kode dan chat langsung dari editor.

## Jalankan chatbot Python

```bash
cp .env.example .env
# Isi GHOSTGPT_API_KEY di file .env
pip install -r requirements.txt
python codebot.py   # chatbot dengan generate kode ke file
# atau
python chatbot.py   # chatbot umum
```

## Gunakan ekstensi VS Code

1. Buka folder `.vscode/ghostgpt-code` di VS Code, atau instal sebagai ekstensi development.
2. Command Palette (`Ctrl+Shift+P`) → `GhostGPT: Set API Key`, masukkan kunci API.
3. Command Palette → `GhostGPT: Generate Code`, ketik deskripsi kode.
4. Hasil disimpan di `generated_code` dan dibuka di editor.
