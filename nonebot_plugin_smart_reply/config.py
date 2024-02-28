from pathlib import Path
from typing import Optional, Sequence, Set, Union

from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, parse_obj_as, validator


class Config(BaseModel):
    bot_nickname: str = "我"
    smart_reply_path: Path = Path("data/smart_reply")
    ai_reply_private: bool = False
    openai_api_key: Optional[Union[Sequence[str], str]] = None
    openai_max_tokens: int = 1000
    openai_cd_time: int = 600
    openai_max_conversation: int = 10
    openai_proxy: str = ""
    superusers: Set[str]

    @validator("openai_api_key")
    def _check_openai_api_key(cls, v):
        if isinstance(v, str):
            logger.info("openai_api_key读取, 初始化成功, 共 1 个api_key")
            return [v]
        elif isinstance(v, Sequence) and v:
            logger.info(f"openai_api_key读取, 初始化成功, 共 {len(v)} 个api_key")
            return v
        else:
            logger.warning("未检测到 openai_api_key，已禁用相关功能")

    class Config:
        extra = "ignore"


config = parse_obj_as(Config, get_driver().config.dict())


if not config.smart_reply_path.exists() or not config.smart_reply_path.is_dir():
    config.smart_reply_path.mkdir(0o755, parents=True, exist_ok=True)
