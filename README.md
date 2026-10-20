# restaurant-db

I'm a bit of a foodie and I love exploring new restaurants, so I thought it would be fun to create a database to track the restaurants I've been to and my ratings of them.

## Database schema

The database has one table, `restaurants`, with the following columns: id, name, cuisine, location, price range, rating.

| Column        | Type    | Notes                                    |
|---------------|---------|------------------------------------------|
| `id`          | INTEGER | Primary key, auto-increments             |
| `name`        | TEXT    | Required                                 |
| `cuisine`     | TEXT    | Optional                                 |
| `location`    | TEXT    | Optional                                 |
| `price_range` | INTEGER | Optional, 1–4 (1 = $, 4 = $$$$)          |
| `rating`      | REAL    | Optional, 1–5 (decimals like 4.5 are ok) |

The same name + location can't be added twice, so I don't end up with duplicates of the same spot.

```sql
CREATE TABLE restaurants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    cuisine     TEXT,
    location    TEXT,
    price_range INTEGER CHECK (price_range BETWEEN 1 AND 4),  -- 1 = $, 4 = $$$$
    rating      REAL    CHECK (rating BETWEEN 1 AND 5),
    UNIQUE (name, location)
);
```

## How to run it

All you need is Python 3. `sqlite3` comes built into Python, so there's nothing else to install.

```bash
cd restaurant-db
python3 restaurant_db.py
```

The first time it runs, it creates `restaurant.db` and the table. After that, you get a menu:

```
Restaurant Tracker
  1. Create
  2. Read
  3. Update
  4. Delete
  5. Quit
```

Type a number to pick an option, and 5 to quit.

## CRUD Operations

1. **CREATE**: Choose `1` to add a restaurant. It asks for the name (required), then cuisine, location, price range (1–4), and rating (1–5). You can press Enter to skip any of the optional ones. If the price or rating is out of range, it asks again.
2. **READ**: Choose `2` to look at the restaurants. You can see all of them, search by name (any part of the name works), or filter by cuisine. The results print as a table sorted by name.
3. **UPDATE**: Choose `3` to edit a restaurant. It shows the list with ids, you type the id of the one you want to change, and then it goes through each field showing the current value. Press Enter to keep a value or type a new one (handy for bumping up a rating after a second visit).
4. **DELETE**: Choose `4` to remove a restaurant. It shows the list, you type the id, and it asks you to confirm with `y` before it actually deletes anything.
