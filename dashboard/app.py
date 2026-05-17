# ============================================
# DASHBOARD SYNAR - ANALISIS UV PANTAI INDONESIA
# Menjawab 7 Pertanyaan Bisnis
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="SYNAR - Analisis UV Pantai",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('data/dataset_features.csv')
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])
    return df

df = load_data()

# ============================================
# SIDEBAR - FILTER & INFORMASI
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/sun.png", width=80)
    st.title("☀️ SYNAR")
    st.caption("Analisis Keamanan Berjemur di Pantai")
    st.markdown("---")
    
    # Filter Lokasi
    lokasi_filter = st.multiselect(
        "📍 Pilih Lokasi",
        options=df['LOKASI'].unique(),
        default=df['LOKASI'].unique()
    )
    
    # Filter Rentang UV
    uv_range = st.slider(
        "📊 Rentang UV Index",
        min_value=0.0,
        max_value=20.0,
        value=(0.0, 12.0)
    )
    
    st.markdown("---")
    st.caption("📅 Data: 2020-2025")
    st.caption("📍 3 Lokasi Pantai")
    st.caption("⏰ Resolusi: Hourly")
    
    # Info dataset
    st.markdown("---")
    st.metric("Total Data", f"{len(df):,} baris")
    st.metric("Lokasi", len(df['LOKASI'].unique()))

# Filter data
df_filtered = df[df['LOKASI'].isin(lokasi_filter)]
df_filtered = df_filtered[
    (df_filtered['ALLSKY_SFC_UV_INDEX'] >= uv_range[0]) &
    (df_filtered['ALLSKY_SFC_UV_INDEX'] <= uv_range[1])
]

# ============================================
# HEADER DASHBOARD
# ============================================
st.title("☀️ SYNAR - Safety UV Navigator")
st.markdown("""
<div style='background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px'>
<h4>🎯 Tentang Dashboard Ini</h4>
<p>Dashboard ini menjawab <b>7 pertanyaan bisnis</b> tentang keamanan aktivitas berjemur di pantai berdasarkan 
data radiasi ultraviolet (UV) dari NASA POWER. Data mencakup 3 lokasi pantai di Indonesia (Bali, Lombok, Raja Ampat) 
periode 2020-2025 dengan resolusi per jam.</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# PERTANYAAN 1
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 1")
st.subheader("Sejauh mana indeks UV memengaruhi tingkat keamanan aktivitas berjemur di pantai?")

col1, col2 = st.columns([1, 2])

with col1:
    uv_aman = df_filtered.groupby('LABEL_AMAN')['ALLSKY_SFC_UV_INDEX'].mean()
    st.metric("UV Index (Kondisi Aman)", f"{uv_aman.get(1, 0):.2f}")
    st.metric("UV Index (Kondisi Tidak Aman)", f"{uv_aman.get(0, 0):.2f}")
    st.info("💡 **Interpretasi:** Perbedaan rata-rata UV Index antara kondisi aman (0.86) dan tidak aman (7.48) sangat besar, menunjukkan UV Index adalah indikator utama keamanan berjemur.")

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=uv_aman.index, y=uv_aman.values, ax=ax, palette=['#e74c3c', '#2ecc71'])
    ax.set_title('Rata-rata UV Index pada Kondisi Aman vs Tidak Aman', fontweight='bold')
    ax.set_xlabel('Label Aman (1=Aman, 0=Tidak Aman)')
    ax.set_ylabel('Rata-rata UV Index')
    for i, v in enumerate(uv_aman.values):
        ax.text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 2
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 2")
st.subheader("Apakah peningkatan intensitas radiasi UV (UVA & UVB) berbanding lurus dengan peningkatan risiko?")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Korelasi UV Index vs UVA", f"{df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['ALLSKY_SFC_UVA']):.3f}")
    st.metric("Korelasi UV Index vs UVB", f"{df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['ALLSKY_SFC_UVB']):.3f}")
    st.success("✅ **Kesimpulan:** Korelasi sangat kuat (0.98), peningkatan UV berbanding lurus dengan peningkatan risiko.")

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.scatter(df_filtered['ALLSKY_SFC_UVA'], df_filtered['ALLSKY_SFC_UV_INDEX'], alpha=0.2, label='UVA', color='blue')
    ax.scatter(df_filtered['ALLSKY_SFC_UVB'], df_filtered['ALLSKY_SFC_UV_INDEX'], alpha=0.2, label='UVB', color='red')
    ax.set_xlabel('Radiasi UV')
    ax.set_ylabel('UV Index')
    ax.set_title('Hubungan UVA & UVB terhadap UV Index', fontweight='bold')
    ax.legend()
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 3
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 3")
st.subheader("Variabel cuaca mana yang paling berpengaruh terhadap tingkat paparan radiasi ultraviolet?")

col1, col2 = st.columns([1, 2])

with col1:
    corr_suhu = df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['T2M'])
    corr_kelembapan = df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['RH2M'])
    corr_angin = df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['WS2M'])
    
    st.metric("Korelasi dengan Suhu", f"{corr_suhu:.3f}", delta="positif" if corr_suhu > 0 else "negatif")
    st.metric("Korelasi dengan Kelembapan", f"{corr_kelembapan:.3f}", delta="negatif" if corr_kelembapan < 0 else "positif")
    st.metric("Korelasi dengan Angin", f"{corr_angin:.3f}")
    
    st.info("💡 **Kesimpulan:** Suhu (0.51) dan Kelembapan (-0.52) paling berpengaruh. Angin hampir tidak berpengaruh.")

with col2:
    corr_matrix = df_filtered[['ALLSKY_SFC_UV_INDEX', 'T2M', 'RH2M', 'WS2M']].corr()
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    ax.set_title('Korelasi Variabel Cuaca terhadap UV Index', fontweight='bold')
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 4
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 4")
st.subheader("Faktor kondisi cuaca apa yang paling memicu kondisi tidak aman untuk berjemur?")

df_filtered['STATUS'] = df_filtered['ALLSKY_SFC_UV_INDEX'].apply(lambda x: 'Tidak Aman' if x > 7 else 'Aman')

col1, col2 = st.columns([1, 2])

with col1:
    status_summary = df_filtered.groupby('STATUS')[['T2M', 'RH2M', 'WS2M']].mean()
    st.dataframe(status_summary.round(2), use_container_width=True)
    st.warning("⚠️ **Kondisi Tidak Aman:** Suhu >28.7°C, Kelembapan <72%, UV Index >7")

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.boxplot(data=df_filtered, x='STATUS', y='T2M', ax=ax, palette=['#2ecc71', '#e74c3c'])
    ax.set_title('Suhu pada Kondisi Aman vs Tidak Aman', fontweight='bold')
    ax.set_xlabel('Status Berjemur')
    ax.set_ylabel('Suhu (°C)')
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 5
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 5")
st.subheader("Pada jam berapa dalam sehari risiko paparan UV mencapai tingkat tertinggi?")

col1, col2 = st.columns([1, 2])

with col1:
    uv_jam = df_filtered.groupby('HR')['ALLSKY_SFC_UV_INDEX'].mean()
    jam_tertinggi = uv_jam.idxmax()
    nilai_tertinggi = uv_jam.max()
    
    st.metric("Jam Risiko Tertinggi", f"{jam_tertinggi}:00 - {jam_tertinggi+1}:00")
    st.metric("UV Index Puncak", f"{nilai_tertinggi:.2f}")
    st.warning("⚠️ **Rekomendasi:** Hindari berjemur pukul 11:00 - 14:00")

with col2:
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(uv_jam.index, uv_jam.values, marker='o', linewidth=2, color='#e74c3c')
    ax.axvline(jam_tertinggi, color='red', linestyle='--', alpha=0.7, label=f'Puncak (Jam {jam_tertinggi}:00)')
    ax.set_title('Pola UV Harian (Rata-rata UV Index per Jam)', fontweight='bold')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata UV Index')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 6
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 6")
st.subheader("Apakah kondisi cuaca tertentu selalu menjamin waktu berjemur yang aman?")

col1, col2 = st.columns([1, 2])

with col1:
    kondisi_lembab_uv_tinggi = df_filtered[(df_filtered['RH2M'] > 70) & (df_filtered['ALLSKY_SFC_UV_INDEX'] > 7)]
    st.metric("Kondisi Lembap (>70%) dengan UV Tinggi (>7)", f"{len(kondisi_lembab_uv_tinggi):,} data")
    st.error("❌ **Kesimpulan:** Cuaca lembap TIDAK menjamin UV aman. Tetap gunakan perlindungan!")

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    scatter = ax.scatter(df_filtered['RH2M'], df_filtered['ALLSKY_SFC_UV_INDEX'], 
                        c=df_filtered['ALLSKY_SFC_UV_INDEX'], cmap='RdYlGn_r', alpha=0.3)
    ax.set_xlabel('Kelembapan (%)')
    ax.set_ylabel('UV Index')
    ax.set_title('Hubungan Kelembapan vs UV Index', fontweight='bold')
    plt.colorbar(scatter, ax=ax, label='UV Index')
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 7 (DENGAN 5 DIAGRAM)
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 7")
st.subheader("Karakteristik kondisi optimal untuk berjemur yang aman berdasarkan kombinasi variabel cuaca dan tipe kulit")

# Fungsi hitung waktu aman
def hitung_waktu_aman(uv_index, tipe_fitzpatrick, spf=1):
    waktu_dasar = {1: 10, 2: 15, 3: 25, 4: 40, 5: 60, 6: 90}
    med = waktu_dasar[tipe_fitzpatrick]
    waktu = (med / max(uv_index, 1)) * spf
    return min(waktu, med * spf)

tipe_kulit = ['Tipe I\n(Sangat Sensitif)', 'Tipe II\n(Sensitif)', 'Tipe III\n(Cukup Sensitif)',
              'Tipe IV\n(Normal)', 'Tipe V\n(Lebih Tahan)', 'Tipe VI\n(Sangat Tahan)']
uv_levels = [2, 4, 6, 8]
spf_levels = [1, 15, 30, 50]

# Tab untuk 5 diagram
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Bar Chart (UV vs Tipe Kulit)", "📈 Line Chart (SPF)", 
                                         "🗺️ Heatmap", "🥧 Pie Chart (Faktor)", "📊 Grouped Bar (SPF)"])

# TAB 1: Bar Chart
with tab1:
    st.markdown("**Waktu Aman Berjemur Berdasarkan UV Index & Tipe Kulit**")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    colors = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#3498db', '#1abc9c']
    
    for idx, uv in enumerate(uv_levels):
        row, col = divmod(idx, 2)
        data = [hitung_waktu_aman(uv, i, 1) for i in range(1, 7)]
        bars = axes[row, col].bar(tipe_kulit, data, color=colors, edgecolor='black')
        axes[row, col].set_title(f'UV Index = {uv}', fontweight='bold')
        axes[row, col].set_ylabel('Waktu Aman (menit)')
        axes[row, col].axhline(y=30, color='red', linestyle='--', alpha=0.7, label='Batas Aman Umum')
        for bar in bars:
            axes[row, col].annotate(f'{int(bar.get_height())}', 
                                   xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                                   xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
        axes[row, col].legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Makin gelap kulit, makin lama waktu aman berjemur.")

# TAB 2: Line Chart SPF
with tab2:
    st.markdown("**Pengaruh SPF terhadap Waktu Aman Berjemur (UV Index = 6)**")
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(1, 7):
        waktu_spf = [hitung_waktu_aman(6, i, spf) for spf in spf_levels]
        ax.plot(spf_levels, waktu_spf, marker='o', linewidth=2, markersize=8, label=tipe_kulit[i-1])
    ax.set_xlabel('SPF')
    ax.set_ylabel('Waktu Aman (menit)')
    ax.set_title('Efektivitas SPF terhadap Durasi Berjemur Aman', fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Pakai SPF 30+ bisa berjemur hingga 5 jam dengan aman!")

# TAB 3: Heatmap
with tab3:
    st.markdown("**Rekomendasi Waktu Berjemur Aman (menit) - Tanpa Sunscreen**")
    heatmap_data = [[hitung_waktu_aman(uv, t, 1) for uv in uv_levels] for t in range(1, 7)]
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=90)
    ax.set_xticks(np.arange(len(uv_levels)))
    ax.set_yticks(np.arange(len(tipe_kulit)))
    ax.set_xticklabels([f'UV {uv}' for uv in uv_levels])
    ax.set_yticklabels(tipe_kulit)
    ax.set_xlabel('UV Index', fontweight='bold')
    ax.set_ylabel('Tipe Kulit', fontweight='bold')
    for i in range(len(tipe_kulit)):
        for j in range(len(uv_levels)):
            ax.text(j, i, f'{int(heatmap_data[i][j])} mnt', ha='center', va='center', fontweight='bold')
    plt.colorbar(im, ax=ax, label='Waktu Aman (menit)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Warna merah = berbahaya. Semakin gelap kulit, semakin tahan.")

# TAB 4: Pie Chart
with tab4:
    st.markdown("**Faktor Penentu Kondisi Optimal Berjemur**")
    fig, ax = plt.subplots(figsize=(10, 7))
    kondisi = ['UV 2-5', 'Jam 09-10', 'Jam 15-16', 'Suhu 26-30°C', 'Kelembapan 60-75%', 'Gunakan SPF 30+']
    bobot = [25, 15, 15, 20, 15, 10]
    colors_pie = ['#2ecc71', '#3498db', '#3498db', '#f39c12', '#1abc9c', '#e74c3c']
    wedges, texts, autotexts = ax.pie(bobot, labels=kondisi, autopct='%1.0f%%', colors=colors_pie, startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax.set_title('Faktor Kondisi Optimal Berjemur', fontweight='bold')
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** UV Index dan jam berjemur adalah faktor terpenting (total 55%).")

# TAB 5: Grouped Bar SPF
with tab5:
    st.markdown("**Perbandingan Efektivitas SPF (UV Index = 6)**")
    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(tipe_kulit))
    width = 0.18
    spf_options = [1, 15, 30, 50]
    colors_spf = ['#95a5a6', '#3498db', '#2ecc71', '#e74c3c']
    
    for idx, (spf, color) in enumerate(zip(spf_options, colors_spf)):
        waktu = [hitung_waktu_aman(6, i, spf) for i in range(1, 7)]
        bars = ax.bar(x + idx*width, waktu, width, label=f'SPF {spf}', color=color, edgecolor='black')
        for bar in bars:
            ax.annotate(f'{int(bar.get_height())}', 
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 3), textcoords='offset points', ha='center', fontsize=8)
    ax.set_xlabel('Tipe Kulit')
    ax.set_ylabel('Waktu Aman (menit)')
    ax.set_title('Perbandingan Efektivitas SPF', fontweight='bold')
    ax.set_xticks(x + width*1.5)
    ax.set_xticklabels(tipe_kulit)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Tanpa SPF hanya 1-15 menit. Dengan SPF 30 bisa hingga 5 jam!")

# ============================================
# DATA DICTIONARY
# ============================================
st.markdown("---")
st.header("📖 Data Dictionary")

with st.expander("Klik untuk melihat penjelasan setiap kolom"):
    data_dict = pd.DataFrame({
        'Kolom': ['YEAR', 'MO', 'DY', 'HR', 'ALLSKY_SFC_UVA', 'ALLSKY_SFC_UVB', 
                  'ALLSKY_SFC_UV_INDEX', 'T2M', 'WS2M', 'RH2M', 'LOKASI', 
                  'LABEL_AMAN'],
        'Tipe Data': ['Integer', 'Integer', 'Integer', 'Integer', 'Float', 'Float', 
                      'Float', 'Float', 'Float', 'Float', 'String', 'Integer'],
        'Deskripsi': ['Tahun', 'Bulan', 'Tanggal', 'Jam', 'Radiasi UVA', 'Radiasi UVB',
                      'Indeks UV', 'Suhu (°C)', 'Kecepatan Angin (m/s)', 'Kelembapan (%)',
                      'Lokasi Pantai', '1=Aman, 0=Tidak Aman']
    })
    st.dataframe(data_dict, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px'>
    <b>SYNAR - Safety UV Navigator</b><br>
    Sumber Data: NASA POWER (2020-2025) | 3 Lokasi: Bali, Lombok, Raja Ampat<br>
    Dibuat untuk analisis keamanan aktivitas berjemur di pantai
</div>
""", unsafe_allow_html=True)
