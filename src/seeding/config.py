from pydantic import BaseModel, HttpUrl

class SeedingConfig(BaseModel):
    items_source_url: HttpUrl
    batch_size: int = 1000
    enable_tracking_seeding: bool = True
    seed_min_tier: int = 4
    seed_max_tier: int = 8