import os

class Env:
  @classmethod
  def __class_getitem__(cls, key: str) -> str:
    return os.environ.get(key)
    
  @classmethod
  def to_dict(cls) -> dict[str, str]:
    return dict(os.environ)

