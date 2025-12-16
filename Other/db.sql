-- 1. ЛОКАЦИИ
CREATE TABLE locations (
    id SMALLSERIAL PRIMARY KEY,
    api_name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100)
);


-- 2. ПРЕДМЕТЫ
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    unique_name VARCHAR(100) NOT NULL UNIQUE, -- 'T6_BAG@2'
    base_name VARCHAR(50) NOT NULL,           -- 'BAG'
    tier SMALLINT NOT NULL,                   -- 6
    enchantment_level SMALLINT NOT NULL DEFAULT 0, -- 2
    display_name VARCHAR(255)
);


-- 3. ЦЕНЫ (Снэпшоты)
CREATE TABLE market_prices (
    item_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    location_id SMALLINT NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    quality_level SMALLINT NOT NULL DEFAULT 1,

    sell_price_min BIGINT,
    sell_price_min_date TIMESTAMPTZ,
    sell_price_max BIGINT,
    sell_price_max_date TIMESTAMPTZ,

    buy_price_min BIGINT,
    buy_price_min_date TIMESTAMPTZ,
    buy_price_max BIGINT,
    buy_price_max_date TIMESTAMPTZ,

    last_updated TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (item_id, location_id, quality_level)
);

-- 4. ИСТОРИЯ (Партицированная)
CREATE TABLE market_history (
    item_id INT NOT NULL,
    location_id SMALLINT NOT NULL,
    quality_level SMALLINT NOT NULL DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL,

    item_count BIGINT DEFAULT 0,
    average_price BIGINT NOT NULL,

    PRIMARY KEY (item_id, location_id, quality_level, timestamp)
) PARTITION BY RANGE (timestamp);