# Menghubungkan (Pasangkan) GhostGPT.io — Versi Gratis

GhostGPT.io adalah AI chat tak tersensor yang **tidak perlu nomor telepon dan tidak perlu kartu kredit** untuk mulai.

## 1. Cara pakai versi gratis (web chat)

1. Buka https://ghostgpt.io/
2. Klik "Try now" / "Sign in".
3. Masuk dengan email & password, Google, atau Telegram (tidak perlu telepon).
4. **Hari pertama gratis** (tanpa pembayaran, tanpa kartu).
5. Setelah hari pertama, tetap bisa pakai **gratis: 3 pesan per hari** tanpa berlangganan, selama tidak meminta perpanjangan bayar.

Catatan: pembayaran adalah satu kali (non-berlangganan), dimulai dari $9 untuk 30 hari (harga lebih rendah untuk Indonesia dan beberapa negara lainnya). Tidak ada auto-renewal.

## 2. Menghubungkan melalui API (OpenAI-kompatibel)

API GhostGPT dibayar terpisah dari web chat, tetapi tersedia **uji coba (trial) kecil** jika sudah memiliki langganan chat berbayar.

- **Base URL:** `https://api.ghostgpt.io/v1`
- **Model:** `ghostgpt`
- **Autentikasi:** header `Authorization: Bearer SK-...`
- **Kunci API:** ditampilkan hanya sekali, simpan dengan aman (jangan commit ke repositori publik).

### Verifikasi kunci API (tidak menguras kuota)

```bash
curl https://api.ghostgpt.io/v1/models \
  -H "Authorization: Bearer SK-YOUR-KEY"
```

### Contoh chat dengan curl

```bash
curl https://api.ghostgpt.io/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SK-YOUR-KEY" \
  -d '{
    "model": "ghostgpt",
    "messages": [
      {"role": "user", "content": "Halo, apa kabar? Balas dalam bahasa Indonesia."}
    ]
  }'
```

### Contoh Python (pustaka resmi OpenAI, cukup ganti base URL dan kunci)

Lihat file `ghostgpt_client.py` di repositori ini.

## 3. Batasan gratis

| Fitur | Gratis (tanpa bayar) |
|-------|----------------------|
| Web chat hari pertama | 30 pesan |
| Web chat setelah hari pertama | 3 pesan per hari |
| Telepon / kartu | Tidak diperlukan |
| API | Terpisah, berbayar (trial kecil untuk pelanggan chat berbayar) |

## File di repositori ini

- `GHOSTGPT.md` — panduan ini
- `ghostgpt_client.py` — contoh klien Python untuk API GhostGPT

## 4. Menjalankan Chatbot Interaktif

Repositori ini menyertakan `chatbot.py`, sebuah chatbot CLI lengkap yang terhubung ke GhostGPT.io.

### Instalasi

```bash
cp .env.example .env
# Edit .env dan isi GHOSTGPT_API_KEY dengan kunci Anda
pip install -r requirements.txt
python chatbot.py
```

### Perintah chatbot

| Perintah | Keterangan |
|----------|------------|
| `/quit`, `/exit` | Keluar dari chatbot |
| `/clear` | Hapus riwayat percakapan |
| `/help` | Tampilkan daftar perintah |
| `/system <teks>` | Ganti persona/system prompt asisten |
| `/show` | Lihat system prompt saat ini |
| `/models` | Daftar model GhostGPT yang tersedia |
| `/save <file>` | Simpan riwayat ke file |
| `/load <file>` | Muat riwayat dari file |
| `/history` | Lihat riwayat percakapan saat ini |

Riwayat percakapan otomatis tersimpan ke `chat_history.jsonl` setelah setiap balasan, sehingga percakapan dapat dilanjutkan sesi selanjutnya.


## 5. Chatbot dengan Generate Kode (`codebot.py`)

`codebot.py` adalah versi chatbot yang khusus untuk pembuatan kode. Hasil generate disimpan sebagai file siap pakai yang bisa dibuka di VS Code.

### Perintah tambahan di `codebot.py`

| Perintah | Keterangan |
|----------|------------|
| `/code <deskripsi>` | Generate kode lengkap berdasarkan deskripsi, simpan ke file |
| `/files` | Daftar file kode yang dihasilkan sesi ini |
| `/open <file>` | Tampilkan isi file kode hasil generate |

### Contoh penggunaan

```
/code buat website sederhana dengan HTML dan CSS
/code buat skrip Python untuk scraping website
/code buat aplikasi kalkulator dengan tkinter
```

File hasil generate otomatis tersimpan di folder `generated_code/` dengan nama berdasarkan deskripsi Anda.

## 6. Ekstensi VS Code (`.vscode/ghostgpt-code/`)

Ekstensi VS Code asli yang memungkinkan generate kode dan chat langsung dari editor GhostGPT.

### Perintah ekstensi

| Perintah | Keterangan |
|----------|------------|
| `GhostGPT: Set API Key` | Simpan API Key GhostGPT |
| `GhostGPT: Generate Code` | Deskripsi kode, hasil disimpan sebagai file dan dibuka di editor |
| `GhostGPT: Chat` | Obrolan singkat, hasil di Output panel |

### Cara pakai ekstensi

1. Buka Command Palette (`Ctrl+Shift+P`) → `GhostGPT: Set API Key`, masukkan kunci API.
2. Command Palette → `GhostGPT: Generate Code`, ketik deskripsi kode.
3. Hasil disimpan di `generated_code` dan langsung dibuka di editor VS Code.

### Konfigurasi ekstensi

- `ghostgpt-code.apiKey` — API Key GhostGPT
- `ghostgpt-code.baseUrl` — `https://api.ghostgpt.io/v1`
- `ghostgpt-code.model` — `ghostgpt`
- `ghostgpt-code.temperature` — `0.7`

## Catatan Penting

- Web chat GhostGPT gratis (hari pertama gratis, kemudian 3 pesan/hari tanpa kartu).
- **API** GhostGPT berbayar terpisah (ada trial kecil untuk pelanggan chat berbayar).
- Kunci API hanya ditampilkan sekali di ghostgpt.io — simpan dengan aman, jangan commit ke repositori publik.

