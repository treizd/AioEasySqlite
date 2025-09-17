# aioeasysqlite - Async SQLite client for Python
# Copyright (c) 2025 Treizd
#
# This file is part of aioeasysqlite.
#
# aioeasysqlite is free software: you can redistribute it and/or modify
# it under the terms of the MIT License. See the LICENSE file for details.


from . import exceptions
from .db import db

__all__ = ['db', 'exceptions']