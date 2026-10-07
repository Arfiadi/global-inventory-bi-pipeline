SELECT 
    SUM(total_stok_fisik) AS total_stok_fisik_keseluruhan,
    SUM(total_valuasi_rupiah) AS total_valuasi_rupiah_keseluruhan
FROM 
    public.vw_target_executive_health;