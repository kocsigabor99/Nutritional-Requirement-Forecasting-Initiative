# Nutritional Requirement Forecasting Initiative (NRFI)

The Nutritional Requirement Forecasting Initiative (NRFI) aims to estimate the micronutrient needs of a country's population for any given year in the future. This tool helps professionals estimate the optimal food mix required to fulfill the micronutrient needs of different populations across various nations.

## Table of Contents
- [Usage](#usage)
- [Methodology](#methodology)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [Contact](#contact)

## Usage: [Open app in browser](https://nutritional-requirement-forecasting-initiative-inie88ebreaysf5.streamlit.app/)
- Select a country and year to get national nutrient needs.
- Calculate per capita nutrient needs.
- Generate an optimized meal plan that satisfies daily nutrient needs for the population.
- Display scaled meal plans for both daily and annual totals.

## Methodology

The NRFI calculates the nutritional requirements of a population by using data from:

- **Population Projections**: United Nations population data by age and sex.
- **Number of Pregnant/Breastfeeding women**: Estimates the number of pregnant and breastfeeding women from the UN's Birth data by single age group.
- **Nutritional Requirements**: NIH daily intake recommendations for vitamins and minerals, adjusted for age, sex, and pregnancy/breastfeeding status.
- **Food Intake Data**: Based on the Planetary Health Diet (EAT-Lancet Commission) and food composition data from the FAO.

The app randomly selects food combinations to meet the required micronutrient intake, then optimizes this selection after several iterations.

For the project overview and short methodology, refer to this [blog post](https://thegreatplanttransition.blogspot.com/2024/11/project-overview-nutritional.html).
For more detailed methodology, refer to the [project documentation](https://github.com/kocsigabor99/Nutritional-Requirement-Forecasting-Initiative/raw/refs/heads/main/project_documentation.odt).

## Future Improvements

Several enhancements are planned for future updates, including:

- **Food Selection Optimization**: Refining the algorithm to minimize food items.
- **Local Context Customization**: Adapting the food mix to align with cultural preferences and local agricultural capabilities.
- **Population Projection Scenarios**: Enabling the calculation of nutritional needs based on different population projection scenarios. 
- **Environmental Impact**: Optimizing food selection for minimal carbon footprint.
- **Additional Optimization Criteria**: Prioritizing nutrient deficiency reduction, cost-efficiency, and nutrient absorption.
- **Customizable Nutritional Targets**: Allowing users to adjust the app's parameters based on specific needs.

These updates will make the tool more comprehensive and adaptable to a broader range of use cases.

## Contributing

Contributions are welcome! To contribute to the NRFI project:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to your fork and open a pull request.

For major changes, please open an issue first to discuss what you would like to change.

Please follow the coding conventions and provide tests where possible.

## Contact

If you have any questions or feedback, feel free to contact me at: kocsigabor99@gmail.com

