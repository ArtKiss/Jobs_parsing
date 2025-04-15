# Jobs Parsing

A Python-based application for parsing job listings from the [gsz.gov.by](https://gsz.gov.by) website. This tool allows users to search for job vacancies by profession, region, and district, and save the results in a formatted Excel file.

## Features

- **Job Search**: Search for job vacancies by profession, region, and district.
- **Excel Export**: Save parsed job data to an Excel file with automatic formatting and hyperlinks.
- **Customizable Settings**: Adjust browser window size, theme, and headless mode.
- **Progress Tracking**: Real-time progress bar and status updates during parsing.
- **Region and District Selection**: Preloaded region and district data for easy selection.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Jobs_Parsing.git
   cd Jobs_Parsing
   ```
2. Install the required dependencies:
   pip install -r requirements.txt

3. Ensure you have the latest version of Chrome installed, as the project uses Selenium with ChromeDriver.

## Usage
Run the application:
python Jobs_Parser.py

Use the graphical interface to:

Enter the job title you want to search for.
Select a region and district (optional).
Start the parsing process.
Save the results to an Excel file when prompted.

Settings
You can customize the application settings in the GUI or by editing the user_settings.json file:

Headless Mode: Run the browser in the background without a visible window.
Window Size: Set the browser window dimensions.
Default Save Folder: Specify the folder where Excel files will be saved.
Theme: Choose between light and dark themes.