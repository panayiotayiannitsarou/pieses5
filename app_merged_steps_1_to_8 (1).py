
# --- START OF FILE: d6bd581f-3531-4260-be7e-3096c48dad5d.py ---
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

# --- END OF FILE: d6bd581f-3531-4260-be7e-3096c48dad5d.py ---

# --- START OF FILE: 9bdfce57-8af9-4966-954e-2fe989495f58.py ---

# ➤ Βήμα 6 – Φιλικές Ομάδες ανά Γνώση Ελληνικών
def βημα_6_φιλικες_ομαδες_γλωσσικα(df, tmimata):
    υπολοιποι = df[(df['ΤΜΗΜΑ'].isna()) & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    ονοματα = υπολοιποι['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].tolist()
    φιλιες = []
    for i in range(len(ονοματα)):
        for j in range(i + 1, len(ονοματα)):
            a, b = ονοματα[i], ονοματα[j]
            if is_mutual_friend(df, a, b) and not has_conflict(df, a, b):
                φιλιες.append({a, b})
    ομάδες = []
    while φιλιες:
        ομάδα = φιλιες.pop(0)
        συγχωνεύθηκε = False
        for i, υπ in enumerate(φιλιες):
            if ομάδα & υπ:
                νέα_ομάδα = ομάδα | υπ
                if len(νέα_ομάδα) <= 3:
                    ομάδες.append(list(νέα_ομάδα))
                    φιλιες.pop(i)
                    συγχωνεύθηκε = True
                    break
        if not συγχωνεύθηκε:
            ομάδες.append(list(ομάδα))
    κατηγοριες = {'καλη': [], 'οχι': [], 'μικτη': []}
    for ομάδα in ομάδες:
        γνωσεις = [df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == m, 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'].values[0] for m in ομάδα]
        if all(g == 'Ν' for g in γνωσεις):
            κατηγοριες['καλη'].append(ομάδα)
        elif all(g == 'Ο' for g in γνωσεις):
            κατηγοριες['οχι'].append(ομάδα)
        else:
            κατηγοριες['μικτη'].append(ομάδα)
    for κατηγορια in ['οχι', 'καλη', 'μικτη']:
        for ομάδα in κατηγοριες[κατηγορια]:
            καταλληλα = []
            for τμημα in tmimata:
                αν_χωρα = len(tmimata[τμημα]) + len(ομάδα) <= 25
                αν_συγκρουση = any(has_conflict(df, m, a) for m in ομάδα for a in tmimata[τμημα])
                if αν_χωρα and not αν_συγκρουση:
                    καταλληλα.append(τμημα)
            if καταλληλα:
                επιλογη = min(καταλληλα, key=lambda t: abs(
                    sum(df.loc[df['ΤΜΗΜΑ'] == t, 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'] == 'Ν') -
                    sum(df.loc[df['ΤΜΗΜΑ'] == t, 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'] == 'Ο')
                ))
                for μαθητης in ομάδα:
                    τοποθετηση(df, tmimata, μαθητης, επιλογη)

# ➤ Βήμα 7 – Υπόλοιποι Μαθητές Χωρίς Φιλίες
def βημα_7_χωρις_φιλους(df, tmimata):
    υποψηφιοι = df[(df['ΤΜΗΜΑ'].isna()) & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)].copy()
    def εχει_αμοιβαια_φιλια(μαθητης):
        φιλοι = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΦΙΛΙΑ'].values[0]).split(',')
        φιλοι = [f.strip() for f in φιλοι if f.strip()]
        for φ in φιλοι:
            if φ in df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values and is_mutual_friend(df, μαθητης, φ):
                if df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == φ, 'ΤΜΗΜΑ'].isna().values[0]:
                    return True
        return False
    χωρις_φιλους = [m for m in υποψηφιοι['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] if not εχει_αμοιβαια_φιλια(m)]
    for μαθητης in χωρις_φιλους:
        καλυτερο_τμημα = None
        καλυτερο_score = float('inf')
        for τμημα in tmimata:
            αν_χωρα = len(tmimata[τμημα]) < 25
            αν_συγκρουση = any(has_conflict(df, μαθητης, m) for m in tmimata[τμημα])
            if not αν_χωρα or αν_συγκρουση:
                continue
            ομαδα = df[df['ΤΜΗΜΑ'] == τμημα]
            φυλο = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΦΥΛΟ'].values[0]
            ελληνικα = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'].values[0]
            μαθησιακη = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == μαθητης, 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ'].values[0]
            count_φυλο = len(ομαδα[ομαδα['ΦΥΛΟ'] == φυλο])
            count_ελληνικα = len(ομαδα[ομαδα['ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'] == ελληνικα])
            count_μαθησιακη = len(ομαδα[ομαδα['ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ'] == μαθησιακη])
            score = count_φυλο + count_ελληνικα + count_μαθησιακη
            if score < καλυτερο_score:
                καλυτερο_score = score
                καλυτερο_τμημα = τμημα
        if καλυτερο_τμημα:
            τοποθετηση(df, tmimata, μαθητης, καλυτερο_τμημα)

# ➤ Βήμα 8 – Τελικός Έλεγχος Αποκλίσεων
def βημα_8_τελικος_ελεγχος(df, tmimata):
    χαρακτηριστικά = ['ΦΥΛΟ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
    max_diff = 3
    τμηματα = list(tmimata.keys())
    αποκλισεις = []
    for x in χαρακτηριστικά:
        μοναδικες = df[x].dropna().unique()
        for τιμή in μοναδικες:
            for i in range(len(τμηματα)):
                for j in range(i + 1, len(τμηματα)):
                    τμ1, τμ2 = τμηματα[i], τμηματα[j]
                    count1 = len(df[(df['ΤΜΗΜΑ'] == τμ1) & (df[x] == τιμή)])
                    count2 = len(df[(df['ΤΜΗΜΑ'] == τμ2) & (df[x] == τιμή)])
                    diff = abs(count1 - count2)
                    if diff > max_diff:
                        αποκλισεις.append(f"⚠️ Απόκλιση {diff} για '{x} = {τιμή}' μεταξύ {τμ1} και {τμ2}")
    return αποκλισεις

# --- END OF FILE: 9bdfce57-8af9-4966-954e-2fe989495f58.py ---
