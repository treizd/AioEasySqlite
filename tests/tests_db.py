# aioeasysqlite - Async SQLite client for Python
# Copyright (c) 2026 Treizd
#
# This file is part of aioeasysqlite.
#
# aioeasysqlite is free software: you can redistribute it and/or modify
# it under the terms of the MIT License. See the LICENSE file for details.


import pytest
import tempfile
import os

import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if path not in sys.path:
    sys.path.insert(0, path)

from aioeasysqlite.db import Db
from aioeasysqlite.exceptions import *

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmpfile:
        db_path = tmpfile.name
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.mark.asyncio
async def test_init(temp_db):
    db_obj = Db(temp_db)
    assert db_obj.path_to_database == temp_db
    assert db_obj.tables == {}


@pytest.mark.asyncio
async def test_invalid_path_extension():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmpfile:
        txt_path = tmpfile.name
    try:
        with pytest.raises(InvalidDatabasePath):
            Db(txt_path)
    finally:
        if os.path.exists(txt_path):
            os.remove(txt_path)


@pytest.mark.asyncio
async def test_nonexistent_path():
    with pytest.raises(PathNotFound):
        Db("/nonexistent/path/to/database.db")


@pytest.mark.asyncio
async def test_new_table(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    assert "users" in db_obj.tables


@pytest.mark.asyncio
async def test_new_table_invalid_name(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(InvalidCharacterInName):
        await db_obj.new_table(name="users-table")


@pytest.mark.asyncio
async def test_new_table_sqlite_prefix(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(InvalidTableName):
        await db_obj.new_table(name="sqlite_master")


@pytest.mark.asyncio
async def test_new_table_duplicate(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    with pytest.raises(TableAlreadyExists):
        await db_obj.new_table(name="users")


@pytest.mark.asyncio
async def test_add_column(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    assert len(db_obj.tables["users"]["columns"]) == 2


@pytest.mark.asyncio
async def test_add_column_unknown_type(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    with pytest.raises(UnknownColumnType):
        await db_obj.add_column("users", "id", "VARCHAR")


@pytest.mark.asyncio
async def test_add_column_invalid_name(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    with pytest.raises(InvalidCharacterInName):
        await db_obj.add_column("users", "user-id", "TEXT")


@pytest.mark.asyncio
async def test_add_column_duplicate(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(ColumnAlreadyExists):
        await db_obj.add_column("users", "id", "TEXT")


@pytest.mark.asyncio
async def test_add_column_nonexistent_table(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(TableNotFound):
        await db_obj.add_column("nonexistent", "id", "INTEGER")


@pytest.mark.asyncio
async def test_add_column_autoincrement_non_integer(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    with pytest.raises(InvalidAutoincrementUsage):
        await db_obj.add_column("users", "id", "TEXT", primary_key=True, autoincrement=True)


@pytest.mark.asyncio
async def test_add_column_autoincrement_no_primary_key(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    with pytest.raises(InvalidAutoincrementUsage):
        await db_obj.add_column("users", "id", "INTEGER", autoincrement=True)


@pytest.mark.asyncio
async def test_add_column_multiple_primary_keys(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(MultiplePrimaryKeys):
        await db_obj.add_column("users", "uid", "INTEGER", primary_key=True)


@pytest.mark.asyncio
async def test_add_row(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    rows = await db_obj.get_table("users")
    assert len(rows) == 1
    assert rows[0]["name"] == "John"


@pytest.mark.asyncio
async def test_add_row_invalid_args_type(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(InvalidArgsType):
        await db_obj.add_row("users", "invalid")


@pytest.mark.asyncio
async def test_add_row_nonexistent_table(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(TableNotFound):
        await db_obj.add_row("nonexistent", [("id", 1)])


@pytest.mark.asyncio
async def test_add_row_unique_constraint(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", unique=True)
    await db_obj.add_row("users", [("id", 1)])
    with pytest.raises(UniqueConstraintViolation):
        await db_obj.add_row("users", [("id", 1)])


@pytest.mark.asyncio
async def test_add_row_not_null_constraint(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT", not_null=True)
    with pytest.raises(NotNullConstraintViolation):
        await db_obj.add_row("users", [("id", 1)])


@pytest.mark.asyncio
async def test_add_row_invalid_value_conversion(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "balance", "REAL")
    with pytest.raises(InvalidValueConversion):
        await db_obj.add_row("users", [("id", 1), ("balance", "not_a_number")])


@pytest.mark.asyncio
async def test_add_row_duplicate_column_in_args(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(DuplicateColumnInArgs):
        await db_obj.add_row("users", [("id", 1), ("id", 2)])


@pytest.mark.asyncio
async def test_add_row_with_default_value(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True, autoincrement=True)
    await db_obj.add_column("users", "balance", "REAL", default=0)
    await db_obj.add_row("users", [("id", 1)])
    rows = await db_obj.get_table("users")
    assert rows[0]["balance"] == 0


@pytest.mark.asyncio
async def test_get_table(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_row("users", [("id", 1)])
    await db_obj.add_row("users", [("id", 2)])
    rows = await db_obj.get_table("users")
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_get_table_empty(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    rows = await db_obj.get_table("users")
    assert rows == []


@pytest.mark.asyncio
async def test_get_table_nonexistent(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(TableNotFound):
        await db_obj.get_table("nonexistent")


@pytest.mark.asyncio
async def test_get_row(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    await db_obj.add_row("users", [("id", 2), ("name", "Jane")])
    row = await db_obj.get_row("users", [("id", 1)])
    assert row["name"] == "John"


@pytest.mark.asyncio
async def test_get_row_not_found(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    row = await db_obj.get_row("users", [("id", 999)])
    assert row is None


@pytest.mark.asyncio
async def test_get_row_multiple_args(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_column("users", "active", "INTEGER")
    await db_obj.add_row("users", [("id", 1), ("name", "John"), ("active", 1)])
    row = await db_obj.get_row("users", [("name", "John"), ("active", 1)])
    assert row["id"] == 1


@pytest.mark.asyncio
async def test_get_rows(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "status", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("status", "active")])
    await db_obj.add_row("users", [("id", 2), ("status", "active")])
    await db_obj.add_row("users", [("id", 3), ("status", "inactive")])
    rows = await db_obj.get_rows("users", [("status", "active")])
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_get_rows_with_limit(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "status", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("status", "active")])
    await db_obj.add_row("users", [("id", 2), ("status", "active")])
    await db_obj.add_row("users", [("id", 3), ("status", "active")])
    rows = await db_obj.get_rows("users", [("status", "active")], limit=2)
    assert len(rows) == 2


@pytest.mark.asyncio
async def test_edit_row(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    await db_obj.edit_row("users", [("id", 1)], [("name", "Jane")])
    row = await db_obj.get_row("users", [("id", 1)])
    assert row["name"] == "Jane"


@pytest.mark.asyncio
async def test_edit_row_unique_constraint(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "email", "TEXT", unique=True)
    await db_obj.add_row("users", [("id", 1), ("email", "john@example.com")])
    await db_obj.add_row("users", [("id", 2), ("email", "jane@example.com")])
    with pytest.raises(UniqueConstraintViolation):
        await db_obj.edit_row("users", [("id", 1)], [("email", "jane@example.com")])


@pytest.mark.asyncio
async def test_edit_row_not_null_constraint(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT", not_null=True)
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    with pytest.raises(NotNullConstraintViolation):
        await db_obj.edit_row("users", [("id", 1)], [("name", None)])


@pytest.mark.asyncio
async def test_edit_rows(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "status", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("status", "active")])
    await db_obj.add_row("users", [("id", 2), ("status", "active")])
    await db_obj.add_row("users", [("id", 3), ("status", "inactive")])
    await db_obj.edit_rows("users", [("status", "active")], [("status", "processed")])
    rows = await db_obj.get_table("users")
    assert all(row["status"] == "processed" for row in rows if row["id"] in [1, 2])


@pytest.mark.asyncio
async def test_delete_row(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_row("users", [("id", 1)])
    await db_obj.delete_row("users", [("id", 1)])
    row = await db_obj.get_row("users", [("id", 1)])
    assert row is None


@pytest.mark.asyncio
async def test_delete_rows(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "status", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("status", "active")])
    await db_obj.add_row("users", [("id", 2), ("status", "active")])
    await db_obj.add_row("users", [("id", 3), ("status", "inactive")])
    await db_obj.delete_rows("users", [("status", "active")])
    rows = await db_obj.get_table("users")
    assert len(rows) == 1
    assert rows[0]["id"] == 3


@pytest.mark.asyncio
async def test_edit_table(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.edit_table("users", "clients")
    assert "clients" in db_obj.tables
    assert "users" not in db_obj.tables


@pytest.mark.asyncio
async def test_edit_table_duplicate_name(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.new_table(name="clients")
    with pytest.raises(TableAlreadyExists):
        await db_obj.edit_table("users", "clients")


@pytest.mark.asyncio
async def test_delete_table(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.delete_table("users")
    assert "users" not in db_obj.tables


@pytest.mark.asyncio
async def test_delete_table_nonexistent(temp_db):
    db_obj = Db(temp_db)
    with pytest.raises(TableNotFound):
        await db_obj.delete_table("nonexistent")


@pytest.mark.asyncio
async def test_delete_column(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.delete_column("users", "name")
    assert len(db_obj.tables["users"]["columns"]) == 1


@pytest.mark.asyncio
async def test_delete_column_nonexistent(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(ColumnNotFound):
        await db_obj.delete_column("users", "nonexistent")


@pytest.mark.asyncio
async def test_get_column(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    await db_obj.add_row("users", [("id", 2), ("name", "Jane")])
    col = await db_obj.get_column("users", "name", "IND")
    assert len(col) == 2
    assert col[0][1] == "John"
    assert col[1][1] == "Jane"


@pytest.mark.asyncio
async def test_get_column_pk(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    col = await db_obj.get_column("users", "name", "PK")
    assert col[0][0] == 0
    assert col[0][1] == "John"


@pytest.mark.asyncio
async def test_get_column_invalid_type(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(InvalidType):
        await db_obj.get_column("users", "id", "INVALID")


@pytest.mark.asyncio
async def test_clear_database(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_row("users", [("id", 1)])
    await db_obj.clear_database()
    assert os.path.exists(temp_db)
    new_db = Db(temp_db)
    assert new_db.tables == {}


@pytest.mark.asyncio
async def test_load_data(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])

    db_obj2 = Db(temp_db)
    await db_obj2.load_data()
    assert "users" in db_obj2.tables
    assert len(db_obj2.tables["users"]["columns"]) == 2


@pytest.mark.asyncio
async def test_to_dict(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    result = db_obj.to_dict()
    assert isinstance(result, dict)
    assert "path_to_database" in result
    assert "tables" in result


@pytest.mark.asyncio
async def test_str_repr(temp_db):
    db_obj = Db(temp_db)
    str_repr = str(db_obj)
    assert "aioeasysqlite.db" in str_repr
    assert temp_db in str_repr


@pytest.mark.asyncio
async def test_add_column_with_default_invalid(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    with pytest.raises(InvalidDefaultValue):
        await db_obj.add_column("users", "name", "TEXT", not_null=True, default="NULL")


@pytest.mark.asyncio
async def test_edit_row_invalid_find_args(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    with pytest.raises(InvalidArgsType):
        await db_obj.edit_row("users", [], [("name", "Jane")])


@pytest.mark.asyncio
async def test_edit_row_invalid_edit_args(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "name", "TEXT")
    await db_obj.add_row("users", [("id", 1), ("name", "John")])
    with pytest.raises(InvalidArgsType):
        await db_obj.edit_row("users", [("id", 1)], [])


@pytest.mark.asyncio
async def test_add_row_unsupported_type(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "data", "TEXT")
    with pytest.raises(UnsupportedValueType):
        await db_obj.add_row("users", [("id", 1), ("data", [1, 2, 3])])


@pytest.mark.asyncio
async def test_add_row_bytes_column(temp_db):
    db_obj = Db(temp_db)
    await db_obj.new_table(name="users")
    await db_obj.add_column("users", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users", "data", "BLOB")
    await db_obj.add_row("users", [("id", 1), ("data", b"binary_data")])
    row = await db_obj.get_row("users", [("id", 1)])
    assert row["data"] == b"binary_data"