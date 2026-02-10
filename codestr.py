import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide", page_title="Hierarchical Kategori Editor")

# ===============================
# TEMA BIRU CUSTOM
# ===============================
st.markdown(
    """
    <style>
    /* Tombol Terapkan */
    div.stButton > button {
        background-color: #1E90FF !important;  /* DodgerBlue */
        color: white !important;
        font-weight: bold;
    }

    /* Tombol Download */
    button[data-testid="stDownloadButton"] {
        background-color: #1E90FF !important;
        color: white !important;
        font-weight: bold;
    }

    /* Background main area dan sidebar */
    .css-1d391kg {background-color: #E6F0FA;} /* main area */
    .css-1v0mbdj {background-color: #E6F0FA;} /* sidebar */

    /* Header/subheader biru */
    h1, h2, h3, h4, h5, h6 {
        color: #1E90FF;
    }

    /* Info box biru */
    .stAlert {
        border-left: 5px solid #1E90FF;
        background-color: #E6F0FA;
        color: #000080;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("Hierarchical Kategori Editor")

# ===============================
# PATH CSV REFERENSI (BACKEND)
# ===============================
REF_PATH = Path("label_categories.csv")  # ganti sesuai nama file

# ===============================
# UPLOAD CSV PRODUK
# ===============================
file_data = st.file_uploader("CSV PRODUK", type=["csv"])

# ===============================
# LOAD CSV PRODUK
# ===============================
if file_data:
    if (
        "last_uploaded" not in st.session_state
        or st.session_state.last_uploaded != file_data.name
    ):
        df = pd.read_csv(file_data, keep_default_na=False)
        original_cols = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower()

        if "kategori" not in df.columns:
            df["kategori"] = ""

        st.session_state.df_edit = df
        st.session_state.last_uploaded = file_data.name
        st.session_state.original_cols = original_cols

# ===============================
# MAIN APP
# ===============================
if file_data:

    # LOAD REFERENSI BACKEND
    if not REF_PATH.exists():
        st.error(f"File referensi kategori tidak ditemukan: {REF_PATH}")
        st.stop()

    ref = pd.read_csv(REF_PATH, keep_default_na=False)
    ref.columns = ref.columns.str.lower().str.strip()

    df = st.session_state.df_edit
    level_cols = sorted([c for c in ref.columns if c.startswith("level_")])

    col_table, col_edit = st.columns([2,1])

    # ===============================
    # TABEL DATA
    # ===============================
    with col_table:
        st.subheader("Data Produk")
        st.write(f"Jumlah kolom terbaca: {len(df.columns)}")

        idx = st.number_input(
            "Pilih index baris",
            min_value=0,
            max_value=len(df)-1,
            value=0
        )

        st.dataframe(
            df,
            use_container_width=True,
            height=600
        )

    # ===============================
    # EDITOR KATEGORI
    # ===============================
    with col_edit:
        st.subheader("Pilih Kategori")

        subset = ref.copy()
        selections = {}

        for lvl in level_cols:
            options = sorted(subset[lvl].dropna().unique())
            if not options:
                break

            choice = st.selectbox(lvl, options)
            selections[lvl] = choice
            subset = subset[subset[lvl] == choice]

        kategori_final = None
        used_level = None

        for lvl in reversed(level_cols):
            val = selections.get(lvl)
            if val and str(val).strip() != "":
                kategori_final = val
                used_level = lvl
                break

        st.info(f"Kategori final ({used_level}) : {kategori_final}")

        # ===============================
        # TOMBOL TERAPKAN DAN DOWNLOAD SEBARIS
        # ===============================
        col_btn_terapkan, col_btn_download = st.columns([1,1])

        with col_btn_terapkan:
            if st.button("Terapkan"):
                st.session_state.df_edit.at[idx, "kategori"] = kategori_final
                st.success(f"Baris {idx} berhasil diupdate")
                st.rerun()

        with col_btn_download:
            csv = st.session_state.df_edit.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Hasil",
                csv,
                "hasil_kategori.csv",
                "text/csv",
                key="download1"
            )

else:
    st.info("Upload file CSV produk untuk mulai")
