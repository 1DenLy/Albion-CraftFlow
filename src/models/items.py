import re
from typing import Optional, Dict
from pydantic import BaseModel, Field

class ItemDTO(BaseModel):
    """
    Data Transfer Object для предмета из Albion Online.
    """
    unique_name: str = Field(alias="UniqueName")
    localized_names: Optional[Dict[str, str]] = Field(alias="LocalizedNames", default=None)

    @property
    def display_name(self) -> str:
        """EN-US имя или UniqueName, если локализации нет."""
        if self.localized_names:
            return self.localized_names.get("EN-US") or self.unique_name
        return self.unique_name

    @property
    def tier(self) -> int:
        """Извлекает тир из имени (T4_... -> 4). Если не найдено, возвращает 1."""
        match = re.search(r"^T(\d+)_", self.unique_name)
        if match:
            return int(match.group(1))
        return 1

    @property
    def enchantment_level(self) -> int:
        """Извлекает зачарование из конца имени (...@1 -> 1). По умолчанию 0."""
        match = re.search(r"@(\d+)$", self.unique_name)
        if match:
            return int(match.group(1))
        return 0

    @property
    def base_name(self) -> Optional[str]:
        """
        Возвращает None, чтобы ItemsSeeder использовал свою логику
        (display_name или unique_name).
        """
        return None

    class Config:
        extra = "ignore"
        populate_by_name = True