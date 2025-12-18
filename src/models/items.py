from typing import Optional, Dict
from pydantic import BaseModel, Field, ValidationError


class ItemDTO(BaseModel):
    """
    Data Transfer Object для предмета из Albion Online.
    Автоматически валидирует входящий JSON и обрабатывает null-значения.
    """
    # map'им JSON "UniqueName" -> python "unique_name"
    unique_name: str = Field(alias="UniqueName")

    # Самое важное: Optional + default=None.
    # Если в JSON придет null или ключ будет отсутствовать, Pydantic подставит None и не упадет.
    localized_names: Optional[Dict[str, str]] = Field(alias="LocalizedNames", default=None)

    # Дополнительные поля (по желанию, чтобы игнорировать лишний мусор из дампа)
    # item_id: str = Field(alias="Index", default="")

    @property
    def display_name(self) -> str:
        """
        Вычисляемое свойство. Гарантирует возврат строки.
        Логика: EN-US имя -> или UniqueName, если локализации нет.
        """
        if self.localized_names:
            # Безопасный get, даже если localized_names существует, но пуст
            return self.localized_names.get("EN-US") or self.unique_name
        return self.unique_name

    class Config:
        # Позволяет игнорировать поля в JSON, которые мы не описали в модели
        extra = "ignore"
        # Позволяет создавать объект и через UniqueName, и через unique_name
        populate_by_name = True