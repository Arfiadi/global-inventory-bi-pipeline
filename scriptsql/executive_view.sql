CREATE OR REPLACE VIEW public.vw_executive_health AS
WITH snapshotterakhir AS (
    SELECT 
        id_gudang_fk,
        id_barang_fk,
        jumlah_stok_akhir,
        total_nilai_stok,
        -- Trik Window Function: Menarik ID pemasok dari transaksi asli, abaikan nilai 0 (N/A)
        FIRST_VALUE(id_pemasok_fk) OVER (
            PARTITION BY id_gudang_fk, id_barang_fk 
            ORDER BY CASE WHEN id_pemasok_fk != 0 THEN 1 ELSE 2 END, id_waktu_fk DESC
        ) AS id_pemasok_valid,
        ROW_NUMBER() OVER (
            PARTITION BY id_gudang_fk, id_barang_fk 
            ORDER BY id_waktu_fk DESC
        ) AS urutan
    FROM public.fact_persediaan_barang
)
SELECT 
    dg.nama_gudang,
    dg.kota,
    dg.negara,
    dp.nama_pemasok,
    dp.negara_asal AS asal_pemasok,
    db.kategori,
    SUM(st.jumlah_stok_akhir) AS total_stok_fisik,
    SUM(st.total_nilai_stok) AS total_valuasi_rupiah
FROM snapshotterakhir st
JOIN public.dim_gudang dg ON st.id_gudang_fk = dg.id_gudang_sk
JOIN public.dim_pemasok dp ON st.id_pemasok_valid = dp.id_pemasok_sk
JOIN public.dim_barang db ON st.id_barang_fk = db.id_barang_sk
WHERE st.urutan = 1
GROUP BY 
    dg.nama_gudang, 
    dg.kota, 
    dg.negara, 
    dp.nama_pemasok, 
    dp.negara_asal, 
    db.kategori
ORDER BY total_valuasi_rupiah DESC;