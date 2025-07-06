import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import random

# ➤ Έλεγχος Κωδικού Πρόσβασης
st.sidebar.title("🔐 Κωδικός Πρόσβασης")
password = st.sidebar.text_input("Εισάγετε τον κωδικό:", type="password")
if password != "katanomi2025":
    st.warning("Παρακαλώ εισάγετε έγκυρο κωδικό για πρόσβαση στην εφαρμογή.")
    st.stop()

# ➤ Ενεργοποίηση/Απενεργοποίηση Εφαρμογής
enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()

# ➤ Βοηθητικές συναρτήσεις

def is_mutual_friend(df, child1, child2):
    f1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΦΙΛΙΑ'].values[0])
    f2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΦΙΛΙΑ'].values[0])
    return (child2 in f1.split(",")) and (child1 in f2.split(","))

def has_conflict(df, child1, child2):
    c1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΣΥΓΚΡΟΥΣΗ'].values[0])
    c2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΣΥΓΚΡΟΥΣΗ'].values[0])
    return (child2 in c1.split(",")) or (child1 in c2.split(","))

def τοποθετηση(df, tmimata, μαθητης, τμημα, κλειδωμα=True):
    df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΤΜΗΜΑ'] = τμημα
    df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = κλειδωμα
    tmimata[τμημα].append(μαθητης)

# ➤ Βήμα 1 – Παιδιά Εκπαιδευτικών

def βημα_1_παιδια_εκπαιδευτικων(df, tmimata):
    παιδια = df[df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν']
    μη_τοποθετημενοι = παιδια[~παιδια['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(df[df['ΚΛΕΙΔΩΜΕΝΟΣ']]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])]
    μη_τοποθετημενοι = μη_τοποθετημενοι.sample(frac=1)
    τμηματα = list(tmimata.keys())
    δεικτης = 0
    for _, row in μη_τοποθετημενοι.iterrows():
        μαθητης = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        for _ in range(len(τμηματα)):
            τμημα = τμηματα[δεικτης % len(τμηματα)]
            ομαδα = df[df['ΤΜΗΜΑ'] == τμημα]
            if len(ομαδα) < 25 and not any(has_conflict(df, μαθητης, m) for m in ομαδα['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']):
                τοποθετηση(df, tmimata, μαθητης, τμημα)
                break
            δεικτης += 1

# ➤ Βήμα 2 – Ζωηροί Μαθητές

def βημα_2_ζωηροι(df, tmimata):
    ζωηροι = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    υπαρχοντες_ζωηροι = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True)]
    συνολο = len(ζωηροι) + len(υπαρχοντες_ζωηροι)
    τμηματα = list(tmimata.keys())
    κατανομη = {t: len(df[(df['ΤΜΗΜΑ'] == t) & (df['ΖΩΗΡΟΣ'] == 'Ν')]) for t in τμηματα}

    for _, row in ζωηροι.iterrows():
        μαθητης = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        τμηματα_sorted = sorted(τμηματα, key=lambda t: κατανομη[t])
        for τμημα in τμηματα_sorted:
            ομαδα = df[df['ΤΜΗΜΑ'] == τμημα]
            if len(ομαδα) < 25 and κατανομη[τμημα] < (συνολο + len(τμηματα) - 1) // len(τμηματα):
                αν_συγκρουση = any(has_conflict(df, μαθητης, m) for m in ομαδα['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])
                if not αν_συγκρουση:
                    τοποθετηση(df, tmimata, μαθητης, τμημα)
                    κατανομη[τμημα] += 1
                    break

# ➤ Βήμα 3 – Παιδιά με Ιδιαιτερότητες

def βημα_3_ιδιαιτεροτητες(df, tmimata):
    παιδια = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    τμηματα = list(tmimata.keys())
    κατανομη = {t: len(df[(df['ΤΜΗΜΑ'] == t) & (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')]) for t in τμηματα}
    for _, row in παιδια.iterrows():
        μαθητης = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        τμηματα_sorted = sorted(τμηματα, key=lambda t: (κατανομη[t], len(tmimata[t])))
        for τμημα in τμηματα_sorted:
            ομαδα = df[df['ΤΜΗΜΑ'] == τμημα]
            if len(ομαδα) < 25 and not any(has_conflict(df, μαθητης, m) for m in ομαδα['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']):
                τοποθετηση(df, tmimata, μαθητης, τμημα)
                κατανομη[τμημα] += 1
                break

# ➤ Βήμα 4 – Φίλοι Παιδιών Βημάτων 1–3

def βημα_4_φιλοι_τοποθετημενων(df, tmimata):
    τοποθετημενοι = df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True]['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].tolist()
    φιλοι = df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False]
    for _, row in φιλοι.iterrows():
        μαθητης = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        φιλοι_του = str(row['ΦΙΛΙΑ']).split(',')
        for φ in φιλοι_του:
            φ = φ.strip()
            if φ in τοποθετημενοι and is_mutual_friend(df, μαθητης, φ):
                τμημα_φ = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == φ, 'ΤΜΗΜΑ'].values[0]
                if len(tmimata[τμημα_φ]) < 25 and not any(has_conflict(df, μαθητης, m) for m in tmimata[τμημα_φ]):
                    τοποθετηση(df, tmimata, μαθητης, τμημα_φ)
                    break

# ➤ Βήμα 5 – Έλεγχος Ποιοτικών Χαρακτηριστικών

def βημα_5_στατιστικα_ανα_τμημα(df):
    στατιστικα = {}
    for τμημα in df['ΤΜΗΜΑ'].dropna().unique():
        ομαδα = df[df['ΤΜΗΜΑ'] == τμημα]
        στατιστικα[τμημα] = {
            'Σύνολο': len(ομαδα),
            'Αγόρια': len(ομαδα[ομαδα['ΦΥΛΟ'] == 'Α']),
            'Κορίτσια': len(ομαδα[ομαδα['ΦΥΛΟ'] == 'Κ']),
            'Καλή Γνώση': len(ομαδα[ομαδα['ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'] == 'Ν']),
            'Μαθησιακή Ικανότητα': len(ομαδα[ομαδα['ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ'] == 'Ν'])
        }
    return στατιστικα

# ➤ Πλήρης Κατανομή (Βήματα 1–5)

def πληρης_κατανομη(df):
    df['ΤΜΗΜΑ'] = None
    df['ΚΛΕΙΔΩΜΕΝΟΣ'] = False
    max_per_class = 25
    num_students = len(df)
    num_classes = (num_students + max_per_class - 1) // max_per_class
    tmimata = {f'Τμήμα {i+1}': [] for i in range(num_classes)}
    βημα_1_παιδια_εκπαιδευτικων(df, tmimata)
    βημα_2_ζωηροι(df, tmimata)
    βημα_3_ιδιαιτεροτητες(df, tmimata)
    βημα_4_φιλοι_τοποθετημενων(df, tmimata)
    στατιστικα = βημα_5_στατιστικα_ανα_τμημα(df)
    return df, tmimata, στατιστικα
