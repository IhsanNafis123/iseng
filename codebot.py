#!/usr/bin/env python3
"""
codebot.py

Chatbot GhostGPT dengan kemampuan generate kode lengkap dan simpan ke file.
Dapat digunakan sebagai asisten coding yang hasilnya siap dibuka di VS Code.

Perintah tambahan:
  /code <deskripsi>   - Generate kode lengkap berdasarkan deskripsi, simpan ke file
  /files              - Daftar file yang dihasilkan sesi ini
  /open <file>        - Buka/tampilkan isi file hasil generate

Cara pakai:
    1. Salin .env.example -> .env, isi GHOSTGPT_API_KEY.
    2. pip install -r requirements.txt
    3. python codebot.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessageParam

from ghostgpt import GhostGPTClient, GhostGPTConfig

load_dotenv()

HISTORY_FILE = os.getenv("GHOSTGPT_HISTORY_FILE", "chat_history.jsonl")
CODE_DIR = os.getenv("GHOSTGPT_CODE_DIR", "generated_code")
SYSTEM_PROMPT_DEFAULT = (
    "Kamu adalah asisten AI yang ramah, membantu, dan berbicara dalam bahasa Indonesia. "
    "Jawablah pertanyaan pengguna dengan jelas, singkat, dan sopan."
)

PERINTAH_HELP = """
Perintah yang tersedia:
  /quit   , /exit   - Keluar dari chatbot
  /clear            - Hapus riwayat percakapan (mulai baru)
  /help             - Tampilkan bantuan ini
  /system <teks>    - Ganti system prompt (persona asisten)
  /show             - Tampilkan system prompt saat ini
  /models           - Daftar model yang tersedia di GhostGPT
  /save <file>      - Simpan riwayat percakapan ke file
  /load <file>      - Muat riwayat percakapan dari file
  /history          - Tampilkan riwayat percakapan saat ini
  /code <deskripsi> - Generate kode lengkap dan simpan ke file (siap buka di VS Code)
  /files            - Daftar file kode yang dihasilkan sesi ini
  /open <file>      - Tampilkan isi file kode hasil generate
"""


def muat_riwayat(path: str) -> list[ChatCompletionMessageParam]:
    if not os.path.exists(path):
        return []
    pesan: list[ChatCompletionMessageParam] = []
    with open(path, "r", encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if not baris:
                continue
            try:
                data = json.loads(baris)
                if "role" in data and "content" in data:
                    pesan.append({"role": data["role"], "content": data["content"]})
            except json.JSONDecodeError:
                continue
    return pesan


def simpan_riwayat(path: str, pesan: list[ChatCompletionMessageParam]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for p in pesan:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")


def tampilkan_riwayat(pesan: list[ChatCompletionMessageParam]) -> None:
    if not pesan:
        print("(belum ada riwayat percakapan)")
        return
    for p in pesan:
        role = p["role"]
        isi = p["content"]
        if role == "system":
            print(f"\n[system] {isi}")
        elif role == "user":
            print(f"\nAnda: {isi}")
        elif role == "assistant":
            print(f"\nGhostGPT: {isi}")


def ambil_input(prompt: str = "Anda> ") -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n")
        return "/quit"


def nama_file_dari_deskripsi(deskripsi: str) -> str:
    import re

    aman = re.sub(r"[^a-zA-Z0-9 _-]", "", deskripsi.strip()).strip().replace(" ", "_")
    if not aman:
        aman = "skrip"
    return aman[:60]


class CodeBot:
    def __init__(self, config: Optional[GhostGPTConfig] = None):
        self.config = config or GhostGPTConfig()
        try:
            self.klien = GhostGPTClient(self.config)
        except ValueError as exc:
            print(f"Error: {exc}")
            print("Silakan isi GHOSTGPT_API_KEY di file .env terlebih dahulu.")
            sys.exit(1)

        self.file_hasil: list[dict] = []

        system_prompt = os.getenv("GHOSTGPT_SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
        self.pesan: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

        if os.path.exists(HISTORY_FILE):
            self.pesan = muat_riwayat(HISTORY_FILE)
            if not self.pesan or self.pesan[0]["role"] != "system":
                self.pesan.insert(0, {"role": "system", "content": system_prompt})

        Path(CODE_DIR).mkdir(parents=True, exist_ok=True)

    def jalankan(self) -> None:
        print("=" * 60)
        print(" GhostGPT CodeBot")
        print(" Ketik /help untuk daftar perintah, /quit untuk keluar.")
        print("=" * 60)
        print(f"Model: {self.config.model} | Base URL: {self.config.base_url}")
        print(f"Folder hasil kode: {os.path.abspath(CODE_DIR)}")
        print("-" * 60)

        while True:
            teks = ambil_input("\nAnda> ").strip()
            if not teks:
                continue

            if teks.startswith("/"):
                self._handle_command(teks)
                if getattr(self, "_keluar", False):
                    break
                continue

            if self._deteksi_permintaan_kode(teks):
                print("\n[CodeBot] Deteksi permintaan kode. Gunakan /code <deskripsi> untuk generate file lengkap.")
                self.pesan.append({"role": "user", "content": teks})
                self._kirim_dan_tampilkan(self.pesan)
                continue

            self.pesan.append({"role": "user", "content": teks})
            self._kirim_dan_tampilkan(self.pesan)

    def _deteksi_permintaan_kode(self, teks: str) -> bool:
        kata_kunci = [
            "buat kode", "tulis kode", "generate kode", "coding", "program",
            "skrip", "script", "fungsi", "class", "aplikasi", "website",
            "script python", "kode python", "code",
        ]
        lower = teks.lower()
        return any(k in lower for k in kata_kunci)

    def _kirim_dan_tampilkan(self, pesan: list[ChatCompletionMessageParam]) -> None:
        print("\nGhostGPT> ", end="", flush=True)
        balasan_utuh = ""
        try:
            alur = self.klien.chat(pesan, stream=True)
            for potongan in alur:
                delta = potongan.choices[0].delta.content
                if delta:
                    print(delta, end="", flush=True)
                    balasan_utuh += delta
            print()
        except Exception as exc:
            print(f"\n[Error GhostGPT] {exc}")
            if pesan and pesan[-1]["role"] == "user":
                pesan.pop()
            return

        if balasan_utuh:
            pesan.append({"role": "assistant", "content": balasan_utuh})
            self._simpan_otomatis()

    def _handle_command(self, teks: str) -> None:
        bagian = teks.split(maxsplit=1)
        cmd = bagian[0].lower()
        arg = bagian[1].strip() if len(bagian) > 1 else ""

        self._keluar = False

        if cmd in ("/quit", "/exit"):
            print("Sampai jumpa!")
            self._keluar = True
        elif cmd == "/help":
            print(PERINTAH_HELP)
        elif cmd == "/clear":
            system_prompt = self.pesan[0]["content"] if self.pesan else SYSTEM_PROMPT_DEFAULT
            self.pesan = [{"role": "system", "content": system_prompt}]
            print("(Riwayat percakapan dibersihkan.)")
        elif cmd == "/system":
            if not arg:
                print("Contoh: /system Kamu adalah asisten coding yang ahli Python.")
                return
            if self.pesan and self.pesan[0]["role"] == "system":
                self.pesan[0]["content"] = arg
            else:
                self.pesan.insert(0, {"role": "system", "content": arg})
            print(f"(System prompt diubah: {arg})")
        elif cmd == "/show":
            if self.pesan and self.pesan[0]["role"] == "system":
                print(f"\n[system] {self.pesan[0]['content']}")
            else:
                print("(Tidak ada system prompt.)")
        elif cmd == "/models":
            try:
                models = self.klien.list_models()
                print("Model yang tersedia:")
                for m in models:
                    print(f" - {m}")
            except Exception as exc:
                print(f"[Error] Gagal mengambil model: {exc}")
        elif cmd == "/save":
            if not arg:
                arg = HISTORY_FILE
            simpan_riwayat(arg, self.pesan)
            print(f"(Riwayat disimpan ke {arg})")
        elif cmd == "/load":
            if not arg:
                print("Contoh: /load chat_history.jsonl")
                return
            if not os.path.exists(arg):
                print(f"File {arg} tidak ditemukan.")
                return
            self.pesan = muat_riwayat(arg)
            if not self.pesan or self.pesan[0]["role"] != "system":
                self.pesan.insert(0, {"role": "system", "content": SYSTEM_PROMPT_DEFAULT})
            print(f"(Riwayat dimuat dari {arg}, {len(self.pesan)} pesan.)")
        elif cmd == "/history":
            tampilkan_riwayat(self.pesan)
        elif cmd == "/code":
            self._generate_kode(arg)
        elif cmd == "/files":
            self._daftar_file()
        elif cmd == "/open":
            self._buka_file(arg)
        else:
            print(f"Perintah tidak dikenal: {cmd}. Ketik /help untuk bantuan.")

    def _generate_kode(self, deskripsi: str) -> None:
        if not deskripsi:
            print("Contoh: /code buat website sederhana dengan HTML dan CSS")
            return

        bahasa_terduga = self._deteksi_bahasa(deskripsi)

        prompt_kode = (
            f"Buat kode lengkap dan siap pakai untuk: {deskripsi}\n"
            f"Bahasa yang diusulkan: {bahasa_terduga}\n"
            "Berikan kode dalam satu blok markdown dengan penanda bahasa, "
            "contoh ```python\n...kode...\n```.\n"
            "Jangan tambahkan penjelasan di luar blok kode. Kode harus lengkap, "
            "tidak ada placeholder seperti 'TODO' atau 'isi di sini', dan dapat dijalankan langsung."
        )

        pesan_kode = list(self.pesan)
        pesan_kode.append({"role": "user", "content": prompt_kode})

        print("\nGhostGPT> ", end="", flush=True)
        balasan_utuh = ""
        try:
            alur = self.klien.chat(pesan_kode, stream=True)
            for potongan in alur:
                delta = potongan.choices[0].delta.content
                if delta:
                    print(delta, end="", flush=True)
                    balasan_utuh += delta
            print()
        except Exception as exc:
            print(f"\n[Error GhostGPT] {exc}")
            return

        if not balasan_utuh:
            return

        self.pesan.append({"role": "assistant", "content": balasan_utuh})
        self._simpan_otomatis()

        blok = self.klien.extract_code_blocks(balasan_utuh)
        if not blok:
            print("\n[CodeBot] Tidak ditemukan blok kode dalam respons.")
            return

        print("\n" + "=" * 60)
        print("[CodeBot] Menyimpan hasil generate ke file...")
        for i, b in enumerate(blok, 1):
            bahasa = b["language"] or bahasa_terduga
            ekstensi = self._ekstensi_dari_bahasa(bahasa)
            nama_default = f"{nama_file_dari_deskripsi(deskripsi)}_{i}.{ekstensi}"
            path = Path(CODE_DIR) / nama_default

            counter = 1
            while path.exists():
                stem = Path(nama_default).stem
                path = Path(CODE_DIR) / f"{stem}_{counter}.{ekstensi}"
                counter += 1

            path.write_text(b["code"], encoding="utf-8")
            self.file_hasil.append(
                {"nama": path.name, "path": str(path), "bahasa": bahasa}
            )
            print(f"  [{i}] {path}  ({bahasa})")

        print("=" * 60)
        print("File siap dibuka di VS Code. Ketik /files untuk daftar lengkap.")

    def _deteksi_bahasa(self, deskripsi: str) -> str:
        lower = deskripsi.lower()
        if any(k in lower for k in ["python", "py "]):
            return "python"
        if any(k in lower for k in ["javascript", "js ", "node"]):
            return "javascript"
        if any(k in lower for k in ["typescript", "ts "]):
            return "typescript"
        if any(k in lower for k in ["html"]):
            return "html"
        if any(k in lower for k in ["css"]):
            return "css"
        if any(k in lower for k in ["java"]):
            return "java"
        if any(k in lower for k in ["cpp", "c++"]):
            return "cpp"
        if any(k in lower for k in ["go", "golang"]):
            return "go"
        if any(k in lower for k in ["rust", "rs "]):
            return "rust"
        if any(k in lower for k in ["php"]):
            return "php"
        if any(k in lower for k in ["ruby", "rb "]):
            return "ruby"
        if any(k in lower for k in ["swift"]):
            return "swift"
        if any(k in lower for k in ["kotlin", "kt "]):
            return "kotlin"
        if any(k in lower for k in ["bash", "shell", "sh "]):
            return "bash"
        return "python"

    def _ekstensi_dari_bahasa(self, bahasa: str) -> str:
        tabel = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "html": "html",
            "css": "css",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "ruby": "rb",
            "swift": "swift",
            "kotlin": "kt",
            "bash": "sh",
            "json": "json",
            "markdown": "md",
            "text": "txt",
        }
        return tabel.get(bahasa.lower(), "txt")

    def _daftar_file(self) -> None:
        if not self.file_hasil:
            print("(Belum ada file kode yang dihasilkan sesi ini.)")
            return
        print("\nFile kode hasil generate:")
        for i, f in enumerate(self.file_hasil, 1):
            print(f"  [{i}] {f['nama']}  ({f['bahasa']})")
            print(f"       {f['path']}")

    def _buka_file(self, nama: str) -> None:
        if not nama:
            print("Contoh: /open skrip_python_1.py")
            return
        target = None
        for f in self.file_hasil:
            if f["nama"] == nama:
                target = f["path"]
                break
        if not target:
            calon = Path(CODE_DIR) / nama
            if calon.exists():
                target = str(calon)
        if not target:
            print(f"File {nama} tidak ditemukan. Ketik /files untuk daftar.")
            return

        path = Path(target)
        isi = path.read_text(encoding="utf-8")
        print(f"\n=== {path.name} ===")
        print(isi)
        print("=" * (len(path.name) + 8))

    def _simpan_otomatis(self) -> None:
        try:
            simpan_riwayat(HISTORY_FILE, self.pesan)
        except Exception:
            pass


def main() -> None:
    bot = CodeBot()
    bot.jalankan()


if __name__ == "__main__":
    main()

