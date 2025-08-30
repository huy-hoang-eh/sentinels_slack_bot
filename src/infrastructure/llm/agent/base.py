from abc import ABC, abstractmethod

from google.genai import types


class Base(ABC):

  @abstractmethod
  async def open_session(self, config: dict):
    pass

  @abstractmethod
  async def send_message(self, prompt: str, config: dict | None = None) -> str:
    pass

  @abstractmethod
  async def close_session(self):
    pass

  @abstractmethod
  def is_session_opened(self):
    pass