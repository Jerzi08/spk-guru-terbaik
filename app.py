import streamlit as st
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.model_selection import LeaveOneOut
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import spearmanr

st.set_page_config(page_title="Sistem Pemilihan Guru Terbaik", layout="wide")

# ================= FUNGSI KOMPETENSI GURU =================
def hitung_kompetensi(df):
    """
    Menghitung skor 4 kompetensi utama dari 16 kriteria
    """
    # Pembagian kriteria per kompetensi
    kompetensi = {
        'Pedagogik': ['K1', 'K2', 'K3', 'K4'],
        'Profesional': ['K5', 'K6', 'K7', 'K8'],
        'Sosial': ['K9', 'K10', 'K11', 'K12'],
        'Kepribadian': ['K13', 'K14', 'K15', 'K16']
    }
    
    df_kompetensi = df.copy()
    
    for nama, kriteria in kompetensi.items():
        # Hitung rata-rata per kompetensi
        df_kompetensi[nama] = df[kriteria].mean(axis=1).round(2)
    
    return df_kompetensi

# ================= STYLE =================
st.markdown("""
<style>
.big-title {font-size:32px !important; font-weight:bold; color:#1f4e79;}
.highlight-box {padding:25px; border-radius:12px; background-color:#f0f8ff; border-left:8px solid #1f4e79;}
.gold {color:#d4af37; font-weight:bold; font-size:26px;}
.section-title {font-size:20px; font-weight:bold; margin-top:25px; color:#1f4e79;}
.metric-card {background-color:#f8f9fa; padding:15px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🏆 Sistem Cerdas Pemilihan Guru Terbaik</div>', unsafe_allow_html=True)
st.markdown("### Hybrid : Naive Bayes Classifier (NBC) + Analytical Hierarchy Process (AHP)")

uploaded_file = st.file_uploader("Upload File Excel (.xlsx)", type=["xlsx"])

# ================= SIDEBAR =================
menu = st.sidebar.selectbox(
    "Pilih Menu",
    ["Dashboard Keputusan", "Evaluasi Model", "Analisis Detail Guru", "Analisis Strategis"]
)

# ================= MAIN =================
if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    if "Label" not in df.columns:
        st.error("Kolom 'Label' tidak ditemukan.")
        st.stop()

    df["Label_numeric"] = df["Label"].map({
        "Terpilih": 1,
        "Tidak Terpilih": 0
    })

    fitur = df.drop(columns=["Nama", "Label", "Label_numeric"])
    X = fitur.values
    y = df["Label_numeric"].values
    
    # Definisikan kriteria_names dari kolom fitur
    kriteria_names = fitur.columns.tolist()

    # ================= LOOCV =================
    loo = LeaveOneOut()
    model = GaussianNB()

    y_pred_cv = np.zeros(len(y))
    y_prob_cv = np.zeros(len(y))

    for train_index, test_index in loo.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train = y[train_index]

        model.fit(X_train, y_train)

        y_pred_cv[test_index] = model.predict(X_test)
        y_prob_cv[test_index] = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y, y_pred_cv)
    prec = precision_score(y, y_pred_cv)
    rec = recall_score(y, y_pred_cv)
    f1 = f1_score(y, y_pred_cv)
    cm = confusion_matrix(y, y_pred_cv)

   # ================= FINAL MODEL =================
    model_final = GaussianNB()
    model_final.fit(X, y)

    y_pred = model_final.predict(X)
    y_prob = model_final.predict_proba(X)[:, 1]

    df["Prediksi"] = np.where(y_pred == 1, "Terpilih", "Tidak Terpilih")
    df["Probabilitas_Terpilih"] = np.round(y_prob, 4)

    df_layak = df[df["Prediksi"] == "Terpilih"].copy()

    # ================= AHP (HITUNG DULU) =================
    bobot = np.array([
        0.221, 0.129, 0.096, 0.079,
        0.061, 0.054, 0.047, 0.042,
        0.050, 0.035, 0.030, 0.031,
        0.047, 0.035, 0.024, 0.019
    ])

    if len(df_layak) > 0:
        # Hitung skor AHP
        skor = df_layak.drop(
            columns=["Nama", "Label", "Label_numeric", "Prediksi", "Probabilitas_Terpilih"]
        ).values.dot(bobot)

        df_layak["Skor_AHP"] = skor
        df_layak = df_layak.sort_values(by="Skor_AHP", ascending=False).reset_index(drop=True)
        df_layak["Ranking"] = df_layak.index + 1
        
        # Hitung indeks kinerja
        min_skor = df_layak["Skor_AHP"].min()
        max_skor = df_layak["Skor_AHP"].max()
        
        if max_skor == min_skor:
            df_layak["Indeks_Kinerja"] = 100
        else:
            df_layak["Indeks_Kinerja"] = (
                (df_layak["Skor_AHP"] - min_skor) / (max_skor - min_skor)
            ) * 100
        df_layak["Indeks_Kinerja"] = df_layak["Indeks_Kinerja"].round(2)
        
        # Kategori
        def kategori_kinerja(nilai):
            if nilai >= 85:
                return "Sangat Baik"
            elif nilai >= 70:
                return "Baik"
            elif nilai >= 55:
                return "Cukup"
            else:
                return "Perlu Pembinaan"
        
        df_layak["Kategori"] = df_layak["Indeks_Kinerja"].apply(kategori_kinerja)
        
        # Rekomendasi
        def rekomendasi_otomatis(kategori):
            if kategori == "Sangat Baik":
                return "Direkomendasikan sebagai mentor atau role model."
            elif kategori == "Baik":
                return "Dapat diberikan pelatihan penguatan kompetensi lanjutan."
            elif kategori == "Cukup":
                return "Perlu pelatihan terarah pada indikator prioritas."
            else:
                return "Disarankan mengikuti program pembinaan intensif."
        
        df_layak["Rekomendasi"] = df_layak["Kategori"].apply(rekomendasi_otomatis)
        
        # TAMPILKAN KONFIRMASI
        st.sidebar.success(f"✅ AHP selesai: {len(df_layak)} guru terpilih")

    # ================= HITUNG KOMPETENSI (SETELAH AHP) =================
    df_kompetensi = hitung_kompetensi(df)

    if len(df_layak) > 0:
        df_layak_kompetensi = hitung_kompetensi(df_layak)
        # Gabungkan dengan data AHP (SEKARANG SUDAH ADA)
        df_layak_kompetensi = df_layak_kompetensi.merge(
            df_layak[['Nama', 'Skor_AHP', 'Ranking', 'Kategori', 'Rekomendasi']], 
            on='Nama', 
            how='left'
        )
        st.sidebar.success(f"✅ Kompetensi selesai")
    else:
        df_layak_kompetensi = pd.DataFrame()
        st.sidebar.warning("⚠️ Tidak ada guru terpilih")
    
    # ================= INDEKS KINERJA =================
    if len(df_layak) > 0:
        min_skor = df_layak["Skor_AHP"].min()
        max_skor = df_layak["Skor_AHP"].max()

        if max_skor == min_skor:
            df_layak["Indeks_Kinerja"] = 100
        else:
            df_layak["Indeks_Kinerja"] = (
                (df_layak["Skor_AHP"] - min_skor) / (max_skor - min_skor)
            ) * 100

        df_layak["Indeks_Kinerja"] = df_layak["Indeks_Kinerja"].round(2)

        # ================= KATEGORI =================
        def kategori_kinerja(nilai):
            if nilai >= 85:
                return "Sangat Baik"
            elif nilai >= 70:
                return "Baik"
            elif nilai >= 55:
                return "Cukup"
            else:
                return "Perlu Pembinaan"

        df_layak["Kategori"] = df_layak["Indeks_Kinerja"].apply(kategori_kinerja)

        # ================= REKOMENDASI =================
        def rekomendasi_otomatis(kategori):
            if kategori == "Sangat Baik":
                return "Direkomendasikan sebagai mentor atau role model."
            elif kategori == "Baik":
                return "Dapat diberikan pelatihan penguatan kompetensi lanjutan."
            elif kategori == "Cukup":
                return "Perlu pelatihan terarah pada indikator prioritas."
            else:
                return "Disarankan mengikuti program pembinaan intensif."

        df_layak["Rekomendasi"] = df_layak["Kategori"].apply(rekomendasi_otomatis)

    # ================= HITUNG AHP UNTUK SEMUA GURU =================
    def hitung_ahp_semua_guru(df, bobot):
        """
        Menghitung nilai AHP untuk semua guru (termasuk yang tidak terpilih)
        """
        df_all = df.copy()
        
        # Kolom kriteria (K1-K16)
        kriteria_cols = [f'K{i}' for i in range(1, 17)]
        
        # Hitung skor AHP untuk semua guru
        skor_ahp_all = df_all[kriteria_cols].values.dot(bobot)
        df_all["Skor_AHP_Semua"] = skor_ahp_all
        
        # Ranking semua guru
        df_all = df_all.sort_values(by="Skor_AHP_Semua", ascending=False).reset_index(drop=True)
        df_all["Ranking_Semua"] = df_all.index + 1
        
        return df_all

    # Panggil fungsi
    df_all_ahp = hitung_ahp_semua_guru(df, bobot)

   
    # =========================================================
    # ================= MENU UTAMA ============================
    # =========================================================

    if menu == "Dashboard Keputusan":
        # ================= DASHBOARD =====================
        st.markdown('<div class="section-title">📊 Dashboard Keputusan</div>', unsafe_allow_html=True)

        # Tambahkan di bagian bawah Dashboard Keputusan
        st.markdown("### 📄 Draft Surat Keputusan")

        if len(df_layak) > 0:
            # Pilihan nama Kepala Sekolah
            col_sk1, col_sk2 = st.columns([2, 1])
            with col_sk1:
                nama_kepsek = st.text_input("Nama Kepala Sekolah", value="H. Ahmad Saepudin, M.Pd")
            with col_sk2:
                nip_kepsek = st.text_input("NIP", value="196501011990031005")
            
            # Data yang diperlukan
            guru_terbaik = df_layak.iloc[0]
            tiga_besar = df_layak.head(3)
            
            # Statistik kategori
            kategori_counts = df_layak['Kategori'].value_counts()
            sangat_baik = kategori_counts.get('Sangat Baik', 0)
            baik = kategori_counts.get('Baik', 0)
            cukup = kategori_counts.get('Cukup', 0)
            perlu_pembinaan = kategori_counts.get('Perlu Pembinaan', 0)
            
            # Daftar lengkap guru terpilih
            daftar_guru = ""
            for i, (_, row) in enumerate(df_layak.iterrows(), 1):
                daftar_guru += f"{i:2d}. {row['Nama']:<10} - Skor: {row['Skor_AHP']:.2f} - {row['Kategori']}\n"
            
            # Tanggal
            from datetime import datetime
            tgl_sk = datetime.now().strftime("%d %B %Y")
            tahun = datetime.now().strftime("%Y")
            bulan = datetime.now().strftime("%m")
            
            # Format SK Formal
            sk_content = f"""
        {'='*70}
                            KEPUTUSAN KEPALA SEKOLAH
                            NOMOR: 421.3/{tahun[-2:]}.{bulan}/SK/GT/{tahun}
        {'='*70}
                            TENTANG
                    PENETAPAN GURU TERBAIK TAHUN {tahun}
        {'='*70}

        DENGAN RAHMAT TUHAN YANG MAHA ESA
        KEPALA SEKOLAH {nama_kepsek},

        Menimbang  : a. bahwa dalam rangka meningkatkan mutu pendidikan,
                        perlu dilakukan apresiasi terhadap guru berprestasi;
                     b. bahwa berdasarkan hasil seleksi menggunakan sistem
                        pendukung keputusan, diperoleh guru-guru terbaik;

        Mengingat   : 1. Undang-Undang Nomor 20 Tahun 2003 tentang Sistem
                        Pendidikan Nasional;
                      2. Undang-Undang Nomor 14 Tahun 2005 tentang Guru dan Dosen;
                      3. Program Kerja Sekolah Tahun {tahun};

        Memperhatikan : Hasil seleksi sistem pendukung keputusan tanggal
                        {tgl_sk};

                                    MEMUTUSKAN:

        Menetapkan   : 
        KESATUAN    : Menetapkan Guru Terbaik Tahun {tahun} sebagai berikut:

                    GURU TERBAIK : {guru_terbaik['Nama']}
                    Skor Akhir   : {guru_terbaik['Skor_AHP']:.2f}
                    Kategori     : {guru_terbaik['Kategori']}

        KEDUA       : 3 (Tiga) Besar Guru Terbaik adalah:
                      1. {tiga_besar.iloc[0]['Nama']} (Skor: {tiga_besar.iloc[0]['Skor_AHP']:.2f})
                      2. {tiga_besar.iloc[1]['Nama'] if len(tiga_besar) > 1 else '-'} (Skor: {tiga_besar.iloc[1]['Skor_AHP'] if len(tiga_besar) > 1 else 0:.2f})
                      3. {tiga_besar.iloc[2]['Nama'] if len(tiga_besar) > 2 else '-'} (Skor: {tiga_besar.iloc[2]['Skor_AHP'] if len(tiga_besar) > 2 else 0:.2f})

        KETIGA      : Daftar lengkap guru terpilih sebagaimana tercantum dalam
                    lampiran keputusan ini.

        KEEMPAT     : Keputusan ini mulai berlaku sejak tanggal ditetapkan.

        Ditetapkan di : {nama_kepsek}
        Pada tanggal  : {tgl_sk}

        {' '*50}{nama_kepsek}
        {' '*50}NIP. {nip_kepsek}

        {'='*70}
                                    LAMPIRAN KEPUTUSAN
                            NOMOR: 421.3/{tahun[-2:]}.{bulan}/SK/GT/{tahun}
        {'='*70}

        I.  DAFTAR GURU TERPILIH
            {'-'*50}
            {daftar_guru}
            {'-'*50}
            Total Guru Terpilih : {len(df_layak)} orang

        II. DISTRIBUSI KATEGORI KINERJA
            {'-'*50}
            - Sangat Baik     : {sangat_baik} orang
            - Baik            : {baik} orang
            - Cukup           : {cukup} orang
            - Perlu Pembinaan : {perlu_pembinaan} orang

        III. REKOMENDASI
            {'-'*50}
            1. Guru "Sangat Baik" direkomendasikan sebagai mentor.
            2. Guru "Baik" dan "Cukup" diprioritaskan untuk pelatihan.
            3. Guru "Perlu Pembinaan" akan mengikuti program pembinaan.

        {' '*50}{nama_kepsek}
        {' '*50}NIP. {nip_kepsek}
        """
            
            # Tampilkan SK
            st.markdown("### 📄 Surat Keputusan Guru Terbaik")
            st.text_area("Draft SK (siap cetak)", sk_content, height=500)
            
            # Tombol download
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d2:
                st.download_button(
                    label="📥 Download SK (TXT)",
                    data=sk_content,
                    file_name=f"SK_Guru_Terbaik_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            # Preview ringkas
            with st.expander("📋 Preview Ringkas SK"):
                st.markdown(f"""
                **GURU TERBAIK:** {guru_terbaik['Nama']} (Skor: {guru_terbaik['Skor_AHP']:.2f})
                
                **3 BESAR:**
                1. {tiga_besar.iloc[0]['Nama']} ({tiga_besar.iloc[0]['Skor_AHP']:.2f})
                2. {tiga_besar.iloc[1]['Nama'] if len(tiga_besar) > 1 else '-'} ({tiga_besar.iloc[1]['Skor_AHP'] if len(tiga_besar) > 1 else 0:.2f})
                3. {tiga_besar.iloc[2]['Nama'] if len(tiga_besar) > 2 else '-'} ({tiga_besar.iloc[2]['Skor_AHP'] if len(tiga_besar) > 2 else 0:.2f})
                
                **KATEGORI:** SB:{sangat_baik}, B:{baik}, C:{cukup}, PB:{perlu_pembinaan}
                """)

        # Tabel Hasil Klasifikasi
        st.markdown("### 🔎 Hasil Klasifikasi Naive Bayes")
        st.markdown("#### Tabel Hasil Klasifikasi")
        df_nb = df[["Nama", "Label", "Prediksi", "Probabilitas_Terpilih"]].copy()
        df_nb["Probabilitas_Terpilih"] = df_nb["Probabilitas_Terpilih"].apply(lambda x: f"{x:.2%}")
        st.dataframe(df_nb, use_container_width=True)
        
        st.markdown("---")
        
        col_nb1, col_nb2 = st.columns(2)
        with col_nb1:
            st.markdown("#### Distribusi Prediksi")
            pred_counts = df["Prediksi"].value_counts().reset_index()
            pred_counts.columns = ["Status", "Jumlah"]
            fig_pie = px.pie(pred_counts, values="Jumlah", names="Status", 
                            color_discrete_sequence=["#28a745", "#dc3545"],
                            title="Proporsi Guru Terpilih vs Tidak Terpilih")
            st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart_dashboard")
        
        with col_nb2:
            st.markdown("#### Distribusi Probabilitas")
            fig_hist = px.histogram(df, x="Probabilitas_Terpilih", nbins=20,
                                   title="Sebaran Probabilitas Terpilih",
                                   labels={"Probabilitas_Terpilih": "Probabilitas"})
            st.plotly_chart(fig_hist, use_container_width=True, key="histogram_dashboard")
        
        # Peringkat Akhir
        if len(df_layak) > 0:
            st.markdown("### 🏆 Peringkat Akhir Guru")
            
            tab1, tab2, tab3 = st.tabs(["✅ Guru Terpilih (AHP)", "❌ Guru Tidak Terpilih", "📊 Semua Guru (AHP)"])
            
            with tab1:
                st.markdown("#### Tabel Nilai Akhir AHP Guru Terpilih")
                df_ahp = df_layak[["Ranking", "Nama", "Skor_AHP", "Indeks_Kinerja", "Kategori", "Rekomendasi"]].copy()
                df_ahp["Skor_AHP"] = df_ahp["Skor_AHP"].round(3)
                df_ahp["Indeks_Kinerja"] = df_ahp["Indeks_Kinerja"].astype(str) + "%"
                st.dataframe(df_ahp, use_container_width=True)
            
            with tab2:
                st.markdown("#### 📊 Nilai AHP Guru Tidak Terpilih (Untuk Perbandingan)")
                st.caption("ℹ️ Guru tidak terpilih oleh Naive Bayes, namun nilai AHP dihitung untuk perbandingan")
                
                # Ambil guru tidak terpilih
                df_tidak = df_all_ahp[df_all_ahp["Prediksi"] == "Tidak Terpilih"][
                    ["Ranking_Semua", "Nama", "Skor_AHP_Semua", "Probabilitas_Terpilih"]
                ].copy()
                
                df_tidak = df_tidak.sort_values("Skor_AHP_Semua", ascending=False).reset_index(drop=True)
                df_tidak["Ranking_AHP"] = df_tidak.index + 1
                df_tidak["Skor_AHP_Semua"] = df_tidak["Skor_AHP_Semua"].round(3)
                df_tidak["Probabilitas_Terpilih"] = df_tidak["Probabilitas_Terpilih"].apply(lambda x: f"{x:.2%}")
                
                st.dataframe(
                    df_tidak[["Ranking_AHP", "Nama", "Skor_AHP_Semua", "Probabilitas_Terpilih"]],
                    use_container_width=True
                )
                
                # Statistik perbandingan
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.metric("Rata-rata AHP Tidak Terpilih", 
                             f"{df_tidak['Skor_AHP_Semua'].mean():.2f}")
                with col_t2:
                    st.metric("Nilai AHP Tertinggi (Tidak Terpilih)", 
                             f"{df_tidak['Skor_AHP_Semua'].max():.2f}")
                with col_t3:
                    # Bandingkan dengan rata-rata terpilih
                    if len(df_layak) > 0:
                        selisih = df_layak["Skor_AHP"].mean() - df_tidak["Skor_AHP_Semua"].mean()
                        st.metric("Selisih dengan Rata-rata Terpilih", 
                                 f"{selisih:+.2f}")
                
                # Grafik perbandingan
                st.markdown("#### 📊 Perbandingan Distribusi AHP")
                
                # Siapkan data untuk box plot
                df_box = pd.DataFrame({
                    'Nilai AHP': pd.concat([
                        df_layak["Skor_AHP"],
                        df_tidak["Skor_AHP_Semua"]
                    ]),
                    'Kategori': ['Terpilih']*len(df_layak) + ['Tidak Terpilih']*len(df_tidak)
                })
                
                fig_box = px.box(df_box, x='Kategori', y='Nilai AHP', 
                                color='Kategori',
                                title='Perbandingan Distribusi Nilai AHP',
                                color_discrete_map={'Terpilih': '#28a745', 'Tidak Terpilih': '#dc3545'})
                
                st.plotly_chart(fig_box, use_container_width=True, key="box_plot_distribusi_ahp")
            
            with tab3:
                st.markdown("#### 📋 Peringkat AHP Semua Guru")
                
                df_semua = df_all_ahp[["Ranking_Semua", "Nama", "Prediksi", "Skor_AHP_Semua"]].copy()
                df_semua["Skor_AHP_Semua"] = df_semua["Skor_AHP_Semua"].round(3)
                df_semua = df_semua.head(20)
                
                # Warna berdasarkan prediksi
                def warnai_status(val):
                    if val == "Terpilih":
                        return 'background-color: #d4edda; color: #155724'
                    else:
                        return 'background-color: #f8d7da; color: #721c24'
                
                st.dataframe(
                    df_semua.style.applymap(warnai_status, subset=['Prediksi']),
                    use_container_width=True
                )
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Total Guru Terpilih", len(df_layak))
            with col_stats2:
                st.metric("Total Guru Tidak Terpilih", len(df[df["Prediksi"] == "Tidak Terpilih"]))
            with col_stats3:
                st.metric("Persentase Lolos Seleksi", f"{(len(df_layak)/len(df)*100):.1f}%")
            
            st.markdown("---")
            
            top_n = st.slider("Jumlah Guru yang Ditampilkan", min_value=5, max_value=len(df_layak), value=min(10, len(df_layak)), key="slider_top_n")
            
            df_top = df_layak.head(top_n).copy()
            colors = ['#ffd700' if i == 0 else '#c0c0c0' if i == 1 else '#cd7f32' if i == 2 else '#1f77b4' 
                     for i in range(len(df_top))]
            
            fig_rank = px.bar(df_top, y="Nama", x="Skor_AHP", 
                             orientation='h',
                             title=f"Top {top_n} Guru Terbaik",
                             labels={"Skor_AHP": "Skor Akhir", "Nama": ""},
                             color_discrete_sequence=colors,
                             text="Skor_AHP")
            fig_rank.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_rank, use_container_width=True, key="bar_chart_ranking")

            st.markdown("### 🥇 Top 3 Guru Terbaik")
            col1, col2, col3 = st.columns(3)
            
            for idx, col in enumerate([col1, col2, col3]):
                if idx < len(df_layak):
                    guru = df_layak.iloc[idx]
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="text-align:center; {'color:#ffd700' if idx==0 else '#c0c0c0' if idx==1 else '#cd7f32'}">
                                {'🏆' if idx==0 else '🥈' if idx==1 else '🥉'} #{idx+1}
                            </h3>
                            <h2 style="text-align:center">{guru['Nama']}</h2>
                            <p style="text-align:center; font-size:24px; font-weight:bold">{guru['Skor_AHP']:.2f}</p>
                            <p style="text-align:center">{guru['Kategori']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            # ================= REKOMENDASI PASCA SELEKSI =================
            # ================= REKOMENDASI PASCA SELEKSI =================
            if len(df_layak) > 0:
                st.markdown("---")
                st.markdown("### 🎯 Rencana Tindak Lanjut & Penghargaan")
                
                # Siapkan data guru tidak terpilih
                df_tidak = df_all_ahp[df_all_ahp["Prediksi"] == "Tidak Terpilih"].copy()
                
                # ===== HITUNG DF_GAP DI SINI =====
                rata_semua = df[fitur.columns].mean()
                maks_ideal = 100
                n_gap = min(16, len(fitur.columns))
                df_gap = pd.DataFrame({
                    "Kriteria": fitur.columns[:n_gap],
                    "Rata-rata Semua Guru": rata_semua.values[:n_gap],
                    "Kesenjangan": maks_ideal - rata_semua.values[:n_gap]
                }).sort_values("Kesenjangan", ascending=False)
                # ===== SELESAI HITUNG DF_GAP =====
                
                # Pastikan df_tidak tidak kosong
                if len(df_tidak) == 0:
                    # Buat data dummy jika kosong
                    df_tidak = pd.DataFrame({
                        'Nama': ['-', '-', '-'],
                        'Probabilitas_Terpilih': [0.3, 0.5, 0.7]
                    })
                
                # Tabs untuk setiap kelompok
                tab_g1, tab_g2, tab_g3 = st.tabs([
                    "🏆 Guru Terpilih",
                    "📈 Guru Tidak Terpilih", 
                    "🏫 Rencana Sekolah"
                ])
                
                with tab_g1:
                    st.markdown("#### 🏆 Penghargaan & Goals Guru Terpilih")
                    
                    # Guru Terbaik (Peringkat 1)
                    if len(df_layak) > 0:
                        guru_terbaik = df_layak.iloc[0]
                        st.success(f"### 🌟 GURU TERBAIK: {guru_terbaik['Nama']} (Skor: {guru_terbaik['Skor_AHP']:.2f})")
                        
                        col_g1, col_g2 = st.columns(2)
                        with col_g1:
                            st.markdown("**🏅 Penghargaan Khusus:**")
                            st.markdown("""
                            - ✅ Piagam Penghargaan Kepala Sekolah
                            - ✅ Uang Pembinaan (sesuai kebijakan sekolah)
                            - ✅ Prioritas Mengikuti Pelatihan
                            - ✅ Menjadi Duta Sekolah
                            - ✅ Dispensasi tugas tertentu
                            """)
                        
                        with col_g2:
                            st.markdown("**🎯 Goals 1 Tahun:**")
                            st.markdown("""
                            - Mempertahankan predikat guru terbaik
                            - Menjadi mentor minimal 3 guru lain
                            - Membuat 1 publikasi ilmiah
                            - Mewakili sekolah di lomba
                            """)
                    
                    # Per kategori
                    kategori_list = [
                        ("Sangat Baik", "🏆", "#d4edda", "#155724"),
                        ("Baik", "📚", "#fff3cd", "#856404"),
                        ("Cukup", "📋", "#fff3cd", "#856404"),
                        ("Perlu Pembinaan", "⚠️", "#f8d7da", "#721c24")
                    ]
                    
                    for kategori, icon, bg_color, text_color in kategori_list:
                        jumlah = len(df_layak[df_layak['Kategori'] == kategori])
                        if jumlah > 0:
                            with st.expander(f"{icon} **{kategori}** ({jumlah} orang)"):
                                col_a, col_b = st.columns(2)
                                
                                with col_a:
                                    st.markdown("**🏅 Penghargaan:**")
                                    if kategori == "Sangat Baik":
                                        st.markdown("""
                                        - Piagam Penghargaan
                                        - Tunjangan Kinerja
                                        - Prioritas pelatihan
                                        """)
                                    elif kategori == "Baik":
                                        st.markdown("""
                                        - Piagam Penghargaan
                                        - Prioritas diklat
                                        """)
                                    elif kategori == "Cukup":
                                        st.markdown("""
                                        - Surat Keterangan Prestasi
                                        """)
                                    else:
                                        st.markdown("""
                                        - Surat Tugas Pembinaan
                                        """)
                                
                                with col_b:
                                    st.markdown("**🎯 Goals:**")
                                    if kategori == "Sangat Baik":
                                        st.markdown("""
                                        - Pertahankan prestasi
                                        - Mentor 2 guru
                                        - Skor >90 tahun depan
                                        """)
                                    elif kategori == "Baik":
                                        st.markdown("""
                                        - Naik ke Sangat Baik
                                        - Ikuti 2 pelatihan
                                        """)
                                    elif kategori == "Cukup":
                                        st.markdown("""
                                        - Naik ke Baik (6 bulan)
                                        - Perbaiki 3 kriteria
                                        """)
                                    else:
                                        st.markdown("""
                                        - Naik ke Cukup
                                        - Ikuti pembinaan
                                        """)
                
                with tab_g2:
                    st.markdown("#### 📈 Rekomendasi untuk Guru Tidak Terpilih")
                    
                    if len(df_tidak) > 0 and 'Probabilitas_Terpilih' in df_tidak.columns:
                        # Kelompokkan berdasarkan probabilitas
                        prob_tinggi = df_tidak[df_tidak['Probabilitas_Terpilih'] > 0.6]
                        prob_sedang = df_tidak[(df_tidak['Probabilitas_Terpilih'] <= 0.6) & (df_tidak['Probabilitas_Terpilih'] > 0.4)]
                        prob_rendah = df_tidak[df_tidak['Probabilitas_Terpilih'] <= 0.4]
                        
                        kelompok = [
                            ("Probabilitas Tinggi (>60%)", prob_tinggi, "🟢"),
                            ("Probabilitas Sedang (40-60%)", prob_sedang, "🟡"),
                            ("Probabilitas Rendah (<40%)", prob_rendah, "🔴")
                        ]
                        
                        for label, data, icon in kelompok:
                            if len(data) > 0:
                                with st.expander(f"{icon} **{label}** ({len(data)} orang)"):
                                    st.markdown(f"**Contoh Guru:** {', '.join(data['Nama'].tolist()[:3])}")
                                    
                                    col_x, col_y = st.columns(2)
                                    with col_x:
                                        st.markdown("**📋 Rekomendasi:**")
                                        if "Tinggi" in label:
                                            st.markdown("""
                                            - Program akselerasi 1 bulan
                                            - Fokus pada 3 kriteria terendah
                                            - Bisa jadi kandidat cadangan
                                            """)
                                        elif "Sedang" in label:
                                            st.markdown("""
                                            - Pembinaan reguler 6 bulan
                                            - Evaluasi setiap bulan
                                            - Identifikasi kelemahan
                                            """)
                                        else:
                                            st.markdown("""
                                            - Program pelatihan dasar
                                            - Pendampingan khusus
                                            - Konsultasi dengan pengawas
                                            """)
                                    
                                    with col_y:
                                        st.markdown("**🎯 Goals:**")
                                        if "Tinggi" in label:
                                            st.markdown("- Target terpilih tahun depan")
                                        elif "Sedang" in label:
                                            st.markdown("- Masuk probabilitas tinggi")
                                        else:
                                            st.markdown("- Kenaikan nilai 15 poin")
                    else:
                        st.info("Tidak ada data guru tidak terpilih")
                
                with tab_g3:
                    st.markdown("#### 🏫 Rencana Tindak Lanjut Sekolah")
                    
                    col_s1, col_s2 = st.columns(2)
                    
                    with col_s1:
                        st.markdown("**📅 Program Tindak Lanjut:**")
                        st.markdown("""
                        - 📅 Rapat pleno penetapan guru terbaik
                        - 📢 Pengumuman resmi di papan pengumuman
                        - 🎉 Acara apresiasi dan penyerahan penghargaan
                        - 📝 Penerbitan SK resmi
                        - 🤝 Program mentoring dimulai
                        """)
                        
                        st.markdown("**💰 Alokasi Anggaran:**")
                        st.markdown("""
                        - 💰 Anggaran penghargaan guru terbaik
                        - 📚 Anggaran program pembinaan
                        - 🖥️ Anggaran pengembangan kompetensi
                        """)
                    
                    with col_s2:
                        st.markdown("**⏱️ Timeline:**")
                        st.markdown("""
                        - **Minggu 1:** Penetapan & pengumuman
                        - **Minggu 2:** Acara apresiasi
                        - **Minggu 3:** Program mentoring dimulai
                        - **Bulan 1-3:** Evaluasi berkala
                        - **Bulan 6:** Evaluasi tengah tahun
                        """)
                        
                        st.markdown("**📊 Indikator Keberhasilan:**")
                        st.markdown("""
                        - ✅ 80% guru terpilih mempertahankan predikat
                        - ✅ 50% guru tidak terpilih meningkat
                        - ✅ Rata-rata nilai sekolah naik 5%
                        - ✅ Program mentoring berjalan aktif
                        """)
                
                # Ringkasan eksekutif
                st.markdown("---")
                st.markdown("#### 📊 Ringkasan Program")
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                with col_r1:
                    st.metric("Guru Terpilih", len(df_layak))
                with col_r2:
                    st.metric("Guru Tidak Terpilih", len(df_tidak))
                with col_r3:
                    st.metric("Program Pembinaan", f"{len(df_tidak)} orang")
                with col_r4:
                    mentor = len(df_layak[df_layak['Kategori']=='Sangat Baik'])
                    st.metric("Mentor Tersedia", mentor)

            # ================= PROFIL 4 KOMPETENSI =================
            if len(df_layak) > 0 and len(df_layak_kompetensi) > 0:
                st.markdown("### 📊 Profil 4 Kompetensi Utama")
                
                # Pilih guru untuk dilihat
                guru_pilih = st.selectbox(
                    "Pilih Guru untuk Lihat Profil Kompetensi",
                    df_layak["Nama"].tolist(),
                    key="guru_kompetensi"
                )
                
                # Data guru terpilih
                guru_data = df_layak_kompetensi[df_layak_kompetensi["Nama"] == guru_pilih].iloc[0]
                
                # Tampilkan radar chart 4 kompetensi
                kompetensi_cols = ['Pedagogik', 'Profesional', 'Sosial', 'Kepribadian']
                nilai_kompetensi = [guru_data[col] for col in kompetensi_cols]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=nilai_kompetensi + [nilai_kompetensi[0]],
                    theta=kompetensi_cols + [kompetensi_cols[0]],
                    fill='toself',
                    name=guru_pilih,
                    line_color='gold'
                ))
                
                # Tambahkan rata-rata semua guru terpilih
                if len(df_layak_kompetensi) > 0:
                    rata_kompetensi = df_layak_kompetensi[kompetensi_cols].mean().values
                    fig.add_trace(go.Scatterpolar(
                        r=rata_kompetensi.tolist() + [rata_kompetensi[0]],
                        theta=kompetensi_cols + [kompetensi_cols[0]],
                        fill='toself',
                        name='Rata-rata Guru Terpilih',
                        line_color='blue',
                        opacity=0.5
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    title=f"Profil 4 Kompetensi - {guru_pilih}",
                    showlegend=True,
                    height=500
                )
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.plotly_chart(fig, use_container_width=True, key=f"radar_kompetensi_{guru_pilih}")
                
                with col2:
                    st.markdown("#### Detail Nilai")
                    for komp in kompetensi_cols:
                        st.metric(komp, f"{guru_data[komp]:.1f}")
                    
                    # PERBAIKAN: CEK DULU APAKAH KOLOM ADA
                    if 'Ranking' in guru_data.index:
                        st.metric("Ranking", f"#{guru_data['Ranking']}")
                    else:
                        # Cari ranking dari df_layak
                        ranking_value = df_layak[df_layak["Nama"] == guru_pilih]['Ranking'].values
                        if len(ranking_value) > 0:
                            st.metric("Ranking", f"#{ranking_value[0]}")
                    
                    if 'Skor_AHP' in guru_data.index:
                        st.metric("Skor AHP", f"{guru_data['Skor_AHP']:.2f}")
                    else:
                        skor_value = df_layak[df_layak["Nama"] == guru_pilih]['Skor_AHP'].values
                        if len(skor_value) > 0:
                            st.metric("Skor AHP", f"{skor_value[0]:.2f}")

                # Tabel perbandingan kompetensi top 10
                st.markdown("#### 📋 Perbandingan 4 Kompetensi (Top 10 Guru)")

                # Ambil top 10 guru
                top10 = df_layak.head(10)

                # Siapkan data untuk ditampilkan
                df_komp_tampil = top10[['Ranking', 'Nama']].copy()

                # Tambahkan kolom kompetensi dari df_kompetensi
                for komp in ['Pedagogik', 'Profesional', 'Sosial', 'Kepribadian']:
                    df_komp_tampil[komp] = df_kompetensi[df_kompetensi['Nama'].isin(top10['Nama'])][komp].values

                # Tambahkan Skor AHP
                df_komp_tampil['Skor_AHP'] = top10['Skor_AHP'].values

                # Tambahkan warna berdasarkan nilai
                def warnai_nilai(val):
                    if isinstance(val, (int, float)):
                        if val >= 85:
                            return 'background-color: #d4edda; color: #155724'
                        elif val >= 70:
                            return 'background-color: #fff3cd; color: #856404'
                        else:
                            return 'background-color: #f8d7da; color: #721c24'
                    return ''

                st.dataframe(
                    df_komp_tampil.style.applymap(warnai_nilai, subset=['Pedagogik', 'Profesional', 'Sosial', 'Kepribadian']),
                    use_container_width=True
                )

            st.markdown("### 📊 Perbandingan Skor AHP vs Probabilitas Naive Bayes")
            
            df_compare = df_layak.head(10).copy()
            df_compare['Probabilitas_Normalisasi'] = df_compare['Probabilitas_Terpilih'] * 100
            
            df_compare_melted = pd.melt(df_compare, 
                                       id_vars=['Nama'], 
                                       value_vars=['Skor_AHP', 'Probabilitas_Normalisasi'],
                                       var_name='Metode', value_name='Nilai')
            
            df_compare_melted['Metode'] = df_compare_melted['Metode'].replace({
                'Skor_AHP': 'Skor AHP (0-100)',
                'Probabilitas_Normalisasi': 'Probabilitas NB (0-100%)'
            })
            
            fig_compare = px.bar(df_compare_melted, x='Nama', y='Nilai', color='Metode',
                                barmode='group', title='Perbandingan Skor AHP vs Probabilitas Naive Bayes',
                                color_discrete_map={'Skor AHP (0-100)': '#1f77b4', 
                                                   'Probabilitas NB (0-100%)': '#ff7f0e'})
            st.plotly_chart(fig_compare, use_container_width=True, key="bar_chart_compare")

        st.markdown("### ⚖️ Bobot Kriteria AHP")
        
        n_kriteria = min(len(bobot), len(kriteria_names))
        kriteria_ahp = kriteria_names[:n_kriteria]
        bobot_ahp = bobot[:n_kriteria]
        
        df_bobot = pd.DataFrame({
            'Kriteria': kriteria_ahp,
            'Bobot': bobot_ahp
        }).sort_values('Bobot', ascending=True)
        
        fig_bobot = px.bar(df_bobot, y='Kriteria', x='Bobot', orientation='h',
                          title='Bobot Kriteria dalam Pemilihan Guru Terbaik',
                          color='Bobot', color_continuous_scale='Blues',
                          text=df_bobot['Bobot'].apply(lambda x: f'{x:.1%}'))
        fig_bobot.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_bobot, use_container_width=True, key="bar_chart_bobot")

    elif menu == "Evaluasi Model":
        # ================= EVALUASI =====================
        st.markdown('<div class="section-title">📊 Evaluasi Model (LOOCV)</div>', unsafe_allow_html=True)

        tab_eval1, tab_eval3 = st.tabs([
            "📊 Metrik Klasifikasi",
            "📈 ROC Curve"
        ])
        
        with tab_eval1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Accuracy</h3>
                    <p style="font-size:28px; font-weight:bold">{acc:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Precision</h3>
                    <p style="font-size:28px; font-weight:bold">{prec:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Recall</h3>
                    <p style="font-size:28px; font-weight:bold">{rec:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>F1-Score</h3>
                    <p style="font-size:28px; font-weight:bold">{f1:.3f}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### Confusion Matrix")
            fig_cm, ax_cm = plt.subplots(figsize=(6,4))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm,
                       xticklabels=['Tidak Terpilih', 'Terpilih'],
                       yticklabels=['Tidak Terpilih', 'Terpilih'])
            ax_cm.set_ylabel('Aktual')
            ax_cm.set_xlabel('Prediksi')
            st.pyplot(fig_cm)
                
        with tab_eval3:
            st.markdown("### ROC Curve")
            fpr, tpr, _ = roc_curve(y, y_prob_cv)
            roc_auc = auc(fpr, tpr)

            fig_roc, ax_roc = plt.subplots(figsize=(6,4))
            ax_roc.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
            ax_roc.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
            ax_roc.set_xlim([0.0, 1.0])
            ax_roc.set_ylim([0.0, 1.05])
            ax_roc.set_xlabel('False Positive Rate')
            ax_roc.set_ylabel('True Positive Rate')
            ax_roc.set_title('Receiver Operating Characteristic')
            ax_roc.legend(loc="lower right")
            ax_roc.grid(True, alpha=0.3)
            st.pyplot(fig_roc)

    elif menu == "Analisis Detail Guru":
        # ================= ANALISIS DETAIL =====================
        st.markdown('<div class="section-title">🔍 Analisis Detail Guru</div>', unsafe_allow_html=True)

        nama_guru = st.selectbox("Pilih Guru", df["Nama"].unique(), key="select_guru")
        data_guru = df[df["Nama"] == nama_guru].iloc[0]

        status = data_guru["Prediksi"]
        prob = data_guru["Probabilitas_Terpilih"]

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Status</h3>
                <p style="font-size:24px; font-weight:bold; color:{'#28a745' if status=='Terpilih' else '#dc3545'}">
                    {status}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_info2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Probabilitas</h3>
                <p style="font-size:24px; font-weight:bold">{prob:.2%}</p>
            </div>
            """, unsafe_allow_html=True)

        fitur_guru = data_guru[fitur.columns]

        if status == "Terpilih" and len(df_layak) > 0 and nama_guru in df_layak["Nama"].values:
            
            skor_guru = df_layak[df_layak["Nama"] == nama_guru]["Skor_AHP"].values[0]
            ranking_guru = df_layak[df_layak["Nama"] == nama_guru]["Ranking"].values[0]
            
            with col_info3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Ranking</h3>
                    <p style="font-size:24px; font-weight:bold">#{ranking_guru}</p>
                    <p>Skor: {skor_guru:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            # ===== TAMBAHKAN PROFIL 4 KOMPETENSI DI SINI =====
            if len(df_kompetensi) > 0:
                st.markdown("### 🎯 Ringkasan 4 Kompetensi")
                
                # Ambil data kompetensi guru
                guru_komp = df_kompetensi[df_kompetensi["Nama"] == nama_guru].iloc[0]
                
                kompetensi_cols = ['Pedagogik', 'Profesional', 'Sosial', 'Kepribadian']
                
                # Tampilkan dalam 4 kolom
                col_k1, col_k2, col_k3, col_k4 = st.columns(4)
                
                with col_k1:
                    st.metric("🧑‍🏫 Pedagogik", f"{guru_komp['Pedagogik']:.1f}")
                with col_k2:
                    st.metric("📚 Profesional", f"{guru_komp['Profesional']:.1f}")
                with col_k3:
                    st.metric("🤝 Sosial", f"{guru_komp['Sosial']:.1f}")
                with col_k4:
                    st.metric("⭐ Kepribadian", f"{guru_komp['Kepribadian']:.1f}")
                
                # Analisis kekuatan dan kelemahan
                strengths = []
                weaknesses = []
                
                for komp in kompetensi_cols:
                    nilai = guru_komp[komp]
                    if nilai >= 85:
                        strengths.append(f"✅ {komp}: {nilai:.1f}")
                    elif nilai < 70:
                        weaknesses.append(f"⚠️ {komp}: {nilai:.1f}")
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown("**💪 KEKUATAN**")
                    for s in strengths:
                        st.markdown(s)
                    if not strengths:
                        st.markdown("Tidak ada kompetensi sangat baik")
                
                with col_s2:
                    st.markdown("**📉 PERLU PENINGKATAN**")
                    for w in weaknesses:
                        st.markdown(w)
                    if not weaknesses:
                        st.markdown("Semua kompetensi sudah baik")
            
            st.markdown("### 📡 Profil Kriteria Guru")
            
            n_radar = min(8, len(kriteria_names))
            kriteria_radar = kriteria_names[:n_radar]
            nilai_guru_radar = fitur_guru[kriteria_radar].values
            
            if len(df[df["Prediksi"] == "Terpilih"]) > 0:
                rata_terpilih = df[df["Prediksi"] == "Terpilih"][kriteria_radar].mean().values
            else:
                rata_terpilih = [0] * n_radar
            
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=nilai_guru_radar,
                theta=kriteria_radar,
                fill='toself',
                name=nama_guru,
                line_color='gold'
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=rata_terpilih,
                theta=kriteria_radar,
                fill='toself',
                name='Rata-rata Guru Terpilih',
                line_color='blue',
                opacity=0.5
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title=f"Profil Kompetensi {nama_guru} vs Rata-rata Guru Terpilih"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True, key=f"radar_{nama_guru}")

            st.markdown("### 📊 Kontribusi Kriteria terhadap Skor Akhir")

            n_kontribusi = min(len(bobot), len(fitur_guru.values))
            kontribusi = fitur_guru.values[:n_kontribusi] * bobot[:n_kontribusi]
            kontribusi = kontribusi.astype(float)

            df_kontribusi = pd.DataFrame({
                "Kriteria": kriteria_names[:n_kontribusi],
                "Kontribusi": kontribusi,
                "Nilai Asli": fitur_guru.values[:n_kontribusi].astype(float)
            }).sort_values(by="Kontribusi", ascending=True)

            top3 = df_kontribusi.nlargest(3, "Kontribusi")
            st.markdown("### 🥇 Top 3 Kriteria Paling Berpengaruh")
            
            col_t1, col_t2, col_t3 = st.columns(3)
            for idx, (_, row) in enumerate(top3.iterrows()):
                with [col_t1, col_t2, col_t3][idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{'🥇' if idx==0 else '🥈' if idx==1 else '🥉'} {row['Kriteria']}</h4>
                        <p style="font-size:20px; font-weight:bold">{row['Kontribusi']:.2f}</p>
                        <p>Nilai: {row['Nilai Asli']:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            st.markdown("### 📉 Analisis Kelemahan (Guru Tidak Terpilih)")
            
            if len(df_layak) > 0:
                rata2_terpilih = df[df["Prediksi"] == "Terpilih"][fitur.columns].mean()
                nilai_guru = fitur_guru.values
                
                selisih = nilai_guru - rata2_terpilih.values
                
                df_selisih = pd.DataFrame({
                    "Kriteria": fitur.columns,
                    "Selisih": selisih,
                    "Nilai Guru": nilai_guru,
                    "Rata-rata Terpilih": rata2_terpilih.values
                }).sort_values(by="Selisih")
                
                fig_selisih = px.bar(df_selisih.head(10), y="Kriteria", x="Selisih",
                                    orientation='h',
                                    title="Top 10 Kriteria dengan Selisih Terbesar (Terendah)",
                                    color="Selisih",
                                    color_continuous_scale='RdBu_r',
                                    text=df_selisih.head(10)["Selisih"].apply(lambda x: f'{x:.1f}'))
                fig_selisih.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_selisih, use_container_width=True, key=f"bar_selisih_{nama_guru}")
                
                st.markdown("### 📊 Perbandingan dengan Rata-rata Guru Terpilih")
                
                n_compare = min(10, len(fitur.columns))
                df_compare = pd.DataFrame({
                    "Kriteria": fitur.columns[:n_compare],
                    "Nilai Guru": nilai_guru[:n_compare],
                    "Rata-rata Terpilih": rata2_terpilih.values[:n_compare]
                })
                
                df_compare_melted = pd.melt(df_compare, id_vars=["Kriteria"], 
                                           var_name="Kategori", value_name="Nilai")
                
                fig_compare = px.bar(df_compare_melted, x="Kriteria", y="Nilai", 
                                    color="Kategori", barmode="group",
                                    title="Perbandingan Nilai Guru vs Rata-rata Terpilih",
                                    color_discrete_map={"Nilai Guru": "#dc3545", 
                                                       "Rata-rata Terpilih": "#28a745"})
                st.plotly_chart(fig_compare, use_container_width=True, key=f"bar_compare_{nama_guru}")

    elif menu == "Analisis Strategis":
        # ================= ANALISIS STRATEGIS =====================
        st.markdown('<div class="section-title">🎯 Analisis Strategis untuk Kebijakan Sekolah</div>', unsafe_allow_html=True)
        
        if len(df_layak) > 0:
            
            st.markdown("### 📈 Analisis Kesenjangan (Gap Analysis) per Kriteria")
            
            rata_semua = df[fitur.columns].mean()
            rata_terpilih = df[df["Prediksi"] == "Terpilih"][fitur.columns].mean()
            maks_ideal = 100
            
            n_gap = min(16, len(fitur.columns))
            df_gap = pd.DataFrame({
                "Kriteria": fitur.columns[:n_gap],
                "Rata-rata Semua Guru": rata_semua.values[:n_gap],
                "Rata-rata Guru Terpilih": rata_terpilih.values[:n_gap],
                "Target Ideal": [maks_ideal] * n_gap,
                "Kesenjangan": maks_ideal - rata_semua.values[:n_gap]
            }).sort_values("Kesenjangan", ascending=False)
            
            df_gap_top = df_gap.head(10)
            
            fig_gap = go.Figure()
            
            fig_gap.add_trace(go.Bar(
                name='Rata-rata Semua Guru',
                x=df_gap_top['Kriteria'],
                y=df_gap_top['Rata-rata Semua Guru'],
                marker_color='lightblue'
            ))
            
            fig_gap.add_trace(go.Bar(
                name='Target Ideal',
                x=df_gap_top['Kriteria'],
                y=df_gap_top['Target Ideal'],
                marker_color='lightgray',
                opacity=0.5
            ))
            
            fig_gap.update_layout(
                title='10 Kriteria dengan Kesenjangan Terbesar dari Target Ideal',
                xaxis_title='Kriteria',
                yaxis_title='Nilai',
                barmode='overlay',
                yaxis=dict(range=[0, 105])
            )
            
            st.plotly_chart(fig_gap, use_container_width=True, key="bar_gap_analysis")

            # Tambahkan setelah gap analysis
            st.markdown("### 🏫 Rekomendasi Program Pelatihan")

            if len(df_gap) > 0:
                for i, row in df_gap.head(3).iterrows():
                    with st.expander(f"📚 {row['Kriteria']}"):
                        st.markdown(f"""
                        - **Kesenjangan:** {row['Kesenjangan']:.1f} poin dari target 100
                        - **Rata-rata saat ini:** {row['Rata-rata Semua Guru']:.1f}
                        - **Jumlah guru perlu pembinaan:** {len(df[df[row['Kriteria']] < 70])} orang
                        - **Rekomendasi:** {row['Rekomendasi'] if 'Rekomendasi' in row else 'Perlu pelatihan intensif'}
                        """)
            
            st.markdown("### 📋 Rekomendasi Kebijakan Berdasarkan Gap Analysis")
            
            rekomendasi_kebijakan = []
            for _, row in df_gap.head(5).iterrows():
                gap = row['Kesenjangan']
                if gap > 30:
                    prioritas = "TINGGI"
                    rekom = f"Segera adakan program pelatihan intensif untuk {row['Kriteria']}"
                elif gap > 20:
                    prioritas = "SEDANG"
                    rekom = f"Fasilitasi workshop pengembangan {row['Kriteria']}"
                else:
                    prioritas = "RENDAH"
                    rekom = f"Monitoring dan evaluasi berkala untuk {row['Kriteria']}"
                
                rekomendasi_kebijakan.append({
                    "Prioritas": prioritas,
                    "Kriteria": row['Kriteria'],
                    "Kesenjangan": f"{row['Kesenjangan']:.1f}",
                    "Rata-rata Saat Ini": f"{row['Rata-rata Semua Guru']:.1f}",
                    "Rekomendasi": rekom
                })
            
            df_rekom_kebijakan = pd.DataFrame(rekomendasi_kebijakan)
            st.dataframe(df_rekom_kebijakan, use_container_width=True)
            
            # Tambahkan setelah rekomendasi kebijakan
            st.markdown("### 👥 Program Mentoring")

            guru_mentor = df_layak[df_layak['Kategori'] == 'Sangat Baik']
            guru_mentee = df_layak[df_layak['Kategori'] == 'Perlu Pembinaan']

            if len(guru_mentor) > 0 and len(guru_mentee) > 0:
                st.success(f"**{len(guru_mentor)} mentor** siap membimbing **{len(guru_mentee)} mentee**")
                
                for i, (_, mentor) in enumerate(guru_mentor.head(3).iterrows()):
                    st.markdown(f"""
                    **Mentor {i+1}:** {mentor['Nama']} (Skor: {mentor['Skor_AHP']:.2f})
                    - Keunggulan: {mentor['Kategori']}
                    - Rekomendasi: {mentor['Rekomendasi']}
                    """)
            else:
                st.info("Belum ada pasangan mentor-mentee yang sesuai")

            st.markdown("### 🔥 Heatmap Perbandingan Kriteria (Top 10 Guru)")
            
            top10 = df_layak.head(10)
            n_heatmap_kriteria = min(8, len(fitur.columns))
            n_heatmap_guru = min(10, len(top10))
            
            if n_heatmap_guru > 0:
                kriteria_heatmap = fitur.columns[:n_heatmap_kriteria]
                
                data_heatmap = top10[kriteria_heatmap].values[:n_heatmap_guru]
                
                fig_heatmap = px.imshow(data_heatmap,
                                        labels=dict(x="Kriteria", y="Guru", color="Nilai"),
                                        x=kriteria_heatmap,
                                        y=top10['Nama'].values[:n_heatmap_guru],
                                        color_continuous_scale='RdYlGn',
                                        aspect="auto",
                                        title="Heatmap Nilai Kriteria Top 10 Guru")
                
                fig_heatmap.update_layout(height=500)
                st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_top10")
            
            st.markdown("### 📊 Distribusi Probabilitas Naive Bayes")
            
            fig_dist = px.histogram(df, x="Probabilitas_Terpilih", 
                                   nbins=20,
                                   title="Sebaran Probabilitas Terpilih (Naive Bayes)",
                                   labels={"Probabilitas_Terpilih": "Probabilitas"},
                                   color_discrete_sequence=['#1f77b4'])
            
            fig_dist.add_vline(x=df["Probabilitas_Terpilih"].mean(), 
                              line_dash="dash", line_color="red",
                              annotation_text=f"Rata-rata: {df['Probabilitas_Terpilih'].mean():.2%}")
            
            st.plotly_chart(fig_dist, use_container_width=True, key="histogram_prob_strategis")
            
            st.markdown("---")
            
                        
            # ================= TREND SKOR AHP 2025-2030 DENGAN INPUT MANUAL =================
            st.markdown("### 📈 Trend Skor 2025-2030 (Dengan Input Manual)")

            # Gabungkan semua guru (terpilih dan tidak terpilih)
            all_guru = df["Nama"].tolist()

            st.markdown("#### ✏️ Input Manual Skor per Guru")
            st.caption(f"Total: {len(all_guru)} guru")

            # Buat tabs untuk setiap guru (dengan scrolling)
            tabs = st.tabs([f"📊 {guru}" for guru in all_guru])

            # Dictionary untuk menyimpan input user
            user_inputs = {}

            for idx, (tab, guru) in enumerate(zip(tabs, all_guru)):
                with tab:
                    # Tentukan skor dasar 2025
                    if guru in df_layak["Nama"].values:
                        # Guru terpilih: pakai skor AHP
                        guru_data = df_layak[df_layak["Nama"] == guru].iloc[0]
                        skor_2025 = guru_data["Skor_AHP"]
                        ranking = guru_data["Ranking"]
                        kategori = guru_data["Kategori"]
                        status = "✅ Terpilih"
                        warna = "green"
                    else:
                        # Guru tidak terpilih: pakai rata-rata kriteria
                        guru_data = df[df["Nama"] == guru].iloc[0]
                        kriteria_cols = [f'K{i}' for i in range(1, 17)]
                        skor_2025 = guru_data[kriteria_cols].mean()
                        ranking = "-"
                        kategori = "Tidak Terpilih"
                        status = "❌ Tidak Terpilih"
                        warna = "red"
                    
                    # Tampilkan info guru
                    st.markdown(f"""
                    <div style="padding:10px; border-radius:5px; background-color:#f0f2f6; margin-bottom:10px">
                        <span style="color:{warna}; font-weight:bold">{status}</span><br>
                        <b>Ranking:</b> {ranking} | <b>Kategori:</b> {kategori}<br>
                        <b>Skor 2025:</b> {skor_2025:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Input untuk setiap tahun
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        input_2026 = st.number_input(
                            "2026", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=round(skor_2025 * 1.02, 2),
                            key=f"2026_{guru}"
                        )
                    with col2:
                        input_2027 = st.number_input(
                            "2027", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=round(input_2026 * 1.02, 2),
                            key=f"2027_{guru}"
                        )
                    with col3:
                        input_2028 = st.number_input(
                            "2028", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=round(input_2027 * 1.02, 2),
                            key=f"2028_{guru}"
                        )
                    with col4:
                        input_2029 = st.number_input(
                            "2029", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=round(input_2028 * 1.02, 2),
                            key=f"2029_{guru}"
                        )
                    with col5:
                        input_2030 = st.number_input(
                            "2030", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=round(input_2029 * 1.02, 2),
                            key=f"2030_{guru}"
                        )
                    
                    user_inputs[guru] = {
                        "2025": skor_2025,
                        "2026": input_2026,
                        "2027": input_2027,
                        "2028": input_2028,
                        "2029": input_2029,
                        "2030": input_2030,
                        "status": status,
                        "ranking": ranking,
                        "kategori": kategori
                    }

            # Tombol reset
            col_reset1, col_reset2 = st.columns([1, 5])
            with col_reset1:
                if st.button("🔄 Reset Semua"):
                    st.rerun()

            st.markdown("---")

            # ================= GRAFIK TREND =================
            st.markdown("#### 📊 Grafik Trend 2025-2030")

            # Filter untuk grafik
            filter_status = st.radio(
                "Tampilkan Guru:",
                ["Semua", "Terpilih Only", "Tidak Terpilih Only"],
                horizontal=True,
                key="filter_status_trend"
            )

            # Pilih guru berdasarkan filter
            if filter_status == "Terpilih Only":
                available_gurus = [g for g in all_guru if g in df_layak["Nama"].values]
            elif filter_status == "Tidak Terpilih Only":
                available_gurus = [g for g in all_guru if g not in df_layak["Nama"].values]
            else:
                available_gurus = all_guru

            # Pilih guru untuk grafik
            semua_guru = st.checkbox("Pilih Semua Guru", key="checkbox_semua_guru")
            if semua_guru:
                selected_gurus = available_gurus
            else:
                selected_gurus = st.multiselect(
                    "Pilih Guru untuk Ditampilkan di Grafik",
                    options=available_gurus,
                    default=available_gurus[:5] if len(available_gurus) > 5 else available_gurus,
                    key="multiselect_guru_trend"
                )

            if selected_gurus:
                tahun = ['2025', '2026', '2027', '2028', '2029', '2030']
                
                fig = go.Figure()
                
                for guru in selected_gurus:
                    if guru in user_inputs:
                        data = user_inputs[guru]
                        skor = [data[t] for t in tahun]
                        
                        # Tentukan style berdasarkan status
                        if "Terpilih" in data['status']:
                            line_style = dict(width=2.5)
                            name = f"✅ {guru} (Rank {data['ranking']})"
                        else:
                            line_style = dict(width=1.5, dash='dash')
                            name = f"❌ {guru}"
                        
                        fig.add_trace(go.Scatter(
                            x=tahun,
                            y=skor,
                            mode='lines+markers+text',
                            name=name,
                            line=line_style,
                            marker=dict(size=8),
                            text=[f"{s:.1f}" for s in skor],
                            textposition="top center",
                            textfont=dict(size=9)
                        ))
                
                fig.update_layout(
                    title=f'Trend Skor 2025-2030 ({len(selected_gurus)} Guru)',
                    xaxis_title='Tahun',
                    yaxis_title='Skor',
                    height=600,
                    hovermode='x unified',
                    xaxis=dict(tickmode='array', tickvals=tahun),
                    yaxis=dict(range=[0, 100], gridcolor='lightgray'),
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=10)
                    ),
                    margin=dict(r=250)
                )
                
                st.plotly_chart(fig, use_container_width=True, key="line_chart_trend")
                
                # ================= TABEL PERBANDINGAN =================
                st.markdown("#### 📋 Tabel Perbandingan Semua Guru")
                
                compare_data = []
                for guru in all_guru:
                    if guru in user_inputs:
                        data = user_inputs[guru]
                        
                        # Hitung CAGR
                        cagr = ((data["2030"] / data["2025"]) ** (1/5) - 1) * 100
                        
                        compare_data.append({
                            "Nama": guru,
                            "Status": data['status'],
                            "Ranking": data['ranking'],
                            "Kategori": data['kategori'],
                            "2025": data["2025"],
                            "2026": data["2026"],
                            "2027": data["2027"],
                            "2028": data["2028"],
                            "2029": data["2029"],
                            "2030": data["2030"],
                            "CAGR": f"{cagr:.1f}%"
                        })
                
                df_compare = pd.DataFrame(compare_data)
                st.dataframe(df_compare, use_container_width=True)
                
                # ================= STATISTIK =================
                st.markdown("#### 📊 Statistik Ringkasan")
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric("Total Guru", len(all_guru))
                with col_s2:
                    st.metric("Guru Terpilih", len(df_layak))
                with col_s3:
                    avg_2025 = df_compare['2025'].mean()
                    st.metric("Rata-rata 2025", f"{avg_2025:.2f}")
                with col_s4:
                    avg_2030 = df_compare['2030'].mean()
                    st.metric("Rata-rata 2030", f"{avg_2030:.2f}")
                
                # ================= EKSPOR DATA =================
                st.markdown("#### 💾 Ekspor Data")
                
                csv = df_compare.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data Semua Guru (CSV)",
                    data=csv,
                    file_name="trend_semua_guru_2025_2030.csv",
                    mime="text/csv",
                )
            
            st.markdown("### 📝 Ringkasan Eksekutif untuk Kepala Sekolah")
            
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            
            with col_sum1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Guru</h3>
                    <p style="font-size:32px; font-weight:bold">{len(df)}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_sum2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Lolos Seleksi</h3>
                    <p style="font-size:32px; font-weight:bold; color:#28a745">{len(df_layak)}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_sum3:
                pct_lolos = (len(df_layak) / len(df)) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Persentase Lolos</h3>
                    <p style="font-size:32px; font-weight:bold">{pct_lolos:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            if len(df_gap) > 0:
                kriteria_lemah = df_gap.head(3)['Kriteria'].tolist()
                
                st.markdown("### 💡 Rekomendasi Strategis")
                
                st.info(f"""
                **Berdasarkan analisis komprehensif, berikut rekomendasi strategis untuk pengembangan SDM:**
                
                1. **Prioritas Pengembangan:** Fokus pada peningkatan kompetensi di area {', '.join(kriteria_lemah)} yang memiliki kesenjangan terbesar dari target ideal.
                
                2. **Program Unggulan:** Manfaatkan guru dengan kategori "Sangat Baik" ({len(df_layak[df_layak['Kategori']=='Sangat Baik'])} orang) sebagai mentor untuk program peer teaching.
                
                3. **Pembinaan Intensif:** Sebanyak {len(df_layak[df_layak['Kategori']=='Perlu Pembinaan'])} guru memerlukan program pembinaan intensif, terutama di aspek {kriteria_lemah[0] if kriteria_lemah else 'yang perlu ditingkatkan'}.
                
                4. **Evaluasi Berkala:** Lakukan evaluasi setiap 6 bulan untuk memantau progress peningkatan kompetensi.
                """)
            
else:
    st.info("👈 Silakan upload file Excel untuk memulai analisis")

