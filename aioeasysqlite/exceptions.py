# aioeasysqlite - Async SQLite client for Python
# Copyright (c) 2025 Treizd
#
# This file is part of aioeasysqlite.
#
# aioeasysqlite is free software: you can redistribute it and/or modify
# it under the terms of the MIT License. See the LICENSE file for details.


class AioEasySqliteError(Exception):
    """Base class for aioeasysqlite exceptions ^-^."""
    pass

class EncodeError(AioEasySqliteError):
    """Raised when could not convert value to bytes."""
    pass

class PathNotFound(AioEasySqliteError):
    """Raised when the specified database path does not exist."""
    pass


class InvalidDatabasePath(AioEasySqliteError):
    """Raised when the provided path is not a valid .db file."""
    pass


class InvalidTableName(AioEasySqliteError):
    """Raised when the table name is invalid (e.g., starts with 'sqlite_')."""
    pass


class InvalidCharacterInName(AioEasySqliteError):
    """Raised when a name contains invalid characters."""
    pass


class TableAlreadyExists(AioEasySqliteError):
    """Raised when attempting to create a table that already exists."""
    pass


class TableNotFound(AioEasySqliteError):
    """Raised when a table is not found."""
    pass


class UnknownColumnType(AioEasySqliteError):
    """Raised when an unknown column type is specified."""
    pass


class ColumnAlreadyExists(AioEasySqliteError):
    """Raised when attempting to create a column that already exists."""
    pass


class InvalidAutoincrementUsage(AioEasySqliteError):
    """Raised when autoincrement is used on a non-integer column."""
    pass


class InvalidDefaultValue(AioEasySqliteError):
    """Raised when an invalid default value is used (e.g., NULL for NOT NULL)."""
    pass


class ColumnNotFound(AioEasySqliteError):
    """Raised when a column is not found."""
    pass


class InvalidArgsType(AioEasySqliteError):
    """Raised when the 'args' parameter has an incorrect type."""
    pass


class InvalidArgsLength(AioEasySqliteError):
    """Raised when the length of a tuple in 'args' is incorrect."""
    pass


class InvalidValueConversion(AioEasySqliteError):
    """Raised when a value cannot be converted to the required type."""
    pass


class UnsupportedValueType(AioEasySqliteError):
    """Raised when a value has an unsupported type."""
    pass


class DuplicateColumnInArgs(AioEasySqliteError):
    """Raised when trying to add multiple values to the same column."""
    pass


class UniqueConstraintViolation(AioEasySqliteError):
    """Raised when a unique constraint is violated."""
    pass


class NotNullConstraintViolation(AioEasySqliteError):
    """Raised when a not-null constraint is violated."""
    pass


class MissingRequiredArgument(AioEasySqliteError):
    """Raised when a required argument is missing."""
    pass


class InvalidIndexType(AioEasySqliteError):
    """Raised when an index has an invalid type."""
    pass


class InvalidIndexValue(AioEasySqliteError):
    """Raised when an index has an invalid value."""
    pass


class IndexOutOfRange(AioEasySqliteError):
    """Raised when an index is out of range."""
    pass

class InvalidType(AioEasySqliteError):
    """Raised when type is invalid"""
    pass
