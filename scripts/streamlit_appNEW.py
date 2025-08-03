import streamlit as st
import pandas as pd
import numpy as np

# Data source URLs
results_url = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/result_sum_adj_df.csv"
food_data_url = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/WAFCT2019%2BPULSES.csv"
population_url = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/UN_PPP2024_Output_PopTot.csv"

# Load datasets
nutrient_needs_df = pd.read_csv(results_url)
food_data_df = pd.read_csv(food_data_url)
population_df = pd.read_csv(population_url, encoding='ISO-8859-1')

# Streamlit UI
st.title("National Nutrient-Based Meal Planner")

country = st.selectbox("Select Country", nutrient_needs_df['Region, subregion, country or area'].unique())
year = st.selectbox("Select Year", sorted(nutrient_needs_df['Year'].astype(str).unique()))

# Filter data
filtered_needs = nutrient_needs_df[
    (nutrient_needs_df['Region, subregion, country or area'] == country) &
    (nutrient_needs_df['Year'].astype(str) == year)
]

population_row = population_df[population_df['Region, subregion, country or area *'] == country]
population = population_row[year].values[0] if not population_row.empty else 1

daily_needs_per_citizen = filtered_needs.copy()
numeric_columns = daily_needs_per_citizen.select_dtypes(include=[np.number]).columns
numeric_columns = numeric_columns.drop('Year', errors='ignore')
daily_needs_per_citizen[numeric_columns] /= population

st.subheader(f"Total Nutrient Needs for {country} in {year} (Daily Total for Country)")
st.write(filtered_needs)

st.subheader(f"Per Capita Daily Nutrient Needs for {country} in {year}")
st.write(daily_needs_per_citizen)

food_group_calorie_limits = {
    "DAIRY": 250,
    "MEAT": 56,
    "FISH": 28,
    "FATS AND OILS": 40,
    "GRAINS": 250,
    "STARCHY ROOTS/TUBERS": 100,
    "LEGUMES SOAKED & BOILED & DRAINED": 75,
    "VEGETABLES": 400,
    "FRUITS": 200,
    "NUTS": 50
}

max_foods = 30
max_attempts = 50

def clean_nutrient_value(value):
    try:
        value = str(value).replace('[', '').replace(']', '').strip()
        return float(value)
    except ValueError:
        return 0.0

def calculate_percentage_met(needs_df, total_nutrients):
    result = {}
    for nutrient in total_nutrients:
        if nutrient in needs_df.columns:
            required = needs_df[nutrient].values[0]
            if required > 0:
                result[nutrient] = (total_nutrients[nutrient] / required) * 100
    return result

def generate_optimized_meal_plan(daily_needs, food_data, max_foods, max_attempts, population, total_needs):
    best_iteration = None
    best_score = float('-inf')
    all_results = []

    for attempt in range(max_attempts):
        meal_plan = {}
        total_nutrients = {nutrient: 0 for nutrient in daily_needs.columns[2:]}
        food_type_sums = {ftype: 0 for ftype in food_group_calorie_limits}
        total_selected = 0

        def add_food(food_item, ftype, grams):
            if ftype not in meal_plan:
                meal_plan[ftype] = []
            meal_plan[ftype].append({"Food": food_item['Food name in English'], "Grams": grams})

            nutrient_vals = {
                'Vitamin A (RAE, mcg)': clean_nutrient_value(food_item.get('Vitamin A (RAE, mcg)', 0)),
                'Thiamine (vitamin B1) (mg)': clean_nutrient_value(food_item.get('Thiamine (vitamin B1) (mg)', 0)),
                'Riboflavin (vitamin B2) (mg)': clean_nutrient_value(food_item.get('Riboflavin (vitamin B2) (mg)', 0)),
                'Niacin equivalents or [niacin, preformed] (vitamin B3) (mg)': clean_nutrient_value(food_item.get('Niacin equivalents or [niacin, preformed] (vitamin B3) (mg)', 0)),
                'Vitamin B6 (mg)': clean_nutrient_value(food_item.get('Vitamin B6 (mg)', 0)),
                'Folate, total or [folate, sum of vitamers] (vitamin B9) (mcg)': clean_nutrient_value(food_item.get('Folate, total or [folate, sum of vitamers] (vitamin B9) (mcg)', 0)),
                'Vitamin B12 (mcg)': clean_nutrient_value(food_item.get('Vitamin B12 (mcg)', 0)),
                'Vitamin C (mg)': clean_nutrient_value(food_item.get('Vitamin C (mg)', 0)),
                'Vitamin E (expressed in alpha-tocopherol equivalents) or [alpha-tocopherol] (mg)': clean_nutrient_value(food_item.get('Vitamin E (expressed in alpha-tocopherol equivalents) or [alpha-tocopherol] (mg)', 0)),
                'Calcium (mg)': clean_nutrient_value(food_item.get('Calcium (mg)', 0)),
                'Potassium (mg)': clean_nutrient_value(food_item.get('Potassium (mg)', 0)),
                'Copper (mg)': clean_nutrient_value(food_item.get('Copper (mg)', 0)),
                'Iron (mg)': clean_nutrient_value(food_item.get('Iron (mg)', 0)),
                'Magnesium (mg)': clean_nutrient_value(food_item.get('Magnesium (mg)', 0)),
                'Zinc (mg)': clean_nutrient_value(food_item.get('Zinc (mg)', 0))
            }

            for nutrient, val in nutrient_vals.items():
                total_nutrients[nutrient] += val * (grams / 100.0)

            if ftype in food_type_sums:
                food_type_sums[ftype] += grams

        while total_selected < max_foods:
            added = False
            for ftype, limit in food_group_calorie_limits.items():
                if food_type_sums[ftype] < limit:
                    candidates = food_data[food_data['FOOD TYPE'] == ftype]
                    if not candidates.empty:
                        food_item = candidates.sample(n=1).iloc[0]
                        grams = min(limit - food_type_sums[ftype], 50)
                        if grams > 0:
                            add_food(food_item, ftype, grams)
                            total_selected += 1
                            added = True
                            if total_selected >= max_foods:
                                break
            if not added:
                break

        percentage_met = calculate_percentage_met(daily_needs, total_nutrients)
        avg_score = np.mean(list(percentage_met.values())) if percentage_met else 0

        iteration_result = {
            "Iteration": attempt + 1,
            "Meal Plan (grams)": meal_plan,
            "Total Nutrients": total_nutrients,
            "Percentage Fulfillment (%)": percentage_met
        }
        all_results.append(iteration_result)

        if avg_score > best_score:
            best_score = avg_score
            best_iteration = iteration_result

    final_scaled = {
        ftype: [
            {**item, "Total (kg)": item["Grams"] * population / 1000} for item in items
        ] for ftype, items in best_iteration["Meal Plan (grams)"].items()
    }

    return all_results, best_iteration, final_scaled

if st.button("Generate Country-Scale Meal Plan"):
    all_results, best_result, scaled_plan = generate_optimized_meal_plan(
        daily_needs_per_citizen, food_data_df, max_foods, max_attempts, population, filtered_needs
    )

    if best_result:
        st.subheader("Best Iteration Results")
        st.write("Meal Plan (grams):", best_result["Meal Plan (grams)"])
        st.write("Total Nutrients:", best_result["Total Nutrients"])
        st.write("Percentage Fulfillment (%):", best_result["Percentage Fulfillment (%)"])

        st.subheader("Scaled-Up Meal Plan (Daily Total for Population)")
        st.write(scaled_plan)

        scaled_nutrients = {k: v * population for k, v in best_result["Total Nutrients"].items()}
        scaled_percentages = calculate_percentage_met(filtered_needs, scaled_nutrients)

        st.subheader("Scaled-Up Nutrient Totals (Daily for Population)")
        st.write("Nutrient Totals:", scaled_nutrients)
        st.write("Fulfillment Percentages:", scaled_percentages)

        st.subheader("Annual Meal Plan and Nutrients")
        annual_plan = {
            ftype: [
                {**item, "Total (kg/year)": item["Grams"] * population * 365 / 1000} for item in items
            ] for ftype, items in scaled_plan.items()
        }
        annual_nutrients = {k: v * 365 for k, v in scaled_nutrients.items()}

        st.write("Annual Meal Plan (kg):", annual_plan)
        st.write("Annual Nutrients:", annual_nutrients)
    else:
        st.error("No suitable meal plan found.")
