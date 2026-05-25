# DOKUMEN PERSYARATAN PRODUK (PRD)
## Mesin Audit Berkelanjutan & Kontrol Keuangan Otomatis
### *Automated Financial Controls & Continuous Auditing Engine* (AFC-CAE)

---

> **Klasifikasi:** INTERNAL — TERBATAS | Praktik Tata Kelola Data & Jaminan Mutu
>
> **Versi Dokumen:** 1.1 — *Revisi Pasca Kajian Rekayasa: Optimasi Cakupan & Peningkatan Teknis*
>
> **Status:** DRAFT UNTUK DITINJAU

---

> **Kendali Dokumen**
>
> | Atribut | Keterangan |
> |---|---|
> | Nama Produk | Mesin Audit Berkelanjutan & Kontrol Keuangan Otomatis (AFC-CAE) |
> | Dataset | Lending Club — 466.285 baris × 75 kolom |
> | Metodologi | CRISP-DM (Adaptasi Konteks Kepatuhan & Jaminan Mutu) |
> | Pemangku Kepentingan Utama | Audit Teknologi Informasi, Manajemen Risiko, Tata Kelola Data |
> | Platform Target | Workstation Lokal — Linux Mint (RAM Standar) |
> | Target Peluncuran | Sesuai Persetujuan Dewan Tata Kelola |
> | Pemilik Dokumen | Manajer Produk Utama, Praktik Tata Kelola Data |
> | Siklus Tinjauan | Triwulanan |
>
> **Catatan Revisi v1.1:**
> Revisi ini mencerminkan hasil kajian rekayasa untuk penerapan pada workstation lokal. Tiga perubahan cakupan utama diterapkan: (1) penghapusan algoritma *Local Outlier Factor* (LOF) karena kompleksitas memori O(n²) yang tidak efisien untuk dataset 466K baris, digantikan sepenuhnya oleh *Isolation Forest*; (2) pembatasan format file masukan pada `.csv` dan `.parquet` saja, menghilangkan dukungan `.xlsx` guna mencegah beban memori berlebih dari *parser* Excel; (3) penghapusan *Celery workers* dan integrasi pemindaian virus, digantikan oleh mekanisme asinkronus *BackgroundTasks* bawaan FastAPI. Dua peningkatan teknis utama juga ditambahkan: (a) Gerbang Konsistensi Tipe Data pada tahap penyerapan data; (b) spesifikasi *Explainable AI* (XAI) untuk setiap rekaman yang ditandai sebagai anomali.

---

## DAFTAR ISI

1. Ringkasan Eksekutif & Konteks Bisnis
2. Cakupan Produk & Fitur Inti (Berbasis CRISP-DM)
3. Kamus Data & Pemetaan Kontrol
4. Arsitektur Sistem & Alur Data
5. Persyaratan Non-Fungsional
6. Kriteria Penerimaan & Definisi Selesai
7. Daftar Risiko & Isu Terbuka
8. Lampiran

---

---

# BAGIAN 1 — RINGKASAN EKSEKUTIF & KONTEKS BISNIS

---

## 1.1 Identitas Produk

**AFC-CAE** adalah mesin jaminan kontrol keuangan bertenaga kecerdasan buatan yang beroperasi secara berkelanjutan, dirancang khusus untuk lingkungan platform pinjaman. Produk ini mengoperasionalkan audit data tingkat populasi penuh (100%) dengan mengubah data transaksi mentah menjadi aliran terstruktur berupa **Sinyal Kerentanan Sistem** (*System Vulnerability Signals* / SVS), temuan bermutu audit, dan memoranda regulatori yang dihasilkan secara otomatis.

AFC-CAE **bukan** model prediksi risiko kredit. Ia bukan dirancang untuk mengklasifikasikan pinjaman sebagai "baik" atau "buruk". AFC-CAE adalah sebuah **sistem kontrol detektif** — sebuah mesin intelijen kepatuhan yang mengidentifikasi ketidakkonsistenan logika, pelanggaran aturan bisnis, dan anomali multidimensi yang berpotensi menandakan kesalahan sistem, kegagalan kontrol proses, atau sinyal risiko kecurangan.

---

## 1.2 Pernyataan Masalah

### Kegagalan Struktural Audit Tradisional

Operasi pinjaman modern memproses ratusan ribu rekaman setiap tahunnya. Metodologi audit yang berlaku saat ini — pengujian berbasis sampel secara manual — secara struktural tidak memadai untuk skala ini:

| Dimensi | Audit Manual Tradisional | Target AFC-CAE |
|---|---|---|
| **Cakupan Populasi** | < 1% rekaman yang diambil sebagai sampel | 100% dari seluruh rekaman |
| **Waktu Siklus** | 5–15 hari kerja per siklus audit | < 4 jam per eksekusi dataset penuh |
| **Latensi Deteksi** | Triwulanan atau tahunan | Berkelanjutan / dipicu oleh peristiwa |
| **Kedalaman Pernyataan** | Berbasis daftar periksa, ~15–20 pemeriksaan | 40+ pernyataan matematis lintas kolom |
| **Deteksi Anomali** | Penilaian manusia atas sampel | ML tanpa pengawasan pada populasi penuh |
| **Dokumentasi Audit** | Penulisan memo secara manual | PFM/CIR otomatis dengan jejak kriptografis |
| **Reproduktibilitas** | Rendah (bergantung pada analis) | Sepenuhnya terversi MLflow, diverifikasi dengan hash |

### Akar Penyebab Kesenjangan

Tiga kegagalan sistemik mendorong ketidakcukupan audit tradisional:

**1. Kebutaan Volume (*Volume Blindness*):**
Dataset Lending Club dengan 466.285 baris saja mengandung ~34,97 juta titik data individual di 75 kolom. Tidak ada proses manual yang dapat menegakkan relasi matematis lintas kolom pada skala ini secara konsisten dan andal.

**2. Misklasifikasi Semantik:**
Pra-pemrosesan data dikategorikan sebagai tugas rekayasa, bukan fungsi kepatuhan. Misklasifikasi ini berarti inkonsistensi logika — misalnya, jumlah yang didanai (*funded amount*) melebihi jumlah pinjaman yang diminta — diperlakukan sebagai "masalah kualitas data" daripada **sinyal pengesampingan tidak sah** yang memerlukan investigasi.

**3. Kebutaan Terhadap Nilai Kosong (*Null Blindness*):**
Nilai yang hilang (*missing values*) secara operasional diperlakukan sebagai data yang perlu diimputasi atau dihapus. Dalam konteks pinjaman yang diatur, pola *null* tertentu merupakan **temuan audit yang informatif** — ketidakhadirannya sama bermaknanya dengan kehadirannya. Misalnya, `mths_since_last_delinq` = *null* berarti peminjam tidak memiliki riwayat tunggakan; penanganan yang keliru mendistorsi logika penyaringan kecurangan.

---

## 1.3 Proposisi Nilai

AFC-CAE menghadirkan empat layanan jaminan mutu yang berbeda di bawah satu mesin otomatis:

**V1 — Pemantauan Kontrol Berkelanjutan (*Continuous Controls Monitoring* / CCM):**
Setiap dataset yang diserap akan dikenai 40+ pemeriksaan pernyataan di seluruh lima modul audit. Kegagalan diklasifikasikan, dicatat, dan dieskalasi tanpa inisiasi manusia.

**V2 — Intelijen Anomali Multidimensi:**
*Isolation Forest* mengidentifikasi anomali yang tidak dapat ditangkap oleh pemeriksaan berbasis aturan mana pun secara individual — rekaman yang secara sendiri-sendiri tampak masuk akal tetapi secara kolektif menyimpang dalam ruang fitur risiko keuangan.

**V3 — Dokumentasi Audit Otomatis:**
Mesin menghasilkan secara otomatis **Memorandum Temuan Awal** (*Preliminary Findings Memorandum* / PFM) untuk temuan zona pantau (*watch zone*), dan **Laporan Insiden Kritis** (*Critical Incident Report* / CIR) untuk peristiwa berkeparahan P1, lengkap dengan rantai bukti bertanda waktu dan sidik jari data SHA-256.

**V4 — Keterlacakan Bermutu Regulasi:**
Setiap eksekusi audit diberi versi dalam MLflow dengan pencatatan parameter lengkap, hash dataset, hasil pernyataan, dan skor anomali. Setiap eksekusi sepenuhnya dapat direproduksi untuk pemeriksaan regulasi atau dukungan litigasi.

---

## 1.4 Pengguna Target & Persona

| Persona | Peran | Kebutuhan Utama | Interaksi dengan Mesin |
|---|---|---|---|
| **P1 — Auditor TI Senior** | Pengujian kontrol, dokumentasi temuan | Cakupan pernyataan populasi 100% | Meninjau keluaran PFM/CIR; mengonfigurasi ambang batas modul |
| **P2 — Chief Risk Officer (CRO)** | Pengawasan risiko sistemik | Peringatan eskalasi; tren tingkat anomali | Menerima peringatan otomatis Skenario B/C; meninjau KPI dasbor |
| **P3 — Pemimpin Tata Kelola Data** | Kepatuhan skema, tata kelola *null* | Validasi arsitektur metadata | Meninjau keluaran Modul 5 (Kepatuhan Struktural); menyetujui perubahan kamus data |
| **P4 — Petugas Kepatuhan** | Kepatuhan regulasi (ECOA, FCRA, SOX) | Hasil pernyataan aturan kebijakan | Meninjau temuan modul Kepatuhan Kebijakan (seri POL) |
| **P5 — Pemimpin Rekayasa Data** | Integritas *pipeline*, kesehatan penyerapan | Akar penyebab anomali sistemik | Menerima CIR Skenario C; menyelidiki batch ETL yang ditandai |

---

---

# BAGIAN 2 — CAKUPAN PRODUK & FITUR INTI (BERBASIS CRISP-DM)

---

## 2.1 Adaptasi Metodologi CRISP-DM

Kerangka kerja CRISP-DM standar diadaptasi di sini dari konteks pemodelan prediktif ke **konteks jaminan kepatuhan**. Pemetaannya adalah sebagai berikut:

| Fase CRISP-DM | Interpretasi Standar | Interpretasi AFC-CAE |
|---|---|---|
| **Fase 1: Pemahaman Bisnis** | Mendefinisikan tujuan ML | Mendefinisikan tujuan kontrol audit; memetakan kerangka regulasi (COSO, SR 11-7, DAMA DMBOK) |
| **Fase 2: Pemahaman Data** | EDA, pemrofilan awal | Audit Kepatuhan Arsitektur Metadata; tata kelola *null*; deteksi pergeseran skema |
| **Fase 3: Persiapan Data** | Rekayasa fitur, pembersihan | Mesin Pernyataan Berbasis Aturan (40+ pemeriksaan); klasifikasi SVS; gerbang karantina |
| **Fase 4: Pemodelan** | Membangun model prediktif | Deteksi anomali tanpa pengawasan (*Isolation Forest*); penilaian ensemble; **eksplikabilitas berbasis XAI** |
| **Fase 5: Evaluasi** | Metrik akurasi model | Ambang batas tingkat anomali; logika eskalasi Skenario A/B/C; tinjauan positif palsu |
| **Fase 6: Penerapan** | API penyajian model | Layanan penyerapan FastAPI; registri audit MLflow; pembuatan PFM/CIR otomatis |

---

## 2.2 FASE 1 & 2 — PEMAHAMAN BISNIS & PEMAHAMAN DATA

### 2.2.1 Audit Kepatuhan Arsitektur Metadata & Gerbang Konsistensi Tipe Data

**Tujuan:** Sebelum pemeriksaan pernyataan apa pun, mesin harus menetapkan apakah profil struktural dataset sesuai dengan versi kamus data yang terdaftar, dan memastikan bahwa setiap kolom ditafsirkan dengan tipe data yang benar sejak awal. Pergeseran skema (*schema drift*) dan salah tafsir tipe data merupakan temuan audit tersendiri.

#### Fitur A: Validasi Sidik Jari Skema

Pada setiap peristiwa penyerapan, mesin menghitung:
- Pernyataan jumlah kolom: diharapkan 75 kolom ± 0 toleransi
- Perbandingan himpunan nama kolom: kecocokan tepat terhadap skema terdaftar v{N}
- Pemeriksaan kesesuaian tipe data: tipe data yang disimpulkan dari setiap kolom dibandingkan terhadap tipe data yang diharapkan sesuai kamus
- Gerbang volume baris: tandai jika jumlah rekaman menyimpang > ±10% dari eksekusi sebelumnya tanpa persetujuan eksplisit

Setiap penyimpangan skema memicu `SCHEMA-DRIFT-ALERT` sebelum pemrosesan dimulai. Pemrosesan dapat dilanjutkan dalam mode `SOFT_GATE` tetapi seluruh keluaran ditandai sebagai `SCHEMA_UNCONFIRMED`.

#### Fitur B: Gerbang Konsistensi Tipe Data (Peningkatan Baru v1.1)

**Latar Belakang dan Justifikasi Teknis:**
Pandas memiliki perilaku inferensi tipe data yang tidak deterministik ketika sebuah kolom mengandung campuran nilai numerik dan nilai *null* (`NaN`). Sebagai contoh, kolom integer seperti `delinq_2yrs` (yang seharusnya bertipe `int64`) akan secara otomatis diubah menjadi `float64` oleh Pandas ketika ada nilai *null* di dalamnya, karena `NaN` hanya ada dalam representasi `float` di NumPy. Jika dibiarkan tidak ditangani, kondisi ini dapat menyebabkan kegagalan pernyataan palsu (*false assertion failures*) — misalnya, pemeriksaan CRS-06 yang menegakkan bahwa `inq_last_6mths` adalah nilai integer akan gagal terhadap sebuah `float64` bahkan jika nilai numeriknya secara konseptual adalah bilangan bulat.

**Spesifikasi Gerbang:**

Pemetaan tipe data yang telah ditentukan sebelumnya (*predefined dtype mapping*) **wajib** diterapkan pada saat penyerapan menggunakan parameter `dtype` dari `pd.read_csv()` atau `pd.read_parquet()`, atau melalui konversi eksplisit segera setelah pemuatan. Pemetaan ini bersifat kanonik dan diatur dalam file konfigurasi `audit_config_v{N}.yaml`.

**Pemetaan Tipe Data Kanonik (Contoh Representatif):**

```yaml
# audit_config_v1.yaml — bagian: dtype_schema
dtype_mapping:
  # Kolom Integer — Selalu gunakan nullable integer Pandas (Int64) untuk mengakomodasi NaN
  delinq_2yrs:       "Int64"   # Nullable integer
  inq_last_6mths:    "Int64"
  open_acc:          "Int64"
  pub_rec:           "Int64"
  total_acc:         "Int64"
  collections_12_mths_ex_med: "Int64"
  acc_now_delinq:    "Int64"
  policy_code:       "Int64"
  # Kolom Float — Wajib float64
  loan_amnt:         "float64"
  funded_amnt:       "float64"
  funded_amnt_inv:   "float64"
  int_rate:          "float64"
  installment:       "float64"
  annual_inc:        "float64"
  dti:               "float64"
  revol_bal:         "float64"
  revol_util:        "float64"
  out_prncp:         "float64"
  out_prncp_inv:     "float64"
  total_pymnt:       "float64"
  total_rec_prncp:   "float64"
  total_rec_int:     "float64"
  recoveries:        "float64"
  collection_recovery_fee: "float64"
  # Kolom String / Kategorikal
  grade:             "category"
  sub_grade:         "category"
  term:              "category"
  loan_status:       "category"
  home_ownership:    "category"
  verification_status: "category"
  application_type:  "category"
  purpose:           "category"
  initial_list_status: "category"
  # Kolom Tanggal — Diparsing terpisah setelah pemuatan awal
  issue_d:           "object"   # Dikonversi ke datetime64 pasca-muat
  earliest_cr_line:  "object"
  last_pymnt_d:      "object"
  next_pymnt_d:      "object"
  last_credit_pull_d: "object"
```

**Prosedur Implementasi Wajib:**

```python
# WAJIB: Gunakan nullable integer Pandas (huruf kapital 'I' dalam 'Int64')
# untuk membedakan dari NumPy int64 — ini mengizinkan NaN pada kolom integer
integer_cols = [
    'delinq_2yrs', 'inq_last_6mths', 'open_acc', 'pub_rec',
    'total_acc', 'collections_12_mths_ex_med', 'acc_now_delinq', 'policy_code'
]

# Untuk CSV: terapkan dtype pada pemuatan
df = pd.read_csv(filepath, dtype={col: 'float64' for col in float_cols})

# Segera setelah muat, konversi integer kolom ke Int64 nullable
for col in integer_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Konversi kolom tanggal
date_cols = ['issue_d', 'earliest_cr_line', 'last_pymnt_d',
             'next_pymnt_d', 'last_credit_pull_d']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%b-%Y', errors='coerce')
```

**Tindakan Mesin jika Gerbang Tipe Data Gagal:**
Jika sebuah kolom tidak dapat dikonversi ke tipe yang ditentukan — misalnya, ditemukan nilai string yang tidak terduga dalam kolom yang seharusnya numerik — mesin mencatat `DTYPE_COERCION_FAILURE` dengan daftar nilai yang bermasalah, menandai kolom tersebut sebagai `TYPE_UNVERIFIED`, dan melanjutkan pemrosesan dalam mode terdegradasi (*degraded mode*). Setiap pemeriksaan pernyataan yang bergantung pada kolom `TYPE_UNVERIFIED` diberi anotasi dengan `DTYPE_CAVEAT` dalam laporan hasilnya.

---

### 2.2.2 Taksonomi Arsitektur *Null*

**Ini adalah pembeda inti produk.** Mesin mengklasifikasikan semua pola *null* ke dalam empat kategori tata kelola sebelum imputasi atau transformasi apa pun terjadi:

**Kategori 1 — Null Arsitektur Berbasis Kebijakan (*Policy-Driven Architecture Null* / PDAN)**
*Null* yang secara struktural benar berdasarkan desain, dapat ditelusuri ke keputusan kebijakan yang terdokumentasi.

*Contoh kolom:* `annual_inc_joint`, `dti_joint`, `verification_status_joint`
*Dasar:* `application_type` = 'Individual' untuk 100% rekaman. Kolom bersama (*joint*) dinonaktifkan oleh kebijakan untuk aplikasi perseorangan.
*Tindakan Mesin:* Dokumentasikan dalam log audit sebagai `NULL_TYPE: PDAN`. Tanpa imputasi. Tegaskan bahwa homogenitas `application_type` mendukung pola *null* sebagai **kontrol kompensasi**.

**Kategori 2 — Null Epoch Fitur (*Feature Epoch Null* / FEN)**
*Null* yang menunjukkan kumpulan fitur yang belum aktif atau belum diaktifkan untuk periode pembuatan dataset ini.

*Contoh kolom:* `open_acc_6m`, `open_il_6m` hingga `inq_last_12m` (14 kolom, semuanya 0 nilai tidak-null)
*Dasar:* Metrik pelacakan pinjaman cicilan diperkenalkan setelah tanggal pembuatan dataset.
*Tindakan Mesin:* Tandai semua kolom FEN dengan `FEATURE_EPOCH: PRE_ACTIVATION`. Tandai setiap nilai tidak-null dalam kolom FEN sebagai `SVS-SEVERITY: HIGH` — data yang tidak terduga dalam fitur yang dinonaktifkan adalah **anomali konfigurasi sistem**.

**Kategori 3 — Ketidakhadiran Informatif (*Informative Missingness* / IM)**
*Null* yang membawa sinyal positif yang dapat diinterpretasikan. Ketidakhadiran data itu sendiri adalah informasinya.

*Contoh kolom:* `mths_since_last_delinq` (~54% null), `mths_since_last_record` (~87% null), `mths_since_last_major_derog` (~79% null), `desc` (~73% null)
*Dasar:*
- `mths_since_last_delinq` null → peminjam tidak memiliki riwayat tunggakan (sinyal kredit positif)
- `mths_since_last_record` null → tidak ada catatan publik (tanpa kebangkrutan, putusan pengadilan)
- `desc` null → peminjam tidak menyerahkan narasi opsional (sinyal perilaku)

*Tindakan Mesin:*
- Buat fitur indikator biner: `has_delinquency_history`, `has_public_record`, `has_desc_narrative`
- Imputasi nilai sentinel numerik `999` untuk kolom IM berbasis waktu (mempertahankan semantik urutan sort)
- Validasi silang: jumlah *null* `mths_since_last_record` harus mendekati jumlah `pub_rec = 0` dalam toleransi ±2%. Penyimpangan > 2% = `TEMUAN_AUDIT: NULL_RECORD_MISMATCH`

**Kategori 4 — Kesenjangan Kelengkapan Penjaminan (*Underwriting Completeness Gap* / UCG)**
*Null* yang menunjukkan rekaman di mana kolom yang diperlukan tidak ditangkap — potensi kegagalan kontrol dalam alur kerja originasi.

*Contoh kolom:* `emp_title` (~6% null), `emp_length` (~4.5% null), `annual_inc` (4 rekaman null)
*Tindakan Mesin:*
- `emp_title` + `emp_length` keduanya *null* secara bersamaan: tandai sebagai `UCG-DUAL-EMPLOYMENT-NULL` — sinyal ketipisan identitas untuk penyaringan kecurangan
- `annual_inc` null: keparahan P1 — pendapatan adalah kolom penjaminan yang wajib. Setiap *null* adalah `TEMUAN_KRITIS` yang langsung.

---

### 2.2.3 Tabel Ringkasan Tata Kelola *Null*

| Kolom | Jumlah Null | % Null | Kategori Null | Tindakan Audit |
|---|---|---|---|---|
| `annual_inc_joint` | ~466.285 | ~100% | PDAN | Tegaskan PDAN; tanpa tindakan |
| `dti_joint` | ~466.285 | ~100% | PDAN | Tegaskan PDAN; tanpa tindakan |
| `open_acc_6m` hingga `inq_last_12m` (14 kolom) | ~466.285 | ~100% | FEN | Tandai PRE_ACTIVATION; peringatkan jika ada nilai tidak-null |
| `desc` | ~340.304 | ~73% | IM | Buat indikator biner |
| `mths_since_last_major_derog` | ~367.311 | ~79% | IM | Sentinel 999; validasi silang |
| `mths_since_last_record` | ~403.647 | ~87% | IM | Sentinel 999; validasi silang vs pub_rec |
| `mths_since_last_delinq` | ~250.351 | ~54% | IM | Sentinel 999; validasi silang vs delinq_2yrs |
| `next_pymnt_d` | ~227.214 | ~49% | Kondisional Siklus Hidup | Tegaskan null untuk Lunas/Dihapusbukukan |
| `emp_title` | ~27.588 | ~6% | UCG | Tandai null ganda; pemeriksaan kecurangan |
| `emp_length` | ~21.008 | ~4.5% | UCG | Validasi silang dengan emp_title |
| `annual_inc` | 4 | ~0,001% | UCG KRITIS | Temuan P1; karantina rekaman |
| `tot_coll_amt` / `tot_cur_bal` | ~70.276 | ~15% | Potensi BDFF | Analisis kluster temporal |

---

## 2.3 FASE 3 — PERSIAPAN DATA: MESIN PERNYATAAN BERBASIS ATURAN

### 2.3.1 Arsitektur Mesin

Mesin Pernyataan Berbasis Aturan (*Rule-Based Assertion Engine* / RBAE) adalah gerbang pemrosesan pertama. Ia mengeksekusi 40+ pemeriksaan deterministik, matematis, dan logis yang diorganisir ke dalam lima modul audit. Semua pemeriksaan berjalan secara paralel (operasi NumPy yang divektorisasi). Target waktu eksekusi: < 90 detik untuk 466.285 rekaman.

**Keluaran per pemeriksaan:** `{check_id, record_count_tested, failure_count, failure_rate_pct, severity, sample_failing_ids[10], execution_time_ms}`

---

### 2.3.2 MODUL 1 — Integritas Rekonsiliasi Keuangan (Seri FIN)

**Cakupan:** Semua nilai moneter, metrik keuangan yang dihitung, dan saldo siklus hidup pembayaran.

**Definisi Ambang Batas:**

| ID Pemeriksaan | Pernyataan | Toleransi | Keparahan | Eskalasi Otomatis |
|---|---|---|---|---|
| `FIN-01` | `funded_amnt <= loan_amnt` | Toleransi nol | 🔴 P1 KRITIS | Ya |
| `FIN-02` | `funded_amnt_inv <= funded_amnt` | Toleransi nol | 🔴 P1 KRITIS | Ya |
| `FIN-03` | Angsuran yang dihitung ulang ≈ angsuran yang tersimpan. Rumus: `PMT = P × [r(1+r)^n] / [(1+r)^n - 1]` di mana `P = loan_amnt`, `r = int_rate / 1200`, `n = term_months`. Delta yang dapat diterima: ≤ $1,00 | ±$1,00 | 🔴 P1 KRITIS | Ya |
| `FIN-04` | `total_pymnt >= total_rec_prncp + total_rec_int + total_rec_late_fee` | ±$0,01 | 🟠 P2 TINGGI | Tidak |
| `FIN-05` | `total_pymnt_inv <= total_pymnt` | Toleransi nol | 🟠 P2 TINGGI | Tidak |
| `FIN-06` | `out_prncp` ≈ `funded_amnt - total_rec_prncp` untuk pinjaman aktif/berjalan | ±$10,00 | 🟠 P2 TINGGI | Tidak |
| `FIN-07` | `out_prncp_inv <= out_prncp` | Toleransi nol | 🟡 P3 SEDANG | Tidak |
| `FIN-08` | `revol_util ≈ (revol_bal / total_rev_hi_lim) × 100` ketika keduanya tidak null | ±0,5% | 🟡 P3 SEDANG | Tidak |
| `FIN-09` | `recoveries >= collection_recovery_fee` | Toleransi nol | 🔴 P1 KRITIS | Ya |
| `FIN-10` | `loan_status = 'Fully Paid'` → `out_prncp = 0` DAN `out_prncp_inv = 0` | Toleransi nol | 🔴 P1 KRITIS | Ya |
| `FIN-11` | `loan_status = 'Charged Off'` → `recoveries >= 0` (negatif = kritis) | >= 0 | 🔴 P1 jika negatif | Ya jika negatif |
| `FIN-12` | `last_pymnt_amnt > 0` untuk rekaman dengan aktivitas pembayaran apa pun | > 0 | 🟡 P3 SEDANG | Tidak |
| `FIN-13` | `int_rate > 0` DAN `int_rate < 36` (pernyataan tarif maksimum platform) | (0, 36) | 🟠 P2 TINGGI | Tidak |
| `FIN-14` | `installment > 0` | > 0 | 🔴 P1 KRITIS | Ya |

**Klasifikasi SVS untuk Kegagalan FIN:**
- `FIN-01/02`: **Risiko Transaksi Tidak Sah (*Unauthorized Transaction Risk* / UTR-1)** — jumlah yang didanai melebihi yang diminta; kemungkinan pengesampingan manual atau korupsi ETL
- `FIN-03`: **Kegagalan Integritas Mesin Kalkulasi (*Calculation Engine Integrity Failure* / CEIF-1)** — nilai yang tersimpan tidak sesuai dengan kalkulasi ulang matematis; kemungkinan manipulasi tarif
- `FIN-09`: **Indikator Kecurangan — Inversi Biaya Pemulihan (*Recovery Fee Inversion* / FI-RFI)** — secara matematis mustahil dalam operasi yang sah; tinjauan forensik segera diperlukan
- `FIN-10`: **Sinyal Liabilitas Semu (*Phantom Liability Signal* / PLS-1)** — kegagalan integritas neraca keuangan; pinjaman yang telah lunas masih membawa pokok yang tersisa

---

### 2.3.3 MODUL 2 — Integritas Profil Peminjam (Seri PRF)

**Cakupan:** Identitas peminjam, pekerjaan, pendapatan, data geografis, dan konsistensi jenis aplikasi.

| ID Pemeriksaan | Pernyataan | Keparahan | Klasifikasi SVS |
|---|---|---|---|
| `PRF-01` | Keunikan `member_id` di seluruh dataset — toleransi nol duplikat | 🔴 P1 KRITIS | Pelanggaran Integritas Data (DIB-1) / Kecurangan Identitas Sintetis |
| `PRF-02` | `annual_inc > 0` untuk semua yang tidak null | 🔴 P1 KRITIS | Kegagalan Kontrol Penjaminan |
| `PRF-03` | Konsistensi arah `dti`: rasio angsuran-terhadap-pendapatan yang lebih tinggi → DTI lebih tinggi. Korelasi Spearman tingkat segmen > 0,5 diharapkan | 🟠 P2 TINGGI | Ketidaksesuaian Kalkulasi DTI |
| `PRF-04` | `annual_inc > 3× batas atas IQR` DAN `verification_status = 'Not Verified'` → tandai ganda | 🟠 P2 TINGGI | Vektor Kecurangan Aplikasi (AFV-1) |
| `PRF-05` | `application_type = 'Joint App'` → `annual_inc_joint` TIDAK NULL DAN `dti_joint` TIDAK NULL | 🔴 P1 KRITIS | Rekaman Penjaminan Tidak Lengkap (kesenjangan ECOA) |
| `PRF-06` | `application_type = 'Individual'` → `annual_inc_joint`, `dti_joint`, `verification_status_joint` SEMUA NULL | 🟡 P3 SEDANG | Pelanggaran PDAN |
| `PRF-07` | Tanggal `earliest_cr_line` ≤ tanggal `issue_d` | 🔴 P1 KRITIS | Kemustahilan Temporal / Sinyal Fabrikasi Rekaman |
| `PRF-08` | Awalan kode pos (3 digit pertama) secara geografis konsisten dengan `addr_state` | 🟠 P2 TINGGI | Kecurangan Alamat / Kesalahan Pemetaan Penyerapan |
| `PRF-09` | `emp_length` ∈ enum yang ditentukan | 🟡 P3 SEDANG | Pelanggaran Kosakata Skema |
| `PRF-10` | `home_ownership` ∈ `{RENT, OWN, MORTGAGE, OTHER, NONE, ANY}` | 🟡 P3 SEDANG | Pelanggaran Kosakata Skema |
| `PRF-11` | `annual_inc` ≤ nilai persentil ke-99 yang dihitung per segmen `grade` | 🟠 P2 TINGGI | Sinyal Kelayakan Pendapatan |
| `PRF-12` | `dti >= 0` DAN `dti <= 100` | 🟠 P2 TINGGI | Pelanggaran Rentang DTI |

---

### 2.3.4 MODUL 3 — Kepatuhan Kebijakan & Siklus Hidup Pinjaman (Seri POL)

**Cakupan:** Validitas siklus hidup status pinjaman, keselarasan peringkat/tarif, konsistensi temporal, dan kepatuhan kebijakan platform.

| ID Pemeriksaan | Pernyataan | Keparahan | Klasifikasi SVS |
|---|---|---|---|
| `POL-01` | `loan_status` ∈ enum yang ditentukan (9 nilai valid) | 🔴 P1 KRITIS | Pelanggaran Mesin Status Siklus Hidup |
| `POL-02` | `sub_grade` adalah subdivisi valid dari `grade` (misal, grade='B' → sub_grade ∈ {B1..B5}) | 🔴 P1 KRITIS | Kegagalan Integritas Sistem Penilaian Kredit |
| `POL-03` | `policy_code` = 1 untuk semua rekaman (homogen dalam dataset ini) | 🟠 P2 TINGGI | Pelanggaran Epoch Kebijakan |
| `POL-04` | `pymnt_plan = 'y'` HANYA untuk status tunggakan/kesulitan — bukan `Current`, `Fully Paid`, `In Grace Period` | 🔴 P1 KRITIS | Kesalahan Mesin Status Alur Kerja |
| `POL-05` | `next_pymnt_d` ADALAH NULL untuk `loan_status ∈ {Fully Paid, Charged Off}` | 🟠 P2 TINGGI | Sinyal Jadwal Pembayaran Zombie |
| `POL-06` | `last_pymnt_d >= issue_d` DAN `last_pymnt_d <= tanggal_eksekusi_saat_ini` | 🔴 P1 KRITIS | Sinyal Manipulasi Stempel Waktu |
| `POL-07` | `last_credit_pull_d >= issue_d` | 🟡 P3 SEDANG | Pelanggaran Urutan Temporal |
| `POL-08` | `issue_d` adalah format tanggal yang valid dan dalam rentang tanggal operasional platform | 🟠 P2 TINGGI | Rekaman Originasi Tidak Valid |
| `POL-09` | `initial_list_status ∈ {w, f}` | 🟡 P3 SEDANG | Pelanggaran Kosakata Status Pencatatan |
| `POL-10` | Statistik: dalam setiap `grade`, distribusi `int_rate` harus lebih tinggi dari grade sebelumnya. Tandai segmen grade di mana tingkat median berbalik. | 🟠 P2 TINGGI | Korupsi Algoritmik Mesin Penetapan Harga (SR 11-7) |
| `POL-11` | `term` ∈ `{' 36 months', ' 60 months'}` | 🟡 P3 SEDANG | Nilai Jangka Waktu Tidak Valid |
| `POL-12` | `verification_status` ∈ `{Verified, Source Verified, Not Verified}` | 🟡 P3 SEDANG | Pelanggaran Kosakata |

---

### 2.3.5 MODUL 4 — Konsistensi Sinyal Risiko Kredit (Seri CRS)

**Cakupan:** Indikator tunggakan, jumlah permintaan, catatan publik, dan konsistensi internal metrik koleksi.

| ID Pemeriksaan | Pernyataan | Keparahan | Klasifikasi SVS |
|---|---|---|---|
| `CRS-01` | `open_acc <= total_acc` — secara universal | 🔴 P1 KRITIS | Pelanggaran Integritas Data Biro Kredit |
| `CRS-02` | `delinq_2yrs = 0` → `mths_since_last_delinq` ADALAH NULL ATAU > 24 | 🟠 P2 TINGGI | Ketidakkonsistenan Temporal Tunggakan |
| `CRS-03` | `pub_rec = 0` → `mths_since_last_record` ADALAH NULL | 🟠 P2 TINGGI | Kesenjangan Sinkronisasi Catatan Publik |
| `CRS-04` | `acc_now_delinq > 0` → `delinq_2yrs > 0` | 🟠 P2 TINGGI | Kegagalan Sinkronisasi Data Real-Time vs. Batch |
| `CRS-05` | `tot_coll_amt >= 0` (tidak ada koleksi negatif) | 🔴 P1 KRITIS | Kesalahan Tanda Jumlah Koleksi |
| `CRS-06` | `inq_last_6mths >= 0` DAN bernilai integer | 🟡 P3 SEDANG | Pelanggaran Tipe Bidang Hitungan |
| `CRS-07` | `collections_12_mths_ex_med >= 0` DAN bernilai integer | 🟡 P3 SEDANG | Pelanggaran Tipe Bidang Hitungan |
| `CRS-08` | `delinq_2yrs >= 0` DAN bernilai integer | 🟡 P3 SEDANG | Pelanggaran Tipe Bidang Hitungan |
| `CRS-09` | `pub_rec >= 0` DAN bernilai integer | 🟡 P3 SEDANG | Pelanggaran Tipe Bidang Hitungan |
| `CRS-10` | `total_acc >= open_acc >= 1` untuk peminjam dengan riwayat kredit (earliest_cr_line tidak null) | 🟡 P3 SEDANG | Ketidakmasukakalan Jumlah Akun Kredit |
| `CRS-11` | Jika `tot_coll_amt > 0`: tandai silang dengan `delinq_2yrs = 0` — koleksi historis tanpa tunggakan yang tercatat memerlukan investigasi | 🟠 P2 TINGGI | Ketidaksesuaian Narasi Koleksi-Tunggakan |
| `CRS-12` | `revol_bal >= 0` | 🔴 P1 KRITIS | Anomali Saldo Negatif |

---

### 2.3.6 MODUL 5 — Kepatuhan Struktural & Arsitektur Null (Seri STR)

**Cakupan:** Kesesuaian struktural tingkat dataset, validasi pernyataan PDAN/FEN.

| ID Pemeriksaan | Pernyataan | Keparahan |
|---|---|---|
| `STR-01` | Semua 14 kolom FEN memiliki 0 nilai tidak-null (konfirmasi kumpulan fitur yang dinonaktifkan benar-benar kosong) | 🟠 P2 TINGGI |
| `STR-02` | `application_type` bersifat homogen ('Individual') — kontrol kompensasi PDAN | 🟡 P3 SEDANG |
| `STR-03` | Jumlah null `mths_since_last_delinq` ≈ jumlah `delinq_2yrs = 0` dalam toleransi ±5% | 🟠 P2 TINGGI |
| `STR-04` | Jumlah null `mths_since_last_record` ≈ jumlah `pub_rec = 0` dalam toleransi ±2% | 🟠 P2 TINGGI |
| `STR-05` | Jumlah null `tot_coll_amt` dan `tot_cur_bal` adalah identik (pola kegagalan penarikan biro yang sama) | 🟡 P3 SEDANG |
| `STR-06` | Jika null `tot_coll_amt`/`tot_cur_bal` mengelompok dalam jendela `issue_d` tertentu → tandai sebagai `BDFF` (*Bureau Data Fetch Failure*) | 🟠 P2 TINGGI |

---

### 2.3.7 Skema Keluaran Mesin Pernyataan

Setiap eksekusi menghasilkan manifes hasil pernyataan (JSON):

```json
{
  "run_id": "AFC-CAE-EKSEKUSI-20240115-001",
  "dataset_hash_sha256": "a3f9c2...",
  "total_records": 466285,
  "run_timestamp_utc": "2024-01-15T08:30:00Z",
  "schema_version": "v1",
  "dtype_gate_status": "PASSED",
  "modules_executed": ["FIN", "PRF", "POL", "CRS", "STR"],
  "assertion_results": [
    {
      "check_id": "FIN-01",
      "records_tested": 466285,
      "failures": 0,
      "failure_rate_pct": 0.0,
      "severity": "P1_KRITIS",
      "status": "LULUS",
      "execution_time_ms": 112
    }
  ],
  "aggregate_anomaly_rate_pct": 0.34,
  "escalation_scenario": "A",
  "quarantined_record_count": 0,
  "auto_generated_docs": []
}
```

---

## 2.4 FASE 4 & 5 — PEMODELAN & EVALUASI: DETEKSI ANOMALI BERTENAGA AI

### 2.4.1 Arsitektur Model — Isolation Forest (Sole Engine)

**Catatan Perubahan Cakupan v1.1:** *Local Outlier Factor* (LOF) telah **dihapus sepenuhnya** dari spesifikasi ini. Algoritma LOF memiliki kompleksitas komputasi O(n²) untuk fase fitting, yang pada dataset 466.285 baris dapat mengonsumsi > 8 GB memori dan membutuhkan waktu > 2 jam pada workstation standar — tidak layak untuk lingkungan penerapan target (Linux Mint, RAM standar). *Isolation Forest* diadopsi sebagai satu-satunya mesin deteksi anomali karena kompleksitasnya yang linier O(n) dalam memori dan waktu fitting yang jauh lebih cepat.

**Tujuan Lapisan AI:** Lapisan RBAE menangkap pola pelanggaran yang *diketahui*. Lapisan AI menangkap anomali multidimensi yang *tidak diketahui* — rekaman yang lolos semua 40+ pemeriksaan individual tetapi secara kolektif menyimpang dalam ruang fitur risiko keuangan.

**Spesifikasi Model Isolation Forest:**

```python
from sklearn.ensemble import IsolationForest

iforest_model = IsolationForest(
    n_estimators=200,          # Jumlah pohon: keseimbangan antara akurasi dan kecepatan
    contamination=0.05,        # Dapat dikonfigurasi melalui audit_config_v1.yaml
    max_features=1.0,          # Gunakan semua fitur untuk setiap pohon
    max_samples='auto',        # Default: min(256, n_samples)
    bootstrap=False,           # Tanpa bootstrap untuk isolasi murni
    n_jobs=-1,                 # Gunakan semua core CPU yang tersedia
    random_state=42,           # Dipersyaratkan untuk reproduktibilitas audit
    warm_start=False
)
```

**Justifikasi Pemilihan Parameter:**
- `n_estimators=200`: Memberikan skor anomali yang stabil; ditingkatkan dari default 100 untuk dataset > 100K baris
- `contamination=0.05`: Nilai awal konservatif; dapat disetel melalui konfigurasi tanpa perubahan kode
- `random_state=42`: **Wajib** untuk reproduktibilitas audit — dua eksekusi pada dataset yang sama harus menghasilkan skor yang identik secara bit

---

### 2.4.2 Rekayasa Fitur untuk Deteksi Anomali

**Justifikasi Pemilihan Fitur:** Fitur dipilih untuk merepresentasikan profil risiko keuangan setiap rekaman pinjaman. Kolom dengan status null PDAN atau FEN dikecualikan. Fitur IM direpresentasikan sebagai indikator biner.

**Kumpulan Fitur Utama (18 Fitur):**

| Fitur | Transformasi | Justifikasi |
|---|---|---|
| `loan_amnt` | RobustScaler | Eksposur keuangan inti |
| `funded_amnt` | RobustScaler | Integritas pencairan |
| `int_rate` | RobustScaler | Sinyal penetapan harga |
| `installment` | RobustScaler | Beban pembayaran |
| `annual_inc` | RobustScaler + log1p | Sinyal pendapatan (distribusi ekor kanan) |
| `dti` | RobustScaler | Rasio beban utang |
| `delinq_2yrs` | RobustScaler | Riwayat tunggakan |
| `inq_last_6mths` | RobustScaler | Aktivitas permintaan kredit |
| `open_acc` | RobustScaler | Keluasan akun |
| `pub_rec` | RobustScaler | Riwayat catatan publik |
| `revol_bal` | RobustScaler + log1p | Eksposur bergulir |
| `revol_util` | RobustScaler | Sinyal utilisasi |
| `total_acc` | RobustScaler | Kedalaman riwayat kredit |
| `total_pymnt` | RobustScaler | Kinerja pembayaran total |
| `out_prncp` | RobustScaler | Eksposur tersisa |
| `has_delinquency_history` | Biner (0/1) | Indikator turunan IM |
| `has_public_record` | Biner (0/1) | Indikator turunan IM |
| `grade_encoded` | OrdinalEncoder (A=1...G=7) | Sinyal tingkat kredit |

**Justifikasi Pemilihan Scaler:** `RobustScaler` (berbasis median/IQR) **diwajibkan** menggantikan `StandardScaler` karena data keuangan pinjaman menunjukkan ekor kanan yang berat dan nilai ekstrem yang sering terjadi. Penggunaan `StandardScaler` akan menekan sinyal anomali tepat di mana sinyal tersebut paling penting — di bagian ekor distribusi.

---

### 2.4.3 Spesifikasi Explainable AI (XAI) untuk Anomali (Peningkatan Baru v1.1)

**Latar Belakang dan Justifikasi:**
Sebuah skor anomali `-1` dari *Isolation Forest* — tanpa penjelasan pendukung — tidak dapat digunakan sebagai temuan audit yang dapat dipertahankan. Seorang auditor atau manajer risiko yang menerima laporan yang hanya menyatakan "Rekaman ini adalah anomali" tidak memiliki dasar untuk memutuskan apakah perlu ditindaklanjuti atau diabaikan. Spesifikasi XAI ini mewajibkan mesin untuk menghasilkan **bukti eksplikatif** bagi setiap rekaman yang ditandai — jawaban atas pertanyaan: *"Mengapa AI menandai rekaman ini secara spesifik?"*

**Metode yang Diwajibkan:**

AFC-CAE v1.1 mengimplementasikan dua mekanisme eksplikabilitas yang saling melengkapi, tanpa ketergantungan pada *library* eksternal yang berat (seperti SHAP untuk *Isolation Forest*, yang secara komputasional mahal):

#### Metode XAI-1: Deviasi dari Median Segmen (*Segment Median Deviation*)

Untuk setiap rekaman yang ditandai sebagai anomali (skor Isolation Forest < ambang batas), mesin menghitung **deviasi relatif** setiap fitur dari median segmennya. Segmentasi dilakukan berdasarkan `grade` dan `term` — dua dimensi risiko yang paling bermakna dalam konteks pinjaman.

```python
def generate_xai_deviation_report(
    flagged_record: pd.Series,
    segment_medians: pd.DataFrame,  # Median per grade × term
    feature_cols: list
) -> dict:
    """
    Menghasilkan laporan deviasi fitur untuk satu rekaman yang ditandai.
    Mengembalikan dict dengan skor deviasi per fitur, diurutkan dari
    yang paling menyimpang ke yang paling sedikit menyimpang.
    """
    grade = flagged_record['grade']
    term = flagged_record['term']
    segment_med = segment_medians.loc[(grade, term)]

    deviations = {}
    for col in feature_cols:
        if segment_med[col] != 0:
            pct_deviation = (flagged_record[col] - segment_med[col]) / abs(segment_med[col]) * 100
        else:
            pct_deviation = float('inf') if flagged_record[col] != 0 else 0.0
        deviations[col] = {
            "record_value": flagged_record[col],
            "segment_median": segment_med[col],
            "pct_deviation": round(pct_deviation, 2)
        }

    # Urutkan berdasarkan nilai absolut deviasi (paling menyimpang pertama)
    sorted_deviations = dict(
        sorted(deviations.items(), key=lambda x: abs(x[1]['pct_deviation']), reverse=True)
    )
    return {
        "top_3_anomaly_drivers": list(sorted_deviations.keys())[:3],
        "full_deviation_profile": sorted_deviations
    }
```

#### Metode XAI-2: Skor Jalur Isolation Forest (*Isolation Forest Path Score Decomposition*)

*Isolation Forest* menghasilkan skor kontaminasi melalui fungsi `score_samples()`. Untuk setiap rekaman yang ditandai, mesin juga mencatat **skor per fitur** menggunakan pendekatan univariat: melatih model *Isolation Forest* terpisah pada setiap fitur tunggal dan mencatat skor anomali individu-nya. Fitur dengan skor anomali univariat paling rendah (*paling terisolasi*) adalah kontributor terkuat terhadap anomali multidimensi.

```python
def compute_univariate_isolation_scores(
    flagged_record: pd.Series,
    training_data: pd.DataFrame,
    feature_cols: list,
    random_state: int = 42
) -> dict:
    """
    Melatih model iForest univariat per fitur dan mencatat skor isolasi
    untuk rekaman yang ditandai. Digunakan sebagai proksi kontribusi fitur.
    Catatan: Fungsi ini dieksekusi HANYA untuk rekaman yang ditandai,
    bukan seluruh dataset, untuk menjaga efisiensi memori.
    """
    univariate_scores = {}
    for col in feature_cols:
        if flagged_record[col] is not None and not pd.isna(flagged_record[col]):
            iso = IsolationForest(
                n_estimators=50,  # Lebih sedikit pohon untuk efisiensi
                random_state=random_state
            )
            iso.fit(training_data[[col]].dropna())
            score = iso.score_samples([[flagged_record[col]]])[0]
            univariate_scores[col] = round(float(score), 4)

    # Skor lebih negatif = lebih terisolasi = kontributor anomali lebih kuat
    sorted_scores = dict(
        sorted(univariate_scores.items(), key=lambda x: x[1])
    )
    return sorted_scores
```

#### Skema Keluaran XAI per Rekaman yang Ditandai

Setiap rekaman anomali dalam laporan keluaran HARUS menyertakan blok `xai_explanation`:

```json
{
  "record_id": "loan_id_123456",
  "member_id": "MASKED",
  "composite_anomaly_score": -0.412,
  "anomaly_flag": -1,
  "xai_explanation": {
    "method": "segment_median_deviation + univariate_isolation",
    "segment_context": {
      "grade": "B",
      "term": "36 months"
    },
    "top_3_anomaly_drivers": [
      "annual_inc",
      "revol_bal",
      "dti"
    ],
    "deviation_profile": {
      "annual_inc": {
        "record_value": 2400000.0,
        "segment_median": 68000.0,
        "pct_deviation": 3429.41,
        "univariate_isolation_score": -0.821,
        "interpretation": "Pendapatan tahunan 34x lipat di atas median segmen Grade B, 36 bulan. Dikombinasikan dengan status 'Not Verified' (lihat PRF-04) — sinyal Vektor Kecurangan Aplikasi Kelas Tinggi."
      },
      "revol_bal": {
        "record_value": 385000.0,
        "segment_median": 12400.0,
        "pct_deviation": 2905.64,
        "univariate_isolation_score": -0.743,
        "interpretation": "Saldo bergulir 29x lipat di atas median segmen. Eksposur bergulir yang sangat tinggi pada peminjam Grade B adalah tidak lazim secara statistik."
      },
      "dti": {
        "record_value": 1.2,
        "segment_median": 14.8,
        "pct_deviation": -91.89,
        "univariate_isolation_score": -0.612,
        "interpretation": "DTI jauh di bawah median segmen meskipun saldo bergulir sangat tinggi — ketidakkonsistenan antara beban utang dan eksposur bergulir memerlukan validasi silang."
      }
    },
    "audit_narrative": "Rekaman ini ditandai karena kombinasi pendapatan yang sangat tidak lazim (tapi belum terverifikasi), saldo bergulir ekstrem, dan DTI rendah yang tidak konsisten dengan profil keseluruhan. Pola ini konsisten dengan Vektor Kecurangan Aplikasi AFV-1 — deklarasi pendapatan yang digelembungkan tanpa verifikasi. Direkomendasikan: tinjauan manual berkas penjaminan dan permintaan verifikasi pendapatan kepada sumber."
  }
}
```

**Persyaratan Kinerja XAI:**
- Pembuatan penjelasan XAI hanya dijalankan untuk rekaman yang ditandai (bukan seluruh dataset)
- Waktu pemrosesan XAI per rekaman yang ditandai: target ≤ 2 detik pada workstation standar
- Untuk dataset dengan > 1.000 rekaman yang ditandai: pembuatan XAI diparalelkan menggunakan `concurrent.futures.ThreadPoolExecutor`

---

### 2.4.4 Logika Eskalasi Bertingkat Risiko (Skenario A / B / C)

**Tingkat Anomali Komposit** = `(rekaman gagal RBAE ∪ rekaman ditandai ML) / total_rekaman × 100`

```
EKSEKUSI DETEKSI ANOMALI (RBAE + Isolation Forest)
                │
                ├──── Tingkat Anomali < 0,5%  ──────────────► SKENARIO A
                │
                ├──── Tingkat Anomali 0,5% – 5%  ──────────► SKENARIO B (Zona Pantau)
                │
                └──── Tingkat Anomali > 5%  ─────────────────► SKENARIO C (Eskalasi Kritis)
```

---

#### SKENARIO A — Tingkat Anomali Rendah (< 0,5%)

**Interpretasi:** Varians kesalahan operasional normal. Tidak ada indikasi kegagalan integritas sistemik.

**Tindakan Mesin Otomatis:**
1. Tandai rekaman anomali: `AUDIT_FLAG = 'LOW_RISK_OUTLIER'`; pertahankan dalam dataset dengan anotasi
2. Terapkan imputasi terbatas untuk null UCG: median segmen berdasarkan `{grade, term, purpose}`
3. Terapkan `RobustScaler` pada fitur kontinu; `OrdinalEncoder` pada kategoris
4. Bidang IM: indikator biner + imputasi sentinel 999
5. Catat eksekusi ke MLflow dengan `scenario = 'A'`, `action = 'ANNOTATE_AND_PROCEED'`
6. Hasilkan **Pemberitahuan Penyelesaian Audit (ACN)** standar — tidak diperlukan PFM

**Instruksi Dokumentasi Auditor:**
> *"Penilaian kualitas data terhadap dataset [HASH] selesai pada [TIMESTAMP]. Tingkat anomali komposit: [X]% di seluruh [N] pemeriksaan pernyataan pada [466.285] rekaman. Semua penyimpangan yang teridentifikasi diklasifikasikan sebagai varians entri data terisolasi, non-sistemik. Rekaman diberi anotasi sesuai kebijakan tata kelola data DGP-04. Tidak diperlukan eskalasi. Eksekusi diarsipkan di bawah eksperimen MLflow [ID]."*

---

#### SKENARIO B — Zona Pantau (0,5% – 5%)

**Interpretasi:** Tingkat penyimpangan yang meningkat. Kemungkinan mengindikasikan masalah sistemik yang terlokalisasi — batch penyerapan data tertentu, periode originasi tertentu, atau subset agen pemrosesan.

**Tindakan Mesin Otomatis:**
1. Aktifkan **analisis segmentasi temporal**: stratifikasi anomali berdasarkan `issue_d` — identifikasi apakah anomali mengelompok dalam bulan tertentu (pola kegagalan batch ETL)
2. Aktifkan **pemrofilan segmen**: kelompokkan anomali berdasarkan `{grade, addr_state, purpose}` — isolasi apakah kategori pinjaman tertentu terpengaruh secara tidak proporsional
3. Karantina rekaman yang gagal pernyataan P1/P2 ke partisi `staging_review`; kecualikan dari kumpulan fitur produksi tanpa persetujuan remediasi
4. Pemeriksaan toleransi nol (FIN-01, FIN-03, FIN-09, PRF-01, POL-02) yang dipicu pada TINGKAT KEGAGALAN BERAPA PUN → eskalasi tanpa syarat terlepas dari klasifikasi skenario agregat
5. Hasilkan **Memorandum Temuan Awal (PFM)** — lihat Bagian 4 untuk template
6. Catat ke MLflow dengan `scenario = 'B'`, `action = 'QUARANTINE_AND_INVESTIGATE'`, sertakan koordinat kluster temporal

**Peringatan Manajemen yang Dihasilkan Otomatis:**
```
PERINGATAN AUDIT OTOMATIS
Tanggal/Waktu: [TIMESTAMP] UTC
Dataset: Platform Pinjaman v[VERSI] | SHA-256: [HASH]
Tingkat Anomali: [Y]% — MELEBIHI AMBANG BATAS (0,5%)
Klasifikasi Skenario: B — ZONA PANTAU

Analisis Segmen:
  - Konsentrasi tertinggi: issue_d [PERIODE] | Grade [X] | Negara Bagian [Y]
  - Rekaman dikarantina: [N]
  - Kegagalan pernyataan toleransi nol: [DAFTAR ID PEMERIKSAAN]

Tindakan yang Direkomendasikan:
  Investigasi liniage data dari pipeline penyerapan untuk segmen yang terpengaruh.

Ditugaskan Kepada: Pemimpin Rekayasa Data / Operasi Risiko
SLA Respons: 48 jam kerja
Referensi: PFM-[YYYYMMDD-SEQ]
```

---

#### SKENARIO C — Eskalasi Kritis (> 5%)

**Interpretasi:** Tingkat anomali komposit > 5% bukan sekadar masalah kualitas data. Ini adalah **sinyal kegagalan kontrol sistemik**. Penyebab potensial mencakup: (a) pipeline penyerapan yang rusak; (b) migrasi sistem sumber tanpa validasi integritas; (c) kampanye kecurangan aplikasi yang terkoordinasi; atau (d) modifikasi skema yang tidak sah.

**Tindakan Mesin Otomatis:**
1. **HENTIKAN** semua pipeline hilir (*downstream*) — data yang terkontaminasi tidak boleh merambat ke sistem penilaian, pelaporan, atau pengambilan keputusan mana pun
2. Pertahankan **snapshot forensik**: tulis dataset mentah ke penyimpanan yang tidak dapat diubah dengan hash SHA-256 yang dicatat sebelum transformasi apa pun
3. Hasilkan **Laporan Insiden Kritis (CIR)** — klasifikasi P1; uraian pernyataan lengkap, peta kluster anomali, analisis distribusi temporal
4. Catat ke MLflow dengan `scenario = 'C'`, `action = 'EMERGENCY_HALT'`, `pipeline_status = 'SUSPENDED'`
5. Mulai **penelusuran asal-usul data (*data provenance trace*)**: identifikasi sistem sumber, stempel waktu penyerapan, log transformasi ETL, pemilik pipeline yang bertanggung jawab
6. Beritahu: CRO, Ketua Komite Tata Kelola Data, Direktur Audit TI, CISO (jika eksfiltrasi data tidak dapat dikecualikan)

**Header CIR yang Dihasilkan Otomatis:**
```
LAPORAN INSIDEN INTEGRITAS DATA KRITIS
Keparahan: P1 | Klasifikasi: KRITIS
Tanggal/Waktu: [TIMESTAMP] UTC
Referensi Insiden: CIR-[YYYYMMDD-SEQ]
SHA-256 Dataset: [HASH] | Salinan Forensik: [JALUR PENYIMPANAN]

TINGKAT ANOMALI: [Y]% | AMBANG BATAS TERLAMPAUI SEBESAR: [Y-5]%
STATUS PIPELINE: DITANGGUHKAN

Modul yang Terpengaruh: [DAFTAR]
Kegagalan Toleransi Nol: [JUMLAH di FIN-01, FIN-09, PRF-01, dll.]
Rekaman Dikarantina: [N] | % dari Populasi: [%]

TINDAKAN WAJIB (SLA: SEGERA):
  [ ] Notifikasi CRO — dalam 1 jam
  [ ] Rekayasa Data: pembekuan pipeline + investigasi akar penyebab
  [ ] Audit TI: tinjauan liniage data independen
  [ ] CISO: penilaian akses tidak sah / eksfiltrasi data

Disiapkan Oleh: Mesin Otomatis AFC-CAE v[VERSI]
```

---

## 2.5 FASE 6 — SPESIFIKASI PENERAPAN & REKAYASA

### 2.5.1 Layanan Penyerapan FastAPI

**Catatan Perubahan Cakupan v1.1:**
- **Format file yang didukung**: `.csv` dan `.parquet` SAJA. Dukungan `.xlsx` **dihapus** karena *parser* Excel (openpyxl/xlrd) memuat seluruh buku kerja ke dalam memori secara bersamaan, yang untuk file > 50MB dapat mengonsumsi > 2GB RAM — tidak layak untuk workstation lokal.
- **Infrastruktur asinkronus**: *Celery workers* dan *message broker* (Redis/RabbitMQ) **dihapus**. Digantikan oleh mekanisme `BackgroundTasks` bawaan FastAPI untuk pemrosesan ringan dan lokal. Pemindaian virus (*virus scan*) **dihapus** dari versi ini; titik kait (*hook*) tetap ada dalam kode sebagai konfigurasi yang dapat diaktifkan untuk versi mendatang.

**Spesifikasi Endpoint:**

| Endpoint | Metode | Deskripsi | Autentikasi |
|---|---|---|---|
| `/api/v1/audit/ingest` | `POST` | Terima unggahan file `.csv` atau `.parquet`; picu pipeline audit penuh | Kunci API + JWT |
| `/api/v1/audit/status/{run_id}` | `GET` | Kembalikan status pipeline dan kemajuan untuk sebuah eksekusi | Kunci API |
| `/api/v1/audit/results/{run_id}` | `GET` | Kembalikan manifes hasil pernyataan lengkap (JSON) | Kunci API |
| `/api/v1/audit/report/{run_id}` | `GET` | Kembalikan dokumen PFM/CIR yang dihasilkan (PDF/JSON) | Kunci API |
| `/api/v1/audit/config` | `GET`/`PUT` | Ambil atau perbarui konfigurasi ambang batas modul | Kunci API + Peran Admin |
| `/api/v1/audit/schema` | `GET` | Kembalikan versi skema terdaftar dan sidik jarinya | Kunci API |
| `/health` | `GET` | Pemeriksaan kesehatan layanan | Tidak ada |

**Gerbang Validasi Penyerapan (Pra-Pemrosesan):**
- Batas ukuran file: 500MB (dapat dikonfigurasi)
- Format yang diterima: `.csv` dan `.parquet` saja (validasi ekstensi dan tipe MIME)
- Validasi sidik jari skema sebelum pemrosesan dimulai
- Hash MD5 dari file yang diunggah dicatat ke jejak audit
- Titik kait pemindaian virus (stub dikonfigurasi; dinonaktifkan dalam v1.1)

**Pola Pemrosesan Asinkronus (BackgroundTasks):**
Pendekatan ini menggantikan Celery dan sepenuhnya bergantung pada mekanisme asinkronus bawaan FastAPI:

```python
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
import uuid

app = FastAPI(title="AFC-CAE API", version="1.1")

@app.post("/api/v1/audit/ingest")
async def ingest_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # Validasi format file
    if not file.filename.endswith(('.csv', '.parquet')):
        return JSONResponse(
            status_code=415,
            content={
                "error": "Format tidak didukung. Hanya .csv dan .parquet yang diterima.",
                "supported_formats": [".csv", ".parquet"]
            }
        )

    run_id = f"AFC-CAE-EKSEKUSI-{uuid.uuid4().hex[:12].upper()}"

    # Simpan file sementara ke disk lokal
    temp_path = f"/tmp/afc_cae/{run_id}/{file.filename}"
    await save_upload_to_disk(file, temp_path)

    # Daftarkan tugas latar belakang — respons segera dikembalikan
    background_tasks.add_task(
        run_full_audit_pipeline,
        run_id=run_id,
        file_path=temp_path,
        original_filename=file.filename
    )

    return JSONResponse(
        status_code=202,
        content={
            "run_id": run_id,
            "status": "DITERIMA",
            "message": "Pipeline audit dimulai. Pantau status di /api/v1/audit/status/{run_id}",
            "estimated_completion_minutes": 15
        }
    )
```

**Justifikasi Penghapusan Celery:**
`BackgroundTasks` FastAPI menjalankan fungsi secara asinkronus dalam proses yang sama setelah respons dikirimkan. Untuk workstation lokal dengan satu pengguna dan beban kerja batch, ini sepenuhnya memadai tanpa overhead infrastruktur *message broker*. *Celery* tetap menjadi jalur migrasi yang direkomendasikan ketika produk ditingkatkan ke lingkungan multi-pengguna atau produksi skala penuh.

---

### 2.5.2 Spesifikasi Registri Audit MLflow

**Struktur Eksperimen:**

```
Eksperimen MLflow: "AFC-CAE-Produksi"
│
├── Eksekusi: AFC-CAE-EKSEKUSI-[TIMESTAMP]-[SEQ]
│   ├── Parameter (dicatat di awal):
│   │   ├── dataset_sha256: [hash]
│   │   ├── dataset_version: [string versi]
│   │   ├── schema_version: [id_skema_v]
│   │   ├── audit_config_version: [versi konfigurasi yaml]
│   │   ├── iforest_n_estimators: 200
│   │   ├── iforest_contamination: 0.05
│   │   ├── iforest_random_state: 42
│   │   ├── escalation_threshold_b: 0.005
│   │   └── escalation_threshold_c: 0.05
│   │
│   ├── Metrik (dicatat per modul + agregat):
│   │   ├── fin_failure_rate
│   │   ├── prf_failure_rate
│   │   ├── pol_failure_rate
│   │   ├── crs_failure_rate
│   │   ├── str_failure_rate
│   │   ├── composite_anomaly_rate
│   │   ├── ml_flagged_count
│   │   ├── quarantine_count
│   │   ├── xai_explanations_generated
│   │   └── run_duration_seconds
│   │
│   ├── Artefak:
│   │   ├── assertion_results.json
│   │   ├── anomaly_scores_with_xai.parquet
│   │   ├── quarantine_manifest.csv
│   │   ├── pfm_atau_cir.pdf (jika dihasilkan)
│   │   ├── dtype_gate_report.json
│   │   └── dataset_fingerprint.txt (SHA-256 + jumlah baris + jumlah kolom)
│   │
│   └── Tag:
│       ├── scenario: A | B | C
│       ├── pipeline_status: SELESAI | DITANGGUHKAN | ERROR
│       └── auto_escalated: true | false
```

---

### 2.5.3 Spesifikasi Sistem Pencatatan Log

**Format Log Terstruktur (JSON):**
```json
{
  "timestamp": "2024-01-15T08:30:15.234Z",
  "level": "INFO",
  "service": "AFC-CAE",
  "run_id": "AFC-CAE-EKSEKUSI-20240115-001",
  "module": "MESIN_PERNYATAAN",
  "check_id": "FIN-03",
  "event": "PEMERIKSAAN_SELESAI",
  "records_tested": 466285,
  "failures": 142,
  "failure_rate_pct": 0.030,
  "severity": "P1_KRITIS",
  "auto_escalated": true,
  "execution_time_ms": 89
}
```

**Tingkat Log dan Perutean:**

| Tingkat | Pemicu | Tujuan |
|---|---|---|
| `DEBUG` | Detail tingkat rekaman individual | File lokal saja (dapat dinonaktifkan) |
| `INFO` | Penyelesaian pemeriksaan, modul, eksekusi | Log aplikasi + MLflow |
| `WARNING` | Kegagalan pernyataan P3, tingkat anomali mendekati ambang batas | Log aplikasi + pemantauan |
| `ERROR` | Kegagalan pernyataan P2, pengecualian pemrosesan | Log aplikasi + sistem peringatan |
| `CRITICAL` | Kegagalan pernyataan P1, pemicu Skenario C, penghentian pipeline | Log aplikasi + peringatan segera + jejak audit |

---

---

# BAGIAN 3 — KAMUS DATA & PEMETAAN KONTROL

---

## 3.1 Transformasi Semantik: Fitur ML → Titik Kontrol Audit

Tabel berikut mendokumentasikan reinterpretasi kolom kunci dari peran ML konvensional mereka ke fungsi audit AFC-CAE.

| Kolom | Peran ML Standar | Titik Kontrol Audit AFC-CAE | Jenis Kontrol | Seri Pernyataan |
|---|---|---|---|---|
| `loan_amnt` | Target regresi / fitur | **Kontrol batas atas** — menetapkan jumlah yang didanai dan diinvestasikan yang diizinkan secara maksimum. Kolom keuangan lain yang melebihi nilai ini adalah temuan P1 | Kontrol Batas | FIN-01, FIN-02 |
| `funded_amnt` | Fitur | **Gerbang integritas pencairan** — harus ≤ `loan_amnt`. Penyimpangan = sinyal pengesampingan tidak sah atau korupsi ETL | Integritas Transaksi | FIN-01 |
| `funded_amnt_inv` | Fitur | **Pembatas eksposur investor** — harus ≤ `funded_amnt`. Penyimpangan = kesalahan alokasi investasi fraksional | Integritas Transaksi | FIN-02 |
| `installment` | Fitur | **Validator rumus amortisasi** — dihitung ulang dari `loan_amnt`, `int_rate`, `term` menggunakan rumus PMT standar. Nilai tersimpan ditegaskan terhadap nilai yang dihitung ±$1,00 | Integritas Kalkulasi | FIN-03 |
| `int_rate` | Fitur | **Jangkar audit mesin penetapan harga** — digunakan dalam kalkulasi ulang angsuran; divalidasi terhadap pengurutan `grade` (grade lebih tinggi tidak boleh membawa tarif lebih tinggi dari grade lebih rendah pada tingkat median segmen) | Kontrol Penetapan Harga | FIN-03, FIN-13, POL-10 |
| `annual_inc` | Fitur | **Bidang wajib kelengkapan penjaminan** — toleransi nol untuk null. Nilai ekstrem dikombinasikan dengan status 'Not Verified' = Vektor Kecurangan Aplikasi | Kontrol Penjaminan | PRF-02, PRF-04 |
| `dti` | Fitur | **Kontrol kelayakan beban utang** — harus ≥ 0, ≤ 100. Korelasi arah dengan rasio angsuran-terhadap-pendapatan ditegaskan pada tingkat segmen | Kontrol Kualitas Kredit | PRF-03, PRF-12 |
| `loan_status` | Target ML (pinjaman Baik/Buruk) | **Kontrol mesin status siklus hidup** — setiap nilai status mengatur ekspektasi bidang keuangan hilir (misal, 'Fully Paid' → `out_prncp = 0`; 'Charged Off' → `recoveries ≥ 0`) | Kontrol Siklus Hidup | POL-01, POL-04, POL-05, FIN-10 |
| `out_prncp` | Fitur | **Jangkar rekonsiliasi neraca keuangan** — untuk pinjaman aktif, harus direkonsiliasi dengan `funded_amnt - total_rec_prncp`. Untuk pinjaman lunas, harus sama dengan nol. Saldo residual pada pinjaman tertutup = liabilitas semu | Kontrol Rekonsiliasi | FIN-06, FIN-10 |
| `delinq_2yrs` | Fitur | **Kontrol integritas riwayat tunggakan** — hitungan integer yang mengatur bidang temporal (`mths_since_last_delinq`). Hitungan nol dengan bidang temporal tidak null = kegagalan sinkronisasi | Kontrol Sinyal Kredit | CRS-02 |
| `policy_code` | Biasanya tidak digunakan | **Sentinel epoch kebijakan** — bidang nilai tunggal (`1`) yang memvalidasi bahwa dataset termasuk dalam satu rezim kebijakan. Nilai alternatif apa pun = konfigurasi kebijakan tidak sah atau pencampuran data | Kontrol Kepatuhan | POL-03 |
| `verification_status` | Fitur | **Sinyal integritas proses penjaminan** — rekaman berpendapatan tinggi dengan status 'Not Verified' = eskalasi bertingkat risiko. Pola 'Not Verified' yang sistematis di seluruh jumlah pinjaman tinggi = kegagalan kontrol proses | Kontrol Penjaminan | PRF-04 |
| `pymnt_plan` | Fitur | **Kontrol status rencana kesulitan** — tanda biner yang harus 'n' untuk semua status pinjaman yang berjalan. 'y' pada pinjaman berjalan/lunas = kesalahan mesin status | Kontrol Alur Kerja | POL-04 |
| `recoveries` | Fitur | **Kontrol integritas pasca-penghapusbukuan** — harus ≥ `collection_recovery_fee`. Pemulihan negatif = kemustahilan aritmetika = temuan P1 | Integritas Transaksi | FIN-09, FIN-11 |
| `member_id` | Kunci penggabungan | **Kontrol keunikan entitas** — harus unik di seluruh rekaman. Duplikat `member_id` = sinyal kecurangan penumpukan pinjaman atau tabrakan basis data | Kontrol Identitas | PRF-01 |
| `earliest_cr_line` | Fitur | **Jangkar kelayakan temporal** — tanggal mulai riwayat kredit harus mendahului tanggal penerbitan pinjaman. Pelanggaran = sinyal fabrikasi rekaman | Kontrol Temporal | PRF-07 |
| `total_acc` | Fitur | **Batas atas hitungan akun** — `open_acc` tidak boleh melebihi `total_acc`. Pelanggaran = kegagalan integritas data biro kredit | Kontrol Sinyal Kredit | CRS-01 |

---

---

# BAGIAN 4 — ARSITEKTUR SISTEM & ALUR DATA

---

## 4.1 Ikhtisar Pipeline Fungsional

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE DATA AFC-CAE v1.1                           │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐ │
│  │  PENYERAPAN     │───►│  GERBANG SKEMA &     │───►│  TATA KELOLA NULL   │ │
│  │  MENTAH         │    │  TIPE DATA           │    │  PDAN / FEN / IM    │ │
│  │  FastAPI POST   │    │  (Fitur Baru v1.1)   │    │  / UCG              │ │
│  │  .csv / .parquet│    │  Sidik Jari Skema    │    │  Klasifikasi        │ │
│  └─────────────────┘    │  dtype Enforcement   │    └──────────┬───────────┘ │
│                         └─────────────────────┘               │             │
│                                   │                           │             │
│                           SCHEMA DRIFT? /                     │             │
│                           DTYPE FAILURE?                      │             │
│                           → ALERT + SOFT_GATE                 │             │
│                                                               ▼             │
│                                                    ┌──────────────────────┐  │
│                                                    │  MESIN PERNYATAAN   │  │
│                                                    │  BERBASIS ATURAN    │  │
│                                                    │  (RBAE)             │  │
│                                                    │  40+ Pemeriksaan    │  │
│                                                    │  FIN/PRF/POL/       │  │
│                                                    │  CRS/STR Modul      │  │
│                                                    └──────────┬───────────┘  │
│                                                               │              │
│                                 ┌─────────────────────────────┤             │
│                                 │                             │             │
│                    Kegagalan P1?                   HITUNG TINGKAT ANOMALI    │
│                    → Karantina                     ├─ < 0,5%: SKENARIO A    │
│                    → Eskalasi                      ├─ 0,5-5%: SKENARIO B    │
│                      Toleransi Nol                └─ > 5%:   SKENARIO C    │
│                                 │                             │             │
│                                 │                             ▼             │
│                                 │                  ┌──────────────────────┐  │
│                                 │                  │  ISOLATION FOREST   │  │
│                                 │                  │  (Sole ML Engine)   │  │
│                                 │                  │  + XAI Explainer    │  │
│                                 │                  │  (Deviation +       │  │
│                                 │                  │   Univariate Score) │  │
│                                 │                  └──────────┬───────────┘  │
│                                 │                             │              │
│                                 └──────────────┬──────────────┘              │
│                                                │                             │
│                                                ▼                             │
│                                     ┌──────────────────────┐                │
│                                     │    ROUTER SKENARIO   │                │
│                                     └──────────┬───────────┘                │
│                  ┌────────────────────────────┬─┴───────────────┐           │
│                  ▼                            ▼                 ▼           │
│       ┌──────────────────┐      ┌──────────────────────┐  ┌────────────────┐│
│       │   SKENARIO A     │      │     SKENARIO B       │  │  SKENARIO C   ││
│       │   ACN + Log      │      │   Pembuatan PFM      │  │  CIR + HALT   ││
│       │   MLflow         │      │   Log MLflow         │  │  Snapshot     ││
│       │   Lanjutkan      │      │   Peringatan 48 jam  │  │  Forensik     ││
│       └──────────────────┘      └──────────────────────┘  └────────────────┘│
│                                                │                             │
│                                                ▼                             │
│                                     ┌──────────────────────┐                │
│                                     │   REGISTRI AUDIT     │                │
│                                     │   MLFLOW             │                │
│                                     │   Param/Metrik/      │                │
│                                     │   Artefak/Tag        │                │
│                                     └──────────────────────┘                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4.2 Spesifikasi Pembuatan PFM & CIR Otomatis

### Memorandum Temuan Awal (PFM) — Pemicu Skenario B

**Bagian Template:**
1. **Blok Header:** ID Eksekusi, stempel waktu, hash dataset, klasifikasi skenario, auditor-yang-bertanggung-jawab (sistem)
2. **Ringkasan Eksekutif:** Tingkat anomali agregat, total rekaman yang gagal, uraian per modul
3. **Tabel Temuan:** Satu baris per pemeriksaan yang gagal; ID pemeriksaan, deskripsi, jumlah kegagalan, tingkat kegagalan, klasifikasi SVS, keparahan
4. **Analisis Segmen:** Grafik kluster temporal; peta panas kegagalan per grade/negara bagian/tujuan
5. **Manifes Karantina:** Daftar ID rekaman yang dikarantina beserta alasan kegagalan
6. **Laporan XAI:** Ringkasan 10 rekaman anomali teratas dengan narasi eksplikasi penuh (dari Metode XAI-1 dan XAI-2)
7. **Tindakan yang Direkomendasikan:** Terisi otomatis berdasarkan ID pemeriksaan yang dipicu dan klasifikasi SVS-nya
8. **Blok Tanda Tangan:** Dihasilkan sistem, dengan ruang untuk tanda tangan peninjauan manusia

### Laporan Insiden Kritis (CIR) — Pemicu Skenario C

**Bagian tambahan di atas PFM:**
- **Konfirmasi Penghentian Pipeline:** Stempel waktu penghentian, sistem yang terpengaruh, catatan inisiasi penelusuran liniage data
- **Rantai Kustodi Forensik:** SHA-256 dari snapshot mentah, jalur penyimpanan, referensi log kontrol akses
- **Daftar Distribusi Eskalasi:** Terisi otomatis dari konfigurasi (CRO, Ketua DGC, Direktur Audit TI, CISO)
- **Penilaian Kewajiban Pelaporan Regulasi:** Daftar periksa kewajiban pelaporan regulasi yang berlaku (SOX, ECOA, persyaratan integritas data tingkat negara bagian)

---

---

# BAGIAN 5 — PERSYARATAN NON-FUNGSIONAL

---

## 5.1 Skalabilitas & Kinerja

| Persyaratan | Spesifikasi | Metode Pengukuran |
|---|---|---|
| **Eksekusi pipeline penuh — 466K rekaman** | ≤ 4 jam ujung-ke-ujung; RBAE saja ≤ 90 detik | Dibandingkan pada instansi cloud standar (4 vCPU, 16GB RAM) dan workstation lokal Linux Mint |
| **Vektorisasi RBAE** | Semua 40+ pemeriksaan pernyataan diimplementasikan sebagai operasi Pandas/NumPy yang divektorisasi. Nol loop Python tingkat-baris dalam logika pernyataan | Gerbang tinjauan kode; pemrofilan dengan `cProfile` |
| **Efisiensi memori** | Penggunaan memori puncak ≤ 4GB untuk dataset 466K × 75 | Pemantauan `memory_profiler` selama CI/CD |
| **Optimasi tipe data** | Penurunan tipe data otomatis pada penyerapan: integer nullable `Int64` untuk kolom hitungan; `float32` untuk fitur non-keuangan di lapisan ML | Suite uji jejak memori |
| **Waktu fitting model** | iForest fit dan skor pada 466K rekaman ≤ 10 menit pada workstation standar | Benchmark dalam pipeline CI/CD |
| **Target skalabilitas** | Arsitektur harus mendukung 2 juta rekaman dengan integrasi Dask (titik integrasi ditentukan) | Spesifikasi uji beban |
| **Pembuatan XAI** | ≤ 2 detik per rekaman yang ditandai; paralelisasi menggunakan `ThreadPoolExecutor` untuk > 1.000 rekaman yang ditandai | Profil benchmark |

---

## 5.2 Keterlacakan & Reproduktibilitas

| Persyaratan | Spesifikasi |
|---|---|
| **Sidik jari dataset** | Hash SHA-256 dari file mentah yang diunggah dihitung dan dicatat sebelum transformasi apa pun. Hash disimpan dalam MLflow, log audit, dan laporan yang dihasilkan |
| **Reproduktibilitas eksekusi** | Diberikan hash dataset yang sama + parameter MLflow yang sama, AFC-CAE harus menghasilkan hasil `assertion_results.json` yang identik secara bit. Diberlakukan melalui seed acak tetap (`random_state=42`) dan urutan pemrosesan deterministik |
| **Ketidakubahan parameter** | Semua nilai ambang batas (tingkat kontaminasi, nilai toleransi, klasifikasi keparahan) dikontrol versinya dalam file konfigurasi (`audit_config_v{N}.yaml`), bukan dikodekan keras. Versi konfigurasi dicatat per eksekusi |
| **Retensi log audit** | Semua log eksekusi disimpan minimal 7 tahun (standar audit keuangan). Penyimpanan tulis-sekali yang tidak dapat diubah untuk artefak CIR |
| **Liniage data** | Setiap transformasi yang diterapkan pada dataset dicatat dengan: kolom masukan, operasi, kolom keluaran, alasan, dan referensi run_id |
| **Otoritas stempel waktu** | Semua stempel waktu dicatat dalam UTC. Tidak ada stempel waktu zona waktu lokal dalam artefak audit |

---

## 5.3 Kemudahan Pemeliharaan & Modularitas

**Prinsip Arsitektur yang Diwajibkan:**

**1. Pemisahan Kepentingan (*Separation of Concerns*):**
Logika bisnis (aturan pernyataan, nilai ambang batas) harus sepenuhnya dipisahkan dari kode infrastruktur (rute FastAPI, klien MLflow). Tidak ada nilai ambang batas yang boleh muncul dalam kode penangan API.

**2. Aturan Berbasis Konfigurasi:**
Semua ambang batas pernyataan, klasifikasi keparahan, dan pemicu eskalasi didefinisikan dalam file konfigurasi YAML berversi (`audit_config_v{N}.yaml`). Tidak ada perubahan aturan yang memerlukan penerapan kode — hanya promosi konfigurasi melalui alur persetujuan tata kelola.

**3. Independensi Modul:**
Setiap modul audit (FIN, PRF, POL, CRS, STR) harus dapat dieksekusi dan diuji secara independen. Menambahkan modul baru tidak boleh memerlukan modifikasi kode modul yang sudah ada.

**4. Struktur Kode:**
```
afc_cae/
├── api/
│   ├── routes/          # Penangan rute FastAPI saja
│   └── middleware/      # Auth, pencatatan log, penanganan kesalahan
├── ingestion/
│   ├── file_reader.py   # Pembaca CSV & Parquet saja (.xlsx dihapus)
│   ├── dtype_gate.py    # Gerbang Konsistensi Tipe Data (Baru v1.1)
│   └── schema_validator.py  # Pemeriksaan sidik jari skema
├── audit_engine/
│   ├── modules/
│   │   ├── fin_module.py        # Rekonsiliasi Keuangan
│   │   ├── prf_module.py        # Profil Peminjam
│   │   ├── pol_module.py        # Kepatuhan Kebijakan
│   │   ├── crs_module.py        # Sinyal Risiko Kredit
│   │   └── str_module.py        # Kepatuhan Struktural
│   ├── null_governance.py       # Pengklasifikasi taksonomi null
│   └── assertion_runner.py      # Orkestrator (tanpa logika bisnis)
├── ml_layer/
│   ├── feature_engineering.py   # Rekayasa fitur + RobustScaler
│   ├── isolation_forest.py      # Sole ML engine (LOF dihapus)
│   ├── xai_explainer.py         # Deviasi Median + Skor Isolasi Univariat (Baru v1.1)
│   └── scenario_router.py       # Logika klasifikasi A/B/C
├── reporting/
│   ├── pfm_generator.py
│   ├── cir_generator.py
│   └── acn_generator.py
├── tracking/
│   └── mlflow_client.py         # Semua interaksi MLflow
├── config/
│   └── audit_config_v1.yaml     # SEMUA ambang batas, aturan, & pemetaan dtype
└── tests/
    ├── unit/                    # Uji unit per pemeriksaan
    ├── integration/             # Uji pipeline penuh
    └── fixtures/                # Dataset sintetis dengan anomali yang diketahui
```

**5. Persyaratan Cakupan Uji:**
- Cakupan uji unit ≥ 90% untuk semua kode modul audit
- Setiap pemeriksaan pernyataan harus memiliki: (a) uji dengan dataset yang lulus, (b) uji dengan dataset yang sengaja gagal, (c) uji kondisi batas
- Uji integrasi: eksekusi pipeline penuh pada dataset fixture sintetis 10.000 rekaman dengan anomali yang disuntikkan secara sengaja, menegaskan klasifikasi skenario yang benar dan pembuatan dokumen
- Uji gerbang tipe data: uji khusus untuk `dtype_gate.py` dengan kolom yang memiliki pencampuran string/numerik dan pola null yang bervariasi

---

## 5.4 Persyaratan Keamanan

| Persyaratan | Spesifikasi |
|---|---|
| **Autentikasi API** | Semua endpoint (kecuali `/health`) memerlukan token bearer JWT + kunci API |
| **Data dalam Transit** | TLS 1.3 minimum untuk semua komunikasi API |
| **Data saat Istirahat** | Snapshot forensik (artefak CIR) dienkripsi saat istirahat (AES-256) |
| **Kontrol Akses** | Akses berbasis peran: `AUDITOR` (baca hasil), `ANALIS` (picu eksekusi), `ADMIN` (ubah konfigurasi). Tidak ada peran yang dapat menghapus log audit |
| **Penyamaran Bidang Sensitif** | `member_id`, `zip_code`, `emp_title` disembunyikan dalam semua keluaran log dan respons API yang tidak aman |
| **Sanitasi Masukan** | Validasi format file dan tipe MIME pada unggahan; pencegahan injeksi CSV diberlakukan |
| **Titik Kait Pemindaian Virus** | Stub dikonfigurasi dalam `file_reader.py` sebagai fungsi yang dapat diaktifkan; dinonaktifkan dalam v1.1 untuk penerapan lokal |

---

---

# BAGIAN 6 — KRITERIA PENERIMAAN & DEFINISI SELESAI

---

## 6.1 Kriteria Penerimaan Tingkat Fitur

| Fitur | Kriteria Penerimaan |
|---|---|
| Gerbang Validasi Skema | Diberikan dataset dengan 1 kolom yang diganti namanya, mesin harus mengembalikan `SCHEMA-DRIFT-ALERT` dalam 10 detik setelah penyerapan tanpa memproses file |
| Gerbang Tipe Data (Baru v1.1) | Diberikan file CSV di mana `delinq_2yrs` berisi campuran integer dan string "N/A", gerbang harus: (a) mendeteksi kegagalan koersi, (b) mencatat `DTYPE_COERCION_FAILURE`, (c) menandai kolom sebagai `TYPE_UNVERIFIED`, (d) melanjutkan dengan kaveat yang sesuai |
| Pengklasifikasi Tata Kelola Null | Diberikan dataset Lending Club, semua 14 kolom FEN harus diklasifikasikan sebagai `FEN: PRE_ACTIVATION` dan semua 3 kolom bersama sebagai `PDAN` — diverifikasi terhadap manifes kebenaran dasar |
| FIN-03 (Pemeriksaan Angsuran) | Diberikan 10 rekaman sintetis dengan angsuran yang dihitung pada tarif bunga yang salah (delta > $1,00), semua 10 harus ditandai. Diberikan 10 rekaman dengan delta $0,50, semua 10 harus lulus |
| Router Skenario | Diberikan dataset dengan tingkat anomali sintetis 6%, mesin harus menghentikan pipeline, menghasilkan CIR, dan mengirimkan notifikasi eskalasi dalam siklus eksekusi |
| Keterlacakan MLflow | Diberikan dua eksekusi identik (file yang sama, konfigurasi yang sama), kedua eksekusi harus menghasilkan artefak `assertion_results.json` yang identik — diverifikasi dengan hash |
| Pembuatan PFM Otomatis | Diberikan pemicu Skenario B, PFM PDF yang valid secara struktural harus dihasilkan dengan semua 8 bagian yang diperlukan terisi dalam siklus eksekusi |
| Keluaran XAI (Baru v1.1) | Untuk setiap rekaman yang ditandai, blok `xai_explanation` harus hadir dalam keluaran `anomaly_scores_with_xai.parquet` dengan: `top_3_anomaly_drivers`, `deviation_profile` dengan `pct_deviation` per fitur, dan `audit_narrative` yang tidak kosong |
| Ketersediaan API | Endpoint `/health` harus mengembalikan `200 OK` dengan latensi ≤ 100ms dalam kondisi tanpa beban |
| Pembatasan Format File (Baru v1.1) | Permintaan unggahan dengan file `.xlsx` harus mengembalikan `415 Unsupported Media Type` dengan pesan kesalahan yang jelas |

---

---

# BAGIAN 7 — DAFTAR RISIKO & ISU TERBUKA

---

## 7.1 Daftar Risiko Produk

| ID Risiko | Deskripsi | Kemungkinan | Dampak | Mitigasi |
|---|---|---|---|---|
| `RISIKO-01` | Tingkat positif palsu dalam lapisan XAI menyebabkan narasi audit yang menyesatkan (misalnya, atribusi driver anomali yang salah) | Sedang | Tinggi | Uji validasi XAI dengan rekaman yang anomalinya sudah diketahui; penambahan catatan kualifikasi pada semua narasi XAI |
| `RISIKO-02` | `BackgroundTasks` FastAPI tidak memberikan jaminan penyelesaian yang kuat; kegagalan proses dapat mengakibatkan eksekusi audit terhenti tanpa notifikasi | Rendah | Tinggi | Implementasikan pencatatan status eksekusi ke file/basis data lokal; tambahkan endpoint heartbeat; dokumentasikan jalur migrasi ke Celery untuk versi produksi |
| `RISIKO-03` | Pergeseran skema dalam sistem sumber menyebabkan misklasifikasi FEN/PDAN massal | Rendah | Kritis | Penyematan versi skema; peringatan pergeseran sebelum pemrosesan; alur kerja pengesampingan manual |
| `RISIKO-04` | CIR yang dihasilkan otomatis memicu kewajiban pelaporan kepatuhan — tinjauan hukum diperlukan sebelum notifikasi Skenario C dirutekan secara eksternal | Sedang | Tinggi | Gerbang persetujuan hukum/kepatuhan sebelum penerapan produksi |
| `RISIKO-05` | Hash kriptografis dataset berubah dengan perbedaan spasi/pengkodean di seluruh sistem, merusak reproduktibilitas | Rendah | Sedang | Format serialisasi kanonik ditentukan (UTF-8, akhiran baris LF) sebelum hashing |
| `RISIKO-06` | Pembuatan XAI univariat (Metode XAI-2) memiliki overhead komputasi untuk dataset dengan > 5.000 rekaman yang ditandai dalam Skenario C | Sedang | Sedang | Batasi XAI-2 pada top 500 rekaman yang paling menyimpang per run Skenario C; catat keluarnya sebagai `XAI_PARTIAL_COVERAGE` |

---

## 7.2 Isu Terbuka

| ID Isu | Deskripsi | Pemilik | Target Resolusi |
|---|---|---|---|
| `ISU-01` | PRF-08 (validasi ZIP-terhadap-Negara) memerlukan tabel referensi pencarian; sumber belum dikonfirmasi | Rekayasa Data | Sprint 2 |
| `ISU-02` | Logika kluster temporal BDFF — ambang batas untuk "pengelompokan" belum didefinisikan secara formal | Pemimpin Audit TI | Sprint 3 |
| `ISU-03` | Daftar periksa pengungkapan regulasi CIR — tinjauan hukum terhadap kewajiban kontrol TI SOX yang berlaku sedang menunggu | Hukum / Kepatuhan | Pra-peluncuran |
| `ISU-04` | Hosting server MLflow: keputusan lokal vs. terkelola (Databricks) menunggu tinjauan infrastruktur | Rekayasa Platform | Sprint 1 |
| `ISU-05` | Format output narasi `audit_narrative` XAI belum dikonfirmasi sebagai teks bebas atau terstruktur (JSON vs string) — mempengaruhi desain template PFM | Manajer Produk | Sprint 2 |

---

---

# BAGIAN 8 — LAMPIRAN

---

## Lampiran A — Penyelarasan Kerangka Regulasi

| Kerangka Kerja | Kontrol AFC-CAE yang Berlaku |
|---|---|
| **COSO Kontrol Internal — Kerangka Terpadu** | Mesin pernyataan berbasis aturan = Aktivitas Kontrol; keterlacakan MLflow = Aktivitas Pemantauan; PFM/CIR = Informasi & Komunikasi |
| **SR 11-7 (Manajemen Risiko Model)** | POL-10 (inversi grade/tarif) secara langsung mengimplementasikan validasi model penetapan harga SR 11-7; versi MLflow mendukung persyaratan inventarisasi model |
| **DAMA DMBOK** | Taksonomi tata kelola null (PDAN/FEN/IM/UCG) mengimplementasikan dimensi Kualitas Data DMBOK; sidik jari skema mengimplementasikan manajemen Arsitektur Data |
| **Kontrol Umum TI SOX** | Log audit penuh dengan retensi yang tidak dapat diubah; kontrol akses pada perubahan konfigurasi; keterlacakan kriptografis artefak audit |
| **ECOA / FCRA** | PRF-05 (kelengkapan aplikasi bersama); PRF-08 (integritas geografis); PRF-04 (kecukupan verifikasi pendapatan) |

---

## Lampiran B — Referensi Klasifikasi Keparahan

| Tingkat | Kode | Definisi | Tindakan Pipeline | SLA Respons |
|---|---|---|---|---|
| Kritis | P1 | Kemustahilan matematis, sinyal kecurangan, atau kegagalan kontrol toleransi nol | Karantina segera; eskalasi tanpa syarat | Segera |
| Tinggi | P2 | Kelemahan kontrol sistemik, kesenjangan regulasi, atau masalah integritas data signifikan | Tandai untuk investigasi; sertakan dalam PFM jika Skenario B | 24–48 jam |
| Sedang | P3 | Varians kualitas data, pelanggaran kosakata, atau sinyal peningkatan proses | Catat dan beri anotasi; sertakan dalam ACN | 5 hari kerja |
| Rendah | P4 | Temuan informasional, kesenjangan dokumentasi | Catat saja | Siklus audit berikutnya |

---

## Lampiran C — Glosarium

| Istilah | Definisi |
|---|---|
| **SVS** (*System Vulnerability Signal*) | Sinyal Kerentanan Sistem — anomali data yang diklasifikasikan berdasarkan jenis dan keparahan sebagai indikator kegagalan sistem, proses, atau integritas |
| **RBAE** (*Rule-Based Assertion Engine*) | Mesin Pernyataan Berbasis Aturan — lapisan pemeriksaan deterministik yang memvalidasi pernyataan matematis dan logis lintas kolom |
| **PDAN** (*Policy-Driven Architecture Null*) | Null Arsitektur Berbasis Kebijakan — pola null yang secara struktural benar berdasarkan keputusan kebijakan yang terdokumentasi |
| **FEN** (*Feature Epoch Null*) | Null Epoch Fitur — pola null yang disebabkan oleh fitur yang belum aktif pada periode pembuatan dataset |
| **IM** (*Informative Missingness*) | Ketidakhadiran Informatif — pola null yang membawa sinyal positif yang dapat diinterpretasikan |
| **UCG** (*Underwriting Completeness Gap*) | Kesenjangan Kelengkapan Penjaminan — null dalam bidang yang seharusnya wajib menurut kebijakan penjaminan |
| **BDFF** (*Bureau Data Fetch Failure*) | Kegagalan Penarikan Data Biro — pola null yang mengindikasikan non-respons API biro kredit untuk subset rekaman |
| **PFM** (*Preliminary Findings Memorandum*) | Memorandum Temuan Awal — dokumen Skenario B yang dihasilkan otomatis yang merangkum temuan zona pantau untuk tinjauan manajemen |
| **CIR** (*Critical Incident Report*) | Laporan Insiden Kritis — dokumen Skenario C yang dihasilkan otomatis untuk kegagalan sistemik berkeparahan P1 yang memerlukan eskalasi segera |
| **ACN** (*Audit Completion Notice*) | Pemberitahuan Penyelesaian Audit — catatan penyelesaian eksekusi Skenario A yang mengonfirmasi tidak diperlukan eskalasi |
| **XAI** (*Explainable AI*) | Kecerdasan Buatan yang Dapat Dijelaskan — mekanisme yang menghasilkan penjelasan yang dapat diinterpretasikan manusia tentang mengapa model AI menandai rekaman tertentu sebagai anomali |
| **iForest** (*Isolation Forest*) | Algoritma deteksi anomali tanpa pengawasan (Liu dkk., 2008) yang digunakan sebagai satu-satunya mesin ML dalam AFC-CAE v1.1 |
| **RobustScaler** | Penskalaan fitur berbasis median/IQR dari scikit-learn; dipilih karena ketahanannya terhadap nilai ekstrem dalam distribusi data keuangan |
| **Schema Drift** | Pergeseran Skema — kondisi di mana dataset yang diserap menyimpang dari definisi skema yang terdaftar (nama kolom, tipe data, jumlah kolom) |
| **dtype** | Tipe data (*data type*) kolom dalam Pandas/NumPy; penerapan yang tepat adalah fondasi dari Gerbang Konsistensi Tipe Data dalam v1.1 |
| **BackgroundTasks** | Mekanisme asinkronus bawaan FastAPI untuk mengeksekusi fungsi setelah mengembalikan respons HTTP; menggantikan Celery dalam v1.1 untuk penerapan workstation lokal |

---

*Akhir Dokumen — PRD AFC-CAE v1.1*
*Klasifikasi: INTERNAL — TERBATAS | Praktik Tata Kelola Data & Jaminan Mutu*
*Tinjauan Terjadwal Berikutnya: [TANGGAL + 90 hari]*
*Disiapkan oleh: Kantor Manajemen Produk Utama, Praktik Tata Kelola Data*
