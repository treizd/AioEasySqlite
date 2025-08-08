<p align="center">
    <a href="https://github.com/treizd/AioEasySqlite">
        <img src="https://raw.githubusercontent.com/treizd/aioeasysqlite/main/image.png" alt="AioEasySqlite" width="256">
    </a>
    <br>
    <b>Easier aiosqlite version</b>
    <br>
    <a href="example.com">
        Documentation
    </a>
    •
    <a href="https://t.me/+4h_rZvpLwSA3NWIy">
        Chat
    </a>
</p>

## AioEasySqlite
License: MIT

> [!NOTE]
> Column type "BLOB" is not available at the moment.



``` python
from aioeasysqlite import db

db = db(path_to_database="C:\\Users\\user\\Desktop\\project\\users.db")


async def main():
    await db.new_table(name="users")
    await db.add_column(table="users", name="id", type="INTEGER", primary_key=True)
    await db.add_column(table="users", name="name", type="TEXT")
    await db.add_row(table="users", args=[("id", 12345678), ("name", "Josh")])
    
    table_info = await get_table(users)
    print(table_info)

asyncio.run(main())  # OUTPUT: [{"id": 12345678, "name": "Josh"}]
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


### Resources

- Check out the [docs](example.com) to learn more about AioEasySqlite.
- Join the [official channel](https://t.me/opentracing) and stay tuned for news, updates and announcements.
- Join the [official chat](https://t.me/+4h_rZvpLwSA3NWIy) to communicate with people.