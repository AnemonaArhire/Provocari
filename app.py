import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURARE SECRETE ---
# Citim JSON-ul din secretele Streamlit
creds_json = st.secrets["GOOGLE_SHEETS_JSON"]
creds_dict = json.loads(creds_json)

# Conectare
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open("AppProvocari")  # <--- AICI PUNE NUMELE EXACT AL TABELULUI TĂU

# Încărcăm filele
ws_utilizatori = sh.worksheet("Utilizatori")
ws_istoric = sh.worksheet("Istoric")
ws_provocari = sh.worksheet("Provocari")

st.title("🏆 Dashboard Provocări")

tab1, tab2, tab3 = st.tabs(["Clasament", "Istoric", "Admin"])

with tab1:
    st.header("Punctaj Total")
    # Citim datele și le afișăm
    data_utilizatori = ws_utilizatori.get_all_records()
    df = pd.DataFrame(data_utilizatori)
    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Istoric Provocări")
    data_istoric = ws_istoric.get_all_records()
    st.table(pd.DataFrame(data_istoric))

with tab3:
    st.header("Modificare Date")
    parola = st.text_input("Parolă Admin", type="password")

    if parola == "secret123":  # Schimbă parola aici
        # Listăm utilizatorii și provocările
        users = ws_utilizatori.col_values(1)[1:]  # Sărim peste cap de tabel
        provocari_data = ws_provocari.get_all_records()
        df_provocari = pd.DataFrame(provocari_data)

        nume_selectat = st.selectbox("Selectează Utilizator", users)
        prov_selectata = st.selectbox("Selectează Provocare", df_provocari['Nume_Provocare'].tolist())

        if st.button("Adaugă Punctaj"):
            # 1. Găsim punctele pentru provocarea selectată
            puncte_provocare = int(
                df_provocari.loc[df_provocari['Nume_Provocare'] == prov_selectata, 'Puncte_Standard'].values[0])

            # 2. Adăugăm în Istoric
            data_azi = datetime.now().strftime("%d/%m/%Y")
            ws_istoric.append_row([data_azi, nume_selectat, prov_selectata, puncte_provocare])

            # 3. Update Punctaj Total
            # Căutăm rândul utilizatorului
            celula_user = ws_utilizatori.find(nume_selectat)
            row_index = celula_user.row

            # Citim punctajul vechi
            scor_vechi = int(ws_utilizatori.cell(row_index, 2).value)

            # Calculăm și salvăm
            ws_utilizatori.update_cell(row_index, 2, scor_vechi + puncte_provocare)

            st.success(f"Adăugat: {puncte_provocare} puncte pentru {nume_selectat}!")
            st.rerun()  # Reîmprospătăm pagina să se vadă scorul nou

    else:
        st.warning("Acces interzis.")
