#!/usr/bin/env python3
"""
chatbot.py

Chatbot interaktif berbasis GhostGPT.io (OpenAI-kompatibel).
Fitur:
  - Riwayat percakapan (context) dipertahankan selama sesi
  - Streaming respons (ketik sehabis diterima)
  - Perintah: /quit, /exit, /clear, /help, /system, /models, /save, /load
  - Konfigurasi melalui file .env

Cara pakai:
    1. Salin .env.example -> .env, isi GHOSTGPT_API_KEY.
    2. pip install -r requirements.txt
    3. python chatbot.py
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessageParam

from ghostgpt import GhostGPTClient, GhostGPTConfig

load_dotenv()

HISTORY_FILE = os.getenv("GHOSTGPT_HISTORY_FILE", "chat_history.jsonl")
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


class Chatbot:
    def __init__(self, config: Optional[GhostGPTConfig] = None):
        self.config = config or GhostGPTConfig()
        try:
            self.klien = GhostGPTClient(self.config)
        except ValueError as exc:
            print(f"Error: {exc}")
            print("Silakan isi GHOSTGPT_API_KEY di file .env terlebih dahulu.")
            sys.exit(1)

        system_prompt = os.getenv("GHOSTGPT_SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
        self.pesan: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

        if os.path.exists(HISTORY_FILE):
            self.pesan = muat_riwayat(HISTORY_FILE)
            if not self.pesan or self.pesan[0]["role"] != "system":
                self.pesan.insert(0, {"role": "system", "content": system_prompt})
    def jalankan(self) -> None:
        print("=" * 60)
        print(" GhostGPT Chatbot")
        print(" Ketik /help untuk daftar perintah, /quit untuk keluar.")
        print("=" * 60)
        print(f"Model: {self.config.model} | Base URL: {self.config.base_url}")
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

            self.pesan.append({"role": "user", "content": teks})

            print("\nGhostGPT> ", end="", flush=True)
            balasan_utuh = ""
            try:
                alur = self.klien.chat(self.pesan, stream=True)
                for potongan in alur:
                    delta = potongan.choices[0].delta.content
                    if delta:
                        print(delta, end="", flush=True)
                        balasan_utuh += delta
                print()
            except Exception as exc:
                print(f"\n[Error GhostGPT] {exc}")
                if self.pesan and self.pesan[-1]["role"] == "user":
                    self.pesan.pop()
                continue

            if balasan_utuh:
                self.pesan.append({"role": "assistant", "content": balasan_utuh})
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
                print("Contoh: /system Kamu adalah asisten yang terbuka dan ramah.")
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
        else:
            print(f"Perintah tidak dikenal: {cmd}. Ketik /help untuk bantuan.")

    def _simpan_otomatis(self) -> None:
        try:
            simpan_riwayat(HISTORY_FILE, self.pesan)
        except Exception:
            pass


def main() -> None:
    bot = Chatbot()
    bot.jalankan()


if __name__ == "__main__":
    main()

