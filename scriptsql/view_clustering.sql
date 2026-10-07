CREATE OR REPLACE VIEW public.vw_view_clustering AS
WITH ringkasan_sirkulasi AS (
    SELECT 
        id_barang_fk,
        SUM(jumlah_keluar) AS total_unit_terjual,
        COUNT(DISTINCT id_waktu_fk) AS jumlah_hari_aktif_transaksi,
        AVG(biaya_per_unit) AS rata_rata_biaya_per_unit,
        AVG(jumlah_stok_akhir) AS rata_rata_stok_fisik
    FROM public.fact_persediaan_barang
    GROUP BY id_barang_fk
),
kondisi_stok_terakhir AS (
    SELECT DISTINCT ON (id_barang_fk)
        id_barang_fk,
        total_nilai_stok AS valuasi_stok_aktual
    FROM public.fact_persediaan_barang
    ORDER BY id_barang_fk, id_waktu_fk DESC 
)
SELECT 
    db.id_barang_sk,
    db.sku,
    db.nama_barang,
    db.merek,             -- [DITAMBAHKAN] Fitur Deskriptif: Merek
    db.kategori,
    db.satuan_ukur,       -- [DITAMBAHKAN] Fitur Deskriptif: Satuan Ukur
    
    COALESCE(rs.total_unit_terjual, 0) AS total_unit_terjual,
    COALESCE(rs.jumlah_hari_aktif_transaksi, 0) AS jumlah_hari_aktif_transaksi,
    ROUND(COALESCE(rs.rata_rata_biaya_per_unit, 0)::numeric, 2) AS rata_rata_biaya_per_unit,
    COALESCE(kst.valuasi_stok_aktual, 0) AS total_valuasi_aset_mengendap,
    
    CASE 
        WHEN COALESCE(rs.rata_rata_stok_fisik, 0) <= 0 THEN 0
        ELSE ROUND((COALESCE(rs.total_unit_terjual, 0)::numeric / rs.rata_rata_stok_fisik::numeric), 4)
    END AS turnover_ratio

FROM public.dim_barang db
LEFT JOIN ringkasan_sirkulasi rs ON db.id_barang_sk = rs.id_barang_fk
LEFT JOIN kondisi_stok_terakhir kst ON db.id_barang_sk = kst.id_barang_fk;