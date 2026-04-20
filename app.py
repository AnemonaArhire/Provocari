import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime


# Funcție utilitară pentru numere
def safe_int(value):
    try:
        return int(str(value).strip())
    except:
        return 0


# --- CONFIGURARE ---
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_JSON"])
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open("AppProvocari")

ws_utilizatori = sh.worksheet("Utilizatori")
ws_istoric = sh.worksheet("Istoric")
ws_provocari = sh.worksheet("Provocari")

st.title("🏆 Dashboard Provocări")

tab1, tab2, tab3 = st.tabs(["Clasament", "Istoric", "Admin"])

with tab1:
    st.header("Punctaj Total")
    df = pd.DataFrame(ws_utilizatori.get_all_records())
    st.dataframe(df, width='stretch')

with tab2:
    st.header("Istoric Provocări")

    # Citim datele
    raw_istoric = ws_istoric.get_all_records()
    df_istoric = pd.DataFrame(raw_istoric)

    # Curățăm spațiile goale de pe margini
    df_istoric.columns = df_istoric.columns.str.strip()

    # DEBUG: Această linie va afișa pe ecran exact cum vede Python coloanele tale
    # Verifică ce scrie pe ecran în aplicație!
    # st.write("Coloanele găsite în fila 'Istoric' sunt:", df_istoric.columns.tolist())

    if not df_istoric.empty:
        # Verificăm dacă coloana Nume_Utilizator chiar există
        target_user_col = 'Nume_Utilizator'  # <<--- Dacă debug-ul de mai sus îți arată altceva, schimbă aici
        target_prov_col = 'Tip_Provocare'  # <<--- Dacă debug-ul îți arată altceva, schimbă aici

        if target_user_col in df_istoric.columns and target_prov_col in df_istoric.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                f_user = st.multiselect("Filtrează Utilizator", df_istoric[target_user_col].unique())
            with col2:
                f_prov = st.multiselect("Filtrează Provocare", df_istoric[target_prov_col].unique())
            with col3:
                sort_by = st.selectbox("Sortează după", ["Data", target_user_col, "Puncte_Castigate"])

            # Aplicare Filtre
            dff = df_istoric.copy()
            if f_user: dff = dff[dff[target_user_col].isin(f_user)]
            if f_prov: dff = dff[dff[target_prov_col].isin(f_prov)]

            # Sortare
            if sort_by in dff.columns:
                dff = dff.sort_values(by=sort_by)

            st.table(dff)
        else:
            st.error("Eroare: Nu am găsit coloanele necesare în tabelul 'Istoric'.")
            st.write("Coloanele pe care le-am găsit sunt:", df_istoric.columns.tolist())
    else:
        st.write("Istoricul este gol.")
with tab3:
    st.header("Zona Admin")
    parola = st.text_input("Parolă Admin", type="password")

    if parola == "secret123":
        # 1. Adaugă Punctaj (Partial)
        with st.expander("➕ Adaugă Punctaj"):
            users = ws_utilizatori.col_values(2)[1:]  # Coloana B (Nume utilizator)
            df_provocari = pd.DataFrame(ws_provocari.get_all_records())

            nume_selectat = st.selectbox("Utilizator", users)
            prov_selectata = st.selectbox("Provocare", df_provocari['Nume_Provocare'].tolist())

            # Punctaj Default din tabel
            default_pts = int(
                df_provocari.loc[df_provocari['Nume_Provocare'] == prov_selectata, 'barem punctare'].values[0])
            puncte_input = st.number_input("Puncte acordate", value=default_pts)

            if st.button("Înregistrează Punctaj"):
                # Istoric
                ws_istoric.append_row(
                    [datetime.now().strftime("%d/%m/%Y"), nume_selectat, prov_selectata, puncte_input])

                # Update Punctaj (Coloana 3 = Punctaj toatal)
                celula = ws_utilizatori.find(nume_selectat)
                val_actuala = ws_utilizatori.cell(celula.row, 3).value
                ws_utilizatori.update_cell(celula.row, 3, safe_int(val_actuala) + puncte_input)

                st.success(f"Adăugat {puncte_input} puncte!")
                st.rerun()

        # 2. Adaugă Utilizator Nou
        with st.expander("👤 Adaugă Utilizator Nou"):
            nume_nou = st.text_input("Nume Utilizator")
            if st.button("Salvează Utilizator"):
                # ID (poți automatiza) | Nume | Punctaj
                ws_utilizatori.append_row([len(users) + 1, nume_nou, 0])
                st.rerun()

        # 3. Adaugă Provocare Nouă
        with st.expander("🎯 Adaugă Provocare Nouă"):
            id_prov = st.text_input("ID Provocare")
            nume_prov = st.text_input("Nume Provocare")
            desc_prov = st.text_input("Descriere")
            puncte_prov = st.number_input("Barem Standard", min_value=0)

            if st.button("Salvează Provocare"):
                ws_provocari.append_row([id_prov, nume_prov, desc_prov, puncte_prov])
                st.rerun()
    else:
        st.warning("Introdu parola.")
