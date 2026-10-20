# restaurant-db

I'm a bit of a foodie and I love exploring new restaurants, so I thought it would  be fun to create a database to track the restaurants I've been to and my ratings of them. 
The database schema would consist of the following columns: id, name, cuisine, location, price range, rating:
CREATE TABLE restaurants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    cuisine     TEXT,
    location    TEXT,
    price_range INTEGER CHECK (price_range BETWEEN 1 AND 4),  -- 1 = $, 4 = $$$$
    rating      REAL    CHECK (rating BETWEEN 1 AND 5),
    UNIQUE (name, location)
);

CRUD Operations:
1. CREATE
2. READ
3. UPDATE
4. DELETE
