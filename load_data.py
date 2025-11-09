import csv
from django.db import connection

provider_file = "/Users/yvonnehan/Downloads/EMRTS/npidata_pfile_20050523-20250713.csv"
taxonomy_file = "/Users/yvonnehan/Downloads/EMRTS/nucc_taxonomy_251.csv"

BATCH_SIZE = 5000

def load_taxonomy():
    with open(taxonomy_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        for row in reader:
            code = row["Code"].strip()
            classification = row["Classification"].strip()
            specialization = row.get("Specialization", "").strip()
            with connection.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO medicaid_providers_lookup_taxonomy
                    (code, classification, specialization)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (code) DO NOTHING;
                    """,
                    [code, classification, specialization]
                )
            total += 1
            if total % BATCH_SIZE == 0:
                print(f"  Imported {total} taxonomy rows...")
    print(f"Taxonomy import done. Total: {total}")

def load_providers():
    provider_map = {}
    with open(provider_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        total = 0
        for row in reader:
            npi = row["NPI"].strip()
            first_name = row.get("Provider First Name", "").strip()
            last_name = row.get("Provider Last Name (Legal Name)", "").strip()
            address = row.get("Provider Business Practice Location Address Line 1", "").strip()
            city = row.get("Provider Business Practice Location Address City Name", "").strip()
            state = row.get("Provider Business Practice Location Address State Name", "").strip()
            postal = row.get("Provider Business Practice Location Address Postal Code", "").strip()
            tel = row.get("Provider Business Practice Location Address Telephone Number", "").strip()
            rows.append((npi, first_name, last_name, address, city, state, postal, tel))
            total += 1
            if len(rows) >= BATCH_SIZE:
                _insert_providers_batch(rows)
                rows.clear()
                print(f"  Imported {total} provider rows so far...")
        if rows:
            _insert_providers_batch(rows)
    print(f"Provider import done. Total: {total}")

    # Create provider_map for later use
    with connection.cursor() as cur:
        cur.execute("SELECT provider_id, npi FROM medicaid_providers_lookup_provider")
        provider_map = {npi: pid for pid, npi in cur.fetchall()}
    return provider_map

def _insert_providers_batch(rows):
    from psycopg2.extras import execute_values
    sql = """
        INSERT INTO medicaid_providers_lookup_provider
        (npi, first_name, last_name, address_line_1, city_name, state_name, postal_code, telephone_number)
        VALUES %s
        ON CONFLICT (npi) DO NOTHING
        """
    with connection.cursor() as cur:
        execute_values(cur, sql, rows)

def load_provider_taxonomy(provider_map):
    from psycopg2.extras import execute_values
    with connection.cursor() as cur:
        cur.execute("SELECT taxonomy_id, code FROM medicaid_providers_lookup_taxonomy")
        taxonomy_map = {code: tid for tid, code in cur.fetchall()}

    rows = []
    total = 0
    with open(provider_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            npi = row["NPI"].strip()
            pid = provider_map.get(npi)
            if not pid:
                continue
            for i in range(1, 16):
                code = row.get(f"Healthcare Provider Taxonomy Code_{i}", "").strip()
                switch = row.get(f"Healthcare Provider Primary Taxonomy Switch_{i}", "").strip() or 'N'
                if code and code in taxonomy_map:
                    tid = taxonomy_map[code]
                    rows.append((pid, tid, switch))
                    total += 1
                    if len(rows) >= BATCH_SIZE:
                        _insert_pt_batch(rows)
                        rows.clear()
                        print(f"  Imported {total} provider-taxonomy rows so far...")
        if rows:
            _insert_pt_batch(rows)
    print(f"Provider–taxonomy import done. Total: {total}")

def _insert_pt_batch(rows):
    from psycopg2.extras import execute_values
    sql = """
        INSERT INTO medicaid_providers_lookup_providertaxonomy
        (provider_id, taxonomy_id, primary_switch)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    with connection.cursor() as cur:
        execute_values(cur, sql, rows)

def run():
    print("Starting import...")
    load_taxonomy()
    provider_map = load_providers()
    load_provider_taxonomy(provider_map)
    print("All data imported successfully.")
