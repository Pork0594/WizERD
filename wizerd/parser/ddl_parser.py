"""SQL dump parser for PostgreSQL schemas."""

from __future__ import annotations

import logging
import re
from collections import deque
from pathlib import Path
from typing import Deque, Iterable, List, Optional, Sequence, Tuple

import sqlparse
from sqlparse import sql as sql_nodes
from sqlparse import tokens as T

from wizerd.model.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    SchemaModel,
    Table,
    UniqueConstraint,
)

logger = logging.getLogger(__name__)


class StatementType:
    """Enum-like container for the statement categories we care about."""

    CREATE_TABLE = "create_table"
    ALTER_TABLE = "alter_table"


class DDLParser:
    """Parses PostgreSQL DDL statements into the internal schema model."""

    _POST_TABLE_KEYWORDS = {"IF", "NOT", "EXISTS", "ONLY", "TEMP", "TEMPORARY", "UNLOGGED"}
    _CONSTRAINT_STARTERS = {
        "CONSTRAINT",
        "PRIMARY",
        "REFERENCES",
        "NOT",
        "NULL",
        "UNIQUE",
        "CHECK",
        "DEFAULT",
        "GENERATED",
        "COLLATE",
        "ON",
        "MATCH",
    }
    _IDENT_PATTERN = r'(?:"[^"]+"|[\w$]+)'

    def parse(self, sql_text: str) -> SchemaModel:
        """Parse raw SQL text into a SchemaModel understood by renderers.

        This method applies the same preprocessing as `psql` (strip backslash
        commands and comments), feeds statements through sqlparse, and then
        dispatches to specialized handlers for CREATE TABLE and ALTER TABLE
        statements.  All other statements are logged and ignored so dump files
        can include grants, set commands, etc. without failing the run.
        """
        schema = SchemaModel()
        prepared = self._prepare_sql(sql_text)
        if not prepared.strip():
            return schema

        for statement in sqlparse.parse(prepared):
            text = statement.value.strip()
            if not text:
                continue

            stmt_type = self._classify_statement(statement)
            if stmt_type == StatementType.CREATE_TABLE:
                table = self._parse_create_table(statement)
                if not table:
                    continue
                existing = schema.tables.get(table.name)
                if existing:
                    table.foreign_keys = existing.foreign_keys + table.foreign_keys
                    table.unique_constraints = (
                        existing.unique_constraints + table.unique_constraints
                    )
                    table.check_constraints = existing.check_constraints + table.check_constraints
                    if not table.primary_key and existing.primary_key:
                        table.primary_key = existing.primary_key
                schema.add_table(table)
            elif stmt_type == StatementType.ALTER_TABLE:
                self._apply_alter_table(statement, schema)
            else:
                logger.debug("Skipping unsupported statement: %s", text.splitlines()[0][:80])

        return schema

    def parse_file(self, path: Path) -> SchemaModel:
        """Read a schema file from disk and delegate to `parse`."""
        return self.parse(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Statement preparation & classification
    # ------------------------------------------------------------------
    def _prepare_sql(self, sql_text: str) -> str:
        """Normalize dump text by removing psql meta-commands and comments."""
        filtered_lines = []
        for line in sql_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("\\"):
                continue
            filtered_lines.append(line)
        cleaned = "\n".join(filtered_lines)
        return sqlparse.format(cleaned, strip_comments=True)

    def _classify_statement(self, statement: sql_nodes.Statement) -> Optional[str]:
        """Return the statement type we know how to handle or None."""
        first_token = statement.token_first(skip_cm=True, skip_ws=True)
        if not first_token:
            return None

        if first_token.match(T.Keyword.DDL, "CREATE") or first_token.match(T.Keyword, "CREATE"):
            result = statement.token_next(
                statement.token_index(first_token), skip_cm=True, skip_ws=True
            )
            if result is not None:
                next_token = result[1]
                if next_token and next_token.match(T.Keyword, "TABLE"):
                    return StatementType.CREATE_TABLE

        if first_token.match(T.Keyword.DDL, "ALTER") or first_token.match(T.Keyword, "ALTER"):
            result = statement.token_next(
                statement.token_index(first_token), skip_cm=True, skip_ws=True
            )
            if result is not None:
                next_token = result[1]
                if next_token and next_token.match(T.Keyword, "TABLE"):
                    return StatementType.ALTER_TABLE

        return None

    # ------------------------------------------------------------------
    # CREATE TABLE parsing
    # ------------------------------------------------------------------
    def _parse_create_table(self, statement: sql_nodes.Statement) -> Optional[Table]:
        """Parse a CREATE TABLE statement into a Table object.

        We collect inline column definitions as well as table-level constraints
        so downstream ALTER TABLE statements only need to merge deltas.
        """
        identifier_result = self._identifier_after_keyword(statement, "TABLE")
        if not identifier_result:
            logger.warning("Unable to find table name in statement: %s", statement.value[:80])
            return None

        schema_name, table_name, full_name, token_index = identifier_result
        table = Table(name=full_name, schema=schema_name)

        body = self._extract_table_body(statement)
        if body is None:
            logger.warning("CREATE TABLE %s missing body", full_name)
            return table

        for definition in self._split_definitions(body):
            if not definition:
                continue
            if self._is_table_constraint(definition):
                self._apply_table_constraint(table, definition, full_name)
            else:
                self._parse_column_definition(table, definition, full_name)

        return table

    def _extract_table_body(self, statement: sql_nodes.Statement) -> Optional[str]:
        """Return the raw text between the parentheses of CREATE TABLE."""
        for token in statement.tokens:
            if isinstance(token, sql_nodes.Parenthesis):
                content = token.value.strip()
                if content.startswith("(") and content.endswith(")"):
                    return content[1:-1]
                return content
        return None

    # ------------------------------------------------------------------
    # ALTER TABLE parsing
    # ------------------------------------------------------------------
    def _apply_alter_table(self, statement: sql_nodes.Statement, schema: SchemaModel) -> None:
        """Apply ALTER TABLE mutations to an existing SchemaModel."""
        identifier_result = self._identifier_after_keyword(statement, "TABLE")
        if not identifier_result:
            logger.warning("Unable to parse ALTER TABLE statement: %s", statement.value[:80])
            return

        schema_name, _, full_name, token_index = identifier_result
        table = schema.tables.get(full_name)
        if not table:
            logger.info("Encountered ALTER TABLE for unknown %s; creating placeholder", full_name)
            table = Table(name=full_name, schema=schema_name)
            schema.add_table(table)

        body = self._tokens_to_string(statement.tokens[token_index + 1 :]).strip()
        if not body:
            return

        body = body.rstrip(";")
        for action in self._split_actions(body):
            if not action:
                continue
            upper_action = action.lstrip().upper()
            if upper_action.startswith("ADD CONSTRAINT"):
                definition = action.strip()[len("ADD ") :].strip()
                self._apply_table_constraint(table, definition, full_name)
            elif upper_action.startswith("ADD PRIMARY KEY"):
                definition = action.strip()[len("ADD ") :].strip()
                self._apply_table_constraint(table, definition, full_name)
            elif (
                upper_action.startswith("ADD UNIQUE")
                or upper_action.startswith("ADD FOREIGN KEY")
                or upper_action.startswith("ADD CHECK")
            ):
                definition = action.strip()[len("ADD ") :].strip()
                self._apply_table_constraint(table, definition, full_name)
            else:
                logger.debug("Skipping ALTER TABLE action on %s: %s", full_name, action.strip())

    # ------------------------------------------------------------------
    # Definition parsing helpers
    # ------------------------------------------------------------------
    def _split_definitions(self, body: str) -> Iterable[str]:
        """Split the CREATE TABLE body into individual column/constraint defs."""
        return self._split_sections(body, delimiter=",")

    def _split_actions(self, body: str) -> Iterable[str]:
        """Split ALTER TABLE statements into individual actions."""
        return self._split_sections(body, delimiter=",")

    def _split_sections(self, body: str, delimiter: str) -> List[str]:
        """Split a comma-separated section while respecting nested parentheses."""
        sections: List[str] = []
        depth = 0
        current: List[str] = []
        in_quotes = False
        quote_char = ""
        for char in body:
            if char in {'"', "'"}:
                if in_quotes and char == quote_char:
                    in_quotes = False
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                current.append(char)
                continue
            if char == delimiter and depth == 0 and not in_quotes:
                section = "".join(current).strip()
                if section:
                    sections.append(section)
                current = []
                continue
            current.append(char)
            if char == "(":
                depth += 1
            elif char == ")" and depth > 0:
                depth -= 1
        if current:
            section = "".join(current).strip()
            if section:
                sections.append(section)
        return sections

    def _is_table_constraint(self, definition: str) -> bool:
        """Return True if the definition represents a table-level constraint."""
        leading = definition.lstrip()
        if not leading:
            return False
        if leading.startswith('"'):
            return False
        match = re.match(r"([A-Za-z_]+)", leading)
        if not match:
            return False
        return match.group(1).upper() in {"CONSTRAINT", "PRIMARY", "FOREIGN", "UNIQUE", "CHECK"}

    def _parse_column_definition(self, table: Table, definition: str, table_name: str) -> None:
        """Parse a single column definition and attach metadata to the table."""
        name, remainder = self._extract_leading_identifier(definition)
        if not name:
            logger.warning(
                "Skipping column definition without name on %s: %s", table_name, definition
            )
            return

        tokens = self._tokenize_definition(remainder)
        type_tokens: List[str] = []
        idx = 0
        while idx < len(tokens):
            token_upper = tokens[idx].upper()
            if token_upper in self._CONSTRAINT_STARTERS:
                break
            type_tokens.append(tokens[idx])
            idx += 1

        column_type = " ".join(type_tokens).strip()
        constraint_tokens: Deque[str] = deque(tokens[idx:])

        nullable = True
        default_expr: Optional[str] = None
        is_primary = False
        pending_name: Optional[str] = None

        while constraint_tokens:
            token = constraint_tokens.popleft()
            upper = token.upper()

            if upper == "CONSTRAINT" and constraint_tokens:
                pending_name = self._normalize_identifier(constraint_tokens.popleft())
                continue

            if upper == "NOT" and constraint_tokens and constraint_tokens[0].upper() == "NULL":
                nullable = False
                constraint_tokens.popleft()
                continue

            if upper == "NULL":
                continue

            if upper == "DEFAULT":
                default_expr_parts: List[str] = []
                while constraint_tokens:
                    peek = constraint_tokens[0]
                    if peek.upper() in self._CONSTRAINT_STARTERS:
                        break
                    default_expr_parts.append(constraint_tokens.popleft())
                default_expr = " ".join(default_expr_parts).strip()
                pending_name = None
                continue

            if upper == "GENERATED":
                generated_parts = [token]
                while constraint_tokens:
                    generated_parts.append(constraint_tokens.popleft())
                    if generated_parts[-1].upper() == "IDENTITY":
                        break
                default_expr = " ".join(generated_parts)
                pending_name = None
                continue

            if upper == "PRIMARY" and constraint_tokens and constraint_tokens[0].upper() == "KEY":
                is_primary = True
                nullable = False
                constraint_tokens.popleft()
                pending_name = None
                continue

            if upper == "UNIQUE":
                table.unique_constraints.append(UniqueConstraint(name=pending_name, columns=[name]))
                pending_name = None
                continue

            if upper == "CHECK" and constraint_tokens:
                expression = self._strip_wrapping_parentheses(constraint_tokens.popleft())
                table.check_constraints.append(
                    CheckConstraint(name=pending_name, expression=expression)
                )
                pending_name = None
                continue

            if upper == "REFERENCES":
                target_token = constraint_tokens.popleft() if constraint_tokens else ""
                table_token = target_token
                column_section: Optional[str] = None
                if "(" in target_token:
                    table_part, _, remainder = target_token.partition("(")
                    table_token = table_part.strip()
                    remainder = remainder.strip()
                    if remainder:
                        column_section = "(" + remainder
                if (
                    column_section is None
                    and constraint_tokens
                    and constraint_tokens[0].startswith("(")
                ):
                    column_section = constraint_tokens.popleft()

                target_full = self._qualify_reference_name(table_token, table.schema)
                target_columns: List[str] = []
                if column_section:
                    target_columns = self._extract_identifier_list(column_section)

                on_delete, on_update = self._extract_fk_actions(" ".join(constraint_tokens))
                fk = ForeignKey(
                    name=pending_name,
                    source_table=table.name,
                    source_columns=[name],
                    target_table=target_full,
                    target_columns=target_columns,
                    on_delete=on_delete,
                    on_update=on_update,
                )
                table.foreign_keys.append(fk)
                pending_name = None
                break

            # Skip other keywords (MATCH, DEFERRABLE, etc.)
        column = Column(
            name=name,
            data_type=column_type,
            nullable=nullable,
            default=default_expr,
            is_primary=is_primary,
        )
        table.add_column(column)
        if is_primary:
            self._apply_primary_key(table, [name])

    def _apply_table_constraint(self, table: Table, definition: str, table_name: str) -> None:
        """Handle PRIMARY KEY / FOREIGN KEY etc. defined at the table level."""
        definition = definition.strip()
        if not definition:
            return

        constraint_name: Optional[str] = None
        upper = definition.upper()
        if upper.startswith("CONSTRAINT"):
            remainder = definition[len("CONSTRAINT") :].lstrip()
            name, remainder = self._extract_leading_identifier(remainder)
            if not name or not remainder:
                logger.warning("Malformed CONSTRAINT clause on %s: %s", table_name, definition)
                return
            constraint_name = self._normalize_identifier(name)
            definition = remainder.strip()
            upper = definition.upper()

        if upper.startswith("PRIMARY KEY"):
            columns = self._extract_identifier_list(definition)
            self._apply_primary_key(table, columns)
            return

        if upper.startswith("UNIQUE"):
            columns = self._extract_identifier_list(definition)
            table.unique_constraints.append(UniqueConstraint(name=constraint_name, columns=columns))
            return

        if upper.startswith("CHECK"):
            expression = self._extract_check_expression(definition)
            table.check_constraints.append(
                CheckConstraint(name=constraint_name, expression=expression)
            )
            return

        if upper.startswith("FOREIGN KEY"):
            try:
                source_columns, target_full, target_columns, fk_options = (
                    self._parse_table_foreign_key_definition(
                        definition,
                        table,
                    )
                )
            except ValueError as exc:
                logger.warning(
                    "Unable to parse FOREIGN KEY on %s: %s (%s)", table_name, definition, exc
                )
                return
            on_delete, on_update = self._extract_fk_actions(fk_options)
            table.foreign_keys.append(
                ForeignKey(
                    name=constraint_name,
                    source_table=table.name,
                    source_columns=source_columns,
                    target_table=target_full,
                    target_columns=target_columns,
                    on_delete=on_delete,
                    on_update=on_update,
                )
            )
            return

        logger.warning("Unhandled table constraint on %s: %s", table_name, definition)

    def _apply_primary_key(self, table: Table, columns: List[str]) -> None:
        """Register (and merge) primary key columns on the table model."""
        if not columns:
            return
        existing = set(table.primary_key)
        merged = list(dict.fromkeys([*existing, *columns]))
        table.set_primary_key(merged)
        for column_name in columns:
            if column_name not in table.columns:
                logger.warning(
                    "PRIMARY KEY references unknown column %s on %s", column_name, table.name
                )

    # ------------------------------------------------------------------
    # Identifier & token helpers
    # ------------------------------------------------------------------
    def _parse_table_foreign_key_definition(
        self,
        definition: str,
        table: Table,
    ) -> Tuple[List[str], str, List[str], str]:
        after_fk = definition[len("FOREIGN KEY") :].lstrip()
        source_section, remainder = self._consume_parenthesized_section(after_fk)
        source_columns = self._extract_identifier_list(source_section)

        remainder = remainder.lstrip()
        if not remainder.upper().startswith("REFERENCES"):
            raise ValueError("FOREIGN KEY must include REFERENCES clause")
        after_refs = remainder[len("REFERENCES") :].lstrip()
        table_chars: List[str] = []
        idx = 0
        in_quotes = False
        while idx < len(after_refs):
            char = after_refs[idx]
            if char == '"':
                in_quotes = not in_quotes
            if not in_quotes and char in {" ", "("}:
                break
            table_chars.append(char)
            idx += 1
        table_name = "".join(table_chars).strip()
        remainder = after_refs[idx:].lstrip()
        if not table_name:
            raise ValueError("REFERENCES clause missing target table")
        target_full = self._qualify_reference_name(table_name, table.schema)
        target_columns: List[str] = []
        if remainder.startswith("("):
            target_section, remainder = self._consume_parenthesized_section(remainder)
            target_columns = self._extract_identifier_list(target_section)

        return source_columns, target_full, target_columns, remainder.strip()

    def _consume_parenthesized_section(self, text: str) -> Tuple[str, str]:
        text = text.lstrip()
        if not text.startswith("("):
            raise ValueError("Expected '(' when parsing section")
        depth = 0
        in_quotes = False
        quote_char = ""
        content: List[str] = []
        for idx, char in enumerate(text):
            if char in {'"', "'"}:
                if in_quotes and char == quote_char:
                    in_quotes = False
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                if depth > 0:
                    content.append(char)
                continue
            if not in_quotes:
                if char == "(":
                    depth += 1
                    if depth > 1:
                        content.append(char)
                    continue
                if char == ")":
                    depth -= 1
                    if depth == 0:
                        remainder = text[idx + 1 :]
                        return "".join(content).strip(), remainder.lstrip()
                    content.append(char)
                    continue
            if depth > 0:
                content.append(char)
        raise ValueError("Unbalanced parentheses in definition")

    def _identifier_after_keyword(
        self, statement: sql_nodes.Statement, keyword: str
    ) -> Optional[Tuple[Optional[str], str, str, int]]:
        """Return (schema, name, full, index) for the identifier after keyword."""
        keyword_index = None
        for idx, token in enumerate(statement.tokens):
            if token.match(T.Keyword, keyword):
                keyword_index = idx
                break
        if keyword_index is None:
            return None

        next_idx: Optional[int] = keyword_index
        next_token: Optional[sql_nodes.Token] = None
        while next_idx is not None:
            result = statement.token_next(next_idx, skip_cm=True, skip_ws=True)
            if result is None:
                next_token = None
                break
            candidate_idx, candidate = result
            if candidate is not None and candidate.match(
                T.Keyword, tuple(self._POST_TABLE_KEYWORDS)
            ):
                next_idx = candidate_idx
                continue
            next_idx = candidate_idx
            next_token = candidate
            break

        if next_token is None or next_idx is None:
            return None

        schema_name, table_name, full_name = self._resolve_identifier(next_token)
        resolved_idx: int = next_idx
        return schema_name, table_name, full_name, resolved_idx

    def _resolve_identifier(self, token: sql_nodes.Token) -> Tuple[Optional[str], str, str]:
        """Normalize sqlparse Identifier tokens into (schema, name, full)."""
        if isinstance(token, sql_nodes.Identifier):
            parent = token.get_parent_name()
            real = token.get_real_name() or token.get_name() or token.value.strip()
            schema = parent
            name = real
            full = f"{schema}.{name}" if schema else name
            return schema, name, full
        return self._normalize_qualified_name(token.value)

    def _normalize_qualified_name(self, identifier: str) -> Tuple[Optional[str], str, str]:
        """Handle dotted identifiers with optional quoting and return parts."""
        identifier = identifier.strip()
        if not identifier:
            return None, "", ""
        parts: List[str] = []
        current: List[str] = []
        in_quotes = False
        idx = 0
        while idx < len(identifier):
            char = identifier[idx]
            if char == '"':
                if in_quotes and idx + 1 < len(identifier) and identifier[idx + 1] == '"':
                    current.append('"')
                    idx += 2
                    continue
                in_quotes = not in_quotes
                idx += 1
                continue
            if char == "." and not in_quotes:
                parts.append("".join(current).strip())
                current = []
                idx += 1
                continue
            current.append(char)
            idx += 1
        if current:
            parts.append("".join(current).strip())

        cleaned = [self._normalize_identifier(part) for part in parts if part]
        if not cleaned:
            return None, "", ""
        if len(cleaned) == 1:
            return None, cleaned[0], cleaned[0]
        schema = ".".join(cleaned[:-1])
        name = cleaned[-1]
        return schema, name, f"{schema}.{name}"

    def _normalize_identifier(self, identifier: str) -> str:
        """Unquote identifiers and collapse doubled quotes."""
        identifier = identifier.strip()
        if identifier.startswith('"') and identifier.endswith('"') and len(identifier) >= 2:
            return identifier[1:-1].replace('""', '"')
        return identifier

    def _qualify_reference_name(self, raw_identifier: str, default_schema: Optional[str]) -> str:
        """Return a fully-qualified table name, defaulting to the parent schema."""
        schema, name, full = self._normalize_qualified_name(raw_identifier)
        if schema:
            return full
        if default_schema:
            return f"{default_schema}.{name}"
        return name

    def _tokens_to_string(self, tokens: Sequence[sql_nodes.Token]) -> str:
        """Collapse a sequence of sqlparse tokens back into raw text."""
        return "".join(token.value for token in tokens)

    def _extract_leading_identifier(self, definition: str) -> Tuple[Optional[str], str]:
        """Return the first identifier and the remaining text from a definition."""
        text = definition.lstrip()
        if not text:
            return None, ""
        if text[0] == '"':
            idx = 1
            value: List[str] = []
            while idx < len(text):
                char = text[idx]
                if char == '"':
                    if idx + 1 < len(text) and text[idx + 1] == '"':
                        value.append('"')
                        idx += 2
                        continue
                    idx += 1
                    break
                value.append(char)
                idx += 1
            remainder = text[idx:].lstrip()
            return "".join(value), remainder

        match = re.match(r"([^\s]+)", text)
        if not match:
            return None, text
        name = match.group(1)
        remainder = text[match.end() :].lstrip()
        return name, remainder

    def _tokenize_definition(self, text: str) -> List[str]:
        """Tokenize a definition while tracking quotes and parentheses depth."""
        tokens: List[str] = []
        current: List[str] = []
        depth = 0
        in_quotes = False
        quote_char = ""
        idx = 0
        while idx < len(text):
            char = text[idx]
            if in_quotes:
                current.append(char)
                if char == quote_char:
                    in_quotes = False
                idx += 1
                continue
            if char in ('"', "'"):
                in_quotes = True
                quote_char = char
                current.append(char)
                idx += 1
                continue
            if char == "(":
                depth += 1
                current.append(char)
                idx += 1
                continue
            if char == ")":
                depth = max(0, depth - 1)
                current.append(char)
                idx += 1
                continue
            if char.isspace() and depth == 0:
                if current:
                    tokens.append("".join(current))
                    current = []
                idx += 1
                continue
            current.append(char)
            idx += 1
        if current:
            tokens.append("".join(current))
        return tokens

    def _extract_identifier_list(self, section: str) -> List[str]:
        """Parse comma-separated identifiers, preserving quoted names."""
        section = section.strip()
        if "(" in section and ")" in section:
            start = section.find("(")
            end = section.rfind(")")
            if start != -1 and end != -1 and end > start:
                section = section[start + 1 : end]
        parts: List[str] = []
        current: List[str] = []
        in_quotes = False
        idx = 0
        while idx < len(section):
            char = section[idx]
            if char == '"':
                in_quotes = not in_quotes
                idx += 1
                continue
            if char == "," and not in_quotes:
                parts.append("".join(current).strip())
                current = []
                idx += 1
                continue
            current.append(char)
            idx += 1
        if current:
            parts.append("".join(current).strip())
        return [self._normalize_identifier(part) for part in parts if part]

    def _extract_check_expression(self, definition: str) -> str:
        """Extract the inner expression from a CHECK (...) clause."""
        start = definition.upper().find("CHECK")
        if start == -1:
            return definition
        expr_start = definition.find("(", start)
        if expr_start == -1:
            return definition[start + len("CHECK") :].strip()
        depth = 0
        content_start = expr_start + 1
        for idx in range(expr_start, len(definition)):
            char = definition[idx]
            if char == "(":
                if depth == 0:
                    content_start = idx + 1
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return definition[content_start:idx].strip()
        return definition[expr_start + 1 :].strip().rstrip(")")

    def _strip_wrapping_parentheses(self, text: str) -> str:
        """Remove redundant outer parentheses without touching inner content."""
        stripped = text.strip()
        while stripped.startswith("(") and stripped.endswith(")"):
            stripped = stripped[1:-1].strip()
        return stripped

    def _extract_fk_actions(self, options: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse ON DELETE / ON UPDATE actions from a FK definition tail."""
        on_delete: Optional[str] = None
        on_update: Optional[str] = None
        tokens = self._tokenize_definition(options)
        idx = 0
        stop_words = {
            "ON",
            "MATCH",
            "NOT",
            "DEFERRABLE",
            "INITIALLY",
            "CONSTRAINT",
            "PRIMARY",
            "UNIQUE",
            "CHECK",
        }
        while idx < len(tokens):
            token = tokens[idx].upper()
            if token == "ON" and idx + 2 < len(tokens):
                action_type = tokens[idx + 1].upper()
                value_tokens: List[str] = []
                j = idx + 2
                while j < len(tokens):
                    upper_j = tokens[j].upper()
                    if upper_j in stop_words:
                        break
                    value_tokens.append(tokens[j])
                    j += 1
                value = " ".join(value_tokens).strip() or None
                if action_type == "DELETE":
                    on_delete = value
                elif action_type == "UPDATE":
                    on_update = value
                idx = j
                continue
            idx += 1
        return on_delete, on_update
