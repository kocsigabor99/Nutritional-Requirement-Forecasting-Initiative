import streamlit as st
import pandas as pd
import numpy as np

results = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/result_sum_adj_df.csv"

food_data = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/WAFCT2019%2BPULSES.csv"

populationstat = "https://raw.githubusercontent.com/kocsigabor99/MAJOR-CROPS-FAODATA/refs/heads/main/data/UN_PPP2024_Output_PopTot.csv"

# Load the CSV files
nutrient_needs_df = pd.read_csv(results)
food_data_df = pd.read_csv(food_data)
population_df = pd.read_csv(populationstat, encoding='ISO-8859-1')

# User interface for selecting country and year
st.title('National Nutrient-Based Meal Planner')

# Select country and year
country = st.selectbox('Select Country', nutrient_needs_df['Region, subregion, country or area'].unique())
year = st.selectbox('Select Year', nutrient_needs_df['Year'].unique().astype(str))

# Filter nutrient needs for the selected country and year
filtered_needs = nutrient_needs_df[(nutrient_needs_df['Region, subregion, country or area'] == country) & 
                                   (nutrient_needs_df['Year'].astype(str) == year)]

# Retrieve population for the selected country and year
population_row = population_df[(population_df['Region, subregion, country or area *'] == country)]
population = population_row[year].values[0] if not population_row.empty else 1  # Default to 1 if data is missing

# Calculate daily nutrient needs per citizen
# Exclude the 'Year' column from calculations
daily_needs_per_citizen = filtered_needs.copy()
numeric_columns = daily_needs_per_citizen.select_dtypes(include=['float64', 'int64']).columns
numeric_columns = numeric_columns.drop('Year', errors='ignore')  # Exclude 'Year' from calculations
daily_needs_per_citizen[numeric_columns] /= population

# Display the total nutrient needs for the country
st.subheader(f'Total Nutrient Needs for {country} in {year} for a day (Countrywide)')
st.write(filtered_needs)

# Display the per capita daily nutrient needs for the country
st.subheader(f'Per Capita Average Daily Nutrient Needs for {country} in {year}')
st.write(daily_needs_per_citizen)


# Define food group calorie limits for daily intake
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

# Set maximum foods and attempts
max_foods = 30
max_attempts = 50

# Helper function to clean nutrient values
def clean_nutrient_value(value):
    try:
        value = str(value).replace('[', '').replace(']', '').strip()
        return float(value)
    except ValueError:
        return 0.0

# Function to calculate percentage of nutrient needs met
def calculate_percentage_met(nutrient_needs_df, total_nutrients):
    percentage_met = {}
    for nutrient in total_nutrients:
        if nutrient in nutrient_needs_df.columns:
            required_amount = nutrient_needs_df[nutrient].values[0]
            if required_amount > 0:
                percentage_met[nutrient] = (total_nutrients[nutrient] / required_amount) * 100
    return percentage_met

# Function to generate optimized meal plans and select the best
def generate_optimized_meal_plan(daily_needs_per_citizen, food_data, max_foods, max_attempts, population, total_needs):
    best_iteration = None
    best_coverage_score = float('-inf')  # Track best-fit score

    all_iterations_results = []

    for attempt in range(max_attempts):
        meal_plan = {}
        total_nutrients = {nutrient: 0 for nutrient in daily_needs_per_citizen.columns[2:]}
        food_type_sums = {food_type: 0 for food_type in food_group_calorie_limits}
        total_foods_selected = 0

        def add_food_item_to_plan(food_item, food_type, grams):
            if food_type not in meal_plan:
                meal_plan[food_type] = []
            meal_plan[food_type].append({"Food": food_item['Food name in English'], "Grams": grams})

            nutrient_values_per_100g = {
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

            for nutrient, value in nutrient_values_per_100g.items():
                total_nutrients[nutrient] += value * (grams / 100.0)

            if food_type in food_type_sums:
                food_type_sums[food_type] += grams

        while total_foods_selected < max_foods:
            food_was_added = False

            for food_type, limit in food_group_calorie_limits.items():
                if food_type_sums[food_type] < limit:
                    food_items = food_data[food_data['FOOD TYPE'] == food_type]
                    if not food_items.empty:
                        food_item = food_items.sample(n=1).iloc[0]
                        grams_to_add = min(limit - food_type_sums[food_type], 50)

                        if grams_to_add > 0:
                            add_food_item_to_plan(food_item, food_type, grams_to_add)
                            total_foods_selected += 1
                            food_was_added = True
                            if total_foods_selected >= max_foods:
                                break

            if not food_was_added:
                break

        # Calculate daily nutrient fulfillment and percentage per nutrient
        daily_percentage_met = calculate_percentage_met(daily_needs_per_citizen, total_nutrients)
        avg_coverage_score = sum(daily_percentage_met.values()) / len(daily_percentage_met)

        all_iterations_results.append({
            "Iteration": attempt + 1,
            "Meal Plan (grams per type)": meal_plan,
            "Total Nutrients": total_nutrients,
            "Percentage Fulfillment (%)": daily_percentage_met
        })

        if avg_coverage_score > best_coverage_score:
            best_coverage_score = avg_coverage_score
            best_iteration = all_iterations_results[-1]

    # Ensure we have a best iteration based on the highest average coverage score
    if best_iteration is None and all_iterations_results:
        best_iteration = max(all_iterations_results, key=lambda x: sum(x["Percentage Fulfillment (%)"].values()) / len(x["Percentage Fulfillment (%)"]))

    final_scaled_plan = {
        food_type: [
            {**item, "Total (kg)": item["Grams"] * population} for item in items
        ] for food_type, items in best_iteration["Meal Plan (grams per type)"].items()
    }

    # Return the results
    return all_iterations_results, best_iteration, final_scaled_plan

# Streamlit UI to generate and display results
if st.button("Generate Country-Scale Meal Plan"):
    all_iterations, best_iteration, final_scaled_plan = generate_optimized_meal_plan(
        daily_needs_per_citizen, food_data_df, max_foods, max_attempts, population, filtered_needs
    )

    # Display the best iteration if found
    if best_iteration:
        st.subheader("Best-Fit Iteration")
        st.write("Best Meal Plan (in grams per type):", best_iteration["Meal Plan (grams per type)"])
        st.write("Total Nutrients (unscaled):", best_iteration["Total Nutrients"])
        st.write("Percentage Fulfillment (%) per Nutrient:", best_iteration["Percentage Fulfillment (%)"])

        # Scale best iteration to meet total population needs
        st.subheader("Final Scaled-Up Meal Plan for Total Population for a day")
        st.write("Final Meal Plan (in kg per type):", final_scaled_plan)

        # Calculate scaled-up nutrients and percentage fulfillment for the day
        scaled_total_nutrients = {nutrient: value * population for nutrient, value in best_iteration["Total Nutrients"].items()}
        scaled_percentage_fulfillment = calculate_percentage_met(filtered_needs, scaled_total_nutrients)

        # Display scaled-up nutrients and fulfillment percentages for the day
        st.subheader("Final Nutrient Totals and Fulfillment for Total Population for a day")
        st.write("Scaled-Up Total Nutrients:", scaled_total_nutrients)
        st.write("Percentage Fulfillment (%) for Total Population for a day:", scaled_percentage_fulfillment)

        # Multiply by 365 for annual totals
        st.subheader("Final Scaled-Up Meal Plan for Total Population for a year")
        annual_scaled_plan = {
            food_type: [
                {**item, "Total (kg for a year)": item["Grams"] * population * 365} for item in items
            ] for food_type, items in final_scaled_plan.items()
        }
        st.write("Final Meal Plan (in kg per type for a year):", annual_scaled_plan)

        # Calculate scaled-up nutrients for a year
        annual_scaled_nutrients = {nutrient: value * 365 for nutrient, value in scaled_total_nutrients.items()}
        st.write("Scaled-Up Total Nutrients for a year:", annual_scaled_nutrients)
        
    else:
        st.error("No best-fit iteration found to scale up.")
