"""
ghostgpt_client.py

Contoh klien Python untuk menghubungkan GhostGPT.io (versi gratis / trial).
API GhostGPT kompatibel OpenAI, jadi bisa pakai pustaka resmi `openai`.
Cukup ganti base URL dan kunci API.

Persyaratan:
    pip install openai python-dotenv

Cara pakai:
    1. Salin .env.example menjadi .env dan isi GHOSTGPT_API_KEY.
    2. Jalankan: python ghostgpt_client.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Base URL GhostGPT API (OpenAI-kompatibel)
BASE_URL = os.getenv("GHOSTGPT_BASE_URL", "https://api.ghostgpt.io/v1")
API_KEY = os.getenv("GHOSTGPT_API_KEY", "")
MODEL = os.getenv("GHOSTGPT_MODEL", "ghostgpt")


def buat_klien():
    if not API_KEY or API_KEY == "SK-YOUR-KEY":
        raise RuntimeError(
            "GHOSTGPT_API_KEY belum diisi. Dapatkan kunci di https://ghostgpt.io/ "
            "halaman API key, lalu masukkan ke file .env"
        )
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


def verifikasi_kunci(klien):
    """Cek kunci API tanpa menguras kuota (endpoint /v1/models)."""
    models = klien.models.list()
    print("Model yang tersedia:")
    for m in models.data:
        print(" -", m.id)
    return True


def kirim_pesan(klien, pesan, stream=True):
    """Kirim satu pesan ke GhostGPT dan cetak balasannya."""
    print("\nAnda:", pesan)
    print("GhostGPT:", end=" ", flush=True)

    respons = klien.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": pesan}],
        stream=stream,
    )

    if stream:
        for potongan in respons:
            teks = potongan.choices[0].delta.content
            if teks:
                print(teks, end="", flush=True)
        print()  # baris baru setelah selesai
    else:
        teks = respons.choices[0].message.content
        print(teks)
    return teks


def main():
    klien = buat_klien()

    # 1. Verifikasi kunci (tidak menguras kuota)
    print("Memverifikasi kunci API GhostGPT...")
    try:
        verifikasi_kunci(klien)
    except Exception as exc:
        print("Gagal memverifikasi kunci:", exc)
        return

    # 2. Contoh kirim pesan (non-stream)
    kirim_pesan(klien, "Halo, apa kabar? Balas dalam bahasa Indonesia.", stream=False)

    # 3. Contoh kirim pesan (stream)
    kirim_pesan(
        klien,
        "Tuliskan puisi pendek tentang pemrograman dalam bahasa Indonesia.",
        stream=True,
    )


if __name__ == "__main__":
    main()
