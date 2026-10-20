# Prompt Log

## Prompt 1

> i want to create a sqlite database to track restaurants that i've been to. The database schema would consist of the following columns: id, name, cuisine, location, price range, rating. help me write a CREATE TABLE statement and tell me what i'm misisng.

### Output

Here's a starting point with your six columns, plus the things I think you're missing:

```sql
CREATE TABLE restaurants (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    cuisine      TEXT,
    location     TEXT,
    price_range  INTEGER CHECK (price_range BETWEEN 1 AND 4),   -- 1 = $, 4 = $$$$
    rating       REAL    CHECK (rating BETWEEN 1 AND 5),
    date_visited TEXT,                                           -- ISO 8601: 'YYYY-MM-DD'
    notes        TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (name, location)
);
```

#### Notes on your original columns

- **`price_range`:** store it as an integer from 1 to 4 rather than text like `"$$"`. That makes "show me everything under $$$" a simple `WHERE price_range <= 2`.
- **`rating`:** add a `CHECK` constraint so you can't save a 47 by accident. Use `REAL` if you want half-stars, `INTEGER` if you don't.
- **`location`:** decide what it means: a neighborhood ("Shadyside"), a city, or a full address. Keep it consistent so you can filter on it. If you'll want to filter by city, split it into `city` and `neighborhood`.
- **`name NOT NULL` plus `UNIQUE(name, location)`:** these block duplicate entries while still letting you track two branches of the same chain.

#### What's missing

1. **The date you went.** For a log of places you've been to, this matters most. SQLite has no date type, so store it as `'YYYY-MM-DD'` text, which sorts correctly.
2. **Notes.** A spot for what you ordered, who you went with, or whether you'd go back.
3. **Repeat visits.** This is the main design gap. If you go back to a place, one row per restaurant can't hold two dates and two ratings. The cleaner way is two tables:

```sql
CREATE TABLE restaurants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    cuisine     TEXT,
    location    TEXT,
    price_range INTEGER CHECK (price_range BETWEEN 1 AND 4),
    UNIQUE (name, location)
);

CREATE TABLE visits (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    visit_date    TEXT    NOT NULL,
    rating        REAL    CHECK (rating BETWEEN 1 AND 5),
    notes         TEXT
);
```

With this layout you can get a restaurant's average rating with `AVG(rating)` and count visits with `COUNT(*)`. Foreign keys are off by default in SQLite, so run `PRAGMA foreign_keys = ON;` each time you connect.

Other columns you could add: `would_return` (0/1), `favorite_dish`, or `cuisine` as its own table if you want consistent spelling ("Thai" vs "thai").

If you mostly go to each place once, the single table is fine. If you go back to places, use the two-table version. I can save either one as a `schema.sql` file in your restaurant-db folder.

---

## Prompt 2

> The only info I want to keep track of is the rating.

### Output

Then you only need one table with your six columns:

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

With no visit dates or repeat visits, each restaurant has one row and one rating. If you go back and your opinion changes, update the rating:

```sql
UPDATE restaurants SET rating = 4.5 WHERE name = 'Noodle Bar' AND location = 'Oakland';
```

The constraints are optional. They keep your data clean:
- `CHECK` stops a rating outside 1–5 or a price range outside 1–4 from being saved.
- `UNIQUE (name, location)` stops you from entering the same restaurant twice.

Remove any of them if they get in the way. I can also add this to your restaurant_db.py so it creates the table when it runs.

---

## Prompt 3

> Walk me through how to insert a new row in my sqlite database with sqlite3, with INSERT INTO. Use parametrized queries to avoid SQL injection.

### Output

Your restaurant_db.py already connects and creates the table. Inserting a row takes three more steps.

#### 1. Write the query with `?` placeholders

```python
cur.execute(
    "INSERT INTO restaurants (name, cuisine, location, price_range, rating) VALUES (?, ?, ?, ?, ?)",
    ("Noodle Bar", "Thai", "Oakland", 2, 4.5),
)
```

- **Name the columns.** List the columns you're filling and leave out `id`, because SQLite assigns it automatically.
- **Put a `?` where each value goes.** Don't build the string yourself with f-strings or `+`.
- **Pass the values as a tuple in the second argument.** sqlite3 sends them to SQLite separately from the SQL text. SQLite treats them only as data, never as SQL code, which is what prevents injection.

Here's the unsafe version, so you can see why this matters:

```python
# DON'T do this
name = "x'); DROP TABLE restaurants; --"
cur.execute(f"INSERT INTO restaurants (name) VALUES ('{name}')")
```

With `?`, that whole string is saved as an odd restaurant name and nothing else happens.

#### 2. Commit

```python
con.commit()
```

Until you commit, the insert isn't saved to `restaurant.db`. If the script ends without committing, the row is lost.

#### 3. (Optional) Get the new row's id

```python
print(cur.lastrowid)  # the id SQLite assigned
```

#### Putting it together as a function

```python
def add_restaurant(name, cuisine, location, price_range, rating):
    try:
        cur.execute(
            "INSERT INTO restaurants (name, cuisine, location, price_range, rating) VALUES (?, ?, ?, ?, ?)",
            (name, cuisine, location, price_range, rating),
        )
        con.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Couldn't add {name}: {e}")
        return None

add_restaurant("Noodle Bar", "Thai", "Oakland", 2, 4.5)
```

Catching `sqlite3.IntegrityError` matters because of your constraints. It's raised when:
- a rating is outside 1–5 or a price range is outside 1–4 (the `CHECK` constraints)
- the same name and location already exist (the `UNIQUE` constraint)
- `name` is missing (`NOT NULL`)

#### Two more tips

**Named placeholders** are easier to read when there are many columns. You pass a dict instead of a tuple:

```python
cur.execute(
    "INSERT INTO restaurants (name, cuisine, location, price_range, rating) "
    "VALUES (:name, :cuisine, :location, :price_range, :rating)",
    {"name": "Noodle Bar", "cuisine": "Thai", "location": "Oakland", "price_range": 2, "rating": 4.5},
)
```

**Inserting several rows at once:** use `executemany` with a list of tuples:

```python
cur.executemany(
    "INSERT INTO restaurants (name, cuisine, location, price_range, rating) VALUES (?, ?, ?, ?, ?)",
    [
        ("Noodle Bar", "Thai", "Oakland", 2, 4.5),
        ("Pizza Place", "Italian", "Squirrel Hill", 1, 4.0),
    ],
)
con.commit()
```

One limit to know: `?` works only for values. Table and column names can't be placeholders, so keep those written directly in the SQL.

---

## Prompt 4

> make sure you continuously update prompt_log.md with my exact prompts and your outputs.

### Output

Done. prompt_log.md now has all four prompts from this session, each with my full reply, word for word. From now on I'll add every new prompt and reply as soon as I answer.

---

## Prompt 5

> I need users to be able to use CLI that asks them for input and the row to insert it in. that is, the user first selects what they want to do (create, read, update, or delete), and then enter in the specific fields required for it whenever they run the python file.

### Output

I rewrote restaurant_db.py as a menu-driven CLI. Run it with `python3 restaurant_db.py` from the restaurant-db folder.

**How it works**

When the script starts, it shows a menu that repeats until you choose Quit:

```
Restaurant Tracker
  1. Create
  2. Read
  3. Update
  4. Delete
  5. Quit
```

- **Create:** asks for name (required), cuisine, location, price range (1–4) and rating (1–5). Press Enter to skip any optional field.
- **Read:** list all restaurants, search by part of a name, or filter by cuisine. Results print as a table, with price shown as `$`–`$$$$`.
- **Update:** shows every restaurant with its id, asks which id to change, then asks for each field with the current value in brackets. Press Enter to keep a value.
- **Delete:** shows the list, asks for an id, and asks you to confirm with y/n before deleting.

**Details**

- Every query uses `?` placeholders, including the search terms.
- Input is checked before it reaches the database. Bad numbers, out-of-range values and a blank name are asked again instead of crashing. A duplicate name and location is caught by your existing `IntegrityError` handling.
- I kept your `add_restaurant` function, and Create calls it. I removed the `add_restaurant()` call at the bottom, which had no arguments and would have crashed. `main()` now runs under `if __name__ == "__main__":`.

**Testing**

I ran every menu option on a copy of the script in a scratch folder, so your real `restaurant.db` wasn't touched. Create, the field checks, the duplicate check, read, update, delete and quit all worked. The test showed `[None]` in the update prompts for empty fields, so I changed those to show blank. I didn't rerun the test after that change.

One limit: in Update, pressing Enter keeps the old value, so you can't clear a field back to empty. I can add that if you need it.
