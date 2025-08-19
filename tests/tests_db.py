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
from aioeasysqlite.exceptions import * # FIXED BY ADDING TO PATH

# TESTING BEFORE UPLOADING PROJECT

TEST_DB_PATH = r"C:\Users\MSI\Desktop\My\aioeasysqlite\tests\tests.db"

@pytest.mark.asyncio
async def test_init():
    db_obj = db(TEST_DB_PATH)
    assert db_obj.path_to_database == TEST_DB_PATH
    assert db_obj.tables == {}

@pytest.mark.asyncio
async def test_new_table():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users")
    assert "users" in db_obj.tables

@pytest.mark.asyncio
async def test_add_column_create():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users_create")
    await db_obj.add_column("users_create", "id", "INTEGER", primary_key=True)
    table_data = await db_obj.get_table("users_create")
    assert table_data == []

@pytest.mark.asyncio
async def test_add_column_alter():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users_alter")
    await db_obj.add_column("users_alter", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users_alter", "name", "TEXT")
    assert len(db_obj.tables["users_alter"]["columns"]) == 2

@pytest.mark.asyncio
async def test_add_row_and_get_table():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users1")
    await db_obj.add_column("users1", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users1", "name", "TEXT")
    await db_obj.add_row("users1", [("id", 1), ("name", "John")])
    rows = await db_obj.get_table("users1")
    assert rows == [{"id": 1, "name": "John"}]

@pytest.mark.asyncio
async def test_get_row_by_arg():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users2")
    await db_obj.add_column("users2", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users2", "name", "TEXT")
    await db_obj.add_row("users2", [("id", 1), ("name", "John")])
    row = await db_obj.get_row("users2", arg=("id", 1))
    assert row["name"] == "John"

@pytest.mark.asyncio
async def test_edit_row():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users3")
    await db_obj.add_column("users3", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users3", "name", "TEXT")
    await db_obj.add_row("users3", [("id", 1), ("name", "John")])
    await db_obj.edit_row("users3", ("name", "John", "Jane"))
    row = await db_obj.get_row("users3", arg=("id", 1))
    assert row["name"] == "Jane"

@pytest.mark.asyncio
async def test_delete_row():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users4")
    await db_obj.add_column("users4", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users4", "name", "TEXT")
    await db_obj.add_row("users4", [("id", 1), ("name", "John")])
    await db_obj.delete_row("users4", ("id", 1))
    row = await db_obj.get_row("users4", arg=("id", 1))
    assert row is None

@pytest.mark.asyncio
async def test_edit_table():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users5")
    await db_obj.add_column("users5", "id", "INTEGER", primary_key=True)
    await db_obj.edit_table("users5", "clients5")
    assert "clients5" in db_obj.tables
    assert "users5" not in db_obj.tables

@pytest.mark.asyncio
async def test_delete_table():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users6")
    await db_obj.add_column("users6", "id", "INTEGER", primary_key=True)
    await db_obj.delete_table("users6")
    assert "users6" not in db_obj.tables

@pytest.mark.asyncio
async def test_delete_column():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users7")
    await db_obj.add_column("users7", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users7", "name", "TEXT")
    await db_obj.delete_column("users7", "name")
    assert len(db_obj.tables["users7"]["columns"]) == 1

@pytest.mark.asyncio
async def test_get_column():
    db_obj = db(TEST_DB_PATH)
    await db_obj.new_table("users8")
    await db_obj.add_column("users8", "id", "INTEGER", primary_key=True)
    await db_obj.add_column("users8", "name", "TEXT")
    await db_obj.add_row("users8", [("id", 1), ("name", "John")])
    col = await db_obj.get_column("users8", "name", "PK")
    assert col[0][1] == "John"

@pytest.mark.asyncio
async def test_clear_database():
    db_obj = db(TEST_DB_PATH)
    await db_obj.clear_database()
    assert os.path.exists(TEST_DB_PATH)
