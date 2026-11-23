"""
ghostgpt.py

Klien GhostGPT.io (OpenAI-kompatibel) untuk dibangun menjadi chatbot.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()


@dataclass
class GhostGPTConfig:
    base_url: str = os.getenv("GHOSTGPT_BASE_URL", "https://api.ghostgpt.io/v1")
    api_key: str = os.getenv("GHOSTGPT_API_KEY", "")
    model: str = os.getenv("GHOSTGPT_MODEL", "ghostgpt")
    temperature: float = float(os.getenv("GHOSTGPT_TEMPERATURE", "0.7"))
    max_tokens: int | None = (
        int(os.getenv("GHOSTGPT_MAX_TOKENS")) if os.getenv("GHOSTGPT_MAX_TOKENS") else None
    )


class GhostGPTClient:
    """Wrapper ringan di sekitar OpenAI client untuk GhostGPT.io."""

    def __init__(self, config: GhostGPTConfig | None = None):
        self.config = config or GhostGPTConfig()
        if not self.config.api_key or self.config.api_key == "SK-YOUR-KEY":
            raise ValueError(
                "GHOSTGPT_API_KEY belum diatur. Isi file .env atau variabel lingkungan."
            )
        self._client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)

    def list_models(self) -> list[str]:
        return [m.id for m in self._client.models.list().data]

    def chat(
        self,
        messages: list[ChatCompletionMessageParam],
        stream: bool = True,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> Iterable:
        return self._client.chat.completions.create(
            model=model or self.config.model,
            messages=messages,
            stream=stream,
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
        )

    def chat_once(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        respons = self.chat(
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )
        return respons.choices[0].message.content or ""

    @staticmethod
    def extract_code_blocks(teks: str) -> list[dict[str, str]]:
        """Ekstraksi blok kode dari markdown (```bahasa ... ```)."""
        import re

        blok: list[dict[str, str]] = []
        pola = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        for cocok in pola.finditer(teks):
            bahasa = cocok.group(1) or ""
            isi = cocok.group(2).strip()
            blok.append({"language": bahasa, "code": isi})
        return blok
