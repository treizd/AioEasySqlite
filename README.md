![Static Badge](https://img.shields.io/badge/Python->=3.5-3776AB?logo=Python&logoColor=white) ![Static Badge](https://img.shields.io/badge/MyPy-Checked-3776AB?logo=Python&logoColor=white) ![Static Badge](https://img.shields.io/badge/PyTest-Added-3776AB?logo=Python&logoColor=white)
<p align="center">
    <a href="https://github.com/treizd/AioEasySqlite">
        <img src="https://raw.githubusercontent.com/treizd/aioeasysqlite/main/image.png" alt="AioEasySqlite" width="256">
    </a>
    <br>
    <b>Easier aiosqlite version</b>
</p>

## AioEasySqlite
License: MIT


# Example usage (short)
``` python
import asyncio
from aioeasysqlite import Db


async def main():
    db = Db("test.db")

    await db.new_table(name="users")
    await db.add_column("users", "id", "INTEGER", primary_key=True, autoincrement=True)
    await db.add_column("users", "name", "TEXT", not_null=True)
    await db.add_column("users", "balance", "REAL", default=0)

    await db.add_row("users", [("name", "John")])
    await db.add_row("users", [("name", "Jane")])

    rows = await db.get_table("users")
    print(rows)
    # OUTPUT: [{'id': 1, 'name': 'John', 'balance': 0.0}, {'id': 2, 'name': 'Jane', 'balance': 0.0}]

    await db.edit_row("users", [("name", "John")], [("balance", 100)])
    row = await db.get_row("users", [("name", "John")])
    print(row)
    # OUTPUT: {'id': 1, 'name': 'John', 'balance': 100.0}

    await db.delete_row("users", [("name", "Jane")])

if __name__ == "__main__":
    asyncio.run(main())
```

## IMPORTANT NOTE!
- To retrieve old data from database use async load_data method (`await db.load_data()`).

# Example usage (full)
``` python
import asyncio
from aioeasysqlite import Db


async def main():
    db = Db("test.db")

    # Creates a new table named "users"
    await db.new_table(name="users")

    # Adds columns to the "users" table
    await db.add_column("users", "id", "INTEGER", primary_key=True, autoincrement=True)
    await db.add_column("users", "name", "TEXT", not_null=True)
    await db.add_column("users", "email", "TEXT", unique=True)
    await db.add_column("users", "balance", "REAL", default=0)

    # Adds rows to the "users" table
    await db.add_row("users", [("name", "John"), ("email", "john@example.com")])
    await db.add_row("users", [("name", "Jane"), ("email", "jane@example.com")])
    await db.add_row("users", [("name", "Bob"), ("email", "bob@example.com")])

    # Gets all rows from the "users" table
    all_users = await db.get_table("users")
    print("All users:", all_users)

    # Gets row where name is "John"
    john = await db.get_row("users", [("name", "John")])
    print("John:", john)

    # Gets multiple rows where balance is 0
    zero_balance = await db.get_rows("users", [("balance", 0)])
    print("Zero balance users:", zero_balance)

    # Gets column with indices
    names = await db.get_column("users", "name", "IND")
    print("Names:", names)

    # Gets column with primary key
    names_pk = await db.get_column("users", "name", "PK")
    print("Names with PK:", names_pk)

    # Edits one row (first match)
    await db.edit_row("users", [("name", "John")], [("balance", 100)])
    john_updated = await db.get_row("users", [("name", "John")])
    print("John updated:", john_updated)

    # Edits multiple rows at once
    await db.edit_rows("users", [("balance", 0)], [("balance", 50)])
    all_users = await db.get_table("users")
    print("All users after edit_rows:", all_users)

    # Deletes one row (first match)
    await db.delete_row("users", [("name", "Bob")])
    all_users = await db.get_table("users")
    print("All users after delete_row:", all_users)

    # Deletes multiple rows
    await db.delete_rows("users", [("balance", 50)])
    all_users = await db.get_table("users")
    print("All users after delete_rows:", all_users)

    # Renames the "users" table to "clients"
    await db.edit_table("users", "clients")
    print("Tables:", list(db.tables.keys()))

    # Deletes the "email" column from the "clients" table
    await db.delete_column("clients", "email")
    client = await db.get_row("clients", [("name", "John")])
    print("Client without email:", client)

    # Deletes the "clients" table
    await db.delete_table("clients")
    print("Tables after delete:", db.tables)

    # Loads existing data from database
    db2 = Db("test.db")
    await db2.load_data()
    print("Loaded tables:", list(db2.tables.keys()))

    # Clears the entire database
    await db2.clear_database()
    print("Database cleared")

if __name__ == "__main__":
    asyncio.run(main())
```


### Donate
If you enjoy using my library, you can support me by donating.

- `UQB-7m2USzQ451d9orgD4iECLD0FL_BV-zzk3i--bdRl51ho` - TON
- `TUbvCEDE5wpVRsbLmuU8JfkWY4gNcBNbrx` - USDT TRC20

### Key Features
- **Easy**: Makes working with aiosqlite much easier. No need to know SQL query language anymore.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Particularly asynchronus.

### Installing
``` bash
pip3 install aioeasysqlite
```

### Future
All 'arg' will be replaced by 'args', so people could work with multiple filtered rows at once.