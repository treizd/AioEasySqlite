# Changelog

## [1.1.0] - 2025-11-21
## Fixed
- edit_row() method docstring

## [1.0.9] - 2025-09-27
## Fixed
- class name 'db' -> 'Db'

## [1.0.8] - 2025-09-19
### Fixed
- Some type-bugs

## Removed
- `__dict__` method (replaced with `to_dict()`)

### Updated
- README.md

## [1.0.7] - 2025-09-17
### Fixed
- default keyword usage
- multiple primary keys columns

### Added
- autoincrement + primary key usage check
- Some new tests

## [1.0.3] - 2025-08-30
### Fixed
- clear_database method

### Updated
- edit_row method
- README.md example usages

## [1.0.2] - 2025-08-30
### Fixed
- get_column method

## [1.0.1] - 2025-08-29
### Fixed
- get_column method enumeration

## [1.0.0] - 2025-08-29
### Updated
- dir method
- exceptions import

## [0.0.7] - 2025-08-29
### Fixed
- Now you can retrieve existing old data from database using load_data method

### Updated
- Updated tests

## [0.0.6] - 2025-08-28
### Updated
- Added @db_exists decorator instead of repeating same code in every function

## [0.0.5] - 2025-08-26
### Added
- Column type 'BLOB' (class bytes)
- New exception -> EncodeError
- CHANGELOG.md

### Fixed
- Some annotations bugs
- edit_table inappropriate name check
- Other small issues
- Copyright text
- README.MD

### Updated
- Annotations. Now project supports Python of 3.5 or higher version
- Required aiosqlite version

### Removed
- Documentation href

## [0.0.4] - 2025-08-08
### Added
- License

### Fixed
- Some annotations bugs
