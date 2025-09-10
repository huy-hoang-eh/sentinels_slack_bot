import os
from dotenv import dotenv_values

class Env:
  _dotenv_values = None
  
  @classmethod
  def _load_dotenv_values(cls):
    if cls._dotenv_values is None:
      # Load .env file values
      cls._dotenv_values = dotenv_values('.env')
    return cls._dotenv_values
  
  @classmethod
  def __class_getitem__(cls, key: str) -> str:
    # First check .env file, then fallback to system environment
    dotenv_vals = cls._load_dotenv_values()
    return dotenv_vals.get(key) or os.environ.get(key)
    
  @classmethod
  def to_dict(cls) -> dict[str, str]:
    # Start with system environment, then override with .env values
    env_dict = dict(os.environ)
    dotenv_vals = cls._load_dotenv_values()
    env_dict.update(dotenv_vals)  # .env values override system env
    return env_dict

