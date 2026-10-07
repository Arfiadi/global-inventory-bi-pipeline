# Global Inventory BI Pipeline 📦📊

> Integrasi Machine Learning dan Business Intelligence Pipeline End-to-End untuk Mitigasi Risiko Inventaris Global.

🔗 **[Lihat Live Dashboard Power BI di sini](https://app.powerbi.com/view?r=eyJrIjoiYzFkYzE2ZjItMjZmZi00MmFmLTk3ODktMDJjNmY4MDFhNzNiIiwidCI6IjUxZDc5MGQ1LWJlZmItNDg0ZS04NmM2LWQxN2I2NDcyNzYyNCIsImMiOjEwfQ%3D%3D)**

Proyek ini adalah implementasi sistem pendukung keputusan berbasis data (*data-driven decision support system*) untuk memitigasi risiko penumpukan (*overstock*) dan kekosongan stok (*stockout*) pada rantai pasok global. Proyek ini mendemonstrasikan kapabilitas pipeline *Business Intelligence* (BI) *end-to-end*, mulai dari ekstraksi data dari sistem OLTP hingga visualisasi di *dashboard* analitik prediktif.

## 🌟 Fitur Utama
- **Synthetic Data Generation**: Menggunakan data transaksional sintetis untuk mensimulasikan lingkungan operasional rantai pasok global secara realistis.
- **Data Warehouse (Star Schema)**: Desain repositori analitik menggunakan pendekatan *dimensional modeling* (*Star Schema*) pada PostgreSQL.
- **ETL Pipeline**: Alur transformasi data menggunakan Pentaho Data Integration dan SQL untuk memigrasikan log transaksional dari MySQL ke PostgreSQL tanpa anomali.
- **Semantic Layer (SQL View)**: Lapisan terdenormalisasi yang dipersiapkan khusus untuk *Machine Learning* dan analitik.
- **Machine Learning Integration**:
  - **Spectral Clustering**: Segmentasi portofolio inventaris (Klasifikasi ABC Modern) untuk mengidentifikasi produk *Capital Traps*, *Fast-Moving*, dan *Routine/High-Value*.
  - **Time-Series Forecasting**: Peramalan permintaan logistik menggunakan model PROPHET (terbukti memiliki *error rate* MAPE terendah dibandingkan XGBoost dan SARIMAX).
- **Prescriptive Analytical Dashboard**: *Dashboard* interaktif (Power BI) yang memantau *Inventory Health*, memvisualisasikan segmentasi produk, serta memberikan peringatan risiko inventaris (*overstock risk*) secara *real-time*.

## 📂 Struktur Repositori

```text
├── Notebook/       # Jupyter Notebook untuk proses EDA, Clustering (K-Means, GMM, Spectral), dan Forecasting (SARIMAX, XGBoost, Prophet)
├── dashboard/      # File Power BI (.pbix) untuk Executive Dashboard 👉 [dwh dashboard.pbix](./dashboard/dwh%20dashboard.pbix)
├── data dummy/     # Dataset operasional / sintetis yang digunakan (CSV/Excel)
├── docs/           # Dokumentasi proyek (Desain Dashboard, Jurnal, dll.)
├── file Pentaho/   # Transformasi dan Job ETL (.ktr / .kjb) menggunakan Pentaho
├── gambar/         # Aset gambar
└── scriptsql/      # Skrip untuk mysql dan postgress
```

## 🛠️ Tech Stack & Tools
* **Database / Storage**: MySQL (OLTP), PostgreSQL (Data Warehouse)
* **ETL**: Pentaho Data Integration (PDI)
* **Machine Learning**: Python (Pandas, Scikit-Learn, Statsmodels, Prophet, XGBoost)
* **Visualisasi & BI**: Power BI

## 🚀 Alur Kerja (Pipeline)
1. **Sintesis Data & OLTP**: Data operasional disimpan dalam MySQL dengan relasi yang dinamis (transaksional harian).
2. **Proses ETL**: Pentaho mengekstrak data dari MySQL, mentransformasikan (pembersihan, *surrogate key*), dan me-*load* data ke skema bintang di PostgreSQL.
3. **Pembuatan SQL View**: Lapisan semantik dibentuk untuk mendistribusikan data ke *Machine Learning* secara efisien.
4. **Analisis ML**: Model *Spectral Clustering* melabeli portofolio produk, dan algoritma *PROPHET* memproyeksikan peramalan harian.
5. **Dashboard BI**: Semua *insight* bermuara ke *dashboard* eksekutif untuk tindakan mitigatif secara prediktif & preskriptif.

## 👥 Kredit
Dikembangkan sebagai bagian dari tugas mata kuliah Data Warehouse, Politeknik Elektronika Negeri Surabaya.

* **Penulis**: Arfi Adi Nugroho
* **Dosen Pengampu**: Dr. Edi Satriyanto S.Si., M.Si
