============================================================================
-- 0. CLEANING DATA LAMA (Mencegah Constraint Error)
-- ============================================================================
TRUNCATE TABLE public.fact_persediaan_barang RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.dim_barang RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.dim_gudang RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.dim_pemasok RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.dim_jenis_pergerakan RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.dim_waktu RESTART IDENTITY CASCADE;

-- ============================================================================
-- 1. POPULASI TABEL DIMENSI
-- ============================================================================

-- A. Dimensi Jenis Pergerakan
INSERT INTO public.dim_jenis_pergerakan (nama_pergerakan) VALUES
('Barang Masuk (IN)'),
('Barang Keluar (OUT)'),
('Penyesuaian (ADJ)');

-- B. Dimensi Pemasok (Initial Seed ID 0 + Data dari tabel Supplier)
INSERT INTO public.dim_pemasok (id_pemasok_sk, id_pemasok_original, nama_pemasok, alamat_pemasok, kontak, negara_asal)
VALUES (0, 0, 'N/A / Initial Seed', '-', '-', '-');

INSERT INTO public.dim_pemasok (id_pemasok_original, nama_pemasok, alamat_pemasok, kontak, negara_asal)
SELECT 
    SupplierID, 
    NamaPemasok, 
    Alamat, 
    Kontak,
    -- Ekstraksi negara asal dari bagian akhir alamat jika mengandung singkatan negara (FR, UK, TR, ID, dll)
    CASE 
        WHEN Alamat LIKE '%FR' THEN 'France'
        WHEN Alamat LIKE '%UK' THEN 'United Kingdom'
        WHEN Alamat LIKE '%TR' THEN 'Turkey'
        WHEN Alamat LIKE '%ID' THEN 'Indonesia'
        WHEN Alamat LIKE '%KR' THEN 'South Korea'
        WHEN Alamat LIKE '%CA' THEN 'Canada'
        ELSE 'Global'
    END AS negara_asal
FROM staging.Supplier
WHERE SupplierID NOT IN (SELECT id_pemasok_original FROM public.dim_pemasok);

-- C. Dimensi Barang (Join Product dan ProductCategory)
INSERT INTO public.dim_barang (id_barang_original, nama_barang, kategori, sku, subkategori, merek, satuan_ukur)
SELECT 
    p.ProductID, 
    p.NamaProduk, 
    COALESCE(pc.NamaKategori, 'Uncategorized') AS kategori, 
    p.SKU, 
    'general' AS subkategori, 
    SPLIT_PART(p.NamaProduk, ' ', 1) AS merek, -- Mengambil kata pertama (Apple, Asus, Samsung) sebagai Merek
    'unit' AS satuan_ukur
FROM staging.Product p
LEFT JOIN staging.ProductCategory pc ON p.CategoryID = pc.CategoryID
WHERE p.ProductID NOT IN (SELECT id_barang_original FROM public.dim_barang);

-- D. Dimensi Gudang (Ekstraksi Kota & Negara secara Dinamis dari NamaGudang)
INSERT INTO public.dim_gudang (id_gudang_original, nama_gudang, lokasi, kota, negara)
SELECT 
    WarehouseID, 
    NamaGudang, 
    Lokasi, 
    -- Menghapus teks ' Distribution Hub' untuk mendapatkan nama Kota murni
    REPLACE(NamaGudang, ' Distribution Hub', '') AS kota,
    -- Memetakan Negara secara logis berdasarkan pola Nama Gudang
    CASE 
        WHEN NamaGudang LIKE 'New York%' OR NamaGudang LIKE 'Los Angeles%' OR 
             NamaGudang LIKE 'Chicago%' OR NamaGudang LIKE 'Houston%' OR 
             NamaGudang LIKE 'Phoenix%' THEN 'United States'
        WHEN NamaGudang LIKE 'Jakarta%' OR NamaGudang LIKE 'Surabaya%' OR 
             NamaGudang LIKE 'Bandung%' OR NamaGudang LIKE 'Medan%' OR 
             NamaGudang LIKE 'Makassar%' THEN 'Indonesia'
        ELSE 'Global'
    END AS negara
FROM staging.Warehouse
WHERE WarehouseID NOT IN (SELECT id_gudang_original FROM public.dim_gudang);

-- E. Dimensi Waktu (Ekstraksi dari Inventory_Movement_Log.TanggalTrans)
INSERT INTO public.dim_waktu (id_waktu_sk, tanggal, hari, bulan, kuartal, tahun, hari_libur, hari_angka, bulan_angka)
SELECT 
    ROW_NUMBER() OVER (ORDER BY t.tanggal_raw) AS id_waktu_sk,
    t.tanggal_raw,
    TRIM(TO_CHAR(t.tanggal_raw, 'Day')),
    TRIM(TO_CHAR(t.tanggal_raw, 'Month')),
    EXTRACT(QUARTER FROM t.tanggal_raw),
    EXTRACT(YEAR FROM t.tanggal_raw),
    CASE WHEN EXTRACT(DOW FROM t.tanggal_raw) IN (0, 6) THEN TRUE ELSE FALSE END AS hari_libur,
    EXTRACT(DOW FROM t.tanggal_raw),
    EXTRACT(MONTH FROM t.tanggal_raw)
FROM (
    SELECT DISTINCT DATE(TanggalTrans) AS tanggal_raw 
    FROM staging.Inventory_Movement_Log
    WHERE TanggalTrans IS NOT NULL
) t
ORDER BY t.tanggal_raw ASC;


-- ============================================================================
-- 2. LOADING TABEL FAKTA (FACT INVENTORY)
-- ============================================================================
WITH RawData AS (
    SELECT 
        iml.TransID,
        iml.ProductID,
        iml.WarehouseID,
        dw.id_waktu_sk,
        COALESCE(po.SupplierID, 0) AS SupplierID,
        iml.JenisTrans,
        iml.Jumlah,
        p.HargaBeli,
        CASE WHEN iml.JenisTrans = 'IN' THEN iml.Jumlah ELSE 0 END AS jumlah_masuk,
        CASE WHEN iml.JenisTrans IN ('OUT', 'ADJ') THEN iml.Jumlah ELSE 0 END AS jumlah_keluar
    FROM staging.Inventory_Movement_Log iml
    LEFT JOIN staging.PurchaseOrder po ON iml.POID = po.POID
    LEFT JOIN staging.Product p ON iml.ProductID = p.ProductID
    LEFT JOIN public.dim_waktu dw ON DATE(iml.TanggalTrans) = DATE(dw.tanggal)
),
CumulativeCalculation AS (
    SELECT 
        *,
        SUM(jumlah_masuk) OVER (
            PARTITION BY ProductID, WarehouseID 
            ORDER BY id_waktu_sk, TransID
        ) AS total_masuk_kumulatif,
        SUM(jumlah_keluar) OVER (
            PARTITION BY ProductID, WarehouseID 
            ORDER BY id_waktu_sk, TransID
        ) AS total_keluar_kumulatif
    FROM RawData
),
CalculatedMetrics AS (
    SELECT 
        *,
        (total_masuk_kumulatif - total_keluar_kumulatif) AS jumlah_stok_akhir,
        ((total_masuk_kumulatif - total_keluar_kumulatif) - jumlah_masuk + jumlah_keluar) AS jumlah_stok_awal
    FROM CumulativeCalculation
)
INSERT INTO public.fact_persediaan_barang (
    id_barang_fk, id_gudang_fk, id_waktu_fk, id_pemasok_fk, id_jenis_fk,
    jumlah_stok_awal, jumlah_masuk, jumlah_keluar, jumlah_stok_akhir,
    biaya_per_unit, total_nilai_stok
)
SELECT 
    COALESCE(db.id_barang_sk, 0) AS id_barang_fk,
    COALESCE(dg.id_gudang_sk, 0) AS id_gudang_fk,
    COALESCE(cm.id_waktu_sk, 0) AS id_waktu_fk,
    COALESCE(dp.id_pemasok_sk, 0) AS id_pemasok_fk, -- Mengarah ke ID 0 jika tidak ada pemasok (OUT/ADJ)
    COALESCE(dj.id_jenis_sk, 0) AS id_jenis_fk,
    cm.jumlah_stok_awal,
    cm.jumlah_masuk,
    cm.jumlah_keluar,
    cm.jumlah_stok_akhir,
    COALESCE(cm.HargaBeli, 0) AS biaya_per_unit,
    ROUND((cm.jumlah_stok_akhir * COALESCE(cm.HargaBeli, 0)), 2) AS total_nilai_stok
FROM CalculatedMetrics cm
LEFT JOIN public.dim_barang db ON cm.ProductID = db.id_barang_original
LEFT JOIN public.dim_gudang dg ON cm.WarehouseID = dg.id_gudang_original
LEFT JOIN public.dim_pemasok dp ON (cm.SupplierID <> 0 AND cm.SupplierID = dp.id_pemasok_original)
LEFT JOIN public.dim_jenis_pergerakan dj ON (
    CASE 
        WHEN cm.JenisTrans = 'IN' THEN 'Barang Masuk (IN)'
        WHEN cm.JenisTrans = 'OUT' THEN 'Barang Keluar (OUT)'
        WHEN cm.JenisTrans = 'ADJ' THEN 'Penyesuaian (ADJ)'
    END
) = dj.nama_pergerakan
ORDER BY cm.id_waktu_sk, cm.TransID;
