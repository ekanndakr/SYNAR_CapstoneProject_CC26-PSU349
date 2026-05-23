# Feature Specification — SYNAR
**Author:** Satriyo | **Diserahkan ke:** Aikylla (Random Forest Regressor)
**Update:** Berdasarkan review Aikylla

## Target Model
| Nama | Tipe | Satuan | Range | Keterangan |
|------|------|--------|-------|------------|
| DURASI_AMAN_MENIT | float | menit | 0–120 | Output Random Forest Regressor |

> Label aman/tidak TIDAK dihasilkan model.
> Diturunkan di serving API: if durasi < 10 → Tidak Aman
> SKIN_TYPE tidak masuk fitur model — penyesuaian di serving API

## Formula DURASI_AMAN_MENIT
MED_BASELINE = 4.5 J/m² (Fitzpatrick Type III)
DURASI = MED_BASELINE / (UV_INDEX × 0.0025 × 60)
Cap maksimal: 120 menit

## Threshold Aman (Konsisten di seluruh pipeline)
DURASI_AMAN_MENIT >= 10 menit → Aman (1)
DURASI_AMAN_MENIT <  10 menit → Tidak Aman (0)

## Fitur Training (X)
| Nama Fitur | Tipe | Satuan | Sumber |
|------------|------|--------|--------|
| ALLSKY_SFC_UV_INDEX | float | W m-2 x 40 | NASA POWER |
| ALLSKY_SFC_UVA | float | MJ/hr | NASA POWER |
| ALLSKY_SFC_UVB | float | MJ/hr | NASA POWER |
| T2M | float | °C | NASA POWER |
| WS2M | float | m/s | NASA POWER |
| RH2M | float | % | NASA POWER |
| HR | int | jam (0–23) | NASA POWER |
| BULAN | int | 1–12 | Feature Engineering |

## Split Dataset — Time-based 80/10/10
| Split | Proporsi | Periode |
|-------|----------|---------|
| Train | 80% | 2020 – mid 2024 |
| Validation | 10% | mid 2024 – late 2024 |
| Test | 10% | late 2024 – 2025 |

Metode: Time-based split (bukan random shuffle)
Alasan: Data time series — random shuffle menyebabkan data leakage
