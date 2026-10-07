import random
from datetime import datetime, timedelta
from faker import Faker
import time
import os

def generate_sql():
    print("Inisialisasi Generator Data NeoStore Global (Data Science Ready 100k)...")
    fake = Faker('en_US')
    
    # --- SCENARIO SETTINGS ---
    START_DATE = datetime(2022, 1, 1)
    END_DATE = datetime(2025, 12, 31)
    
    NUM_WAREHOUSES = 50   
    NUM_SUPPLIERS = 30    
    NUM_PRODUCTS = 250    
    NUM_CUSTOMERS = 1000  
    NUM_USERS = 20
    
    # Data master lokasi
    countries_data = {
        "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
        "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar"],
        "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg"],
        "Japan": ["Tokyo", "Osaka", "Nagoya", "Fukuoka"],
        "China": ["Shanghai", "Beijing", "Shenzhen", "Guangzhou"],
        "UK": ["London", "Manchester", "Birmingham", "Leeds"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad"],
        "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia"],
        "Australia": ["Sydney", "Melbourne", "Brisbane"],
        "Canada": ["Toronto", "Montreal", "Vancouver"],
        "France": ["Paris", "Lyon", "Marseille"],
        "Singapore": ["Singapore Central", "Jurong"],
        "South Korea": ["Seoul", "Busan", "Incheon"],
        "UAE": ["Dubai", "Abu Dhabi"],
        "Netherlands": ["Amsterdam", "Rotterdam"],
        "Turkey": ["Istanbul", "Ankara"]
    }

    country_to_code = {
        "USA": "USA", "Indonesia": "ID", "Germany": "DE", "Japan": "JP",
        "China": "CN", "UK": "UK", "India": "IN", "Brazil": "BR",
        "Australia": "AUS", "Canada": "CA", "France": "FR", "Singapore": "SG",
        "South Korea": "KR", "UAE": "UAE", "Netherlands": "NL", "Turkey": "TR"
    }
    
    sql_batches = []
    
    def add_batch(table, columns, values_list):
        if not values_list: return
        chunk_size = 1000
        for i in range(0, len(values_list), chunk_size):
            chunk = values_list[i:i+chunk_size]
            values_str = ',\n'.join(chunk)
            sql_batches.append(f"INSERT INTO {table} ({columns}) VALUES\n{values_str};")

    # --- SQL HEADER ---
    sql_batches.append("-- ==========================================")
    sql_batches.append("-- DATABASE: inventory_system_final")
    sql_batches.append("-- SCENARIO: Global Retail Fulfillment (Machine Learning Optimized)")
    sql_batches.append("-- ARCHITECTURE FIX: Connected Inventory Log with POID & SOID")
    sql_batches.append("-- ==========================================\n")
    sql_batches.append("USE inventory_system_final;\n")
    sql_batches.append("SET FOREIGN_KEY_CHECKS=0; SET UNIQUE_CHECKS=0; SET autocommit=0;\n")

    # MENCEGAH ERROR #1062 DUPLICATE ENTRY
    sql_batches.append("-- Membersihkan data lama untuk menghindari Error #1062 Duplicate Entry")
    tables_to_clear = [
        "Inventory_Movement_Log", "SalesOrderItem", "SalesOrder", 
        "PurchaseOrderItem", "PurchaseOrder", "CurrentStock", 
        "Sales_KPI_Target", "Product", "Customer", "Warehouse", 
        "Supplier", "ProductCategory", "KPI_Definition", "SystemUser"
    ]
    for table_name in tables_to_clear:
        sql_batches.append(f"TRUNCATE TABLE {table_name};")
    sql_batches.append("\n")

    # 1. SystemUser
    users = []
    for i in range(1, NUM_USERS + 1):
        role = 'Admin' if i <= 2 else ('Sales' if i <= 10 else 'Gudang')
        name = fake.name().replace("'", "''")
        users.append(f"({i}, '{name}', '{role}')")
    add_batch("SystemUser", "UserID, NamaPengguna, Peran", users)

    # 2. KPI_Definition
    kpis = ["(1, 'Sales Volume', 'Monthly transaction volume target')", 
            "(2, 'Inventory Accuracy', 'Physical vs System stock alignment')", 
            "(3, 'Fulfillment Speed', 'Order to Ship time tracking')"]
    add_batch("KPI_Definition", "KPI_ID, NamaKPI, Target_Description", kpis)

    # 3. ProductCategory
    cats = ["(1, 'Electronics')", "(2, 'Computing & Servers')", "(3, 'Mobile Devices')", 
            "(4, 'Gaming Console & Accs')", "(5, 'Smart Home Appliance')"]
    add_batch("ProductCategory", "CategoryID, NamaKategori", cats)

    # 4. Supplier (DIKEMBALIKAN KE FORMAT ALAMAT ORIGINAL ANDA)
    suppliers = []
    tech_suppliers = [
        "Apple Inc. Global", "Dell Technologies Inc.", "HP Inc. Global", 
        "Lenovo Group Ltd.", "ASUSTeK Computer Inc.", "Acer Inc. Global", 
        "MSI (Micro-Star International)", "Gigabyte Technology", "Microsoft Hardware Div.", 
        "Razer Inc. Global", "Intel Corporation Global", "AMD (Advanced Micro Devices)", 
        "NVIDIA Corporation", "TSMC (Taiwan Semiconductor)", "Qualcomm Technologies",
        "Samsung Electronics", "LG Electronics", "Sony Corporation", "Panasonic Corporation",
        "Toshiba Corporation", "Foxconn Technology Group", "Pegatron Corporation",
        "Wistron Corporation", "Compal Electronics", "Quanta Computer",
        "Seagate Technology", "Western Digital", "Kingston Technology", "Corsair Gaming",
        "Logitech International"
    ]
    
    for i in range(1, NUM_SUPPLIERS + 1):
        company = tech_suppliers[i-1] if i <= len(tech_suppliers) else fake.company().replace("'", "''")
        country_name = random.choice(list(country_to_code.keys()))
        code = country_to_code[country_name]
        
        street = fake.street_address().replace(',', '').replace('\n', ' ')
        city = fake.city().replace("'", "''")
        state = fake.state().replace("'", "''")
        address = f"{street}, {city}, {state}, {code}"
        suppliers.append(f"({i}, '{company}', '{address}', '{fake.phone_number()}')")
    add_batch("Supplier", "SupplierID, NamaPemasok, Alamat, Kontak", suppliers)

    # Flatten kota
    flat_cities = [(country, city) for country, cities in countries_data.items() for city in cities]
    flat_cities = flat_cities[:NUM_WAREHOUSES]

    # 5. Warehouse (DIKEMBALIKAN KE FORMAT ALAMAT ORIGINAL ANDA)
    warehouses = []
    w_to_country = {}
    idx = 1
    for country, city in flat_cities:
        w_name = f"{city} Distribution Hub".replace("'", "''")
        code = country_to_code.get(country, "UNKNOWN")
        
        street = fake.street_address().replace(',', '').replace('\n', ' ')
        state = fake.state().replace("'", "''")
        address = f"{street}, {city}, {state}, {code}"
        warehouses.append(f"({idx}, '{w_name}', '{address}', 'Main hub for {country} region')")
        w_to_country[idx] = country
        idx += 1
    add_batch("Warehouse", "WarehouseID, NamaGudang, Lokasi, Deskripsi", warehouses)

    # 6. Customer (DIKEMBALIKAN KE FORMAT ALAMAT ORIGINAL ANDA)
    customers = []
    cust_to_country = {}
    cust_to_sales = {} 
    valid_countries = list(set([c for c, _ in flat_cities]))
    for i in range(1, NUM_CUSTOMERS + 1):
        country_name = random.choice(valid_countries)
        code = country_to_code[country_name]
        
        if random.random() < 0.3: 
            name = fake.company().replace("'", "''") + " (Corp)"
        else:
            name = fake.name().replace("'", "''")
        
        street = fake.street_address().replace(',', '').replace('\n', ' ')
        city_clean = fake.city().replace("'", "''")
        state = fake.state().replace("'", "''")
        
        address = f"{street}, {city_clean}, {state}, {code}"
        customers.append(f"({i}, '{name}', '{address}', '{fake.phone_number()}')")
        cust_to_country[i] = country_name
        cust_to_sales[i] = random.randint(3, 10) 
    add_batch("Customer", "CustomerID, NamaPelanggan, Alamat, Kontak", customers)

    # 7. Product 
    products = []
    product_meta = {}
    product_weights = []
    product_ids = list(range(1, NUM_PRODUCTS + 1))
    tech_brands = ['Sony', 'Samsung', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Logitech', 'Cisco', 'Apple']
    
    for i in product_ids:
        cid = random.randint(1, 5)
        buy = round(random.uniform(20, 1500), 2)
        sell = round(buy * random.uniform(1.15, 1.35), 2)
        reorder = random.randint(50, 200)
        
        brand = random.choice(tech_brands)
        p_name = f"{brand} {fake.word().capitalize()} {fake.ean8()}".replace("'", "''")
        
        products.append(f"({i}, {cid}, 'SKU-{i:04d}', '{p_name}', {buy}, {sell}, {reorder})")
        product_meta[i] = {'buy': buy, 'sell': sell, 'reorder': reorder}
        
        if i % 5 == 0:
            product_weights.append(random.randint(80, 150))
        else:
            product_weights.append(random.randint(1, 15))

    add_batch("Product", "ProductID, CategoryID, SKU, NamaProduk, HargaBeli, HargaJual, ReorderLevel", products)

    # 8. Transactions Engine (Machine Learning Readiness + POID/SOID Fix)
    print("Membangun Logika Rantai Pasok (Initial Seed + Time Loop)...")
    stocks = {(w, p): 0 for w in range(1, NUM_WAREHOUSES+1) for p in range(1, NUM_PRODUCTS+1)}
    
    po_id, po_item_id = 1, 1
    so_id, so_item_id = 1, 1
    trans_id = 1
    
    mov_log, po_list, so_list, po_item_list, so_item_list = [], [], [], [], []
    
    # -- Initial Stock Injection --
    init_date = (START_DATE - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    for w in range(1, NUM_WAREHOUSES + 1):
        for p in range(1, NUM_PRODUCTS + 1):
            init_qty = random.randint(100, 300)
            stocks[(w, p)] += init_qty
            mov_log.append(f"({trans_id}, {p}, {w}, 1, NULL, NULL, '{init_date}', 'IN', {init_qty}, 'Initial Database Seed')")
            trans_id += 1

    # -- Time Loop --
    current_date = START_DATE
    while current_date <= END_DATE:
        if current_date.day == 1 and current_date.month % 6 == 0:
            print(f" > Progress: {current_date.strftime('%Y-%m')}")
            
        month = current_date.month
        day = current_date.day
        year = current_date.year
        
        if month == 11 and 20 <= day <= 30:
            season_multiplier = 3.5 
        elif month in [10, 11, 12]:
            season_multiplier = 1.5 
        elif month in [1, 2]:
            season_multiplier = 0.8 
        else:
            season_multiplier = 1.0
            
        years_passed = year - 2022
        depreciation_factor = max(0.5, 1.0 - (0.05 * years_passed))
        
        # --- A. PURCHASES (IN) ---
        warehouses_to_check = random.sample(range(1, NUM_WAREHOUSES + 1), 5)
        for w in warehouses_to_check:
            items_to_buy = []
            for p in range(1, NUM_PRODUCTS + 1):
                if stocks[(w, p)] <= product_meta[p]['reorder']:
                    items_to_buy.append((p, random.randint(300, 800)))
            
            if items_to_buy:
                supp = random.randint(1, NUM_SUPPLIERS)
                user = random.randint(11, 20)
                total_po = 0
                
                for p, qty in items_to_buy:
                    sub = round(qty * product_meta[p]['buy'], 2)
                    total_po += sub
                    po_item_list.append(f"({po_item_id}, {po_id}, {p}, {qty}, {product_meta[p]['buy']}, {sub})")
                    stocks[(w, p)] += qty 
                    
                    lead_time = random.randint(7, 30)
                    receive_date = current_date + timedelta(days=lead_time)
                    dt_str = receive_date.strftime('%Y-%m-%d %H:%M:%S')
                    
                    mov_log.append(f"({trans_id}, {p}, {w}, {user}, {po_id}, NULL, '{dt_str}', 'IN', {qty}, 'Restock Auto-Trigger PO #{po_id}')")
                    
                    po_item_id += 1
                    trans_id += 1
                    
                po_list.append(f"({po_id}, {supp}, {user}, '{current_date.date()}', {round(total_po,2)}, 'Received')")
                po_id += 1

        # --- B. SALES (OUT) ---
        num_sales = int(random.randint(15, 45) * season_multiplier)
        for _ in range(num_sales):
            c = random.randint(1, NUM_CUSTOMERS)
            c_country = cust_to_country[c]
            local_ws = [w for w, country in w_to_country.items() if country == c_country]
            
            w = random.choice(local_ws) if local_ws else random.randint(1, NUM_WAREHOUSES)
            user = cust_to_sales[c] 
            total_so, items_sold = 0, 0
            
            primary_p = random.choices(product_ids, weights=product_weights, k=1)[0]
            items_to_sell = [primary_p]
            
            if random.random() < 0.40 and primary_p < NUM_PRODUCTS:
                items_to_sell.append(primary_p + 1)
            
            for p in items_to_sell:
                if stocks[(w, p)] > 0:
                    max_qty = 20 if c <= 200 else 3 
                    qty = random.randint(1, min(max_qty, stocks[(w, p)]))
                    
                    current_sell_price = round(product_meta[p]['sell'] * depreciation_factor, 2)
                    sub = round(qty * current_sell_price, 2)
                    total_so += sub
                    
                    so_item_list.append(f"({so_item_id}, {so_id}, {p}, {qty}, {current_sell_price}, {sub})")
                    stocks[(w, p)] -= qty
                    
                    dt_str = (current_date + timedelta(hours=random.randint(9,20))).strftime('%Y-%m-%d %H:%M:%S')
                    mov_log.append(f"({trans_id}, {p}, {w}, {user}, NULL, {so_id}, '{dt_str}', 'OUT', {qty}, 'Fulfilled SO #{so_id}')")
                    
                    so_item_id += 1
                    trans_id += 1
                    items_sold += 1
            
            if items_sold > 0:
                so_list.append(f"({so_id}, {c}, {user}, '{current_date.date()}', {round(total_so,2)}, 'Completed')")
                so_id += 1
                
        # --- C. ADJUSTMENTS (ADJ) ---
        if random.random() < 0.20:
            w = random.randint(1, NUM_WAREHOUSES)
            p = random.randint(1, NUM_PRODUCTS)
            if stocks[(w, p)] > 10:
                qty = -random.randint(1, 3) 
                stocks[(w, p)] += qty 
                user = random.randint(11, 20)
                dt_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
                mov_log.append(f"({trans_id}, {p}, {w}, {user}, NULL, NULL, '{dt_str}', 'ADJ', {abs(qty)}, 'Warehouse shrink/damage report')")
                trans_id += 1
        
        current_date += timedelta(days=1)

    print(f"Total Pergerakan Inventaris: {trans_id-1} baris.")
    
    # 9. CurrentStock
    cs = []
    inv_id = 1
    for w in range(1, NUM_WAREHOUSES+1):
        for p in range(1, NUM_PRODUCTS+1):
            qty = stocks[(w,p)]
            cs.append(f"({inv_id}, {p}, {w}, {qty})")
            inv_id += 1
    add_batch("CurrentStock", "InventoryID, ProductID, WarehouseID, JumlahTersedia", cs)

    # 10. Sales_KPI_Target
    kpi_targets = []
    target_id = 1
    for year in range(2022, 2026):
        for q in range(1, 5):
            for user_id in range(3, 11):
                t_val = round(random.uniform(100000, 500000), 2)
                kpi_targets.append(f"({target_id}, {user_id}, 1, {t_val}, '{year}-Q{q}')")
                target_id += 1
    add_batch("Sales_KPI_Target", "TargetID, UserID, KPI_ID, TargetValue, Period", kpi_targets)

    # Commit Batches
    add_batch("PurchaseOrder", "POID, SupplierID, UserID, TanggalPO, TotalHarga, Status", po_list)
    add_batch("PurchaseOrderItem", "POItemID, POID, ProductID, Jumlah, HargaSatuan, Subtotal", po_item_list)
    add_batch("SalesOrder", "SOID, CustomerID, UserID, TanggalSO, TotalHarga, Status", so_list)
    add_batch("SalesOrderItem", "SOItemID, SOID, ProductID, Jumlah, HargaSatuan, Subtotal", so_item_list)
    add_batch("Inventory_Movement_Log", "TransID, ProductID, WarehouseID, UserID, POID, SOID, TanggalTrans, JenisTrans, Jumlah, Deskripsi", mov_log)

    sql_batches.append("COMMIT;\nSET FOREIGN_KEY_CHECKS=1;\nSET UNIQUE_CHECKS=1;")
    return "\n".join(sql_batches)

if __name__ == "__main__":
    start = time.time()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, "neo_global_pentaho_sync_final.sql")
    
    print(f"Mulai menyusun script SQL ke file: {filename}...")
    
    try:
        sql_content = generate_sql()
        with open(filename, "w", encoding='utf-8') as f:
            f.write(sql_content)
            
        print(f"\n[SUKSES] Eksekusi Selesai dalam {time.time() - start:.2f} detik.")
    
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")