import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURARE SECRETE ---
creds_json = st.secrets["GOOGLE_SHEETS_JSON"]
creds_dict = json.loads(creds_json)

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
    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Istoric Provocări")
    df_istoric = pd.DataFrame(ws_istoric.get_all_records())
    st.table(df_istoric)

with tab3:
    st.header("Zona Admin")
    parola = st.text_input("Parolă Admin", type="password")

    if parola == "secret123":
        # Expander 1: Adaugă Punctaj
        with st.expander("➕ Adaugă Punctaj pentru Utilizator"):
            users = ws_utilizatori.col_values(1)[1:]
            provocari_data = ws_provocari.get_all_records()
            df_provocari = pd.DataFrame(provocari_data)

            if not df_provocari.empty and 'Nume_Provocare' in df_provocari.columns:
                nume_selectat = st.selectbox("Utilizator", users)
                prov_selectata = st.selectbox("Provocare", df_provocari['Nume_Provocare'].tolist())

                if st.button("Înregistrează Punctaj"):
                    puncte = int(df_provocari.loc[df_provocari['Nume_Provocare'] == prov_selectata, 'Puncte_Standard'].values[0])
                    ws_istoric.append_row([datetime.now().strftime("%d/%m/%Y"), nume_selectat, prov_selectata, puncte])
                    
                    celula = ws_utilizatori.find(nume_selectat)
                    scor_vechi = int(ws_utilizatori.cell(celula.row, 2).value)
                    ws_utilizatori.update_cell(celula.row, 2, scor_vechi + puncte)
                    st.success("Punctaj adăugat!")
                    st.rerun()
            else:
                st.error("Eroare: Verifică dacă fila 'Provocari' are antetul 'Nume_Provocare'.")

        # Expander 2: Adaugă Utilizator Nou
        with st.expander("👤 Adaugă Utilizator Nou"):
            nume_nou = st.text_input("Nume Utilizator")
            if st.button("Salvează Utilizator"):
                ws_utilizatori.append_row([nume_nou, 0])
                st.success(f"Utilizatorul {nume_nou} a fost adăugat!")
                st.rerun()

        # Expander 3: Adaugă Provocare Nouă
        with st.expander("🎯 Adaugă Provocare Nouă"):
            id_prov = st.text_input("ID Provocare (ex: 1, 2, 3)")
            nume_prov = st.text_input("Nume Provocare")
            desc_prov = st.text_input("Descriere")
            puncte_prov = st.number_input("Puncte", min_value=0)
            
            if st.button("Salvează Provocare"):
                ws_provocari.append_row([id_prov, nume_prov, desc_prov, puncte_prov])
                st.success("Provocare adăugată!")
                st.rerun()
    else:
        st.warning("Introdu parola de admin pentru a modifica datele.")
