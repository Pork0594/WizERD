"""Unit tests for the DDL parser."""

import json
from pathlib import Path

from wizerd.parser.ddl_parser import DDLParser

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "dev/dumps/examples"


def test_parse_simple_schema():
    """Simple example schema should produce tables with PKs and FKs."""
    parser = DDLParser()
    schema = parser.parse_file(EXAMPLES_DIR / "simple_schema.sql")

    assert set(schema.tables.keys()) == {"users", "posts", "likes"}

    users = schema.tables["users"]
    assert users.columns["id"].is_primary is True
    assert users.columns["username"].nullable is False

    posts = schema.tables["posts"]
    assert posts.columns["id"].is_primary is True
    assert "user_id" in posts.columns
    assert posts.columns["user_id"].nullable is True

    assert len(posts.foreign_keys) == 1
    fk = posts.foreign_keys[0]
    assert fk.target_table == "users"
    assert fk.source_columns == ["user_id"]
    assert fk.target_columns == ["id"]


def test_parser_handles_complex_constraints():
    """The parser should capture defaults, checks, uniques, and FK options."""
    sql_text = """
    CREATE TABLE data.orders (
        id uuid,
        order_number integer NOT NULL,
        created_at timestamp with time zone DEFAULT now() NOT NULL,
        description text,
        CONSTRAINT chk_description CHECK ((description IS NULL) OR (char_length(description) <= 50)),
        CONSTRAINT uq_order_number UNIQUE (order_number)
    );

    CREATE TABLE data.order_items (
        order_id uuid NOT NULL,
        line_no integer NOT NULL,
        amount numeric(10,2) DEFAULT 0.0,
        note text,
        CONSTRAINT amount_positive CHECK ((amount >= 0))
    );

    ALTER TABLE ONLY data.orders
        ADD CONSTRAINT orders_pkey PRIMARY KEY (id);

    ALTER TABLE ONLY data.order_items
        ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_id, line_no);

    ALTER TABLE ONLY data.order_items
        ADD CONSTRAINT fk_order_items_orders FOREIGN KEY (order_id) REFERENCES data.orders(id) ON DELETE CASCADE;

    ALTER TABLE ONLY data.order_items
        ADD CONSTRAINT order_items_unique UNIQUE (order_id, line_no);
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    assert "data.orders" in schema.tables
    assert "data.order_items" in schema.tables

    orders = schema.tables["data.orders"]
    assert orders.primary_key == ["id"]
    assert orders.columns["created_at"].default == "now()"
    assert any(
        check.expression.startswith("(description IS NULL") for check in orders.check_constraints
    )
    unique_sets = [tuple(unique.columns) for unique in orders.unique_constraints]
    assert ("order_number",) in unique_sets

    order_items = schema.tables["data.order_items"]
    assert order_items.primary_key == ["order_id", "line_no"]
    assert order_items.columns["amount"].default == "0.0"
    assert any(
        check.expression.startswith("(amount >= 0") for check in order_items.check_constraints
    )
    fk = order_items.foreign_keys[0]
    assert fk.target_table == "data.orders"
    assert fk.on_delete == "CASCADE"


def test_parser_handles_real_schema_dump():
    """Large real-world dumps should produce dozens of tables without error."""
    parser = DDLParser()
    schema = parser.parse_file(EXAMPLES_DIR / "large_schema.sql")

    assert len(schema.tables) >= 50
    assert "data.bill_related_bills" in schema.tables
    related = schema.tables["data.bill_related_bills"]
    assert len(related.check_constraints) >= 2
    assert any(fk.target_table == "data.bills" for fk in related.foreign_keys)


def test_self_referencing_foreign_key():
    """Self-referencing FK definitions should keep both ends on same table."""
    sql_text = """
    CREATE TABLE hr.employees (
        id uuid PRIMARY KEY,
        manager_id uuid,
        CONSTRAINT fk_manager FOREIGN KEY (manager_id) REFERENCES hr.employees(id)
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    employees = schema.tables["hr.employees"]
    assert employees.foreign_keys
    fk = employees.foreign_keys[0]
    assert fk.source_table == "hr.employees"
    assert fk.target_table == "hr.employees"
    assert fk.source_columns == ["manager_id"]
    assert fk.target_columns == ["id"]


def test_circular_dependencies_are_tracked():
    """Mutually-referential tables should retain the correct FK targets."""
    sql_text = """
    CREATE TABLE network.a (
        id uuid PRIMARY KEY,
        b_id uuid
    );

    CREATE TABLE network.b (
        id uuid PRIMARY KEY,
        c_id uuid
    );

    CREATE TABLE network.c (
        id uuid PRIMARY KEY,
        a_id uuid
    );

    ALTER TABLE ONLY network.a
        ADD CONSTRAINT fk_a FOREIGN KEY (b_id) REFERENCES network.b(id);

    ALTER TABLE ONLY network.b
        ADD CONSTRAINT fk_b FOREIGN KEY (c_id) REFERENCES network.c(id);

    ALTER TABLE ONLY network.c
        ADD CONSTRAINT fk_c FOREIGN KEY (a_id) REFERENCES network.a(id);
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    assert schema.tables["network.a"].foreign_keys[0].target_table == "network.b"
    assert schema.tables["network.b"].foreign_keys[0].target_table == "network.c"
    assert schema.tables["network.c"].foreign_keys[0].target_table == "network.a"


def test_tables_without_relationships_are_preserved():
    """Standalone tables should still appear in the schema output."""
    sql_text = """
    CREATE TABLE misc.audit_log (
        id uuid PRIMARY KEY,
        payload text NOT NULL
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    audit = schema.tables["misc.audit_log"]
    assert audit.foreign_keys == []
    assert audit.columns["payload"].nullable is False


def test_schema_prefixes_distinguish_tables():
    """Tables with the same name in different schemas must be distinct."""
    sql_text = """
    CREATE TABLE auth.users (
        id uuid PRIMARY KEY
    );

    CREATE TABLE public.users (
        id uuid PRIMARY KEY
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    assert set(schema.tables.keys()) == {"auth.users", "public.users"}
    assert schema.tables["auth.users"].schema == "auth"
    assert schema.tables["public.users"].schema == "public"


def test_unqualified_references_use_table_schema():
    """FKs without schema qualifiers should default to the table's schema."""
    sql_text = """
    CREATE TABLE data.parents (
        id uuid PRIMARY KEY
    );

    CREATE TABLE data.children (
        id uuid PRIMARY KEY,
        parent_id uuid
    );

    ALTER TABLE ONLY data.children
        ADD CONSTRAINT fk_child_parent FOREIGN KEY (parent_id) REFERENCES parents(id);
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    children = schema.tables["data.children"]
    assert children.foreign_keys
    fk = children.foreign_keys[0]
    assert fk.target_table == "data.parents"


def test_handles_quoted_identifiers_and_self_reference():
    """Parser should respect quoted identifiers and complex names."""
    sql_text = """
    CREATE TABLE "SalesDept"."Region Accounts" (
        "Account Id" uuid PRIMARY KEY,
        "Parent Account Id" uuid,
        "Display-Name" text NOT NULL,
        CONSTRAINT "fk parent" FOREIGN KEY ("Parent Account Id") REFERENCES "SalesDept"."Region Accounts"("Account Id")
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    table_key = "SalesDept.Region Accounts"
    assert table_key in schema.tables
    table = schema.tables[table_key]
    assert "Account Id" in table.columns
    assert table.columns["Display-Name"].nullable is False
    fk = table.foreign_keys[0]
    assert fk.target_table == table_key
    assert fk.source_columns == ["Parent Account Id"]
    assert fk.target_columns == ["Account Id"]


def test_inline_foreign_key_with_options():
    """Inline REFERENCES clauses should capture ON DELETE/UPDATE options."""
    sql_text = """
    CREATE TABLE config.parents (
        id uuid PRIMARY KEY
    );

    CREATE TABLE config.children (
        id uuid PRIMARY KEY,
        parent_id uuid REFERENCES config.parents(id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
            MATCH SIMPLE
            DEFERRABLE INITIALLY DEFERRED
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    fk = schema.tables["config.children"].foreign_keys[0]
    assert fk.target_table == "config.parents"
    assert fk.on_delete == "SET NULL"
    assert fk.on_update == "CASCADE"


def test_alter_table_adds_primary_and_unique_without_constraint_names():
    """Unnamed ALTER TABLE constraints should still be applied."""
    sql_text = """
    CREATE TABLE inventory.items (
        sku text,
        name text,
        price numeric
    );

    ALTER TABLE ONLY inventory.items
        ADD PRIMARY KEY (sku);

    ALTER TABLE ONLY inventory.items
        ADD UNIQUE (name);
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    items = schema.tables["inventory.items"]
    assert items.primary_key == ["sku"]
    assert any(unique.columns == ["name"] for unique in items.unique_constraints)


def test_multiline_check_constraints_preserved():
    """Multi-line CHECK expressions should be captured verbatim."""
    sql_text = """
    CREATE TABLE finance.ledger (
        id uuid PRIMARY KEY,
        amount numeric NOT NULL,
        currency char(3) NOT NULL,
        CONSTRAINT chk_amount_valid
            CHECK (
                (amount > 0)
                AND ((currency)::text = upper((currency)::text))
            )
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    ledger = schema.tables["finance.ledger"]
    assert any("amount > 0" in check.expression for check in ledger.check_constraints)


def test_non_table_statements_are_skipped():
    """Non-table statements should be ignored rather than crash the parser."""
    sql_text = """
    SET statement_timeout = 0;
    CREATE VIEW analytics.bill_summary AS SELECT 1;
    CREATE INDEX idx_dummy ON data.bill_actions (bill_id);
    \\connect other_db
    CREATE TABLE analytics.metrics (
        id uuid PRIMARY KEY
    );
    """

    parser = DDLParser()
    schema = parser.parse(sql_text)

    assert set(schema.tables.keys()) == {"analytics.metrics"}


def test_complex_fixture_matches_snapshot():
    """Regression: the complex fixture should match the stored snapshot."""
    parser = DDLParser()
    schema = parser.parse_file(Path("tests/fixtures/complex_sample.sql"))
    expected = json.loads(Path("tests/fixtures/complex_sample.expected.json").read_text())

    assert schema.to_dict() == expected
