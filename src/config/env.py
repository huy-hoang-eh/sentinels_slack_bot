import os

class Env:
  @classmethod
  def __class_getitem__(cls, key: str) -> str:
    return os.environ.get(key)

