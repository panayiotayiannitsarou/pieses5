
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

# ➤ Κατανομή μαθητών (τυχαία προς το παρόν)
def πληρης_κατανομη(df):
    df['ΤΜΗΜΑ'] = None
    df['ΚΛΕΙΔΩΜΕΝΟΣ'] = False

    max_per_class = 25
    num_students = len(df)
    num_classes = (num_students + max_per_class - 1) // max_per_class
    tmimata = {f'Τμήμα {i+1}': [] for i in range(num_classes)}

    μαθητες = df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].tolist()
    random.shuffle(μαθητες)
    for i, μαθητης in enumerate(μαθητες):
        τμημα = f'Τμήμα {i % num_classes + 1}'
        τοποθετηση(df, tmimata, μαθητης, τμημα)

    return df

# ➤ Δημιουργία αρχείου Excel για export
def create_excel_file(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Κατανομή')
    return output.getvalue()

# ➤ Ραβδογράμματα
def plot_distribution(df, column, title):
    fig, ax = plt.subplots()
    df.groupby(['ΤΜΗΜΑ', column]).size().unstack(fill_value=0).plot(kind='bar', stacked=True, ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Αριθμός Μαθητών')
    st.pyplot(fig)

# ➤ Εφαρμογή Streamlit
st.title("📘 Ψηφιακή Κατανομή Μαθητών Α' Δημοτικού")

uploaded_file = st.file_uploader("🔹 Εισαγωγή Excel αρχείου μαθητών", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο φορτώθηκε επιτυχώς!")

    if st.button("🔹 Εκτέλεση Κατανομής Μαθητών"):
        df = πληρης_κατανομη(df)
        st.session_state["df_katanomi"] = df
        st.success("✅ Ολοκληρώθηκε η κατανομή μαθητών.")

if "df_katanomi" in st.session_state:
    df = st.session_state["df_katanomi"]

    if st.button("🔹 Λήψη Excel με Κατανομή"):
        excel_bytes = create_excel_file(df)
        st.download_button("📥 Κατέβασε το αρχείο Excel", data=excel_bytes, file_name="katanomi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("📊 Πίνακας Στατιστικών Κατανομής")
    st.dataframe(df.groupby('ΤΜΗΜΑ')[['ΦΥΛΟ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']].agg(lambda x: (x == 'Ν').sum()))

    st.subheader("📊 Ραβδογράμματα Κατανομής")
    επιλογη = st.radio("Επιλέξτε τύπο γραφήματος:", ["Συγκεντρωτικό", "Ξεχωριστά ανά κατηγορία"])
    if επιλογη == "Συγκεντρωτικό":
        plot_distribution(df, 'ΦΥΛΟ', "Κατανομή Φύλου")
        plot_distribution(df, 'ΖΩΗΡΟΣ', "Κατανομή Ζωηρών Μαθητών")
        plot_distribution(df, 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', "Κατανομή Ιδιαιτεροτήτων")
        plot_distribution(df, 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', "Κατανομή Γνώσης Ελληνικών")
        plot_distribution(df, 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', "Κατανομή Παιδιών Εκπαιδευτικών")
        plot_distribution(df, 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ', "Κατανομή Μαθησιακής Ικανότητας")
    else:
        for col in ['ΦΥΛΟ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']:
            plot_distribution(df, col, f"Κατανομή βάσει {col}")

# ➤ Δήλωση Πνευματικών Δικαιωμάτων
st.markdown("---")
st.markdown(
    "📝 **Νομική Δήλωση**: Η χρήση της εφαρμογής επιτρέπεται μόνο με ρητή γραπτή άδεια της δημιουργού, Παναγιώτας Γιαννίτσαρου. "
    "Όλα τα πνευματικά δικαιώματα ανήκουν στη Γιαννίτσαρου Παναγιώτα. Για άδεια χρήσης: "
    "[yiannitsaroupanayiota.katanomi@gmail.com](mailto:yiannitsaroupanayiota.katanomi@gmail.com)"
)




# === ΔΙΟΡΘΩΜΕΝΟΣ ΠΙΝΑΚΑΣ ΣΤΑΤΙΣΤΙΚΩΝ ΚΑΤΑΝΟΜΗΣ ===
st.subheader("📊 Πίνακας Στατιστικών Κατανομής")

# Αν υπάρχουν δεδομένα με ΤΜΗΜΑ
if 'ΤΜΗΜΑ' in df.columns and df['ΤΜΗΜΑ'].notna().sum() > 0:
    df_placed = df[df['ΤΜΗΜΑ'].notna()].copy()

    df_placed['ΑΓΟΡΙ'] = df_placed['ΦΥΛΟ'].apply(lambda x: 1 if str(x).strip().upper() == 'Α' else 0)
    df_placed['ΚΟΡΙΤΣΙ'] = df_placed['ΦΥΛΟ'].apply(lambda x: 1 if str(x).strip().upper() == 'Κ' else 0)

    for col in ['ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']:
        df_placed[col] = df_placed[col].apply(lambda x: 1 if str(x).strip().upper() == 'Ν' else 0)

    stats = df_placed.groupby('ΤΜΗΜΑ').agg({
        'ΑΓΟΡΙ': 'sum',
        'ΚΟΡΙΤΣΙ': 'sum',
        'ΖΩΗΡΟΣ': 'sum',
        'ΙΔΙΑΙΤΕΡΟΤΗΤΑ': 'sum',
        'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ': 'sum',
        'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ': 'sum',
        'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ': 'sum'
    }).reset_index()

    st.dataframe(stats)

    # Χρωματική απεικόνιση heatmap
    def color_gradient(val):
        if isinstance(val, (int, float)):
            if val > 5:
                return 'background-color: lightcoral'
            elif val > 3:
                return 'background-color: khaki'
            else:
                return 'background-color: lightgreen'
        return ''

    styled_stats = stats.style.applymap(color_gradient, subset=stats.columns[1:])
    st.subheader("🎨 Heatmap Στατιστικών (χρωματική απεικόνιση)")
    st.dataframe(styled_stats, use_container_width=True)
