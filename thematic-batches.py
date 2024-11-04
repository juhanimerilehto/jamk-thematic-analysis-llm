import pandas as pd
import anthropic
import os
from dotenv import load_dotenv
from typing import List, Tuple, Dict
import yaml
from pathlib import Path

class ThematicAnalyzer:
    def __init__(self, config_path: str):
        """
        Initialize the ThematicAnalyzer with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.load_dotenv()
        self.client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.config = self.load_config(config_path)
        self.output_dir = Path(self.config.get('output_directory', 'analysis_output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_batch_size = self.config.get('max_batch_size', 20)  # Default to 20 based on experience
        self.batch_by = self.config.get('batch_by', 'rows')  # 'rows' or 'categories'
        
    @staticmethod
    def load_dotenv() -> None:
        """Load environment variables."""
        load_dotenv()
    
    @staticmethod
    def load_config(config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def collect_categories(self, df: pd.DataFrame, column_name: str) -> List[List[str]]:
        """
        Collect categories from DataFrame with smart batching.
        
        Args:
            df: DataFrame containing the categories
            column_name: Name of the column containing categories
            
        Returns:
            List of category batches
        """
        batches = []
        current_batch = []
        current_count = 0

        if self.batch_by == 'rows':
            # Batch by number of rows
            for i in range(len(df)):
                row = df.iloc[i]
                if pd.notna(row[column_name]):
                    categories = [cat.strip() for cat in row[column_name].split(';') if cat.strip()]
                    
                    if current_count >= self.max_batch_size:
                        batches.append(current_batch)
                        current_batch = []
                        current_count = 0
                    
                    current_batch.extend(categories)
                    current_count += 1
            
        else:  # batch_by == 'categories'
            # Batch by number of individual categories
            for i in range(len(df)):
                row = df.iloc[i]
                if pd.notna(row[column_name]):
                    categories = [cat.strip() for cat in row[column_name].split(';') if cat.strip()]
                    
                    if current_count + len(categories) > self.max_batch_size:
                        batches.append(current_batch)
                        current_batch = []
                        current_count = 0
                    
                    current_batch.extend(categories)
                    current_count += len(categories)

        # Add the last batch if it's not empty
        if current_batch:
            batches.append(current_batch)

        # Debug information
        print(f"\nBatching Summary:")
        print(f"Batch method: {self.batch_by}")
        print(f"Maximum batch size: {self.max_batch_size}")
        print(f"Number of batches created: {len(batches)}")
        for i, batch in enumerate(batches, 1):
            if self.batch_by == 'rows':
                print(f"Batch {i}: {len(batch)} categories from approximately {self.max_batch_size} rows")
            else:
                print(f"Batch {i}: {len(batch)} categories")

        return batches
    def get_analysis_from_claude(self, categories: List[str], 
                               category_type: str, 
                               is_aggregation: bool = False) -> str:
        """
        Get thematic analysis from Claude based on categories.
        
        Args:
            categories: List of categories to analyze
            category_type: Type of categories being analyzed
            is_aggregation: Whether this is a final aggregation step
        """
        if is_aggregation:
            prompt = self.config['aggregation_prompt'].format(
                category_type=category_type,
                categories='; '.join(categories)
            )
        else:
            prompt = self.config['analysis_prompt'].format(
                category_type=category_type,
                categories='; '.join(categories)
            )

        response = self.client.messages.create(
            model=self.config.get('model', "claude-3-5-sonnet-20240620"),
            max_tokens=self.config.get('max_tokens', 4000),
            temperature=self.config.get('temperature', 0),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text

    def analyze_in_batches(self, categories: List[List[str]], 
                          category_type: str) -> Tuple[List[str], int]:
        """
        Analyze categories in batches.
        """
        all_analyses = []
        total_categories = 0
        
        for i, batch in enumerate(categories, 1):
            print(f"Analyzing batch {i}/{len(categories)} for {category_type}...")
            analysis = self.get_analysis_from_claude(batch, category_type)
            all_analyses.append(analysis)
            
            # Count categories in this batch
            batch_categories = len([cat for cat in analysis.split(';') if cat.strip()])
            total_categories += batch_categories
            print(f"Categories in batch: {batch_categories}")
            print(f"Running total: {total_categories}")
            print("---")
        
        return all_analyses, total_categories

    def save_intermediate_results(self, iteration: int, 
                                categories: List[List[str]], 
                                column: str) -> None:
        """Save intermediate analysis results."""
        output_file = self.output_dir / f'{column}_analysis_iteration_{iteration}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Iteration {iteration}\n\n")
            for i, batch in enumerate(categories, 1):
                f.write(f"Batch {i}:\n")
                f.write('; '.join(batch))
                f.write("\n\n")
        print(f"Saved intermediate results to {output_file}")

    def iterative_aggregation(self, df: pd.DataFrame, 
                            column: str, category_type: str) -> None:
        """
        Perform iterative aggregation of categories.
        """
        print(f"\nStarting iterative aggregation for {category_type}...")
        
        categories = self.collect_categories(df, column)
        iteration = 1
        
        while len(categories) > 1:
            print(f"\nIteration {iteration}")
            new_categories = []
            
            for i in range(0, len(categories), 2):
                if i + 1 < len(categories):
                    merged_batch = categories[i] + categories[i+1]
                    analysis = self.get_analysis_from_claude(merged_batch, category_type)
                    new_categories.append(analysis.split(';'))
                else:
                    new_categories.append(categories[i])
            
            categories = new_categories
            print(f"Batches after iteration {iteration}: {len(categories)}")
            
            self.save_intermediate_results(iteration, categories, column)
            iteration += 1
        
        # Final aggregation
        final_analysis = self.get_analysis_from_claude(
            categories[0], category_type, is_aggregation=True
        )
        
        # Save final results
        output_file = self.output_dir / f'{column}_final_analysis.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Final Themes:\n")
            f.write(final_analysis)
        
        print(f"\nFinal themes saved to {output_file}")

def main():
    analyzer = ThematicAnalyzer('thematic_config.yaml')
    input_file = analyzer.config.get('input_file', 'analysis_results.xlsx')
    
    df = pd.read_excel(input_file)
    
    # Process each category type
    for column, category_type in analyzer.config['category_types'].items():
        analyzer.iterative_aggregation(df, column, category_type)

if __name__ == "__main__":
    main()