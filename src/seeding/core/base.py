import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

T = TypeVar("T")


class BaseSeeder(ABC, Generic[T]):
    def __init__(self, session: AsyncSession, batch_size: int = 1000):
        self.session = session
        self.batch_size = batch_size
        self.logger = logging.getLogger(f"seeding.{self.name}")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    async def _fetch_data(self) -> T:
        pass

    @abstractmethod
    def transform_data(self, raw_data: T) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_model(self) -> Type:
        pass

    @abstractmethod
    def get_conflict_statement(self, stmt):
        pass

    async def run(self):
        self.logger.info(f"Start seeding {self.name}")
        try:
            data = await self._fetch_data()
            clean_data = self.transform_data(data)
            total = len(clean_data)

            if total == 0:
                self.logger.info(f"No data to seed for {self.name}")
                return

            for i in range(0, total, self.batch_size):
                batch = clean_data[i: i + self.batch_size]
                if not batch:
                    continue

                # Создаем insert statement
                model = self.get_model()
                stmt = pg_insert(model).values(batch)

                # Применяем стратегию разрешения конфликтов
                stmt = self.get_conflict_statement(stmt)

                await self.session.execute(stmt)
                await self.session.commit()

                self.logger.info(f"Inserted/Updated batch {i}-{min(i + self.batch_size, total)} of {total}")

            self.logger.info(f"Finished seeding {self.name}")

        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Seeding failed for {self.name}: {e}", exc_info=True)
            raise e