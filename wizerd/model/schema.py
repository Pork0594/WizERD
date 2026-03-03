"""Core schema data models."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Column:
    """Represents a single parsed column, including type metadata."""

    name: str
    data_type: str
    nullable: bool = True
    default: Optional[str] = None
    is_primary: bool = False

    def to_dict(self) -> Dict[str, object]:
        """Serialize the column so renderers and tests can inspect metadata."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "nullable": self.nullable,
            "default": self.default,
            "is_primary": self.is_primary,
        }


@dataclass
class Index:
    """Represents a database index from CREATE INDEX statements."""

    name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    index_type: str = "btree"

    def to_dict(self) -> Dict[str, object]:
        """Serialize the index for tooling."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "columns": self.columns,
            "is_unique": self.is_unique,
            "index_type": self.index_type,
        }


@dataclass
class View:
    """Represents a database view from CREATE VIEW statements."""

    name: str
    schema: Optional[str] = None
    definition: str = ""
    columns: List[str] = field(default_factory=list)
    referenced_tables: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Serialize the view for tooling."""
        return {
            "name": self.name,
            "schema": self.schema,
            "definition": self.definition,
            "columns": self.columns,
            "referenced_tables": self.referenced_tables,
        }


@dataclass
class Sequence:
    """Represents a database sequence from CREATE SEQUENCE or SERIAL columns."""

    name: str
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    start_value: int = 1
    increment: int = 1
    min_value: int = 1
    max_value: int = 2147483647

    def to_dict(self) -> Dict[str, object]:
        """Serialize the sequence for tooling."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "start_value": self.start_value,
            "increment": self.increment,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }


@dataclass
class ForeignKey:
    """Internal model of a foreign key relationship."""

    name: Optional[str]
    source_table: str
    source_columns: List[str]
    target_table: str
    target_columns: List[str]
    on_delete: Optional[str] = None
    on_update: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        """Produce a JSON-friendly version that preserves relational context."""
        return {
            "name": self.name,
            "source_table": self.source_table,
            "source_columns": self.source_columns,
            "target_table": self.target_table,
            "target_columns": self.target_columns,
            "on_delete": self.on_delete,
            "on_update": self.on_update,
        }


@dataclass
class UniqueConstraint:
    """Represents a UNIQUE constraint captured from DDL."""

    name: Optional[str]
    columns: List[str]

    def to_dict(self) -> Dict[str, object]:
        """Expose constraint metadata for debugging or export flows."""
        return {
            "name": self.name,
            "columns": self.columns,
        }


@dataclass
class CheckConstraint:
    """Tracks CHECK expressions tied to a given table."""

    name: Optional[str]
    expression: str

    def to_dict(self) -> Dict[str, object]:
        """Represent the check constraint for serialization tools."""
        return {
            "name": self.name,
            "expression": self.expression,
        }


@dataclass
class Table:
    """Logical representation of a CREATE TABLE statement."""

    name: str
    schema: Optional[str] = None
    columns: Dict[str, Column] = field(default_factory=dict)
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    primary_key: List[str] = field(default_factory=list)
    unique_constraints: List[UniqueConstraint] = field(default_factory=list)
    check_constraints: List[CheckConstraint] = field(default_factory=list)
    indexes: List[Index] = field(default_factory=list)
    sequences: List[Sequence] = field(default_factory=list)

    def add_column(self, column: Column) -> None:
        """Insert or replace a column definition on the table."""
        if column.name in self.columns:
            logger.warning("Replacing column definition for %s on table %s", column.name, self.name)
        self.columns[column.name] = column

    def set_primary_key(self, columns: List[str]) -> None:
        """Record the table's primary key and mark participating columns."""
        self.primary_key = columns
        for column_name in columns:
            column = self.columns.get(column_name)
            if column:
                column.is_primary = True
                column.nullable = False

    def to_dict(self) -> Dict[str, object]:
        """Serialize the table, including related constraints, for tooling."""
        return {
            "name": self.name,
            "schema": self.schema,
            "columns": [self.columns[name].to_dict() for name in sorted(self.columns)],
            "foreign_keys": [fk.to_dict() for fk in self.foreign_keys],
            "primary_key": self.primary_key,
            "unique_constraints": [unique.to_dict() for unique in self.unique_constraints],
            "check_constraints": [check.to_dict() for check in self.check_constraints],
            "indexes": [idx.to_dict() for idx in self.indexes],
            "sequences": [seq.to_dict() for seq in self.sequences],
        }


@dataclass
class SchemaModel:
    """High-level container for all parsed tables keyed by their full name."""

    tables: Dict[str, Table] = field(default_factory=dict)
    views: Dict[str, View] = field(default_factory=dict)
    indexes: List[Index] = field(default_factory=list)
    sequences: List[Sequence] = field(default_factory=list)

    def add_table(self, table: Table) -> None:
        """Register or replace a table definition keyed by its full name."""
        if table.name in self.tables:
            logger.warning("Replacing table definition for %s", table.name)
        self.tables[table.name] = table

    def add_view(self, view: View) -> None:
        """Register or replace a view definition keyed by its full name."""
        full_name = f"{view.schema}.{view.name}" if view.schema else view.name
        if full_name in self.views:
            logger.warning("Replacing view definition for %s", full_name)
        self.views[full_name] = view

    def add_index(self, index: Index) -> None:
        """Register an index."""
        self.indexes.append(index)

    def add_sequence(self, sequence: Sequence) -> None:
        """Register a sequence."""
        self.sequences.append(sequence)

    def to_dict(self) -> Dict[str, object]:
        """Produce a nested dictionary for export, tests, or CLI inspection."""
        return {
            "tables": {name: self.tables[name].to_dict() for name in sorted(self.tables)},
            "views": {name: self.views[name].to_dict() for name in sorted(self.views)},
            "indexes": [idx.to_dict() for idx in self.indexes],
            "sequences": [seq.to_dict() for seq in self.sequences],
        }
