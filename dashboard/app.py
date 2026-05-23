# ============================================
# DASHBOARD SYNAR - ANALISIS UV PANTAI INDONESIA
# Menjawab 7 Pertanyaan Bisnis
# UPDATE: Target = DURASI_AMAN_MENIT, Threshold >= 10 menit
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
    df = pd.read_csv('dataset_features.csv')
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

    # [UPDATE] Metric rata-rata durasi aman per lokasi
    st.markdown("---")
    st.markdown("**⏱️ Rata-rata Durasi Aman per Lokasi**")
    for lokasi in df['LOKASI'].unique():
        rata = df[df['LOKASI'] == lokasi]['DURASI_AMAN_MENIT'].mean()
        st.caption(f"📍 {lokasi}: **{rata:.1f} menit**")

# Filter data
df_filtered = df[df['LOKASI'].isin(lokasi_filter)]
df_filtered = df_filtered[
    (df_filtered['ALLSKY_SFC_UV_INDEX'] >= uv_range[0]) &
    (df_filtered['ALLSKY_SFC_UV_INDEX'] <= uv_range[1])
].copy()

# [UPDATE] STATUS dari DURASI_AMAN_MENIT, threshold >= 10 menit (konsisten dengan serving API)
df_filtered['STATUS'] = df_filtered['DURASI_AMAN_MENIT'].apply(
    lambda x: 'Aman' if x >= 10 else 'Tidak Aman'
)

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
<p><b>Target Model:</b> <code>DURASI_AMAN_MENIT</code> (float, 0–120 menit) | 
<b>Threshold Aman:</b> durasi ≥ 10 menit → Aman</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# PERTANYAAN 1
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 1")
st.subheader("Sejauh mana indeks UV memengaruhi durasi aman berjemur di pantai?")

col1, col2 = st.columns([1, 2])

with col1:
    # [UPDATE] groupby STATUS dari DURASI_AMAN_MENIT
    uv_status = df_filtered.groupby('STATUS')['ALLSKY_SFC_UV_INDEX'].mean()
    durasi_status = df_filtered.groupby('STATUS')['DURASI_AMAN_MENIT'].mean()

    st.metric("UV Index (Kondisi Aman)", f"{uv_status.get('Aman', 0):.2f}")
    st.metric("UV Index (Kondisi Tidak Aman)", f"{uv_status.get('Tidak Aman', 0):.2f}")
    st.metric("Rata-rata Durasi Aman", f"{durasi_status.get('Aman', 0):.1f} menit")
    st.info("💡 **Interpretasi:** Semakin tinggi UV Index, semakin pendek durasi aman berjemur. UV Index adalah indikator utama keamanan berjemur.")

with col2:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot UV Index per status
    uv_plot = df_filtered.groupby('STATUS')['ALLSKY_SFC_UV_INDEX'].mean()
    colors = ['#2ecc71' if s == 'Aman' else '#e74c3c' for s in uv_plot.index]
    axes[0].bar(uv_plot.index, uv_plot.values, color=colors, edgecolor='white')
    axes[0].set_title('Rata-rata UV Index\nper Status Berjemur', fontweight='bold')
    axes[0].set_ylabel('Rata-rata UV Index')
    for i, v in enumerate(uv_plot.values):
        axes[0].text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')

    # Plot durasi per status
    dur_plot = df_filtered.groupby('STATUS')['DURASI_AMAN_MENIT'].mean()
    colors2 = ['#2ecc71' if s == 'Aman' else '#e74c3c' for s in dur_plot.index]
    axes[1].bar(dur_plot.index, dur_plot.values, color=colors2, edgecolor='white')
    axes[1].set_title('Rata-rata Durasi Aman\nper Status Berjemur', fontweight='bold')
    axes[1].set_ylabel('Rata-rata Durasi (menit)')
    for i, v in enumerate(dur_plot.values):
        axes[1].text(i, v + 0.5, f'{v:.1f} mnt', ha='center', fontweight='bold')

    plt.tight_layout()
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
    st.metric("Korelasi UV Index vs Durasi", f"{df_filtered['ALLSKY_SFC_UV_INDEX'].corr(df_filtered['DURASI_AMAN_MENIT']):.3f}")
    st.success("✅ **Kesimpulan:** Korelasi UV vs UVA/UVB sangat kuat (>0.98). UV berbanding terbalik dengan durasi aman (korelasi negatif kuat).")

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
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
    st.info("💡 **Kesimpulan:** Suhu dan Kelembapan paling berpengaruh. Angin hampir tidak berpengaruh terhadap UV Index.")

with col2:
    corr_matrix = df_filtered[['ALLSKY_SFC_UV_INDEX', 'T2M', 'RH2M', 'WS2M']].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
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

col1, col2 = st.columns([1, 2])

with col1:
    # [UPDATE] STATUS dari DURASI_AMAN_MENIT, bukan hardcode UV > 7
    status_summary = df_filtered.groupby('STATUS')[['T2M', 'RH2M', 'WS2M', 'DURASI_AMAN_MENIT']].mean()
    st.dataframe(status_summary.round(2), use_container_width=True)
    st.warning("⚠️ **Threshold:** Durasi < 10 menit → Tidak Aman (konsisten dengan serving API)")

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
    palette = {'Aman': '#2ecc71', 'Tidak Aman': '#e74c3c'}
    sns.boxplot(data=df_filtered, x='STATUS', y='T2M', ax=ax, palette=palette)
    ax.set_title('Distribusi Suhu pada Kondisi Aman vs Tidak Aman', fontweight='bold')
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
    durasi_jam = df_filtered.groupby('HR')['DURASI_AMAN_MENIT'].mean()
    jam_tertinggi = uv_jam.idxmax()
    nilai_tertinggi = uv_jam.max()
    durasi_terendah = durasi_jam.min()

    st.metric("Jam Risiko Tertinggi", f"{jam_tertinggi}:00 - {jam_tertinggi+1}:00")
    st.metric("UV Index Puncak", f"{nilai_tertinggi:.2f}")
    st.metric("Durasi Aman Terendah", f"{durasi_terendah:.1f} menit")
    st.warning("⚠️ **Rekomendasi:** Hindari berjemur pukul 11:00 - 14:00")

with col2:
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # UV per jam
    axes[0].plot(uv_jam.index, uv_jam.values, marker='o', linewidth=2, color='#e74c3c')
    axes[0].axvline(jam_tertinggi, color='red', linestyle='--', alpha=0.7, label=f'Puncak (Jam {jam_tertinggi}:00)')
    axes[0].set_title('Pola UV Harian (Rata-rata UV Index per Jam)', fontweight='bold')
    axes[0].set_ylabel('Rata-rata UV Index')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Durasi aman per jam
    axes[1].plot(durasi_jam.index, durasi_jam.values, marker='o', linewidth=2, color='#2ecc71')
    axes[1].axhline(10, color='red', linestyle='--', alpha=0.7, label='Threshold Aman (10 menit)')
    axes[1].set_title('Rata-rata Durasi Aman per Jam', fontweight='bold')
    axes[1].set_xlabel('Jam')
    axes[1].set_ylabel('Durasi Aman (menit)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
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
    # [UPDATE] Pakai DURASI_AMAN_MENIT < 10 untuk tidak aman
    kondisi_lembab_tidak_aman = df_filtered[
        (df_filtered['RH2M'] > 70) & (df_filtered['DURASI_AMAN_MENIT'] < 10)
    ]
    pct_tidak_aman = len(kondisi_lembab_tidak_aman) / len(df_filtered[df_filtered['RH2M'] > 70]) * 100
    st.metric("Kondisi Lembap (>70%) tapi Tidak Aman", f"{len(kondisi_lembab_tidak_aman):,} data")
    st.metric("Persentase", f"{pct_tidak_aman:.1f}%")
    st.error("❌ **Kesimpulan:** Cuaca lembap TIDAK menjamin durasi aman. Tetap cek UV Index!")

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(df_filtered['RH2M'], df_filtered['DURASI_AMAN_MENIT'],
                        c=df_filtered['ALLSKY_SFC_UV_INDEX'], cmap='RdYlGn_r', alpha=0.3)
    ax.axhline(10, color='red', linestyle='--', alpha=0.8, label='Threshold Aman (10 menit)')
    ax.set_xlabel('Kelembapan (%)')
    ax.set_ylabel('Durasi Aman (menit)')
    ax.set_title('Hubungan Kelembapan vs Durasi Aman Berjemur', fontweight='bold')
    ax.legend()
    plt.colorbar(scatter, ax=ax, label='UV Index')
    st.pyplot(fig)
    plt.close()

# ============================================
# PERTANYAAN 7 (DENGAN 5 DIAGRAM)
# ============================================
st.markdown("---")
st.header("📌 Pertanyaan 7")
st.subheader("Karakteristik kondisi optimal untuk berjemur yang aman berdasarkan kombinasi variabel cuaca dan tipe kulit")

# [UPDATE] Formula SED konsisten dengan pipeline
def hitung_waktu_aman_sed(uv_index, fitzpatrick_factor=1.0):
    """
    Formula SED (Standard Erythemal Dose)
    Baseline: Fitzpatrick Type III (MED = 4.5 J/m²)
    fitzpatrick_factor: multiplier per tipe kulit
    """
    MED_BASELINE = 4.5
    if uv_index <= 0:
        return 120.0
    durasi = round(MED_BASELINE / (uv_index * 0.0025 * 60), 1) * fitzpatrick_factor
    return min(durasi, 120.0)

# Fitzpatrick factor relatif terhadap Type III (baseline = 1.0)
fitzpatrick_factors = {1: 0.4, 2: 0.6, 3: 1.0, 4: 1.6, 5: 2.4, 6: 3.6}
tipe_kulit = ['Tipe I\n(Sangat Sensitif)', 'Tipe II\n(Sensitif)', 'Tipe III\n(Cukup Sensitif)',
              'Tipe IV\n(Normal)', 'Tipe V\n(Lebih Tahan)', 'Tipe VI\n(Sangat Tahan)']
uv_levels = [2, 4, 6, 8]
spf_levels = [1, 15, 30, 50]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Bar Chart (UV vs Tipe Kulit)",
    "📈 Line Chart (SPF)",
    "🗺️ Heatmap",
    "🥧 Pie Chart (Faktor)",
    "📊 Grouped Bar (SPF)"
])

# TAB 1: Bar Chart
with tab1:
    st.markdown("**Waktu Aman Berjemur Berdasarkan UV Index & Tipe Kulit (Formula SED)**")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    colors = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#3498db', '#1abc9c']

    for idx, uv in enumerate(uv_levels):
        row, col = divmod(idx, 2)
        data = [hitung_waktu_aman_sed(uv, fitzpatrick_factors[i]) for i in range(1, 7)]
        bars = axes[row, col].bar(tipe_kulit, data, color=colors, edgecolor='black')
        axes[row, col].set_title(f'UV Index = {uv}', fontweight='bold')
        axes[row, col].set_ylabel('Waktu Aman (menit)')
        axes[row, col].axhline(y=10, color='red', linestyle='--', alpha=0.7, label='Threshold Aman (10 menit)')
        for bar in bars:
            axes[row, col].annotate(f'{int(bar.get_height())}',
                                   xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                                   xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
        axes[row, col].legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Makin gelap kulit (Fitzpatrick tinggi), makin lama waktu aman. Garis merah = threshold 10 menit.")

# TAB 2: Line Chart SPF
with tab2:
    st.markdown("**Pengaruh SPF terhadap Waktu Aman Berjemur (UV Index = 6)**")
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(1, 7):
        waktu_spf = [min(hitung_waktu_aman_sed(6, fitzpatrick_factors[i]) * spf, 120) for spf in spf_levels]
        ax.plot(spf_levels, waktu_spf, marker='o', linewidth=2, markersize=8, label=tipe_kulit[i-1])
    ax.axhline(10, color='red', linestyle='--', alpha=0.7, label='Threshold Aman (10 menit)')
    ax.set_xlabel('SPF')
    ax.set_ylabel('Waktu Aman (menit)')
    ax.set_title('Efektivitas SPF terhadap Durasi Berjemur Aman', fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** SPF 30+ sangat meningkatkan durasi aman berjemur untuk semua tipe kulit!")

# TAB 3: Heatmap
with tab3:
    st.markdown("**Rekomendasi Waktu Berjemur Aman (menit) - Tanpa Sunscreen**")
    heatmap_data = [[hitung_waktu_aman_sed(uv, fitzpatrick_factors[t]) for uv in uv_levels] for t in range(1, 7)]
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=120)
    ax.set_xticks(np.arange(len(uv_levels)))
    ax.set_yticks(np.arange(len(tipe_kulit)))
    ax.set_xticklabels([f'UV {uv}' for uv in uv_levels])
    ax.set_yticklabels(tipe_kulit)
    ax.set_xlabel('UV Index', fontweight='bold')
    ax.set_ylabel('Tipe Kulit (Fitzpatrick)', fontweight='bold')
    for i in range(len(tipe_kulit)):
        for j in range(len(uv_levels)):
            val = heatmap_data[i][j]
            color = 'white' if val < 30 else 'black'
            ax.text(j, i, f'{int(val)} mnt', ha='center', va='center', fontweight='bold', color=color)
    plt.colorbar(im, ax=ax, label='Waktu Aman (menit)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Warna gelap = durasi pendek = berbahaya. Semakin gelap kulit, semakin tahan UV.")

# TAB 4: Pie Chart
with tab4:
    st.markdown("**Faktor Penentu Kondisi Optimal Berjemur**")
    fig, ax = plt.subplots(figsize=(10, 7))
    kondisi = ['UV Index\n(2–5)', 'Jam Pagi\n(09-10)', 'Jam Sore\n(15-16)', 'Suhu\n(26-30°C)', 'Kelembapan\n(60-75%)', 'SPF 30+']
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
        waktu = [min(hitung_waktu_aman_sed(6, fitzpatrick_factors[i]) * spf, 120) for i in range(1, 7)]
        bars = ax.bar(x + idx*width, waktu, width, label=f'SPF {spf}', color=color, edgecolor='black')
        for bar in bars:
            ax.annotate(f'{int(bar.get_height())}',
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 3), textcoords='offset points', ha='center', fontsize=8)

    ax.axhline(10, color='red', linestyle='--', alpha=0.7, label='Threshold Aman (10 menit)')
    ax.set_xlabel('Tipe Kulit (Fitzpatrick)')
    ax.set_ylabel('Waktu Aman (menit)')
    ax.set_title('Perbandingan Efektivitas SPF per Tipe Kulit (UV Index = 6)', fontweight='bold')
    ax.set_xticks(x + width*1.5)
    ax.set_xticklabels(tipe_kulit)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    st.pyplot(fig)
    plt.close()
    st.caption("💡 **Interpretasi:** Tanpa SPF durasi aman sangat pendek. Dengan SPF 30 durasi meningkat signifikan!")

# ============================================
# [NEW] POLA MUSIMAN
# ============================================
st.markdown("---")
st.header("📌 Bonus: Pola UV per Musim")
st.subheader("Bagaimana pola UV dan durasi aman berbeda antar musim?")

col1, col2 = st.columns([1, 2])

with col1:
    musim_summary = df_filtered.groupby('MUSIM').agg(
        UV_Rata=('ALLSKY_SFC_UV_INDEX', 'mean'),
        Durasi_Rata=('DURASI_AMAN_MENIT', 'mean'),
        Pct_Aman=('LABEL_AMAN', 'mean')
    ).round(2)
    musim_summary['Pct_Aman'] = (musim_summary['Pct_Aman'] * 100).round(1)
    musim_summary.columns = ['UV Rata-rata', 'Durasi Rata (mnt)', '% Aman']
    st.dataframe(musim_summary, use_container_width=True)
    st.info("💡 Musim Kemarau cenderung punya UV lebih tinggi → durasi aman lebih pendek.")

with col2:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    musim_order = ['Hujan', 'Peralihan', 'Kemarau']
    musim_uv = df_filtered.groupby('MUSIM')['ALLSKY_SFC_UV_INDEX'].mean().reindex(musim_order)
    musim_durasi = df_filtered.groupby('MUSIM')['DURASI_AMAN_MENIT'].mean().reindex(musim_order)

    axes[0].bar(musim_uv.index, musim_uv.values, color=['#3498db', '#f39c12', '#e74c3c'], edgecolor='white')
    axes[0].set_title('Rata-rata UV Index per Musim', fontweight='bold')
    axes[0].set_ylabel('UV Index')
    for i, v in enumerate(musim_uv.values):
        axes[0].text(i, v + 0.05, f'{v:.2f}', ha='center', fontweight='bold')

    axes[1].bar(musim_durasi.index, musim_durasi.values, color=['#3498db', '#f39c12', '#e74c3c'], edgecolor='white')
    axes[1].axhline(10, color='red', linestyle='--', alpha=0.7, label='Threshold Aman')
    axes[1].set_title('Rata-rata Durasi Aman per Musim', fontweight='bold')
    axes[1].set_ylabel('Durasi (menit)')
    axes[1].legend()
    for i, v in enumerate(musim_durasi.values):
        axes[1].text(i, v + 0.3, f'{v:.1f} mnt', ha='center', fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ============================================
# DATA DICTIONARY (UPDATED)
# ============================================
st.markdown("---")
st.header("📖 Data Dictionary")

with st.expander("Klik untuk melihat penjelasan setiap kolom"):
    data_dict = pd.DataFrame({
        'Kolom': [
            'YEAR', 'MO', 'DY', 'HR',
            'ALLSKY_SFC_UVA', 'ALLSKY_SFC_UVB', 'ALLSKY_SFC_UV_INDEX',
            'T2M', 'WS2M', 'RH2M', 'LOKASI', 'DATETIME',
            'JAM_KATEGORI', 'IS_DAYTIME', 'BULAN', 'MUSIM',
            'DURASI_AMAN_MENIT', 'LABEL_AMAN'
        ],
        'Tipe Data': [
            'int', 'int', 'int', 'int',
            'float', 'float', 'float',
            'float', 'float', 'float', 'str', 'datetime',
            'category', 'int', 'int', 'str',
            'float', 'int'
        ],
        'Satuan': [
            'Tahun', 'Bulan', 'Hari', 'Jam (0-23)',
            'MJ/hr', 'MJ/hr', 'W m-2 x 40',
            '°C', 'm/s', '%', '-', 'YYYY-MM-DD HH:MM',
            '-', '0/1', '1-12', '-',
            'menit (0-120)', '0/1'
        ],
        'Deskripsi': [
            'Tahun perekaman', 'Bulan (1-12)', 'Tanggal (1-31)', 'Jam (0-23)',
            'Iradiasi UVA permukaan (All Sky)', 'Iradiasi UVB permukaan (All Sky)', 'Indeks UV permukaan (All Sky)',
            'Suhu 2 meter (°C)', 'Kecepatan angin 2 meter (m/s)', 'Kelembapan relatif 2 meter (%)',
            'Lokasi: Bali/Lombok/Raja Ampat', 'Timestamp gabungan YEAR+MO+DY+HR',
            'Dini Hari/Pagi/Siang/Sore/Malam', '1=siang (6-17), 0=malam', 'Bulan (sama dengan MO)',
            'Hujan/Kemarau/Peralihan',
            'TARGET MODEL: durasi aman berjemur (SED, cap 120 menit)', '1=Aman (≥10 mnt), 0=Tidak Aman — dari serving API'
        ],
        'Sumber': [
            'NASA POWER', 'NASA POWER', 'NASA POWER', 'NASA POWER',
            'NASA POWER', 'NASA POWER', 'NASA POWER',
            'NASA POWER', 'NASA POWER', 'NASA POWER', 'Manual', 'Feature Eng.',
            'Feature Eng.', 'Feature Eng.', 'Feature Eng.', 'Feature Eng.',
            'Feature Eng. (Formula SED)', 'Feature Eng. (dari DURASI_AMAN_MENIT)'
        ]
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
    Target Model: DURASI_AMAN_MENIT | Threshold Aman: ≥ 10 menit<br>
    Dibuat untuk analisis keamanan aktivitas berjemur di pantai
</div>
""", unsafe_allow_html=True)
