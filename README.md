![Static Badge](https://img.shields.io/badge/Python->=3.5-3776AB?style=for-the-badge&logo=Python&logoColor=white) ![Static Badge](https://img.shields.io/badge/MyPy-Checked-3776AB?style=for-the-badge&logo=Python&logoColor=white)

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
from aioeasysqlite import db


async def main():
    database = db(path_to_database="test.db")

    # Creates a new table named "users"
    await database.new_table(name="users")

    # Adds a column "id" to the "users" table with type INTEGER and sets it as the primary key
    await database.add_column(table="users", name="id", type="INTEGER", primary_key=True)

    # Adds a column "name" to the "users" table with type TEXT
    await database.add_column(table="users", name="name", type="TEXT")

    # Adds a new row to the "users" table with data (id=12345678, name="Josh")
    await database.add_row(table="users", args=[("id", 12345678), ("name", "Josh")])
    
    # Gets the entire "users" table
    table_info = await get_table(users)

    print(table_info) # OUTPUT: [{"id": 12345678, "name": "Josh"}]

if __name__ == "__main__":
    asyncio.run(main())
```

## IMPORTANT NOTE!
- To retrieve old data from database use load_data method.

# Example usage (full)
``` python
import asyncio
from aioeasysqlite import db


async def main():
    database = db(path_to_database="test.db")

    # Creates a new table named "users"
    await database.new_table(name="users")

    # Adds a column "id" to the "users" table with type INTEGER and sets it as the primary key
    await database.add_column(table="users", name="id", type="INTEGER", primary_key=True)

    # Adds a column "name" to the "users" table with type TEXT
    await database.add_column(table="users", name="name", type="TEXT")

    # Adds a column "age" to the "users" table with type INTEGER and sets the default value to 20
    await database.add_column(table="users", name="age", type="INTEGER", default=20)

    # Adds a column "email" to the "users" table with type TEXT, makes it unique and does not allow NULL values
    await database.add_column(table="users", name="email", type="TEXT", unique=True, not_null=True)

    # Adds a new row to the "users" table with data (id=1, name="John Doe", age=30, email="john.doe@example.com")
    await database.add_row(table="users", args=[("id", 1), ("name", "John Doe"), ("age", 30), ("email", "john.doe@example.com")])

    # Adds another row to the "users" table with data (id=2, name="Jane Smith", age=25, email="jane.smith@example.com")
    await database.add_row(table="users", args=[("id", 2), ("name", "Jane Smith"), ("age", 25), ("email", "jane.smith@example.com")])

    # Gets the entire "users" table
    users_table = await database.get_table(table="users")
    print("Users Table:", users_table) # OUTPUT: Users Table: [{'id': 1, 'name': 'John Doe', 'age': 30, 'email': 'john.doe@example.com'}, {'id': 2, 'name': 'Jane Smith', 'age': 25, 'email': 'jane.smith@example.com'}]

    # Gets the "name" column from the "users" table with indices
    name_column = await database.get_column(table="users", column="name", type="IND")
    print("Name Column:", name_column) # OUTPUT: Name Column: [(0, 'John Doe'), (1, 'Jane Smith')]

    # Renames the "users" table to "customers"
    await database.edit_table(table="users", new_name="customers")

    # Gets the entire "customers" table
    customers_table = await database.get_table(table="customers")
    print("Customers Table:", customers_table) # OUTPUT: Customers Table: [{'id': 1, 'name': 'John Doe', 'age': 30, 'email': 'john.doe@example.com'}, {'id': 2, 'name': 'Jane Smith', 'age': 25, 'email': 'jane.smith@example.com'}]

    # Edits a row in the "customers" table, changing the name "John Doe" to "Johnny Doe"
    await database.edit_row(table="customers", args=("name", "John Doe"), ("name", "Johnny Doe"))

    # Gets a row from the "customers" table where the name is "Johnny Doe"
    john_row = await database.get_row(table="customers", arg=("name", "Johnny Doe"))
    print("Johnny Doe Row:", john_row) # OUTPUT: Johnny Doe Row: {'id': 1, 'name': 'Johnny Doe', 'age': 30, 'email': 'john.doe@example.com'}

    # Gets a row from the "customers" table by index 1
    jane_row = await database.get_row(table="customers", index=1)
    print("Jane Smith Row:", jane_row) # OUTPUT: Jane Smith Row: {'id': 2, 'name': 'Jane Smith', 'age': 25, 'email': 'jane.smith@example.com'}

    # Adds a column "phone" to the "customers" table with type "TEXT"
    await database.add_column(table="customers", name="phone", type="TEXT")

    # Edits a row to add a phone number (unnecessary edit_row, as phone is null currently)
    await database.edit_row(table="customers", args=("name", "Johnny Doe"), ("name", "Johnny Doe"))


    # Adds a new row with a phone number
    await database.add_row(table="customers", args=[("id", 3), ("name", "Mike Jhonson"), ("age", 40), ("email", "mike.jhonson@example.com"), ("phone", "555-123-4567")])

    # Deletes a row from the "customers" table where the name is "Jane Smith"
    await database.delete_row(table="customers", arg=("name", "Jane Smith"))

    # Gets the entire "customers" table after deleting a row
    customers_table_after_delete = await database.get_table(table="customers")
    print("Customers Table After Delete:", customers_table_after_delete) # OUTPUT: Customers Table After Delete: [{'id': 1, 'name': 'Johnny Doe', 'age': 30, 'email': 'john.doe@example.com', 'phone': None}, {'id': 3, 'name': 'Mike Jhonson', 'age': 40, 'email': 'mike.jhonson@example.com', 'phone': '555-123-4567'}]

    # Deletes the "age" column from the "customers" table
    await database.delete_column(table="customers", column="age")

    # Gets the entire "customers" table after deleting a column
    customers_table_after_delete_column = await database.get_table(table="customers")
    print("Customers Table After Delete Column:", customers_table_after_delete_column) # OUTPUT: Customers Table After Delete Column: [{'id': 1, 'name': 'Johnny Doe', 'email': 'john.doe@example.com', 'phone': None}, {'id': 3, 'name': 'Mike Jhonson', 'email': 'mike.jhonson@example.com', 'phone': '555-123-4567'}]

    # Deletes the "customers" table
    await database.delete_table(table="customers")

    # Tries to get the "customers" table after deletion (should return an error)
    try:
        await database.get_table(table="customers")
    except Exception as e:
        print("Error getting table after deletion:", e) # OUTPUT: Error getting table after deletion: Table 'customers' does not exist

    # Clears the database (deletes and recreates the file)
    await database.clear_database()

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
- **Async**: Fully asynchronous.

### Installing
``` bash
pip3 install aioeasysqlite
```