# app.py

import streamlit as st
import streamlit as st

# ================= LOGIN SEDERHANA =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ================= CEK LOGIN =================
if not st.session_state.logged_in:
    st.markdown("""
        <div style="max-width: 400px; margin: 50px auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; color: #1f4e79;">🔐 Login Admin</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username atau password salah!")
    
    st.stop()  # Berhenti di sini

# ================= APLIKASI UTAMA =================
st.title("Selamat Datang, Administrator...")
st.write("Siap Memulai Seleksi Guru Terbaik?")

# Sidebar dengan logout
with st.sidebar:
    st.write("Menu Utama")
    # ... menu lainnya ...
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
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
from datetime import datetime
import time

st.set_page_config(
    page_title="Sistem Cerdas Pemilihan Guru Terbaik",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= STYLE ELEGAN =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Premium */
    .premium-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ff6b6b 100%);
        padding: 2.5rem;
        border-radius: 30px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .premium-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    .badge-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1.5rem;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
    }
    
    .premium-badge {
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 500;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.8rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.25);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Metric Card Premium */
    .metric-premium {
        background: linear-gradient(145deg, #ffffff, #f5f7ff);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 10px 10px 20px rgba(102, 126, 234, 0.1),
                   -10px -10px 20px rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .metric-premium:hover {
        box-shadow: 15px 15px 30px rgba(102, 126, 234, 0.15),
                   -15px -15px 30px rgba(255, 255, 255, 0.9);
    }
    
    .metric-premium h3 {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value-premium {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    /* Animated Button */
    .btn-premium {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        padding: 0.9rem 1.8rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        width: 100%;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .btn-premium:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(102, 126, 234, 0.4);
    }
    
    .btn-premium::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        bottom: -50%;
        left: -50%;
        background: linear-gradient(to bottom, rgba(229, 172, 142, 0), rgba(255,255,255,0.3) 50%, rgba(229, 172, 142, 0));
        transform: rotateZ(60deg) translate(-5em, 7.5em);
        animation: sheen 4s infinite;
    }
    
    @keyframes sheen {
        100% {
            transform: rotateZ(60deg) translate(1em, -9em);
        }
    }
    
    /* Section Header */
    .section-header-premium {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        position: relative;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-header-premium::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #ff6b6b);
        border-radius: 2px;
        animation: slideGradient 3s infinite;
    }
    
    @keyframes slideGradient {
        0% { left: 0; width: 80px; }
        50% { left: 50%; width: 150px; transform: translateX(-50%); }
        100% { left: calc(100% - 80px); width: 80px; }
    }
    
    /* Stat Card Modern */
    .stat-card-modern {
        background: white;
        border-radius: 15px;
        padding: 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 0.8rem;
    }
    
    .stat-card-modern:hover {
        transform: translateX(5px);
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    .stat-icon-modern {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea20, #764ba220);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #667eea;
        font-size: 1.5rem;
    }
    
    /* Table Premium */
    .dataframe {
        border-collapse: separate;
        border-spacing: 0 8px;
        width: 100%;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 12px 15px;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: none;
    }
    
    .dataframe td {
        background: white;
        padding: 12px 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: none;
        transition: all 0.2s ease;
    }
    
    .dataframe tr:hover td {
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.15);
        transform: scale(1.01);
    }
    
    /* Progress Bar Premium */
    .progress-premium {
        background: #e9ecef;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
        position: relative;
    }
    
    .progress-premium-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2, #ff6b6b);
        border-radius: 10px;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .progress-premium-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Tab Premium */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 0.8rem;
        border-radius: 50px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        color: #6c757d;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar Premium */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Tooltip Premium */
    [data-testid="stTooltip"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Scrollbar Premium */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* Footer Premium */
    .footer-premium {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid rgba(102, 126, 234, 0.1);
        margin-top: 3rem;
        background: linear-gradient(180deg, transparent, rgba(102, 126, 234, 0.05));
    }
</style>
""", unsafe_allow_html=True)

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

# ================= HEADER PREMIUM =================
st.markdown("""
    <div class="premium-header">
        <h1>🏆 Sistem Cerdas Pemilihan Guru Terbaik</h1>
        <p>Hybrid: Naive Bayes Classifier (NBC) + Analytical Hierarchy Process (AHP)</p>
        <div class="badge-container">
            <span class="premium-badge">✨ Akurasi 88%</span>
            <span class="premium-badge">⚡ Real-time Analysis</span>
            <span class="premium-badge">🎯 Multi Kriteria</span>
            <span class="premium-badge">📊 4 Kompetensi</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #667eea; font-weight: 600;">👩‍🎓 Jelajahi Menu</h3>
        <div style="width: 50px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 0.5rem auto;"></div>
    </div>
""", unsafe_allow_html=True)
    
    menu = st.selectbox(
        "Pilih Menu",
        ["Dashboard Keputusan", "Evaluasi Model", "Analisis Detail Guru", "Analisis Strategis"],
        label_visibility="collapsed"
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Upload file dengan desain premium
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <span style="background: linear-gradient(135deg, #667eea20, #764ba220); padding: 0.5rem 1rem; border-radius: 30px; color: #667eea; font-weight: 500;">
                📁 Upload Data
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload File Excel",
        type=["xlsx"],
        label_visibility="collapsed"
    )
    
    st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(102,126,234,0.05); border-radius: 15px;">
            <p style="color: #667eea; font-weight: 600; margin-bottom: 0.5rem;">📌 Format File</p>
            <p style="font-size: 0.9rem; color: #6c757d;">Nama, K1-K16, Label<br><span style="color: #667eea;">Label: Terpilih / Tidak Terpilih</span></p>
        </div>
    """, unsafe_allow_html=True)

# ================= MAIN =================
if uploaded_file is not None:

    with st.spinner("🔮 Sedang memproses data..."):
        time.sleep(1)
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
            st.sidebar.markdown("""
                <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 1rem; border-radius: 10px; color: #155724; font-weight: 500; text-align: center;">
                    ✅ AHP selesai: {} guru terpilih
                </div>
            """.format(len(df_layak)), unsafe_allow_html=True)

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
            st.sidebar.markdown("""
                <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 1rem; border-radius: 10px; color: #155724; font-weight: 500; text-align: center; margin-top: 0.5rem;">
                    ✅ Analisis kompetensi selesai
                </div>
            """, unsafe_allow_html=True)
        else:
            df_layak_kompetensi = pd.DataFrame()
            st.sidebar.markdown("""
                <div style="background: linear-gradient(135deg, #fbc2c2 0%, #ff6b6b 100%); padding: 1rem; border-radius: 10px; color: #721c24; font-weight: 500; text-align: center;">
                    ⚠️ Tidak ada guru terpilih
                </div>
            """, unsafe_allow_html=True)
        
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
            st.markdown('<div class="section-header-premium">📊 Dashboard Keputusan</div>', unsafe_allow_html=True)

            # Tambahkan di bagian bawah Dashboard Keputusan
            st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea10, #764ba210); padding: 1.5rem; border-radius: 20px; margin-bottom: 2rem;">
                    <h3 style="color: #667eea; margin-bottom: 0.5rem;">📄 Draft Surat Keputusan</h3>
                    <p style="color: #6c757d;">Buat SK otomatis berdasarkan hasil seleksi</p>
                </div>
            """, unsafe_allow_html=True)

            if len(df_layak) > 0:
                # Pilihan nama Kepala Sekolah
                col_sk1, col_sk2 = st.columns([2, 1])
                with col_sk1:
                    nama_kepsek = st.text_input("Nama Kepala Sekolah", value="Dr. H. Ahmad Saepudin, M.Pd")
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
                st.markdown("""
                    <div class="glass-card">
                        <h4 style="color: #667eea; margin-bottom: 1rem;">📄 Surat Keputusan Guru Terbaik</h4>
                """, unsafe_allow_html=True)
                
                st.text_area("Draft SK (siap cetak)", sk_content, height=400)
                
                # Tombol download
                # Tombol download dengan styling
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d2:
                    st.markdown("""
                        <style>
                        div.stButton > button {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 0.75rem 1.5rem;
                            border-radius: 50px;
                            font-weight: 600;
                            width: 100%;
                            transition: all 0.3s ease;
                        }
                        div.stButton > button:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 10px 20px rgba(102,126,234,0.3);
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
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
            st.markdown('<div class="section-header-premium" style="margin-top: 2rem;">🔎 Hasil Klasifikasi Naive Bayes</div>', unsafe_allow_html=True)
            
            df_nb = df[["Nama", "Label", "Prediksi", "Probabilitas_Terpilih"]].copy()
            df_nb["Probabilitas_Terpilih"] = df_nb["Probabilitas_Terpilih"].apply(lambda x: f"{x:.2%}")
            st.dataframe(df_nb, use_container_width=True)
            
            st.markdown("---")
            
            col_nb1, col_nb2 = st.columns(2)
            with col_nb1:
                st.markdown('<h4 style="color: #667eea;">📊 Distribusi Prediksi</h4>', unsafe_allow_html=True)
                pred_counts = df["Prediksi"].value_counts().reset_index()
                pred_counts.columns = ["Status", "Jumlah"]
                fig_pie = px.pie(pred_counts, values="Jumlah", names="Status", 
                                color_discrete_sequence=["#667eea", "#ff6b6b"],
                                title="Proporsi Guru Terpilih vs Tidak Terpilih")
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart_dashboard")
            
            with col_nb2:
                st.markdown('<h4 style="color: #667eea;">📈 Distribusi Probabilitas</h4>', unsafe_allow_html=True)
                fig_hist = px.histogram(df, x="Probabilitas_Terpilih", nbins=20,
                                       title="Sebaran Probabilitas Terpilih",
                                       labels={"Probabilitas_Terpilih": "Probabilitas"},
                                       color_discrete_sequence=["#667eea"])
                fig_hist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                st.plotly_chart(fig_hist, use_container_width=True, key="histogram_dashboard")
            
            # Peringkat Akhir
            if len(df_layak) > 0:
                st.markdown('<div class="section-header-premium">🏆 Peringkat Akhir Guru</div>', unsafe_allow_html=True)
                
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
                                    color_discrete_map={'Terpilih': '#667eea', 'Tidak Terpilih': '#ff6b6b'})
                    
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
                colors = ['#ffd700' if i == 0 else '#c0c0c0' if i == 1 else '#cd7f32' if i == 2 else '#667eea' 
                         for i in range(len(df_top))]
                
                fig_rank = px.bar(df_top, y="Nama", x="Skor_AHP", 
                                 orientation='h',
                                 title=f"Top {top_n} Guru Terbaik",
                                 labels={"Skor_AHP": "Skor Akhir", "Nama": ""},
                                 color_discrete_sequence=colors,
                                 text="Skor_AHP")
                fig_rank.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig_rank.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                st.plotly_chart(fig_rank, use_container_width=True, key="bar_chart_ranking")

                st.markdown('<div class="section-header-premium">🥇 Top 3 Guru Terbaik</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                for idx, col in enumerate([col1, col2, col3]):
                    if idx < len(df_layak):
                        guru = df_layak.iloc[idx]
                        with col:
                            st.markdown(f"""
                            <div class="metric-premium">
                                <h3 style="text-align:center; color: {'#ffd700' if idx==0 else '#c0c0c0' if idx==1 else '#cd7f32'}">
                                    {'🏆' if idx==0 else '🥈' if idx==1 else '🥉'} Peringkat #{idx+1}
                                </h3>
                                <h2 style="text-align:center; font-size:1.8rem; margin:0.5rem 0;">{guru['Nama']}</h2>
                                <p style="text-align:center; font-size:2rem; font-weight:700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{guru['Skor_AHP']:.2f}</p>
                                <p style="text-align:center; margin-top:0.5rem;"><span class="badge badge-success">{guru['Kategori']}</span></p>
                            </div>
                            """, unsafe_allow_html=True)

                # ================= REKOMENDASI PASCA SELEKSI =================
                if len(df_layak) > 0:
                    st.markdown('<div class="section-header-premium">🎯 Rencana Tindak Lanjut & Penghargaan</div>', unsafe_allow_html=True)
                    
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
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #ffd70020, #ffed4e20); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border: 1px solid #ffd700;">
                                <h3 style="color: #ffd700;">🌟 GURU TERBAIK: {guru_terbaik['Nama']}</h3>
                                <p style="font-size:1.2rem;">Skor: {guru_terbaik['Skor_AHP']:.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_g1, col_g2 = st.columns(2)
                            with col_g1:
                                st.markdown("""
                                <div class="glass-card">
                                    <h4 style="color: #667eea;">🏅 Penghargaan Khusus</h4>
                                    <ul style="list-style-type: none; padding: 0;">
                                        <li style="margin: 0.5rem 0;">✅ Piagam Penghargaan Kepala Sekolah</li>
                                        <li style="margin: 0.5rem 0;">✅ Uang Pembinaan</li>
                                        <li style="margin: 0.5rem 0;">✅ Prioritas Pelatihan Nasional</li>
                                        <li style="margin: 0.5rem 0;">✅ Menjadi Duta Sekolah</li>
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_g2:
                                st.markdown("""
                                <div class="glass-card">
                                    <h4 style="color: #667eea;">🎯 Goals 1 Tahun</h4>
                                    <ul style="list-style-type: none; padding: 0;">
                                        <li style="margin: 0.5rem 0;">✅ Mempertahankan predikat</li>
                                        <li style="margin: 0.5rem 0;">✅ Menjadi mentor 3 guru lain</li>
                                        <li style="margin: 0.5rem 0;">✅ Membuat 1 publikasi ilmiah</li>
                                        <li style="margin: 0.5rem 0;">✅ Mewakili sekolah di lomba</li>
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Per kategori
                        kategori_list = [
                            ("Sangat Baik", "🏆"),
                            ("Baik", "📚"),
                            ("Cukup", "📋"),
                            ("Perlu Pembinaan", "⚠️")
                        ]
                        
                        for kategori, icon in kategori_list:
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
                            st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #667eea;">📅 Program Tindak Lanjut</h4>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 0.5rem 0;">📅 Rapat pleno penetapan guru terbaik</li>
                                    <li style="margin: 0.5rem 0;">📢 Pengumuman resmi</li>
                                    <li style="margin: 0.5rem 0;">🎉 Acara apresiasi</li>
                                    <li style="margin: 0.5rem 0;">📝 Penerbitan SK</li>
                                    <li style="margin: 0.5rem 0;">🤝 Program mentoring</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #667eea;">💰 Alokasi Anggaran</h4>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 0.5rem 0;">💰 Penghargaan guru terbaik</li>
                                    <li style="margin: 0.5rem 0;">📚 Program pembinaan</li>
                                    <li style="margin: 0.5rem 0;">🖥️ Pengembangan kompetensi</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_s2:
                            st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #667eea;">⏱️ Timeline</h4>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 0.5rem 0;"><b>Minggu 1:</b> Penetapan & pengumuman</li>
                                    <li style="margin: 0.5rem 0;"><b>Minggu 2:</b> Acara apresiasi</li>
                                    <li style="margin: 0.5rem 0;"><b>Minggu 3:</b> Mentoring dimulai</li>
                                    <li style="margin: 0.5rem 0;"><b>Bulan 1-3:</b> Evaluasi berkala</li>
                                    <li style="margin: 0.5rem 0;"><b>Bulan 6:</b> Evaluasi tengah tahun</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #667eea;">📊 Indikator Keberhasilan</h4>
                                <ul style="list-style-type: none; padding: 0;">
                                    <li style="margin: 0.5rem 0;">✅ 80% guru terpilih pertahankan predikat</li>
                                    <li style="margin: 0.5rem 0;">✅ 50% guru tidak terpilih meningkat</li>
                                    <li style="margin: 0.5rem 0;">✅ Rata-rata nilai naik 5%</li>
                                    <li style="margin: 0.5rem 0;">✅ Mentoring berjalan aktif</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Ringkasan eksekutif
                    st.markdown("---")
                    st.markdown('<div class="section-header-premium">📊 Ringkasan Program</div>', unsafe_allow_html=True)
                    
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
                    st.markdown('<div class="section-header-premium">📊 Profil 4 Kompetensi Utama</div>', unsafe_allow_html=True)
                    
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
                        line_color='#667eea',
                        fillcolor='rgba(102, 126, 234, 0.2)'
                    ))
                    
                    # Tambahkan rata-rata semua guru terpilih
                    if len(df_layak_kompetensi) > 0:
                        rata_kompetensi = df_layak_kompetensi[kompetensi_cols].mean().values
                        fig.add_trace(go.Scatterpolar(
                            r=rata_kompetensi.tolist() + [rata_kompetensi[0]],
                            theta=kompetensi_cols + [kompetensi_cols[0]],
                            fill='toself',
                            name='Rata-rata Guru Terpilih',
                            line_color='#ff6b6b',
                            fillcolor='rgba(255, 107, 107, 0.2)'
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        title=f"Profil 4 Kompetensi - {guru_pilih}",
                        showlegend=True,
                        height=500,
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", size=12)
                    )
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.plotly_chart(fig, use_container_width=True, key=f"radar_kompetensi_{guru_pilih}")
                    
                    with col2:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.markdown("#### 📊 Detail Nilai")
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
                        st.markdown('</div>', unsafe_allow_html=True)

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

                st.markdown('<div class="section-header-premium">📊 Perbandingan Skor AHP vs Probabilitas Naive Bayes</div>', unsafe_allow_html=True)
                
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
                                    color_discrete_map={'Skor AHP (0-100)': '#667eea', 
                                                       'Probabilitas NB (0-100%)': '#ff6b6b'})
                fig_compare.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                st.plotly_chart(fig_compare, use_container_width=True, key="bar_chart_compare")

            st.markdown('<div class="section-header-premium">⚖️ Bobot Kriteria AHP</div>', unsafe_allow_html=True)
            
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
            fig_bobot.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12)
            )
            st.plotly_chart(fig_bobot, use_container_width=True, key="bar_chart_bobot")

        elif menu == "Evaluasi Model":
            # ================= EVALUASI =====================
            st.markdown('<div class="section-header-premium">📊 Evaluasi Model (LOOCV)</div>', unsafe_allow_html=True)

            tab_eval1, tab_eval3 = st.tabs([
                "📊 Metrik Klasifikasi",
                "📈 ROC Curve"
            ])
            
            with tab_eval1:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Accuracy</h3>
                        <div class="metric-value-premium">{acc:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Precision</h3>
                        <div class="metric-value-premium">{prec:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col3:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Recall</h3>
                        <div class="metric-value-premium">{rec:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col4:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>F1-Score</h3>
                        <div class="metric-value-premium">{f1:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("### Confusion Matrix")
                fig_cm, ax_cm = plt.subplots(figsize=(6,4))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm,
                           xticklabels=['Tidak Terpilih', 'Terpilih'],
                           yticklabels=['Tidak Terpilih', 'Terpilih'])
                ax_cm.set_ylabel('Aktual')
                ax_cm.set_xlabel('Prediksi')
                plt.title('Confusion Matrix', fontfamily='Inter')
                st.pyplot(fig_cm)
                    
            with tab_eval3:
                st.markdown("### ROC Curve")
                fpr, tpr, _ = roc_curve(y, y_prob_cv)
                roc_auc = auc(fpr, tpr)

                fig_roc, ax_roc = plt.subplots(figsize=(6,4))
                ax_roc.plot(fpr, tpr, color='#667eea', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
                ax_roc.plot([0, 1], [0, 1], color='#ff6b6b', lw=2, linestyle='--', label='Random')
                ax_roc.set_xlim([0.0, 1.0])
                ax_roc.set_ylim([0.0, 1.05])
                ax_roc.set_xlabel('False Positive Rate')
                ax_roc.set_ylabel('True Positive Rate')
                ax_roc.set_title('Receiver Operating Characteristic')
                ax_roc.legend(loc="lower right")
                ax_roc.grid(True, alpha=0.3)
                plt.setp(ax_roc.xaxis.label, fontfamily='Inter')
                plt.setp(ax_roc.yaxis.label, fontfamily='Inter')
                plt.setp(ax_roc.title, fontfamily='Inter')
                st.pyplot(fig_roc)

        elif menu == "Analisis Detail Guru":
            # ================= ANALISIS DETAIL =====================
            st.markdown('<div class="section-header-premium">🔍 Analisis Detail Guru</div>', unsafe_allow_html=True)

            nama_guru = st.selectbox("Pilih Guru", df["Nama"].unique(), key="select_guru")
            data_guru = df[df["Nama"] == nama_guru].iloc[0]

            status = data_guru["Prediksi"]
            prob = data_guru["Probabilitas_Terpilih"]

            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.markdown(f"""
                <div class="metric-premium">
                    <h3>Status</h3>
                    <div class="metric-value-premium" style="color: {'#667eea' if status=='Terpilih' else '#ff6b6b'}">
                        {status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_info2:
                st.markdown(f"""
                <div class="metric-premium">
                    <h3>Probabilitas</h3>
                    <div class="metric-value-premium">{prob:.2%}</div>
                </div>
                """, unsafe_allow_html=True)

            fitur_guru = data_guru[fitur.columns]

            if status == "Terpilih" and len(df_layak) > 0 and nama_guru in df_layak["Nama"].values:
                
                skor_guru = df_layak[df_layak["Nama"] == nama_guru]["Skor_AHP"].values[0]
                ranking_guru = df_layak[df_layak["Nama"] == nama_guru]["Ranking"].values[0]
                
                with col_info3:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Ranking</h3>
                        <div class="metric-value-premium">#{ranking_guru}</div>
                        <p style="font-size:1rem; margin-top:0.5rem;">Skor: {skor_guru:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ===== TAMBAHKAN PROFIL 4 KOMPETENSI DI SINI =====
                if len(df_kompetensi) > 0:
                    st.markdown('<div class="section-header-premium">🎯 Ringkasan 4 Kompetensi</div>', unsafe_allow_html=True)
                    
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
                        st.markdown("""
                        <div class="glass-card">
                            <h4 style="color: #667eea;">💪 KEKUATAN</h4>
                        """, unsafe_allow_html=True)
                        for s in strengths:
                            st.markdown(s)
                        if not strengths:
                            st.markdown("Tidak ada kompetensi sangat baik")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_s2:
                        st.markdown("""
                        <div class="glass-card">
                            <h4 style="color: #ff6b6b;">📉 PERLU PENINGKATAN</h4>
                        """, unsafe_allow_html=True)
                        for w in weaknesses:
                            st.markdown(w)
                        if not weaknesses:
                            st.markdown("Semua kompetensi sudah baik")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="section-header-premium">📡 Profil Kriteria Guru</div>', unsafe_allow_html=True)
                
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
                    line_color='#667eea',
                    fillcolor='rgba(102, 126, 234, 0.2)'
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=rata_terpilih,
                    theta=kriteria_radar,
                    fill='toself',
                    name='Rata-rata Guru Terpilih',
                    line_color='#ff6b6b',
                    fillcolor='rgba(255, 107, 107, 0.2)'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title=f"Profil Kompetensi {nama_guru} vs Rata-rata Guru Terpilih",
                    height=500,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                
                st.plotly_chart(fig_radar, use_container_width=True, key=f"radar_{nama_guru}")

                st.markdown('<div class="section-header-premium">📊 Kontribusi Kriteria terhadap Skor Akhir</div>', unsafe_allow_html=True)

                n_kontribusi = min(len(bobot), len(fitur_guru.values))
                kontribusi = fitur_guru.values[:n_kontribusi] * bobot[:n_kontribusi]
                kontribusi = kontribusi.astype(float)

                df_kontribusi = pd.DataFrame({
                    "Kriteria": kriteria_names[:n_kontribusi],
                    "Kontribusi": kontribusi,
                    "Nilai Asli": fitur_guru.values[:n_kontribusi].astype(float)
                }).sort_values(by="Kontribusi", ascending=True)

                top3 = df_kontribusi.nlargest(3, "Kontribusi")
                st.markdown('<div class="section-header-premium">🥇 Top 3 Kriteria Paling Berpengaruh</div>', unsafe_allow_html=True)
                
                col_t1, col_t2, col_t3 = st.columns(3)
                for idx, (_, row) in enumerate(top3.iterrows()):
                    with [col_t1, col_t2, col_t3][idx]:
                        st.markdown(f"""
                        <div class="metric-premium">
                            <h4 style="color: {'#ffd700' if idx==0 else '#c0c0c0' if idx==1 else '#cd7f32'}">
                                {'🥇' if idx==0 else '🥈' if idx==1 else '🥉'} {row['Kriteria']}
                            </h4>
                            <div class="metric-value-premium">{row['Kontribusi']:.2f}</div>
                            <p style="font-size:1rem; margin-top:0.5rem;">Nilai: {row['Nilai Asli']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)

            else:
                st.markdown('<div class="section-header-premium">📉 Analisis Kelemahan (Guru Tidak Terpilih)</div>', unsafe_allow_html=True)
                
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
                    fig_selisih.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", size=12)
                    )
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
                                        color_discrete_map={"Nilai Guru": "#ff6b6b", 
                                                           "Rata-rata Terpilih": "#667eea"})
                    fig_compare.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", size=12)
                    )
                    st.plotly_chart(fig_compare, use_container_width=True, key=f"bar_compare_{nama_guru}")

        elif menu == "Analisis Strategis":
            # ================= ANALISIS STRATEGIS =====================
            st.markdown('<div class="section-header-premium">🎯 Analisis Strategis untuk Kebijakan Sekolah</div>', unsafe_allow_html=True)
            
            if len(df_layak) > 0:
                
                st.markdown('<div class="section-header-premium">📈 Analisis Kesenjangan (Gap Analysis) per Kriteria</div>', unsafe_allow_html=True)
                
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
                    marker_color='#667eea'
                ))
                
                fig_gap.add_trace(go.Bar(
                    name='Target Ideal',
                    x=df_gap_top['Kriteria'],
                    y=df_gap_top['Target Ideal'],
                    marker_color='#ff6b6b',
                    opacity=0.5
                ))
                
                fig_gap.update_layout(
                    title='10 Kriteria dengan Kesenjangan Terbesar dari Target Ideal',
                    xaxis_title='Kriteria',
                    yaxis_title='Nilai',
                    barmode='overlay',
                    yaxis=dict(range=[0, 105]),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                
                st.plotly_chart(fig_gap, use_container_width=True, key="bar_gap_analysis")

                # Tambahkan setelah gap analysis
                st.markdown('<div class="section-header-premium">🏫 Rekomendasi Program Pelatihan</div>', unsafe_allow_html=True)

                if len(df_gap) > 0:
                    for i, row in df_gap.head(3).iterrows():
                        with st.expander(f"📚 {row['Kriteria']}"):
                            st.markdown(f"""
                            - **Kesenjangan:** {row['Kesenjangan']:.1f} poin dari target 100
                            - **Rata-rata saat ini:** {row['Rata-rata Semua Guru']:.1f}
                            - **Jumlah guru perlu pembinaan:** {len(df[df[row['Kriteria']] < 70])} orang
                            - **Rekomendasi:** {row['Rekomendasi'] if 'Rekomendasi' in row else 'Perlu pelatihan intensif'}
                            """)
                
                st.markdown('<div class="section-header-premium">📋 Rekomendasi Kebijakan Berdasarkan Gap Analysis</div>', unsafe_allow_html=True)
                
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
                st.markdown('<div class="section-header-premium">👥 Program Mentoring</div>', unsafe_allow_html=True)

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

                st.markdown('<div class="section-header-premium">🔥 Heatmap Perbandingan Kriteria (Top 10 Guru)</div>', unsafe_allow_html=True)
                
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
                
                st.markdown('<div class="section-header-premium">📊 Distribusi Probabilitas Naive Bayes</div>', unsafe_allow_html=True)
                
                fig_dist = px.histogram(df, x="Probabilitas_Terpilih", 
                                       nbins=20,
                                       title="Sebaran Probabilitas Terpilih (Naive Bayes)",
                                       labels={"Probabilitas_Terpilih": "Probabilitas"},
                                       color_discrete_sequence=['#667eea'])
                
                fig_dist.add_vline(x=df["Probabilitas_Terpilih"].mean(), 
                                  line_dash="dash", line_color="#ff6b6b",
                                  annotation_text=f"Rata-rata: {df['Probabilitas_Terpilih'].mean():.2%}")
                
                fig_dist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12)
                )
                st.plotly_chart(fig_dist, use_container_width=True, key="histogram_prob_strategis")
                
                st.markdown("---")
                
                            
                # ================= TREND SKOR AHP 2025-2030 DENGAN INPUT MANUAL =================
                st.markdown('<div class="section-header-premium">📈 Trend Skor 2025-2030 (Dengan Input Manual)</div>', unsafe_allow_html=True)

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
                        margin=dict(r=250),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
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
                
                st.markdown('<div class="section-header-premium">📝 Ringkasan Eksekutif untuk Kepala Sekolah</div>', unsafe_allow_html=True)
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Total Guru</h3>
                        <div class="metric-value-premium">{len(df)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_sum2:
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Lolos Seleksi</h3>
                        <div class="metric-value-premium" style="color: #667eea;">{len(df_layak)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_sum3:
                    pct_lolos = (len(df_layak) / len(df)) * 100
                    st.markdown(f"""
                    <div class="metric-premium">
                        <h3>Persentase Lolos</h3>
                        <div class="metric-value-premium" style="color: #ff6b6b;">{pct_lolos:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(df_gap) > 0:
                    kriteria_lemah = df_gap.head(3)['Kriteria'].tolist()
                    
                    st.markdown("""
                    <div class="glass-card">
                        <h4 style="color: #667eea;">💡 Rekomendasi Strategis</h4>
                    """, unsafe_allow_html=True)
                    
                    st.info(f"""
                    **Berdasarkan analisis komprehensif, berikut rekomendasi strategis untuk pengembangan SDM:**
                    
                    1. **Prioritas Pengembangan:** Fokus pada peningkatan kompetensi di area {', '.join(kriteria_lemah)} yang memiliki kesenjangan terbesar dari target ideal.
                    
                    2. **Program Unggulan:** Manfaatkan guru dengan kategori "Sangat Baik" ({len(df_layak[df_layak['Kategori']=='Sangat Baik'])} orang) sebagai mentor untuk program peer teaching.
                    
                    3. **Pembinaan Intensif:** Sebanyak {len(df_layak[df_layak['Kategori']=='Perlu Pembinaan'])} guru memerlukan program pembinaan intensif, terutama di aspek {kriteria_lemah[0] if kriteria_lemah else 'yang perlu ditingkatkan'}.
                    
                    4. **Evaluasi Berkala:** Lakukan evaluasi setiap 6 bulan untuk memantau progress peningkatan kompetensi.
                    """)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
else:
    st.markdown("""
        <div style="text-align: center; padding: 4rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">👋</div>
            <h2 style="color: #667eea; margin-bottom: 1rem;">Selamat Datang di Sistem Cerdas Pemilihan Guru Terbaik</h2>
            <p style="font-size: 1.2rem; color: #6c757d; margin-bottom: 2rem;">
            Silakan upload file Excel melalui sidebar untuk memulai analisis.
            </p>
            <div style="width: 100px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 2rem auto;"></div>
        </div>
    """, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
    <div class="footer-premium">
        <p>© 2026 Sistem Cerdas Pemilihan Guru Terbaik | Hybrid : Naive Bayes + AHP</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;"><p>© Develoved by Jerzi Bleszynski Pratama</p>
    </div>
""", unsafe_allow_html=True)
