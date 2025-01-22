# Global Internet Usage

A Streamlit application that visualizes global internet usage data and related economic indicators. This project provides interactive charts and insights into how internet penetration has evolved across different countries and regions.

## Table of Contents

- [Overview](#overview)  
- [Demo](#demo)  
- [File Structure](#file-structure)  
- [Data Sources](#data-sources)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Contributing](#contributing)  
- [License](#license)

## Overview

**Global Internet Usage** is a simple dashboard application built with [Streamlit](https://streamlit.io/). It allows users to:

- View internet usage statistics by country and region over time.  
- Compare usage data with economic indicators to see potential correlations.  
- Interactively filter and visualize data with dynamic charts.

## Demo

Try out the live application on Streamlit Community Cloud:  
**[Global Internet Usage App](https://global-internet-usage.streamlit.app/)**

## File Structure

```
GLOBAL-INTERNET-USAGE/
├─ .streamlit/
│  └─ (Streamlit configuration files)
├─ data/
│  ├─ economic_indicators.csv
│  └─ internet_usage.csv
├─ app.py
├─ requirements.txt
└─ README.md
```

- **`.streamlit/`**: Contains Streamlit configuration files (e.g., `config.toml`) that control theming and other Streamlit settings.
- **`data/`**: Folder containing the CSV data files used by the dashboard.
  - `economic_indicators.csv` – economic data relevant to each country/region.
  - `internet_usage.csv` – internet usage data over time, by country/region.
- **`app.py`**: The main Streamlit application code. This file loads the data, creates visualizations, and defines the Streamlit layout.
- **`requirements.txt`**: Python dependencies needed to run the app.

## Data Sources

The data used in this project includes:
- **Internet Usage**: Trends and counts for different countries/regions.
- **Economic Indicators**: GDP per capita, population, and other metrics that provide context for internet usage patterns.

*(If your data sets are from publicly available sources, you can cite them here.)*

## Installation

Follow the steps below to run the application locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/global-internet-usage.git
   ```
2. **Navigate into the project folder**:
   ```bash
   cd global-internet-usage
   ```
3. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate.bat # On Windows
   ```
4. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser and visit the URL provided by Streamlit (usually [http://localhost:8501](http://localhost:8501)).

3. **Explore the Dashboard**:
   - Use the sidebar to filter data by region or year.  
   - View the main page for interactive plots of internet usage.  
   - Compare usage with economic indicators to gain insights into potential relationships.

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to add new features:

1. Fork this repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them: `git commit -m "Add your message here"`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Open a pull request on GitHub.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and adapt it as you see fit.

---

*Thank you for checking out the Global Internet Usage dashboard! If you have any feedback or questions, feel free to open an issue or reach out.*
