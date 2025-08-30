from abc import ABC, abstractmethod


class Base(ABC):

  @abstractmethod
  async def open_session(self, config: dict):
    pass

  @abstractmethod
  async def send_message(self, message: str, config: dict | None = None):
    pass

  @abstractmethod
  async def close_session(self):
    pass

  @abstractmethod
  def is_session_opened(self):
    pass