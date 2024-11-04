# Feedback Analyzer

**Version 1.0**
### Creator: Juhani Merilehto - @juhanimerilehto - Jyväskylä University of Applied Sciences (JAMK), Likes institute

![JAMK Likes Logo](./assets/jamklikes.png)

## Overview

Feedback Analyzer is a Python-based tool that processes qualitative data such as feedback in text form, and performs thematic analysis using AI (LLM, here, Claude 3.5 Sonnet). It was developed at JAMK University of Applied Sciences in collaboration with Likes institute. The tool utilizes the Claude API by Anthropic for natural language understanding and thematic analysis, processing data in two stages: initial categorization and iterative thematic analysis.

## Features

- **Initial Feedback Analysis**: Processes raw data and categorizes it into primary and secondary themes
- **Thematic Batch Analysis**: Performs iterative analysis to refine and aggregate themes
- **AI-Powered Analysis**: Uses Anthropic's Claude API for sophisticated natural language understanding
- **Excel Integration**: Works with Excel files for both input and output
- **Configurable Processing**: Flexible configuration through YAML files
- **Smart Batching**: Optimized processing of large datasets with intelligent batch sizing

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/juhanimerilehto/jamk-thematic-analysis.git
   cd jamk-thematic-analysis
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory to store your API key:

   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

1. Prepare your feedback data in an Excel file with appropriate column headers.

2. Configure the analysis by modifying the YAML configuration files:
   - `category_config.yaml` for initial feedback analysis
   - `thematic_config.yaml` for thematic batch analysis

3. Run the initial analysis:

   ```bash
   python categorymaker.py
   ```

4. Run the thematic analysis:

   ```bash
   python thematic_batches.py
   ```

## Configuration

### Category Configuration
Configure the initial analysis in `category_config.yaml`. Example structure with sample column names (replace these with your actual Excel column headers):
```yaml
# Column mapping: Excel column headers to internal names
column_mapping:
  "Question 1": "primary_feedback"    # Replace with your column header
  "Question 2": "secondary_feedback"  # Replace with your column header
  "Additional Comments": "extra"      # Replace with your column header

# Example from Finnish dataset:
# column_mapping:
#   "tyo": "tyo"                    # Work-related questions
#   "tyohyvinvointi": "tyohyvinvointi"  # Wellbeing questions
#   "yleis": "yleis"                # General feedback
#   "vapaa": "vapaa"                # Free comments

# Category names for analysis output
primary_category: "main_theme"
secondary_category: "sub_theme"

# Analysis context template
analysis_context: |
    Analyze the following feedback responses thematically and provide two lists of categories:
    1. List of themes related to primary questions
    2. List of themes related to secondary questions
    Use only keywords or short phrases. Do not use numbers or bullet points.
    Categories should be descriptive.
    If there isn't enough information to form a category, don't force it.
    Separate the lists using ---.
    Separate each item in the lists using semicolons (;).
```

### Thematic Configuration
Configure the thematic analysis in `thematic_config.yaml`:
```yaml
# Batch processing settings
max_batch_size: 20     # Maximum items per batch
batch_by: "rows"       # Can be "rows" or "categories"

# Category types to analyze (match these with your category_config.yaml output)
category_types:
  "primary_feedback_categories": "primary feedback"
  "secondary_feedback_categories": "secondary feedback"

# Example from Finnish dataset:
# category_types:
#   "support_needs_categories": "support needs"
#   "feedback_categories": "feedback"

# Analysis settings
model: "claude-3-5-sonnet-20240620"
max_tokens: 4000
temperature: 0
```

## Output

The tool produces:
1. Initial categorization in Excel format (`analysis_results.xlsx`)
2. Intermediate thematic analysis results in the `analysis_output` folder
3. Final themed categories with frequency analysis in the `analysis_output` folder:
   - `primary_feedback_categories_final_analysis.txt`
   - `secondary_feedback_categories_final_analysis.txt`

## File Structure

```plaintext
jamk-thematic-analysis-llm/
├── assets/
│   └── jamklikes.png
├── analysis_output/        # Generated analysis results
├── categorymaker.py        # Initial analysis script
├── thematic_batches.py    # Thematic analysis script
├── category_config.yaml    # Initial analysis configuration
├── thematic_config.yaml    # Thematic analysis configuration
├── input_data.xlsx        # Your input data
├── analysis_results.xlsx  # Generated intermediate results
└── .env                   # API key configuration
```

## Credits

- **Juhani Merilehto (@juhanimerilehto)** – Specialist, Data and Statistics
- **JAMK Likes** – Organization sponsor, providing use case and requirements for feedback analysis.

## License

This project is licensed for free use under the condition that proper credit is given to Juhani Merilehto (@juhanimerilehto) and JAMK Likes institute. You are free to use, modify, and distribute this project, provided that you mention the original author and institution and do not hold them liable for any consequences arising from the use of the software.