import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide", page_title="Hierarchical Kategori Editor")

# ===============================
# STYLE
# ===============================
st.markdown("""
<style>
div.stButton > button {
    background-color: #1E90FF !important;
    color: white !important;
    font-weight: bold;
}
button[data-testid="stDownloadButton"] {
    background-color: #1E90FF !important;
    color: white !important;
    font-weight: bold;
}
h1, h2, h3 { color: #1E90FF; }
</style>
""", unsafe_allow_html=True)

st.title("Hierarchical Kategori Editor")

REF_PATH = Path("label_categories.csv")

file_data = st.file_uploader("CSV PRODUK", type=["csv"])

# ===============================
# LOAD DATA USER
# ===============================
if file_data:
    if (
        "last_uploaded" not in st.session_state
        or st.session_state.last_uploaded != file_data.name
    ):
        df_raw = pd.read_csv(file_data, keep_default_na=False)
        df_raw.columns = df_raw.columns.str.strip().str.lower()

        base_cols = ["nama_produk", "deskripsi", "nama_kategori"]
        for col in base_cols:
            if col not in df_raw.columns:
                df_raw[col] = ""

        st.session_state.df_edit = df_raw[base_cols].copy()
        st.session_state.last_uploaded = file_data.name

# ===============================
# MAIN APP
# ===============================
if file_data:

    if not REF_PATH.exists():
        st.error("File label_categories.csv tidak ditemukan")
        st.stop()

    # ===== Load referensi kategori =====
    ref = pd.read_csv(REF_PATH, keep_default_na=False)
    ref.columns = ref.columns.str.lower().str.strip()

    level_cols = sorted([c for c in ref.columns if c.startswith("level_")])[:6]

    # ===== Buat kolom last_child =====
    def get_last_child(row):
        for col in reversed(level_cols):
            if str(row[col]).strip():
                return row[col]
        return ""

    ref["last_child"] = ref.apply(get_last_child, axis=1)

    df = st.session_state.df_edit

    # ===============================
    # INISIALISASI LEVEL UNTUK SEMUA BARIS (AUTO MAP)
    # ===============================
    if not all(col in df.columns for col in level_cols):
        merged = df.merge(
            ref[level_cols + ["last_child"]],
            how="left",
            left_on="nama_kategori",
            right_on="last_child"
        )

        for col in level_cols:
            merged[col] = merged[col].fillna("")

        df = merged[["nama_produk", "deskripsi", "nama_kategori"] + level_cols]
        st.session_state.df_edit = df

    col_table, col_edit = st.columns([2, 1])

    # ===============================
    # TABEL DATA
    # ===============================
    with col_table:
        st.subheader("Data Produk")

        idx = st.number_input(
            "Pilih index baris",
            min_value=0,
            max_value=len(df) - 1,
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

            default = (
                options.index(df.at[idx, lvl])
                if df.at[idx, lvl] in options
                else 0
            )

            choice = st.selectbox(lvl, options, index=default, key=f"{lvl}_{idx}")
            selections[lvl] = choice
            subset = subset[subset[lvl] == choice]

        kategori_final = ""
        for lvl in reversed(level_cols):
            if selections.get(lvl):
                kategori_final = selections[lvl]
                break

        st.info(f"Kategori final : {kategori_final}")

        # ===============================
        # TOMBOL TERAPKAN, HAPUS, DOWNLOAD
        # ===============================
        col_terapkan, col_hapus, col_download = st.columns(3)

        # Terapkan kategori
        with col_terapkan:
            if st.button("Terapkan"):
                df.at[idx, "nama_kategori"] = kategori_final
                for lvl in level_cols:
                    df.at[idx, lvl] = selections.get(lvl, "")
                st.session_state.df_edit = df
                st.success("Kategori & parent berhasil diperbarui")
                st.rerun()

        # Hapus baris
        with col_hapus:
            if st.button("Hapus Baris"):
                if 0 <= idx < len(df):
                    df.drop(idx, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    st.session_state.df_edit = df
                    st.success(f"Baris ke-{idx} berhasil dihapus")
                    st.rerun()

        # Download hasil
        with col_download:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Hasil",
                csv,
                "hasil_kategori.csv",
                "text/csv"
            )

else:
    st.info("Upload file CSV produk untuk mulai")
