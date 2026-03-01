CREATE TABLE inventory.products (
    id uuid NOT NULL,
    sku text NOT NULL,
    name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT products_pkey PRIMARY KEY (id),
    CONSTRAINT products_sku_unique UNIQUE (sku)
);

CREATE TABLE inventory.categories (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    CONSTRAINT categories_name_check CHECK ((char_length(name) > 0))
);

CREATE TABLE inventory.product_categories (
    product_id uuid NOT NULL,
    category_id uuid NOT NULL,
    assigned_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT product_categories_pkey PRIMARY KEY (product_id, category_id),
    CONSTRAINT product_categories_product_id_fkey FOREIGN KEY (product_id) REFERENCES inventory.products(id) ON DELETE CASCADE,
    CONSTRAINT product_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES inventory.categories(id) ON DELETE CASCADE
);

ALTER TABLE ONLY inventory.products
    ADD UNIQUE (name);

ALTER TABLE ONLY inventory.product_categories
    ADD CHECK ((assigned_at IS NOT NULL));
