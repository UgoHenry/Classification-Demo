import json
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# LOAD JSON FILES
# ---------------------------------------------------------
@st.cache_data
def load_dictionary(path: str = "dictionary.json") -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

@st.cache_data
def load_bmc_categories(path: str = "bmc_categories.json") -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

@st.cache_data
def load_ukb_mapping(path: str = "ukb_mapping.json") -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)


# ---------------------------------------------------------
# PARSE QUESTIONNAIRE JSON
# ---------------------------------------------------------
def flatten_questionnaire(file_bytes: bytes, filename: str) -> pd.DataFrame:
    obj = json.loads(file_bytes.decode("utf-8"))
    questions = obj.get("questions", [])

    rows = []
    for q in questions:
        rows.append({
            "filename": filename,
            "form_id": obj.get("form_id"),
            "form_machine_id": obj.get("form_machine_id"),
            "language": obj.get("language"),
            "question_number": q.get("question_number"),
            "question_id_human": q.get("question_id_human"),
            "question_id_machine": q.get("question_id_machine"),
            "section": q.get("section"),
            "subsection": q.get("subsection"),
            "question_text": q.get("text"),
            "answer_raw": q.get("answer_raw")
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------
# IMPROVED BMC ONTOLOGY MAPPING
# ---------------------------------------------------------
def apply_improved_bmc(row: pd.Series) -> pd.Series:
    hv = row.get("harmonized_variable")
    leaf = row.get("level_isleaf")

    level_0_imp = None
    level_1_imp = None
    level_2_imp = None
    level_3_imp = None

    # -----------------------------
    # SOCIODEMOGRAPHICS
    # -----------------------------
    if hv in ["sex", "year_of_birth", "place_of_birth", "ethnicity"]:
        level_0_imp = "Sociodemographics"
        level_1_imp = "Demographics"
        level_2_imp = "Core_demographics"
        if hv == "sex":
            level_3_imp = "Sex"
        elif hv == "year_of_birth":
            level_3_imp = "Year_of_birth"
        elif hv == "place_of_birth":
            level_3_imp = "Place_of_birth"
        elif hv == "ethnicity":
            level_3_imp = "Ethnicity"

    elif hv in ["living_conditions", "children", "education_level"]:
        level_0_imp = "Sociodemographics"
        level_1_imp = "Social_factors"
        if hv == "living_conditions":
            level_2_imp = "Living_conditions"
            level_3_imp = "Living_conditions"
        elif hv == "children":
            level_2_imp = "Family_structure"
            level_3_imp = "Children"
        elif hv == "education_level":
            level_2_imp = "Education"
            level_3_imp = "Education_level"

    # -----------------------------
    # LIFESTYLE – SMOKING
    # -----------------------------
    elif hv in ["smoking_status", "smoking_current", "smoking_former", "passive_smoking"]:
        level_0_imp = "Lifestyle"
        level_1_imp = "Smoking"
        if hv == "smoking_status":
            level_2_imp = "Smoking_status"
            level_3_imp = "Smoking_status"
        elif hv in ["smoking_current", "smoking_former"]:
            level_2_imp = "Smoking_history"
            if hv == "smoking_current":
                level_3_imp = "Current_smoking"
            else:
                level_3_imp = "Former_smoking"
        elif hv == "passive_smoking":
            level_2_imp = "Passive_smoking"
            level_3_imp = "Passive_smoking"

    # -----------------------------
    # LIFESTYLE – ALCOHOL
    # -----------------------------
    elif hv in ["alcohol_frequency", "alcohol_use", "alcohol_amount"]:
        level_0_imp = "Lifestyle"
        level_1_imp = "Alcohol"
        if hv == "alcohol_frequency":
            level_2_imp = "Alcohol_frequency"
            level_3_imp = "Alcohol_frequency"
        elif hv == "alcohol_use":
            level_2_imp = "Alcohol_frequency"
            level_3_imp = "Alcohol_use"
        elif hv == "alcohol_amount":
            level_2_imp = "Alcohol_quantity"
            level_3_imp = "Alcohol_amount"

    # -----------------------------
    # LIFESTYLE – PHYSICAL ACTIVITY
    # -----------------------------
    elif hv in ["physical_activity", "lifestyle_past_current"]:
        level_0_imp = "Lifestyle"
        level_1_imp = "Physical_activity"
        if hv == "physical_activity":
            level_2_imp = "Activity_level"
            level_3_imp = "Physical_activity"
        else:
            level_2_imp = "Activity_history"
            level_3_imp = "Lifestyle_past_current"

    # -----------------------------
    # DIET
    # -----------------------------
    elif hv in ["special_diet", "diet_duration", "diet_reason"]:
        level_0_imp = "Diet"
        level_1_imp = "Diet_type"
        if hv == "special_diet":
            level_2_imp = "Diet_type"
            level_3_imp = "Special_diet"
        elif hv == "diet_duration":
            level_2_imp = "Diet_duration"
            level_3_imp = "Diet_duration"
        elif hv == "diet_reason":
            level_2_imp = "Diet_reason"
            level_3_imp = "Diet_reason"

    # -----------------------------
    # LIFESTYLE – STRESS & SLEEP
    # -----------------------------
    elif hv == "stress_level":
        level_0_imp = "Lifestyle"
        level_1_imp = "Psychosocial"
        level_2_imp = "Stress"
        level_3_imp = "Stress_level"

    elif hv == "sleep_duration":
        level_0_imp = "Lifestyle"
        level_1_imp = "Sleep"
        level_2_imp = "Sleep_duration"
        level_3_imp = "Sleep_duration"

    # -----------------------------
    # MEDICATION
    # -----------------------------
    elif hv in [
        "medication_use_3_months",
        "medication_current",
        "medications_2_months",
        "medications_6_months"
    ]:
        level_0_imp = "Medication"
        level_1_imp = "Medication_use"
        if hv == "medication_use_3_months":
            level_2_imp = "Recent_medication_use"
            level_3_imp = "Medication_use_3_months"
        elif hv == "medication_current":
            level_2_imp = "Current_medication"
            level_3_imp = "Medication_current"
        elif hv == "medications_2_months":
            level_2_imp = "Recent_medication_use"
            level_3_imp = "Medications_2_months"
        elif hv == "medications_6_months":
            level_2_imp = "Recent_medication_use"
            level_3_imp = "Medications_6_months"

    elif hv in [
        "antibiotics_2_months",
        "antibiotic_details_2m",
        "antibiotic_name",
        "antibiotic_duration"
    ]:
        level_0_imp = "Medication"
        level_1_imp = "Antibiotics"
        if hv == "antibiotics_2_months":
            level_2_imp = "Antibiotic_use"
            level_3_imp = "Antibiotics_2_months"
        elif hv == "antibiotic_details_2m":
            level_2_imp = "Antibiotic_details"
            level_3_imp = "Antibiotic_details_2m"
        elif hv == "antibiotic_name":
            level_2_imp = "Antibiotic_details"
            level_3_imp = "Antibiotic_name"
        elif hv == "antibiotic_duration":
            level_2_imp = "Antibiotic_details"
            level_3_imp = "Antibiotic_duration"

    # -----------------------------
    # SYMPTOMS
    # -----------------------------
    elif hv in [
        "digestive_issues_past_year",
        "digestive_symptoms",
        "diarrhea_week",
        "post_antibiotic_symptoms"
    ]:
        level_0_imp = "Symptoms"
        level_1_imp = "Digestive"
        if hv == "digestive_issues_past_year":
            level_2_imp = "Digestive_symptoms"
            level_3_imp = "Digestive_issues_past_year"
        elif hv == "digestive_symptoms":
            level_2_imp = "Digestive_symptoms"
            level_3_imp = "Digestive_symptoms"
        elif hv == "diarrhea_week":
            level_2_imp = "Digestive_symptoms"
            level_3_imp = "Diarrhea_week"
        elif hv == "post_antibiotic_symptoms":
            level_2_imp = "Digestive_symptoms"
            level_3_imp = "Post_antibiotic_symptoms"

    # -----------------------------
    # HEALTH CONDITIONS
    # -----------------------------
    elif hv in [
        "digestive_disease_history",
        "digestive_disease_year",
        "digestive_disease_active",
        "digestive_disease",
        "digestive_disease_list"
    ]:
        level_0_imp = "Health_conditions"
        level_1_imp = "Digestive_diseases"
        level_2_imp = "Disease_history"
        level_3_imp = leaf or hv

    elif hv in ["autoimmune_disease", "autoimmune_disease_list"]:
        level_0_imp = "Health_conditions"
        level_1_imp = "Allergies"
        level_2_imp = "Autoimmune_diseases"
        level_3_imp = leaf or hv

    elif hv == "cancer_history":
        level_0_imp = "Health_conditions"
        level_1_imp = "Chronic_diseases"
        level_2_imp = "Cancer_history"
        level_3_imp = "Cancer_history"

    elif hv == "cvd_history":
        level_0_imp = "Health_conditions"
        level_1_imp = "Chronic_diseases"
        level_2_imp = "CVD_history"
        level_3_imp = "CVD_history"

    elif hv == "endocrine_history":
        level_0_imp = "Health_conditions"
        level_1_imp = "Chronic_diseases"
        level_2_imp = "Endocrine_history"
        level_3_imp = "Endocrine_history"

    elif hv in ["other_chronic_history", "chronic_diseases"]:
        level_0_imp = "Health_conditions"
        level_1_imp = "Chronic_diseases"
        level_2_imp = "Other_chronic_history"
        level_3_imp = "Chronic_diseases"

    # -----------------------------
    # PHYSICAL MEASUREMENTS
    # -----------------------------
    elif hv in ["height_cm", "weight_kg", "waist_cm"]:
        level_0_imp = "Physical_measurements"
        level_1_imp = "Anthropometry"
        level_2_imp = "Body_size"
        if hv == "height_cm":
            level_3_imp = "Height_cm"
        elif hv == "weight_kg":
            level_3_imp = "Weight_kg"
        elif hv == "waist_cm":
            level_3_imp = "Waist_cm"

    # -----------------------------
    # EARLY LIFE FACTORS
    # -----------------------------
    elif hv in ["birth_mode", "breastfeeding"]:
        level_0_imp = "Early_life_factors"
        if hv == "birth_mode":
            level_1_imp = "Birth"
            level_2_imp = "Birth_mode"
            level_3_imp = "Birth_mode"
        elif hv == "breastfeeding":
            level_1_imp = "Infant_feeding"
            level_2_imp = "Breastfeeding"
            level_3_imp = "Breastfeeding"

    # Fallback: keep None if not mapped
    return pd.Series({
        "level_0_imp": level_0_imp,
        "level_1_imp": level_1_imp,
        "level_2_imp": level_2_imp,
        "level_3_imp": level_3_imp
    })


# ---------------------------------------------------------
# MERGE PIPELINE
# ---------------------------------------------------------
def build_merged_tables(q_df, dict_df, bmc_df, ukb_df):
    # questionnaire → dictionary
    merged = q_df.merge(
        dict_df,
        on="question_id_machine",
        how="left",
        validate="m:1"
    )

    # dictionary → BMC
    merged = merged.merge(
        bmc_df,
        on="harmonized_variable",
        how="left",
        validate="m:1"
    )

    # dictionary → UKB
    merged = merged.merge(
        ukb_df,
        on="harmonized_variable",
        how="left",
        suffixes=("", "_ukb"),
        validate="m:1"
    )

    # Improved BMC ontology (separate from original BMC levels)
    improved_cols = merged.apply(apply_improved_bmc, axis=1)
    merged = pd.concat([merged, improved_cols], axis=1)

    # Optional: a single path string for display
    merged["improved_classification_path"] = (
        merged["level_0_imp"].fillna("") + " > " +
        merged["level_1_imp"].fillna("") + " > " +
        merged["level_2_imp"].fillna("") + " > " +
        merged["level_3_imp"].fillna("")
    )

    return merged


# ---------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="VIGDB Harmonization Console", layout="wide")

    st.title("VIGDB Harmonization Console")
    st.caption("BMC Latvia • UK Biobank • Improved BMC")

    uploaded_files = st.sidebar.file_uploader(
        "Upload questionnaire JSON files",
        type=["json"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Upload one or more questionnaire JSON files to begin.")
        return

    # Parse all uploaded questionnaires
    q_frames = []
    for f in uploaded_files:
        try:
            df = flatten_questionnaire(f.read(), f.name)
            q_frames.append(df)
        except Exception as e:
            st.error(f"Could not parse {f.name}: {e}")

    if not q_frames:
        st.error("No valid questionnaire files found.")
        return

    q_df = pd.concat(q_frames, ignore_index=True)

    # Load reference tables
    dict_df = load_dictionary()
    bmc_df = load_bmc_categories()
    ukb_df = load_ukb_mapping()

    merged = build_merged_tables(q_df, dict_df, bmc_df, ukb_df)

    # Sidebar file selector
    file_choice = st.sidebar.selectbox(
        "Select a file to view",
        options=["All files"] + sorted(merged["filename"].unique())
    )

    if file_choice != "All files":
        view_df = merged[merged["filename"] == file_choice].copy()
    else:
        view_df = merged.copy()

    # ---------------------------------------------------------
    # TABS
    # ---------------------------------------------------------
    tab_bmc, tab_ukb, tab_improved = st.tabs([
        "BMC Classification",
        "UK Biobank Classification",
        "Improved BMC Classification"
    ])

    # ---------------------------------------------------------
    # BMC TAB (unchanged)
    # ---------------------------------------------------------
    with tab_bmc:
        st.subheader("BMC Classification")

        cols = [
            "filename",
            "question_text",
            "question_id_human",
            "question_id_machine",
            "harmonized_variable",
            "label_lv",
            "label_en",
            "level_0_id",
            "level_0",
            "level_1_id",
            "level_1",
            "level_2_id",
            "level_2",
            "level_isleaf_id",
            "level_isleaf"
        ]

        bmc_view = view_df[cols].sort_values(
            ["filename"],
            na_position="last"
        )

        st.dataframe(bmc_view, use_container_width=True)

        st.download_button(
            "Download BMC CSV",
            bmc_view.to_csv(index=False).encode("utf-8"),
            file_name="bmc_classification.csv"
        )

    # ---------------------------------------------------------
    # UKB TAB (unchanged)
    # ---------------------------------------------------------
    with tab_ukb:
        st.subheader("UK Biobank Classification")

        cols = [
            "filename",
            "question_text",
            "question_id_machine",
            "harmonized_variable",
            "label_lv",
            "label_en",
            "ukb_category_id",
            "ukb_category_name",
            "ukb_subcategory",
            "ukb_field_group",
            "ukb_field_id",
            "ukb_field_name",
            "ukb_field_description",
            "ukb_field_url"
        ]

        ukb_view = view_df[cols].sort_values(
            ["filename"],
            na_position="last"
        )

        st.dataframe(ukb_view, use_container_width=True)

        st.download_button(
            "Download UKB CSV",
            ukb_view.to_csv(index=False).encode("utf-8"),
            file_name="ukb_mapping.csv"
        )

    # ---------------------------------------------------------
    # IMPROVED BMC TAB – NOW USING ONTOLOGY STRUCTURE
    # ---------------------------------------------------------
    with tab_improved:
        st.subheader("Improved BMC Classification")

        cols = [
            "harmonized_variable",
            "label_lv",
            "label_en",
            "level_0_imp",
            "level_1_imp",
            "level_2_imp",
            "level_3_imp",
            "improved_classification_path"
        ]

        improved_view = (
            view_df[cols]
            .drop_duplicates(subset=["harmonized_variable"])
            .sort_values("harmonized_variable")
        )

        st.dataframe(improved_view, use_container_width=True)

        st.download_button(
            "Download Improved BMC CSV",
            improved_view.to_csv(index=False).encode("utf-8"),
            file_name="improved_bmc_classification.csv"
        )


if __name__ == "__main__":
    main()
