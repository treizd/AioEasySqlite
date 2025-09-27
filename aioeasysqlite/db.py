# aioeasysqlite - Async SQLite client for Python
# Copyright (c) 2025 Treizd
#
# This file is part of aioeasysqlite.
#
# aioeasysqlite is free software: you can redistribute it and/or modify
# it under the terms of the MIT License. See the LICENSE file for details.


import os
import re
import json
import string
import aiosqlite
from functools import wraps
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Union, Any
from .exceptions import AioEasySqliteError, EncodeError, PathNotFound, InvalidDatabasePath, InvalidTableName, InvalidCharacterInName, TableAlreadyExists, TableNotFound, UnknownColumnType, ColumnAlreadyExists, InvalidAutoincrementUsage, InvalidDefaultValue, ColumnNotFound, InvalidArgsType, InvalidArgsLength, InvalidValueConversion, UnsupportedValueType, DuplicateColumnInArgs, UniqueConstraintViolation, NotNullConstraintViolation, MissingRequiredArgument, InvalidIndexType, InvalidIndexValue, IndexOutOfRange, InvalidType, MultiplePrimaryKeys



def db_exists(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        if not os.path.exists(self.path_to_database):
            raise PathNotFound(f"No such path: '{self.path_to_database}'.")
        return await f(self, *args, **kwargs)
    return wrapper

@dataclass
class Db:

    """
    Main class of the library.
    
    :param path_to_database: Path to database.
    :type path_to_database: :obj:`str`
    """

    def __dir__(self):
        return ["Db", "exceptions"]
    
    def __init__(self, path_to_database: str):
        if not path_to_database.endswith(".db"):
            raise InvalidDatabasePath(f"Given path '{path_to_database}' does not exists or belongs not to .db file.")

        if not os.path.exists(path_to_database):
            raise PathNotFound(f"No such path: '{path_to_database}'.")

        self.path_to_database = path_to_database
        
        self.tables: Dict[str, Dict] = {}
        self.types: Dict[str, type] = {
            "INTEGER": int,
            "REAL": float,
            "TEXT": str,
            "BLOB": bytes
        }
    
    @db_exists
    async def load_data(self):
        """
        Loads old data from database
        """
        self.tables =  await self._retrieveData()
    

    @db_exists
    async def clear_database(self):
        """
        Clears the entire database by deleting the file and recreating it.
        """
        try:
            if os.path.exists(self.path_to_database):
                os.remove(self.path_to_database)
            self.tables = {}
            async with aiosqlite.connect(self.path_to_database) as conn:
                await conn.commit()
                print("Database was cleared.")
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def new_table(self, name: str):
        """
        This function just saves the name for the new table. It does not create one yet.
        
        :param name: Alphanumeric name of the table.
        :type name: :obj:`str`
        
        :return: None
        """
        available_chars = string.ascii_letters + string.digits + '_'

        if name.startswith("sqlite_"):
            raise InvalidTableName(f"Table name '{name}' can not start with 'sqlite_'.")
        
        if not all([str(char) in available_chars for char in name]):
            raise InvalidCharacterInName(f"Table name '{name}' has inappropriate characters. Appropriate characters are: {available_chars}.")

        if name in self.tables:
            raise TableAlreadyExists(f"Table with name '{name}' already exists.")
        
        self.tables[name] = {"columns": []}

    @db_exists
    async def get_table(self, table: str) -> Union[List[Dict], None]:
        """
        This function returns all values in the table
        
        :param table: Table name.
        :type table: :obj:`str`
        
        :return: All values if table is not empty else None
        :rtype: :obj:`List[Dict] | None`
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"Table '{table}' does not exist")

            if len(self.tables[table]["columns"]) == 0:
                return []

            sql = f"SELECT * FROM {table}"
            async with aiosqlite.connect(self.path_to_database) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
                    rows = await cursor.fetchall()
                    result = [dict(row) for row in rows]

                    return result
        
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
        
    @db_exists
    async def edit_table(self, table: str, new_name: str):
        """
        This function edits the name of selected table.
        
        :param table: The name of the table to change.
        :type table: :obj:`str`
        
        :param new_name: The name to set.
        :type new_name: :obj:`str`
        
        :return: None
        """
        try:
            available_chars = string.ascii_letters + string.digits + '_'

            if not all([str(char) in available_chars for char in new_name]):
                raise InvalidCharacterInName(f"New table name '{new_name}' has inappropriate characters. Appropriate characters are: {available_chars}.")

            if table not in self.tables:
                raise TableNotFound(f"Table with name '{table}' does not exist.")
            
            if new_name in self.tables:
                raise TableAlreadyExists(f"Table with name '{new_name}' already exists.")

            self.tables[new_name] = self.tables[table]
            del self.tables[table]

            sql = f"ALTER TABLE \"{table}\" RENAME TO \"{new_name}\""

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def delete_table(self, table: str):
        """
        This function deletes table.
        
        :param table: The name of the table to delete.
        :type table: :obj:`str`
        
        :return: None
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"Table with name '{table}' does not exist.")
            
            sql = f"DROP TABLE IF EXISTS \"{table}\""
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
                    await conn.commit()

            del self.tables[table]

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def add_column(self, table: str, name: str, type: str, primary_key: bool = False, autoincrement: bool = False, not_null: bool = False, unique: bool = False, default: Union[str, int, float, None] = None):
        """
        This function adds column to a table in database.
        
        :param table: Name of the table.
        :type table: :obj:`str`
        
        :param name: Alphanumeric and "_" column name.
        :type name: :obj:`str`
        
        :param type: Type of the column. Can only be 'TEXT', 'INTEGER', 'REAL', 'BLOB'.
        :type type: :obj:`str`
        
        :param primary_key: Marks if the column is first key. Makes each value unique.
        :type primary_key: Optional[:obj:`bool`]
        
        :param autoincrement: Only for 'INTEGER' type.
        :type autoincrement: Optional[:obj:`bool`]
        
        :param not_null: Marks if values of the column can be.
        :type not_null: Optional[:obj:`bool`]
        
        :param unique: Marks if each value must be unique. Unnecessary if column is used as primary_key.
        :type unique: Optional[:obj:`bool`]
        
        :param default: Default value to set for each row of column. Use "NULL" instead of "False", "None"
        :type default: Optional[:obj:`str, int, float`]
        
        :return: None
        """
        try:
            available_chars = string.ascii_letters + string.digits + '_'

            if not all([str(char) in available_chars for char in name]):
                raise InvalidCharacterInName(f"Column name '{name}' has inappropriate characters. Appropriate characters are: {available_chars}.")

            if type not in ["TEXT", "INTEGER", "REAL", "BLOB"]:
                raise UnknownColumnType(f"Unknown type: '{type}'.")

            if not table in self.tables:
                raise TableNotFound(f"No such table: '{table}'.")

            if name in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnAlreadyExists(f"Column with name '{name}' already exists in table '{table}'")

            self.tables[table]["columns"].append({"name": name, "type": type, "is_unique": unique})

            parameters: List[str] = []

            primary_key_col = await self._get_pk(table)
            
            if primary_key and not primary_key_col:
                parameters.append("PRIMARY KEY")
            
            elif primary_key and primary_key_col:
                raise MultiplePrimaryKeys("Can not add more than one 'primary key' columns.")

            if autoincrement and type == "INTEGER" and primary_key:
                parameters.append("AUTOINCREMENT")

            elif autoincrement and type != "INTEGER" and primary_key:
                raise InvalidAutoincrementUsage("Can not use 'autoincrement' for non-integer column.")

            elif autoincrement and not primary_key:
                raise InvalidAutoincrementUsage("Can not use 'autoincrement' without using 'primary key'.")
            
            if not_null:
                parameters.append("NOT NULL")

            if unique:
                parameters.append("UNIQUE")

            if default is not None:
                if default == "NULL" and not_null:
                    raise InvalidDefaultValue("Can not set 'NULL' default value to 'NOT NULL' column.")
                parameters.append(f"DEFAULT {default}")

            parameters_str = ' '.join(parameters)

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    if len(self.tables[table]["columns"]) == 1:
                        sql = f"CREATE TABLE IF NOT EXISTS \"{table}\" (\"{name}\" {type} {parameters_str})"
                    else:
                        sql = f"ALTER TABLE \"{table}\" ADD COLUMN \"{name}\" {type} {parameters_str}"

                    await cursor.execute(sql)
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def get_column(self, table: str, column: str, type: str) -> Union[List[Tuple], None]:
        """
        This function returns whole column.
        
        :param table: Table name.
        :type table: :obj:`str`
        
        :param column: Column name.
        :type column: :obj:`str`
        
        :param type: First argument of tuple type. Available types: 'PK' for primary key (if exists) or 'IND' for index
        :type type: :obj:`str`
        
        :return: List of tuples or None if database is empty. First argument is either primary key, or index
        :rtype: :obj:`List[Tuple] | None`
        """
        try:
            if not table in self.tables:
                raise TableNotFound(f"No such table '{table}'.")
            
            if not column in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnNotFound(f"No such column '{column}'.")
            
            if len(self.tables[table]["columns"]) == 0:
                return None
            
            if not type in ["PK", "IND"]:
                raise InvalidType(f"No such type '{type}'")

            primary_key = await self._get_pk(table)

            if not primary_key and type == "PK":
                raise AioEasySqliteError(f"Can not use 'PK' type when primary key is not set.")

            if primary_key and type == "PK":
                sql = f"SELECT \"{primary_key}\", \"{column}\" FROM \"{table}\""
            else:
                sql = f"SELECT \"{column}\" FROM \"{table}\""

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
                    
                    rows = await cursor.fetchall()

                    if rows:
                        items = [i[0] for i in rows]
                    
                        output: List[Tuple] = []
                        for index, item in enumerate(items):
                            output.append((index, item))
                        return output
                    else:
                        return None

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
          
    @db_exists  
    async def delete_column(self, table: str, column: str):
        """
        This function deletes column from table
        
        :param table: Table name.
        :type table: :obj:`str`
        
        :param column: Column name.
        :type column: :obj:`str`
        
        :return: None
        """
        try:
            if not table in self.tables:
                raise TableNotFound(f"No such table '{table}'.")
            
            if not column in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnNotFound(f"No such column '{column}'.")
            
            await self._remove_column(table, column)

        except Exception as e:
            raise AioEasySqliteError(f"Unknown error occured: {e}")
        
    @db_exists
    async def add_row(self, table: str, args: List[Tuple[str, Union[str, int, float, bytes, None]]]):
        """
        This function adds new row to database table

        :param table: Table name.
        :type table: :obj:`str`

        :param args: All values to add.
        :type args: :obj:`List[Tuple]`
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"No such table '{table}'.")

            if not isinstance(args, list) or len(args) == 0:
                raise InvalidArgsType(f"Incorrect type of args. Must be not empty list of tuples.")

            for couple in args:
                if len(couple) != 2:
                    raise InvalidArgsLength(f"Len of each tuple in args must be exactly 2, not {len(couple)}.")

            cols: List[str] = []
            vals: List[Union[str, int, float, bytes, None]] = []

            for column, value in args:
                if column not in [i["name"] for i in self.tables[table]["columns"]]:
                    raise ColumnNotFound(f"No such column '{column}'.")

                ctype = await self._get_type(table, column)
                if ctype is None:
                    raise AioEasySqliteError(f"Could not determine type for column '{column}'.")

                if isinstance(value, str) and self.types[ctype] in [int, float] and not all([i.isdigit() for i in value]):
                    raise InvalidValueConversion(f"Could not convert value '{value}' (str) to int or float for column '{column}'.")
                elif isinstance(value, bytes) and not self.types[ctype] is bytes:
                    raise InvalidValueConversion(f"Could not convert value '{value!r}' (bytes) to int, float or str for column '{column}'.")
                elif self.types[ctype] is bytes:
                    if isinstance(value, str):
                        try:
                            value = value.encode()
                        except UnicodeEncodeError:
                            raise EncodeError(f"Could not convert value '{value!r}' to bytes automatically for column '{column}'.")
                    else:
                        raise TypeError(f"Expected str, got {type(value)} for bytes-type column '{column}'.")
                elif not (isinstance(value, int) or isinstance(value, float) or isinstance(value, str) or isinstance(value, bytes) or value is None):
                    raise UnsupportedValueType(f"Type of value '{value}' is unsupported. Supported types: int, float, str, None")

                cols.append(column)
                vals.append(value)

            if len(cols) > len(set(cols)):
                raise DuplicateColumnInArgs(f"Trying to add multiple values to same column.")

            items = await self.get_table(table)
            pk_col = await self._get_pk(table)
            notnull_cols = await self._get_nn(table)
            unique_cols = await self._get_uq(table)

            for column, value in args:
                column_values = await self.get_column(table, column, "IND")
                if column_values:
                    itms = [i[1] for i in column_values]
                else:
                    itms = []

                if column == pk_col or (unique_cols and column in unique_cols):
                    if value in itms:
                        raise UniqueConstraintViolation(f"Trying to insert already existing value(-s) to unique column '{column}'.")

                if notnull_cols and column in notnull_cols:
                    if value is None:
                        raise NotNullConstraintViolation(f"Trying to insert 'NULL' value(-s) to 'NOT NULL' column {column}.")

            vals_sql = ["?" for _ in range(len(vals))]  # Avoiding SQL injections
            cols_sql = ", ".join(f"\"{col}\"" for col in cols)
            values_sql = ", ".join(vals_sql)

            sql = f"INSERT INTO \"{table}\"({cols_sql}) VALUES ({values_sql})"

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, tuple(vals))
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def edit_row(self, table: str, find_args: Tuple[str, Union[str, int, float, bytes, None]], edit_args: Tuple[str, Union[str, int, float, bytes, None]]):
        """
        This function updates row with new value based on args.

        :param table: Table name.
        :type table: :obj:`str`

        :param args: Column name, current value, new value in one tuple
        :type args: :obj:`Tuple`
        :return: None
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"No such table '{table}'.")

            if not isinstance(find_args, tuple) or len(find_args) != 2:
                raise InvalidArgsType(f"Incorrect type of find_args. Must be a non-empty tuple.")
            
            if not isinstance(edit_args, tuple) or len(edit_args) != 2:
                raise InvalidArgsType(f"Incorrect type of edit_args. Must be a non-empty tuple.")

            column_edit, new_value = edit_args
            column_find, current_value = find_args
            

            if column_edit not in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnNotFound(f"No such column '{column_edit}'.")

            if column_find not in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnNotFound(f"No such column '{column_find}'.")

            ctype = await self._get_type(table, column_edit)

            if ctype is None:
                raise AioEasySqliteError(f"Could not determine type for column '{column_edit}'.")

            if isinstance(new_value, str) and self.types[ctype] in [int, float] and not all([i.isdigit() for i in new_value]):
                raise InvalidValueConversion(f"Could not convert value '{new_value}' (str) to int or float for column '{column_edit}'.")
            elif isinstance(new_value, bytes) and not self.types[ctype] is bytes:
                raise InvalidValueConversion(f"Could not convert value '{new_value!r}' (bytes) to int, float or str for column '{column_edit}'.")
            elif self.types[ctype] is bytes:
                if isinstance(new_value, str):
                    try:
                        new_value = new_value.encode()
                    except UnicodeEncodeError:
                        raise EncodeError(f"Could not convert value '{new_value!r}' to bytes automatically for column '{column_edit}'.")
                raise TypeError(f"Expected str, got {type(new_value)} for bytes-type column '{column_edit}'.")
            elif not (isinstance(new_value, int) or isinstance(new_value, float) or isinstance(new_value, str) or isinstance(new_value, bytes) or new_value is None):
                raise UnsupportedValueType(f"Type of value '{new_value}' is unsupported. Supported types: int, float, str, None")

            items = await self.get_table(table)
            pk_col = await self._get_pk(table)
            notnull_cols = await self._get_nn(table)
            unique_cols = await self._get_uq(table)

            column_values = await self.get_column(table, column_edit, "IND")
            if column_values:
                itms = [i[1] for i in column_values]
            else:
                itms = []
            if column_edit == pk_col or (unique_cols and column_edit in unique_cols):
                if new_value in itms and new_value != current_value:
                    raise UniqueConstraintViolation(f"Trying to insert already existing value to unique column '{column_edit}'.")

            if notnull_cols and column_edit in notnull_cols:
                if new_value is None:
                    raise NotNullConstraintViolation(f"Trying to insert 'NULL' value to 'NOT NULL' column '{column_edit}'.")

            sql = f"UPDATE \"{table}\" SET \"{column_edit}\" = ? WHERE rowid = (SELECT rowid FROM \"{table}\" WHERE \"{column_find}\" = ? LIMIT 1)"

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, (new_value, current_value))
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def get_row(self, table: str, arg: Union[Tuple[str, Union[str, int, float, bytes, None]], None] = None, index: Union[int, None] = None) -> Union[Dict, None]:
        """
        This function returns first found row based on arg or row based on index.

        :param table: Table name.
        :type table: :obj:`str`

        :param arg: Tuple of (column, value) to search for
        :type arg: Optional[:obj:`tuple`]

        :param index: Index of row
        :type index: Optional[:obj:`int`]

        :return: Row as dict, where keys are columns and values are names or None
        :rtype: :obj:`Dict | None`
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"No such table '{table}'.")

            if not arg and index is None:
                raise MissingRequiredArgument(f"At least one (arg or index) must be provided for method 'get_row'.")

            result: Union[Dict, None] = None

            if arg and not index:
                if not arg[0] in [i["name"] for i in self.tables[table]["columns"]]:
                    raise ColumnNotFound(f"No such column '{arg[0]}'.")
                
                if not isinstance(arg, tuple) or len(arg) != 2:
                    raise InvalidArgsType(f"Incorrect type of args. Must be not empty tuple.")

                sql = f"SELECT * FROM \"{table}\" WHERE \"{arg[0]}\" = ? LIMIT 1"

                async with aiosqlite.connect(self.path_to_database) as conn:
                    conn.row_factory = aiosqlite.Row
                    async with conn.cursor() as cursor:
                        await cursor.execute(sql, (arg[1],))

                        row = await cursor.fetchone()
                        if row:
                            result = dict(row)

                if result:
                    return result

            elif index is not None:
                if not isinstance(index, int):
                    raise InvalidIndexType(f"Index must be an integer.")

                if index < 0:
                    raise InvalidIndexValue(f"Index must be greater or equal zero.")

                table_info = await self.get_table(table)
                if table_info is None or len(table_info) == 0:
                    return None

                if index >= len(table_info):
                    raise IndexOutOfRange(f"Index out of range.")
                
                return table_info[index]

            return None

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

    @db_exists
    async def delete_row(self, table: str, arg: Tuple[str, Union[str, int, float, bytes, None]]):
        """
        This function deletes first found row based on arg.

        :param table: Table name.
        :type table: :obj:`str`

        :param arg: Tuple of (column, value) to search for
        :type arg: :obj:`tuple`

        :return: None
        """
        try:
            if table not in self.tables:
                raise TableNotFound(f"No such table '{table}'.")

            if not isinstance(arg, tuple) or len(arg) != 2:
                raise InvalidArgsType(f"Incorrect type of args. Must be not empty tuple.")

            column, value = arg

            if not column in [i["name"] for i in self.tables[table]["columns"]]:
                raise ColumnNotFound(f"No such column '{column}'.")

            sql = f"DELETE FROM \"{table}\" WHERE \"{column}\" = ?"

            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, (value,))
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")

            

    def to_dict(self) -> Dict:
        return asdict(self)


    def __str__(self) -> str:
        return (
            "aioeasysqlite.db(\n"
            f'\tpath_to_database="{self.path_to_database}",\n'
            f"\ttables={json.dumps(self.tables, indent=4, ensure_ascii=False)}\n)"
        )
    

    def __repr__(self) -> str:
        return str(self)

    @db_exists
    async def _remove_column(self, table: str, column: str):
        """
        :meta: Private
        """
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"PRAGMA table_info(\"{table}\")")
                    table_info = await cursor.fetchall()

                    columns = [(i[1], i[2]) for i in table_info if i[1] != column]

                    if not columns:
                        await self.delete_table(table)
                        return

                    new_columns_metadata = [i for i in self.tables[table]["columns"] if i["name"] != column]
                    self.tables[table]["columns"] = new_columns_metadata

                    new_def = ", ".join([f"\"{name}\" {type_}" for name, type_ in columns])
                    temp_table_name = f"temp_{table}"
                    temp_sql = f"CREATE TABLE \"{temp_table_name}\" ({new_def})"

                    column_names = [name for name, _ in columns]
                    act_columns = ", ".join(f"\"{col}\"" for col in column_names)
                    insert_sql = f"INSERT INTO \"{temp_table_name}\" ({act_columns}) SELECT {act_columns} FROM \"{table}\""

                    await cursor.execute("BEGIN")
                    await cursor.execute(temp_sql)
                    await cursor.execute(insert_sql)
                    await cursor.execute(f"DROP TABLE \"{table}\"")
                    await cursor.execute(f"ALTER TABLE \"{temp_table_name}\" RENAME TO \"{table}\"")
                    await conn.commit()

        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
        except Exception as e:
            raise AioEasySqliteError(f"Unexpected error occurred: {e}")

    @db_exists
    async def _get_pk(self, table: str) -> Union[str, None]:
        """
        :meta: Private
        """
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"PRAGMA table_info(\"{table}\")")
                    rows = await cursor.fetchall()

            if rows:
                for row in rows:
                    if row[5] == 1:
                        return row[1]
            return None
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
        except Exception as e:
            raise AioEasySqliteError(f"Error in _get_pk method: {e}")

    @db_exists
    async def _get_type(self, table: str, column: str) -> Union[str, None]:
        """
        :meta: Private
        """
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"PRAGMA table_info(\"{table}\")")
                    rows = await cursor.fetchall()

            if rows:
                for row in rows:
                    if row[1] == column:
                        return row[2]
            return None
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
        except Exception as e:
            raise AioEasySqliteError(f"Error in _get_type method: {e}")

    @db_exists
    async def _get_nn(self, table: str) -> Union[List[str], None]:
        """
        :meta: Private
        """
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"PRAGMA table_info(\"{table}\")")
                    rows = await cursor.fetchall()

            result = []
            if rows:
                for row in rows:
                    if row[3] == 1: # Corrected: 0 means nullable, 1 means not nullable
                        result.append(row[1])
            if result:
                return result
            return None
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Database error: {e}")
        except Exception as e:
            raise AioEasySqliteError(f"Error in _get_nn method: {e}")

    async def _get_uq(self, table: str) -> Union[List[str], None]:
        """
        :meta: Private
        """
        try:
            result = []

            for column in self.tables[table]["columns"]:
                if column["is_unique"]:
                    result.append(column["name"])
            if result:
                return result
            return None
        except Exception as e:
            raise AioEasySqliteError(f"Error in _get_uq method: {e}")
    
    async def _retrieveData(self) -> Dict[str, Dict[str, Any]]:
        """
        :meta: Private
        """
        result: Dict[str, Dict[str, Any]] = {}
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    table_names = [row[0] for row in await cursor.fetchall()]

                    for table_name in table_names:
                        result[table_name] = {"columns": []}

                        await cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                        create_table_statement = await cursor.fetchone()
                        create_table_sql = create_table_statement[0] if create_table_statement else ""

                        await cursor.execute(f"PRAGMA table_info('{table_name}')")
                        columns_info = await cursor.fetchall()

                        for column in columns_info:
                            column_name = column[1]
                            
                            is_unique = await self._is_column_unique(table_name, column_name)

                            column_data = {
                                "name": column_name,
                                "type": column[2],
                                "is_unique": is_unique,
                            }
                            result[table_name]["columns"].append(column_data)                   
        except aiosqlite.Error as e:
            raise AioEasySqliteError(f"Error in _retrieveData method: {e}")

        return result


    async def _is_column_unique(self, table_name: str, column_name: str) -> bool:
        """
        :meta: Private
        """
        try:
            async with aiosqlite.connect(self.path_to_database) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"PRAGMA index_list('{table_name}');")
                    indexes = await cursor.fetchall()

                    for index in indexes:
                        index_name = index[1]
                        is_unique = index[2]

                        if is_unique:
                            await cursor.execute(f"PRAGMA index_info('{index_name}');")
                            index_info = await cursor.fetchall()

                            for column_info in index_info:
                                if column_info[2] == column_name:
                                    return True
        except Exception as e:
            print(f"Error in _is_column_unique method: {e}")
        finally:
            return False