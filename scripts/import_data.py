# Database connection setup
import psycopg2
import pandas as pd
from psycopg2.extras import execute_batch  # 批量插入关键库

# Database credentials
DB_CONFIG = {
    'dbname': 'medicaid_providers',
    'user': 'yvonnehan777',
    'password': 'Chivast2020',
    'host': 'localhost',
    'port': '5432'
}


def create_tables():
    """Create all required tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Create taxonomy table
    cur.execute("""
    DROP TABLE IF EXISTS taxonomy CASCADE;
    CREATE TABLE taxonomy (
        id SERIAL PRIMARY KEY,
        code VARCHAR(20) NOT NULL,
        grouping TEXT,
        classification TEXT,
        specialization TEXT,
        definition TEXT,
        notes TEXT,
        display_name TEXT,
        section TEXT
    );
    """)

    # Create providers table
    cur.execute("""
    DROP TABLE IF EXISTS providers CASCADE;
    CREATE TABLE providers (
        id SERIAL PRIMARY KEY,
        npi VARCHAR(20) UNIQUE NOT NULL,
        entity_type_code VARCHAR(10),
        organization_name TEXT,
        last_name TEXT,
        first_name TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        phone TEXT,
        fax TEXT
    );
    """)

    # Create junction table
    cur.execute("""
    DROP TABLE IF EXISTS provider_taxonomy CASCADE;
    CREATE TABLE provider_taxonomy (
        provider_id INTEGER REFERENCES providers(id),
        taxonomy_id INTEGER REFERENCES taxonomy(id),
        PRIMARY KEY (provider_id, taxonomy_id)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully")


def load_taxonomy_data():
    """Load taxonomy data with batch insert"""
    df = pd.read_csv("/Users/yvonnehan/Downloads/EMRTS/nucc_taxonomy_251.csv", dtype=str).fillna('')

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 准备批量数据
    data = [(
        row['Code'], row['Grouping'], row['Classification'],
        row['Specialization'], row['Definition'], row['Notes'],
        row['Display Name'], row['Section']
    ) for _, row in df.iterrows()]

    # 批量插入（每次1000条）
    execute_batch(cur, """
        INSERT INTO taxonomy (
            code, grouping, classification, specialization,
            definition, notes, display_name, section
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, data, page_size=1000)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(df)} taxonomy records (batch insert)")


def load_provider_data():
    """Load provider data with batch insert"""
    cols = [
        "NPI", "Entity Type Code",
        "Provider Organization Name (Legal Business Name)",
        "Provider Last Name (Legal Name)", "Provider First Name",
        "Provider First Line Business Practice Location Address",
        "Provider Second Line Business Practice Location Address",
        "Provider Business Practice Location Address City Name",
        "Provider Business Practice Location Address State Name",
        "Provider Business Practice Location Address Postal Code",
        "Provider Business Practice Location Address Telephone Number",
        "Provider Business Practice Location Address Fax Number"
    ]

    # 分块读取大文件（避免内存不足）
    chunk_size = 50000
    total_records = 0
    for chunk in pd.read_csv(
            "/Users/yvonnehan/Downloads/EMRTS/npidata_pfile_20050523-20250713.csv",
            usecols=cols,
            chunksize=chunk_size,
            dtype=str
    ):
        df = chunk.rename(columns={
            "NPI": "npi",
            "Entity Type Code": "entity_type_code",
            "Provider Organization Name (Legal Business Name)": "organization_name",
            "Provider Last Name (Legal Name)": "last_name",
            "Provider First Name": "first_name",
            "Provider First Line Business Practice Location Address": "address_line1",
            "Provider Second Line Business Practice Location Address": "address_line2",
            "Provider Business Practice Location Address City Name": "city",
            "Provider Business Practice Location Address State Name": "state",
            "Provider Business Practice Location Address Postal Code": "zip",
            "Provider Business Practice Location Address Telephone Number": "phone",
            "Provider Business Practice Location Address Fax Number": "fax"
        }).fillna('')

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 批量插入当前chunk
        execute_batch(cur, """
            INSERT INTO providers (
                npi, entity_type_code, organization_name, last_name, first_name,
                address_line1, address_line2, city, state, zip, phone, fax
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [tuple(row) for _, row in df.iterrows()], page_size=1000)

        conn.commit()
        cur.close()
        conn.close()

        total_records += len(df)
        print(f"Processed {total_records} providers...")

    print(f"Total loaded {total_records} provider records")


def load_provider_taxonomy():
    """Batch insert for relationships"""
    taxonomy_cols = [f"Healthcare Provider Taxonomy Code_{i}" for i in range(1, 16)]
    cols = ["NPI"] + taxonomy_cols

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get mappings
    cur.execute("SELECT id, code FROM taxonomy;")
    taxonomy_map = {code: tid for tid, code in cur.fetchall()}

    cur.execute("SELECT id, npi FROM providers;")
    provider_map = {npi: pid for pid, npi in cur.fetchall()}

    # 分块处理大文件
    chunk_size = 50000
    total_relationships = 0
    for chunk in pd.read_csv(
            "/Users/yvonnehan/Downloads/EMRTS/npidata_pfile_20050523-20250713.csv",
            usecols=cols,
            chunksize=chunk_size,
            dtype=str
    ):
        # 准备批量关系数据
        relationships = []
        for _, row in chunk.iterrows():
            npi = row['NPI']
            if npi not in provider_map:
                continue

            provider_id = provider_map[npi]
            for col in taxonomy_cols:
                code = row[col]
                if code and code in taxonomy_map:
                    relationships.append((provider_id, taxonomy_map[code]))

        # 批量插入关系
        if relationships:
            execute_batch(cur, """
                INSERT INTO provider_taxonomy (provider_id, taxonomy_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING
            """, relationships, page_size=1000)
            conn.commit()
            total_relationships += len(relationships)
            print(f"Created {total_relationships} relationships...")

    cur.close()
    conn.close()
    print(f"Total created {total_relationships} provider-taxonomy relationships")


# Execute all steps
create_tables()
load_taxonomy_data()
load_provider_data()
load_provider_taxonomy()