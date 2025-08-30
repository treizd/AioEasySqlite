# aioeasysqlite - Async SQLite client for Python
# Copyright (c) 2025 Treizd
#
# This file is part of aioeasysqlite.
#
# aioeasysqlite is free software: you can redistribute it and/or modify
# it under the terms of the MIT License. See the LICENSE file for details.


import pytest
import tempfile
import aiosqlite
import os
from typing import List, Tuple, Dict, Union

import sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if path not in sys.path:
    sys.path.insert(0, path)

from aioeasysqlite.db import db # FIXED BY ADDING TO PATH
from aioeasysqlite.exceptions import *  # FIXED BY ADDING TO PATH

# NOW USING TEMPORARY DATABASE FILE
@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmpfile:
        db_path = tmpfile.name
    yield db_path
    os.remove(db_path)


@pytest.mark.asyncio
async def test_init(temp_db):
    db_obj = db(temp_db)
    assert db_obj.path_to_database == temp_db
    assert db_obj.tables == {}


@pytest.mark.asyncio
async def test_new_table(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users")
    assert "users" in db_obj.tables


@pytest.mark.asyncio
async def test_add_column_create(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users_create")
    await db_obj.add_column("users_create", "id", "INTEGER", primary_key=True)
    table_data = await db_obj.get_table("users_create")
    assert isinstance(table_data, list)


@pytest.mark.asyncio
async def test_add_column_alter(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users_alter")
    await db_obj.add_column("users_alter", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users_alter", "name", "TEXT")
    assert len(db_obj.tables["users_alter"]["columns"]) == 2


@pytest.mark.asyncio
async def test_add_row_and_get_table(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users1")
    await db_obj.add_column("users1", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users1", "name", "TEXT")
    await db_obj.add_row("users1", [("id", 1), ("name", "John")])
    rows = await db_obj.get_table("users1")
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["name"] == "John"


@pytest.mark.asyncio
async def test_get_row_by_arg(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users2")
    await db_obj.add_column("users2", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users2", "name", "TEXT")
    await db_obj.add_row("users2", [("id", 1), ("name", "John")])
    row = await db_obj.get_row("users2", arg=("id", 1))
    assert row["name"] == "John"


@pytest.mark.asyncio
async def test_edit_row(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users3")
    await db_obj.add_column("users3", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users3", "name", "TEXT")
    await db_obj.add_row("users3", [("id", 1), ("name", "John")])
    await db_obj.edit_row("users3", ("name", "John"), ("name", "Jane"))
    row = await db_obj.get_row("users3", arg=("id", 1))
    assert row["name"] == "Jane"


@pytest.mark.asyncio
async def test_delete_row(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users4")
    await db_obj.add_column("users4", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users4", "name", "TEXT")
    await db_obj.add_row("users4", [("id", 1), ("name", "John")])
    await db_obj.delete_row("users4", ("id", 1))
    row = await db_obj.get_row("users4", arg=("id", 1))
    assert row is None


@pytest.mark.asyncio
async def test_edit_table(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users5")
    await db_obj.add_column("users5", "id", "INTEGER", primary_key=True)
    await db_obj.edit_table("users5", "clients5")
    assert "clients5" in db_obj.tables
    assert "users5" not in db_obj.tables


@pytest.mark.asyncio
async def test_delete_table(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users6")
    await db_obj.add_column("users6", "id", "INTEGER", primary_key=True)
    await db_obj.delete_table("users6")
    assert "users6" not in db_obj.tables


@pytest.mark.asyncio
async def test_delete_column(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users7")
    await db_obj.add_column("users7", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users7", "name", "TEXT")
    await db_obj.delete_column("users7", "name")
    assert len(db_obj.tables["users7"]["columns"]) == 1


@pytest.mark.asyncio
async def test_get_column(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users8")
    await db_obj.add_column("users8", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users8", "name", "TEXT")
    await db_obj.add_row("users8", [("id", 1), ("name", "John")])
    col = await db_obj.get_column("users8", "name", "PK")
    row = await db_obj.get_row("users8", arg=("id", 1))
    assert row["name"] == "John"


@pytest.mark.asyncio
async def test_clear_database(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users9")
    await db_obj.add_column("users9", "id", "INTEGER", primary_key=True)
    await db_obj.add_row("users9", [("id", 1)])
    await db_obj.clear_database()
    db_obj = db(temp_db)
    assert os.path.exists(temp_db)
    assert isinstance(db_obj.tables, dict)

@pytest.mark.asyncio
async def test_load_data(temp_db):
    db_obj = db(temp_db)
    await db_obj.new_table(name="users10")
    await db_obj.add_column("users10", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users10", "name", "TEXT")
    await db_obj.add_row("users10", [("id", 1), ("name", "John")])

    db_obj2 = db(temp_db)
    await db_obj2.load_data()
    assert "users10" in db_obj2.tables
    assert len(db_obj2.tables["users10"]["columns"]) == 2


@pytest.mark.asyncio
async def test_db_exists_decorator(temp_db):
    db_obj = db(temp_db)

    with pytest.raises(TableNotFound):
        await db_obj.add_column("test_table", "test_column", "INTEGER")

