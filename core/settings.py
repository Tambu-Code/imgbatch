from dataclasses import dataclass, asdict, fields

from core.watermark import POSITIONS


@dataclass
class Settings:
    width: int = 1920
    height: int = 1080
    keep_ratio: bool = True
    fmt_name: str = "Originale"
    quality: int = 85
    wm_text: str = ""
    wm_position: str = POSITIONS[0]
    wm_opacity: int = 50
    wm_size: int = 5
    logo_path: str = ""
    logo_position: str = POSITIONS[0]
    logo_size: int = 15

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})