CREATE TABLE data.bills (
    id uuid PRIMARY KEY,
    bill_number text NOT NULL,
    status text DEFAULT 'draft' NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE data.bill_related_bills (
    id uuid PRIMARY KEY,
    bill_id uuid NOT NULL,
    related_bill_id uuid NOT NULL,
    relation_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_relation_type CHECK (char_length(relation_type) > 0),
    CONSTRAINT chk_distinct_pair CHECK (bill_id <> related_bill_id),
    CONSTRAINT bill_related_bills_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id) ON DELETE CASCADE,
    CONSTRAINT bill_related_bills_related_bill_id_fkey FOREIGN KEY (related_bill_id) REFERENCES data.bills(id) ON DELETE CASCADE
);

CREATE TABLE data.synthetic_01 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_01
    ADD CONSTRAINT synthetic_01_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_02 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_02
    ADD CONSTRAINT synthetic_02_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_03 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_03
    ADD CONSTRAINT synthetic_03_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_04 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_04
    ADD CONSTRAINT synthetic_04_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_05 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_05
    ADD CONSTRAINT synthetic_05_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_06 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_06
    ADD CONSTRAINT synthetic_06_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_07 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_07
    ADD CONSTRAINT synthetic_07_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_08 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_08
    ADD CONSTRAINT synthetic_08_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_09 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_09
    ADD CONSTRAINT synthetic_09_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_10 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_10
    ADD CONSTRAINT synthetic_10_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_11 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_11
    ADD CONSTRAINT synthetic_11_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_12 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_12
    ADD CONSTRAINT synthetic_12_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_13 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_13
    ADD CONSTRAINT synthetic_13_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_14 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_14
    ADD CONSTRAINT synthetic_14_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_15 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_15
    ADD CONSTRAINT synthetic_15_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_16 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_16
    ADD CONSTRAINT synthetic_16_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_17 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_17
    ADD CONSTRAINT synthetic_17_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_18 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_18
    ADD CONSTRAINT synthetic_18_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_19 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_19
    ADD CONSTRAINT synthetic_19_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_20 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_20
    ADD CONSTRAINT synthetic_20_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_21 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_21
    ADD CONSTRAINT synthetic_21_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_22 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_22
    ADD CONSTRAINT synthetic_22_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_23 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_23
    ADD CONSTRAINT synthetic_23_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_24 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_24
    ADD CONSTRAINT synthetic_24_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_25 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_25
    ADD CONSTRAINT synthetic_25_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_26 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_26
    ADD CONSTRAINT synthetic_26_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_27 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_27
    ADD CONSTRAINT synthetic_27_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_28 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_28
    ADD CONSTRAINT synthetic_28_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_29 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_29
    ADD CONSTRAINT synthetic_29_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_30 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_30
    ADD CONSTRAINT synthetic_30_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_31 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_31
    ADD CONSTRAINT synthetic_31_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_32 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_32
    ADD CONSTRAINT synthetic_32_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_33 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_33
    ADD CONSTRAINT synthetic_33_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_34 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_34
    ADD CONSTRAINT synthetic_34_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_35 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_35
    ADD CONSTRAINT synthetic_35_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_36 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_36
    ADD CONSTRAINT synthetic_36_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_37 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_37
    ADD CONSTRAINT synthetic_37_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_38 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_38
    ADD CONSTRAINT synthetic_38_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_39 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_39
    ADD CONSTRAINT synthetic_39_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_40 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_40
    ADD CONSTRAINT synthetic_40_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_41 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_41
    ADD CONSTRAINT synthetic_41_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_42 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_42
    ADD CONSTRAINT synthetic_42_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_43 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_43
    ADD CONSTRAINT synthetic_43_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_44 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_44
    ADD CONSTRAINT synthetic_44_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_45 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_45
    ADD CONSTRAINT synthetic_45_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_46 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_46
    ADD CONSTRAINT synthetic_46_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_47 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_47
    ADD CONSTRAINT synthetic_47_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_48 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_48
    ADD CONSTRAINT synthetic_48_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_49 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_49
    ADD CONSTRAINT synthetic_49_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_50 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_50
    ADD CONSTRAINT synthetic_50_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_51 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_51
    ADD CONSTRAINT synthetic_51_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_52 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_52
    ADD CONSTRAINT synthetic_52_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_53 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_53
    ADD CONSTRAINT synthetic_53_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_54 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_54
    ADD CONSTRAINT synthetic_54_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_55 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_55
    ADD CONSTRAINT synthetic_55_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_56 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_56
    ADD CONSTRAINT synthetic_56_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_57 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_57
    ADD CONSTRAINT synthetic_57_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_58 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_58
    ADD CONSTRAINT synthetic_58_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_59 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_59
    ADD CONSTRAINT synthetic_59_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);

CREATE TABLE data.synthetic_60 (
    id uuid PRIMARY KEY,
    bill_id uuid,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY data.synthetic_60
    ADD CONSTRAINT synthetic_60_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES data.bills(id);
