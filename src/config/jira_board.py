class JiraBoard:
  _BOARD_ID_MAP = {
    "sentinels": 1310
  }

  @classmethod
  def __class_getitem__(cls, board_name: str) -> str:
    return cls._BOARD_ID_MAP.get(board_name)