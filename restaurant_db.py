import sqlite3

# Connect to (or create) a database file
con = sqlite3.connect('restaurant.db')
cur = con.cursor()

# Create your table (if it doesn't already exist)
cur.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        cuisine     TEXT,
        location    TEXT,
        price_range INTEGER CHECK (price_range BETWEEN 1 AND 4),  -- 1 = $, 4 = $$$$
        rating      REAL    CHECK (rating BETWEEN 1 AND 5),
        UNIQUE (name, location)
    )
''')
con.commit()


# ---------- Input helpers ----------

def ask_text(prompt, required=False, default=None):
    """Ask for text. Blank input returns `default` (or re-asks if required)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        if not required:
            return default
        print("  This field is required.")


def ask_number(prompt, cast, low, high, default=None):
    """Ask for a number between low and high. Blank input returns `default`."""
    while True:
        value = input(prompt).strip()
        if not value:
            return default
        try:
            number = cast(value)
        except ValueError:
            print(f"  Please enter a number from {low} to {high}.")
            continue
        if low <= number <= high:
            return number
        print(f"  Please enter a number from {low} to {high}.")


def ask_id(prompt):
    """Ask for a restaurant id and return its row, or None if it doesn't exist."""
    value = input(prompt).strip()
    if not value.isdigit():
        print("  That's not a valid id.")
        return None
    row = cur.execute("SELECT * FROM restaurants WHERE id = ?", (int(value),)).fetchone()
    if row is None:
        print(f"  No restaurant with id {value}.")
    return row


def print_rows(rows):
    if not rows:
        print("  No restaurants found.")
        return
    print(f"  {'ID':<4} {'Name':<25} {'Cuisine':<15} {'Location':<20} {'Price':<6} {'Rating'}")
    for id_, name, cuisine, location, price_range, rating in rows:
        price = "$" * price_range if price_range else "-"
        print(f"  {id_:<4} {name:<25} {cuisine or '-':<15} {location or '-':<20} {price:<6} {rating if rating is not None else '-'}")


# ---------- CRUD operations ----------

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


def create():
    print("\nAdd a restaurant (press Enter to skip optional fields)")
    name = ask_text("  Name: ", required=True)
    cuisine = ask_text("  Cuisine: ")
    location = ask_text("  Location: ")
    price_range = ask_number("  Price range (1-4): ", int, 1, 4)
    rating = ask_number("  Rating (1-5): ", float, 1, 5)
    new_id = add_restaurant(name, cuisine, location, price_range, rating)
    if new_id is not None:
        print(f"  Added {name} with id {new_id}.")


def read():
    print("\nView restaurants")
    print("  1. All restaurants")
    print("  2. Search by name")
    print("  3. Filter by cuisine")
    choice = input("  Choose 1-3: ").strip()
    if choice == "1":
        rows = cur.execute("SELECT * FROM restaurants ORDER BY name").fetchall()
    elif choice == "2":
        term = ask_text("  Name contains: ", required=True)
        rows = cur.execute(
            "SELECT * FROM restaurants WHERE name LIKE ? ORDER BY name", (f"%{term}%",)
        ).fetchall()
    elif choice == "3":
        cuisine = ask_text("  Cuisine: ", required=True)
        rows = cur.execute(
            "SELECT * FROM restaurants WHERE cuisine LIKE ? ORDER BY name", (cuisine,)
        ).fetchall()
    else:
        print("  Invalid choice.")
        return
    print_rows(rows)


def update():
    print("\nUpdate a restaurant")
    print_rows(cur.execute("SELECT * FROM restaurants ORDER BY id").fetchall())
    row = ask_id("  Id of the restaurant to update: ")
    if row is None:
        return
    id_, name, cuisine, location, price_range, rating = row
    print("  Press Enter to keep the current value.")
    name = ask_text(f"  Name [{name}]: ", default=name)
    cuisine = ask_text(f"  Cuisine [{cuisine or ''}]: ", default=cuisine)
    location = ask_text(f"  Location [{location or ''}]: ", default=location)
    price_range = ask_number(f"  Price range (1-4) [{price_range or ''}]: ", int, 1, 4, default=price_range)
    rating = ask_number(f"  Rating (1-5) [{rating or ''}]: ", float, 1, 5, default=rating)
    try:
        cur.execute(
            "UPDATE restaurants SET name = ?, cuisine = ?, location = ?, price_range = ?, rating = ? WHERE id = ?",
            (name, cuisine, location, price_range, rating, id_),
        )
        con.commit()
        print(f"  Updated restaurant {id_}.")
    except sqlite3.IntegrityError as e:
        print(f"  Couldn't update: {e}")


def delete():
    print("\nDelete a restaurant")
    print_rows(cur.execute("SELECT * FROM restaurants ORDER BY id").fetchall())
    row = ask_id("  Id of the restaurant to delete: ")
    if row is None:
        return
    confirm = input(f"  Delete {row[1]}? (y/n): ").strip().lower()
    if confirm == "y":
        cur.execute("DELETE FROM restaurants WHERE id = ?", (row[0],))
        con.commit()
        print(f"  Deleted {row[1]}.")
    else:
        print("  Cancelled.")


# ---------- Main menu ----------

def main():
    actions = {"1": create, "2": read, "3": update, "4": delete}
    while True:
        print("\nRestaurant Tracker")
        print("  1. Create")
        print("  2. Read")
        print("  3. Update")
        print("  4. Delete")
        print("  5. Quit")
        choice = input("Choose 1-5: ").strip()
        if choice == "5":
            break
        if choice in actions:
            actions[choice]()
        else:
            print("  Invalid choice.")
    con.close()


if __name__ == "__main__":
    main()
