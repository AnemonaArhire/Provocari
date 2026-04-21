import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime

# --- FUNCȚIE AJUTĂTOARE ---
def safe_int(value):
    try: return int(str(value).strip())
    except: return 0

# --- CONFIGURARE ---
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_JSON"])
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open("AppProvocari")

ws_utilizatori = sh.worksheet("Utilizatori")
ws_istoric = sh.worksheet("Istoric")
ws_provocari = sh.worksheet("Provocari")

st.title("🏆 Dashboard Provocări")

if st.button("🔄 Reîncarcă datele"):
    st.rerun()

# 4 Tab-uri acum
tab1, tab2, tab3, tab4 = st.tabs(["Clasament", "Istoric", "Provocări", "Admin"])

with tab1:
    st.header("Punctaj Total")
    df = pd.DataFrame(ws_utilizatori.get_all_records())
    st.dataframe(df, width='stretch')

with tab2:
    st.header("Istoric Provocări")
    df_istoric = pd.DataFrame(ws_istoric.get_all_records())
    df_istoric.columns = df_istoric.columns.str.strip() # Curățare spații
    
    if not df_istoric.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            f_user = st.multiselect("Filtrează Utilizator", df_istoric['id utilizat'].unique())
        with col2:
            f_prov = st.multiselect("Filtrează Provocare", df_istoric['tip provocare'].unique())
        with col3:
            sort_by = st.selectbox("Sortează după", ["data", "id utilizat", "punctaj"])

        dff = df_istoric.copy()
        if f_user: dff = dff[dff['id utilizat'].isin(f_user)]
        if f_prov: dff = dff[dff['tip provocare'].isin(f_prov)]
        
        dff = dff.sort_values(by=sort_by)
        st.table(dff)

with tab3:
    st.header("Lista Provocărilor")
    df_prov = pd.DataFrame(ws_provocari.get_all_records())
    df_prov.columns = df_prov.columns.str.strip() # Curățare spații
    
    if not df_prov.empty:
        niv_selectat = st.multiselect("Filtrează după Nivel", df_prov['nivel'].unique())
        if niv_selectat:
            df_prov = df_prov[df_prov['nivel'].isin(niv_selectat)]
        st.dataframe(df_prov, use_container_width=True)

with tab4:
    st.header("Zona Admin")
    parola = st.text_input("Parolă Admin", type="password")

    if parola == "secret123":
        # 1. Adaugă Punctaj
        with st.expander("➕ Adaugă Punctaj"):
            # Coloana 2 in Utilizatori este 'nume utilizator'
            users = ws_utilizatori.col_values(2)[1:] 
            df_provocari = pd.DataFrame(ws_provocari.get_all_records())
            df_provocari.columns = df_provocari.columns.str.strip()
            
            nume_selectat = st.selectbox("Utilizator", users)
            prov_selectata = st.selectbox("Provocare", df_provocari['Nume_Provocare'].tolist())
            
            default_pts = int(df_provocari.loc[df_provocari['Nume_Provocare'] == prov_selectata, 'barem punctare'].values[0])
            puncte_input = st.number_input("Puncte acordate", value=default_pts)

            if st.button("Înregistrează Punctaj"):
                with st.spinner("Se salvează..."):
                    ws_istoric.append_row([datetime.now().strftime("%d/%m/%Y"), nume_selectat, prov_selectata, puncte_input])
                    
                    celula = ws_utilizatori.find(nume_selectat)
                    val_actuala = ws_utilizatori.cell(celula.row, 3).value
                    ws_utilizatori.update_cell(celula.row, 3, safe_int(val_actuala) + puncte_input)
                st.success("Punctaj adăugat!")
                st.rerun()

        # 2. Adaugă Utilizator Nou
        with st.expander("👤 Adaugă Utilizator Nou"):
            nume_nou = st.text_input("nume utilizator")
            if st.button("Salvează Utilizator"):
                with st.spinner("Se salvează..."):
                    ws_utilizatori.append_row([len(users)+1, nume_nou, 0])
                st.success(f"Utilizatorul {nume_nou} a fost adăugat!")
                st.rerun()

        # 3. Adaugă Provocare Nouă
        with st.expander("🎯 Adaugă Provocare Nouă"):
            id_prov = st.text_input("ID Provocare")
            nume_prov = st.text_input("Nume Provocare")
            desc_prov = st.text_input("Descriere")
            nivel_prov = st.text_input("Nivel")
            puncte_prov = st.number_input("Barem Standard", min_value=0)
            
            if st.button("Salvează Provocare"):
                with st.spinner("Se salvează..."):
                    ws_provocari.append_row([id_prov, nume_prov, desc_prov, nivel_prov, puncte_prov])
                st.success("Provocare adăugată!")
                st.rerun()
    else:
        if parola: st.warning("Parolă greșită.")
