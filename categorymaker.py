import pandas as pd
import anthropic
import time
from tqdm import tqdm
import os
from dotenv import load_dotenv
import re
from typing import Dict, Optional
import yaml

class FeedbackAnalyzer:
    def __init__(self, config_path: str):
        """
        Initialize the FeedbackAnalyzer with configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.load_dotenv()
        self.client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.config = self.load_config(config_path)
        self.validate_config()
        # Store the analysis context as class variable
        self.analysis_context = self.config['analysis_context']
        
    @staticmethod
    def load_dotenv() -> None:
        """Load environment variables."""
        load_dotenv()
    
    @staticmethod
    def load_config(config_path: str) -> dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def validate_config(self) -> None:
        """Validate the configuration structure."""
        required_keys = ['column_mapping', 'analysis_context', 'primary_category', 'secondary_category']
        if not all(key in self.config for key in required_keys):
            raise ValueError(f"Configuration must contain: {', '.join(required_keys)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text input.
        
        Args:
            text: Input text to clean
            
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return ""
            
        # Remove ContentBlock formatting
        text = re.sub(r'\[?ContentBlock\(text=\'|\'(?:, type=\'text\')?\)\]?', '', text)
        # Replace escaped newlines with actual newlines
        text = text.replace('\\n', '\n')
        # Remove any remaining backslashes
        text = text.replace('\\', '')
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        # Remove any remaining quotes
        text = text.replace('"', '').replace("'", "")
        # Strip leading/trailing whitespace
        return text.strip()

    def process_row(self, row: pd.Series) -> str:
        """
        Process a single row of feedback data.
        
        Args:
            row: Pandas Series containing feedback data
            
        Returns:
            str: Processed analysis result
        """
        # Debug print to see what data we're receiving
        #print("Input row data:")
        #for col, topic in self.config['column_mapping'].items():
            #if col in row.index:
                #print(f"{topic}: {row[col]}")
        
        prompt = f"{self.analysis_context}\n\n"
        
        # Build prompt with actual data
        has_data = False
        for col, topic in self.config['column_mapping'].items():
            if col in row.index and pd.notna(row[col]):
                prompt += f"{topic}: {row[col]}\n"
                has_data = True
        
        if not has_data:
            print("No data found in row!")
            return "No input data"

        # Debug print the prompt
        #print("\nGenerated prompt:")
        #print(prompt)
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,
                    temperature=0,
                    system=self.config.get('system_prompt', "You are an expert in analyzing open-ended survey responses."),
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extract the text content directly from the first message
                if response.content and len(response.content) > 0:
                    return self.clean_text(response.content[0].text)
                return "No content in response"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Error processing row: {e}")
                    return "Processing error"

    def extract_elements(self, analysis: str) -> pd.Series:
        """
        Extract analyzed elements from the response.
        
        Args:
            analysis: Raw analysis text
            
        Returns:
            pd.Series: Extracted categories
        """
        parts = analysis.split('---')
        
        primary = parts[0].strip() if len(parts) > 0 else ''
        secondary = parts[1].strip() if len(parts) > 1 else ''

        # Remove any text before a colon
        primary = primary.split(':', 1)[-1].strip()
        secondary = secondary.split(':', 1)[-1].strip()
        
        return pd.Series({
            f'{self.config["primary_category"]}_categories': primary,
            f'{self.config["secondary_category"]}_categories': secondary
        })

    def analyze_feedback(self, input_file: str, output_file: str) -> None:
        """
        Analyze feedback data from Excel file.
        """
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Debug prints
        print("\nColumns in Excel file:", df.columns.tolist())
        print("Looking for columns:", list(self.config['column_mapping'].keys()))
        #print("\nFirst row of data:", df.iloc[0].to_dict())

        # Remove entirely empty rows
        df = df.dropna(how='all')

        # Process each row
        tqdm.pandas(desc="Analyzing responses")
        df['Analyysi'] = df.progress_apply(lambda row: self.process_row(row), axis=1)

        # Extract specific elements from the analysis
        df[[f'{self.config["primary_category"]}_categories', 
            f'{self.config["secondary_category"]}_categories']] = df['Analyysi'].apply(self.extract_elements)

        # Drop the 'Analyysi' column as it's no longer needed
        df = df.drop(columns=['Analyysi'])

        # Write the results to a new Excel file
        df.to_excel(output_file, index=False)

        print(f"Analysis complete. Results saved to '{output_file}'")

def main():
    analyzer = FeedbackAnalyzer('category_config.yaml')
    analyzer.analyze_feedback('input_data.xlsx', 'analysis_results.xlsx')

if __name__ == "__main__":
    main()