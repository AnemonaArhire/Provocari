import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# Conectare (folosește fișierul JSON descărcat de la Google Cloud)
gc = gspread.service_account(filename="credentials.json")
sh = gc.open("NumeleDocumentuluiTau")

# Încărcăm datele din fiecare filă
ws_utilizatori = sh.worksheet("Utilizatori")
ws_istoric = sh.worksheet("Istoric")
ws_provocari = sh.worksheet("Provocari")

st.title("🏆 Dashboard Provocări")

# Creăm tab-uri în interfața aplicației pentru o organizare vizuală clară
tab1, tab2, tab3 = st.tabs(["Clasament", "Istoric", "Admin (Doar tu)"])

with tab1:
    st.header("Punctaj Total")
    df_utilizatori = pd.DataFrame(ws_utilizatori.get_all_records())
    st.dataframe(df_utilizatori)

with tab2:
    st.header("Istoric Provocări")
    df_istoric = pd.DataFrame(ws_istoric.get_all_records())
    st.table(df_istoric)

with tab3:
    st.header("Modificare Date")
    parola = st.text_input("Parolă Admin", type="password")

    if parola == "secret123":
        # Formular pentru a adăuga o provocare îndeplinită
        nume = st.selectbox("Utilizator", ws_utilizatori.col_values(1)[1:])
        provocare = st.selectbox("Provocare", ws_provocari.col_values(2)[1:])

        if st.button("Adaugă Punctaj"):
            # 1. Adăugăm în Istoric
            data_azi = datetime.now().strftime("%d/%m/%Y")
            ws_istoric.append_row([data_azi, nume, provocare, 10])  # Presupunem 10 puncte

            # 2. Update Punctaj Total (Logica ta de calcul)
            # Aici cauți rândul utilizatorului și actualizezi coloana Punctaj_Total
            st.success(f"Provocare adăugată pentru {nume}!")
    else:
        st.warning("Acces interzis.")