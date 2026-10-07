-- A. Cek apakah ada data barang keluar di tabel fakta
SELECT 
    COUNT(*) AS total_transaksi,
    SUM(jumlah_keluar) AS total_unit_keluar_semua_gudang,
    COUNT(*) FILTER (WHERE jumlah_keluar > 0) AS jumlah_baris_ada_transaksi_keluar
FROM public.fact_persediaan_barang;

-- B. Cek sampel data yang memiliki transaksi keluar
SELECT * FROM public.fact_persediaan_barang 
WHERE jumlah_keluar > 0 
LIMIT 5;

-- C. Cek apakah ada record yang JOIN-nya gagal (Nilai NULL)
SELECT COUNT(*) 
FROM public.fact_persediaan_barang fp
LEFT JOIN public.dim_waktu dw ON fp.id_waktu_fk = dw.id_waktu_sk
WHERE dw.id_waktu_sk IS NULL;

-- Cek apakah kolom id_waktu_fk berubah seiring berjalannya id_pergerakan_stok
SELECT id_pergerakan_stok, id_waktu_fk 
FROM public.fact_persediaan_barang 
WHERE jumlah_keluar > 0 
ORDER BY id_pergerakan_stok 
LIMIT 20;