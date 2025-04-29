# Klaviyo Flow Email HTML Extractor

![Klaviyo Flow Email HTML Extractor](https://github.com/yourusername/klaviyo-flow-email-extractor/raw/main/docs/images/screenshot.png)

A Streamlit web application that integrates with Klaviyo's API to help you identify flow emails and extract/render their HTML creative content.

## Features

- **Authentication**: Connect securely to your Klaviyo account using private API keys
- **Flow Browser**: View all your Klaviyo flows and their details
- **Email Extractor**: Extract HTML content from flow emails, preview, and download
- **Template Analysis**: Analyze email templates for structure, compatibility, and best practices
- **Bulk Operations**: Export multiple templates and generate comparative reports

## Demo

You can try a demo of the application at: [https://klaviyo-email-extractor.streamlit.app](https://klaviyo-email-extractor.streamlit.app) (replace with your actual Streamlit app URL after deployment)

## Prerequisites

- Python 3.7+
- Klaviyo account with API access
- Private API Key from Klaviyo

## Installation

### Local Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/klaviyo-flow-email-extractor.git
   cd klaviyo-flow-email-extractor
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

### Deploying to Streamlit Cloud

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions on deploying to Streamlit Cloud.

## Usage

### Authentication

1. In the Klaviyo dashboard, go to Account > Settings > API Keys
2. Create a Private API Key with the necessary permissions
3. Enter this API key in the sidebar of the Streamlit app

### Flow Browser

The Flow Browser allows you to view all your Klaviyo flows and their details:

1. Select the "Flow Browser" option from the navigation
2. View the table of all flows in your account
3. Select a specific flow to view its actions and metrics

### Email Extractor

The Email Extractor allows you to view and download HTML content from flow emails:

1. Select the "Email Extractor" option from the navigation
2. Choose a flow from the dropdown
3. Select an email within that flow
4. View the HTML preview and source code
5. Download the HTML content for offline use

### Template Analysis

The Template Analysis feature helps you analyze email templates for best practices:

1. Select the "Template Analysis" option from the navigation
2. Choose to analyze a flow email or upload an HTML file
3. View the analysis results including structure, compatibility, and recommendations

### Bulk Operations

The Bulk Operations feature allows you to work with multiple templates at once:

1. Select the "Bulk Operations" option from the navigation
2. Choose an operation type (extract all templates, generate report)
3. Select flows to include in the operation
4. Download the results as a ZIP file or CSV report

## Project Structure

```
klaviyo-flow-email-extractor/
│
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
│
├── .streamlit/              # Streamlit configuration
│   └── config.toml          # Streamlit theme and settings
│
├── utils/                   # Utility functions
│   ├── __init__.py          # Make utils a proper package
│   ├── klaviyo_api.py       # Klaviyo API interaction functions
│   └── html_utils.py        # HTML processing utilities
│
├── tests/                   # Unit tests
│   ├── test_klaviyo_api.py  # Tests for Klaviyo API functions
│   └── test_html_utils.py   # Tests for HTML utility functions
│
└── docs/                    # Additional documentation
    ├── DEPLOYMENT.md        # Deployment guide
    └── images/              