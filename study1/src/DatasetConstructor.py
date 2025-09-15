import pandas as pd
import os
from pathlib import Path
import random
import shutil
import re

class DatasetConstructor:
    """
    A class to construct the study's datasets from processed articles and their images.
    """
    
    def __init__(self, root_directory, random_state=None):
        """
        Initialize the DatasetConstructor.
        
        Args:
            root_directory (str): Path to the root directory containing processed articles
            random_state (int, optional): Random seed for reproducible results
        """
        self.root_directory = Path(root_directory)
        self.article_index = None
        self.random_state = random_state
        
        if random_state is not None:
            random.seed(random_state)
        
    def create_article_index(self):
        """
        Creates a pandas DataFrame with article names and paths to their processed .md files.
        """
        if not self.root_directory.exists():
            print(f"Directory {self.root_directory} does not exist.")
            return pd.DataFrame(columns=['article_name', 'md_path'])
        
        md_files = []
        for md_file in self.root_directory.rglob('*.md'):
            if md_file.is_file():
                article_name = md_file.stem
                md_files.append({'article_name': article_name, 'md_path': str(md_file)})
        
        self.article_index = pd.DataFrame(md_files).sort_values('md_path').reset_index(drop=True)
        print(f"Found {len(self.article_index)} processed articles.")
        return self.article_index
    
    def add_random_images(self, num_images=1):
        """
        Add random image paths to the article index and extract their surrounding context.
        Avoids images from appendices and reference sections.
        """
        if self.article_index is None:
            print("Please run create_article_index() first.")
            return None
            
        if self.random_state is not None:
            random.seed(self.random_state + 1)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg'}
        
        # Add columns for image paths and contexts
        for i in range(num_images):
            self.article_index[f'image_path_{i+1}'] = None
            self.article_index[f'image_context_{i+1}'] = None
        
        for idx, row in self.article_index.iterrows():
            article_dir = Path(row['md_path']).parent / f"{row['article_name']}_artifacts"
            
            if not article_dir.exists():
                continue
                
            image_files = [f for f in article_dir.rglob('*') 
                        if f.is_file() and f.suffix.lower() in image_extensions]
            
            if image_files:
                image_files.sort()
                md_content = self._read_markdown_file(row['md_path'])
                
                # Try to select valid images one by one
                selected_images = []
                attempts = 0
                max_attempts = len(image_files) * 2  # Prevent infinite loops
                
                while len(selected_images) < num_images and attempts < max_attempts:
                    if not image_files:
                        break
                        
                    # Randomly select an image
                    random_image = random.choice(image_files)
                    
                    # Check if this specific image is valid
                    if self._is_image_in_valid_section(md_content, random_image.name):
                        selected_images.append(random_image)
                        image_files.remove(random_image)  # Don't select it again
                    else:
                        print(f"Image reselection for article {row['article_name']} - image {random_image.name} in references/appendix")
                        image_files.remove(random_image)  # Remove invalid image
                    
                    attempts += 1
                
                # Store the selected valid images
                for i, image_path in enumerate(selected_images):
                    self.article_index.at[idx, f'image_path_{i+1}'] = str(image_path)
                    context = self._extract_image_context(md_content, image_path.name)
                    self.article_index.at[idx, f'image_context_{i+1}'] = context
            else:
                print(f"No valid images found for {row['article_name']} (all in appendices/references)")
        
        print(f"Added {num_images} random image path(s) and contexts to each article.")
        return self.article_index

    def _filter_valid_images(self, image_files, md_content):
        """
        Filter out images that appear in appendices or reference sections.
        """
        if not md_content:
            return image_files
        
        valid_images = []
        
        for image_file in image_files:
            if self._is_image_in_valid_section(md_content, image_file.name):
                valid_images.append(image_file)
        
        return valid_images

    def _is_image_in_valid_section(self, md_content, image_filename):
        lines = md_content.split('\n')
        
        # Find image position
        image_line_idx = None
        for i, line in enumerate(lines):
            if image_filename in line and ('![Image]' in line):
                image_line_idx = i
                break
        
        if image_line_idx is None:
            return False
        
        # Look backwards for "References" section
        for i in range(image_line_idx, -1, -1):
            line = lines[i].strip().lower()
            if line.startswith('#') and 'references' in line:
                return False  # Found references before image = invalid
        
        return True  # No references found = valid
    
    def _read_markdown_file(self, md_path):
        """Read and return the content of a markdown file."""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
            return ""
    
    def _extract_image_context(self, md_content, image_filename):
        """
        Extract the surrounding context (section/subsection) where the image is located.
        Handles both # headers and **bold** section markers.
        """
        if not md_content or not image_filename:
            return ""
        
        lines = md_content.split('\n')
        image_line_idx = None
        
        # Find the line containing the image reference
        for i, line in enumerate(lines):
            if image_filename in line and ('![Image]' in line):
                image_line_idx = i
                break
        
        if image_line_idx is None:
            return ""
        
        # Find the current section structure
        current_section_start = 0
        current_section_level = 0
        
        # Look backwards to find the most recent heading (# or **)
        for i in range(image_line_idx, -1, -1):
            line = lines[i].strip()
            if line.startswith('#') or line.startswith('**'):
                if line.startswith('#'):
                    # Count the number of # to determine heading level
                    level = len(line) - len(line.lstrip('#'))
                else:
                    # Treat **bold** as level 1 heading
                    level = 1
                
                if level > 0:
                    current_section_start = i
                    current_section_level = level
                    break
        
        # Find the end of the current section
        section_end = len(lines)
        for i in range(image_line_idx + 1, len(lines)):
            line = lines[i].strip()
            if line.startswith('#') or line.startswith('**'):
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                else:
                    level = 1
                
                if level > 0 and level <= current_section_level:
                    section_end = i
                    break
        
        # Extract the section content
        section_lines = lines[current_section_start:section_end]
        return '\n'.join(section_lines).strip()
    
    def _clean_context_text(self, context_text):
        """
        Clean the extracted context by removing formula and image placeholders.
        """
        if not context_text:
            return ""
        
        # Remove formula placeholders
        context_text = re.sub(r'<!-- formula-not-decoded -->', '', context_text)

        # Remove image references: ![Image](...anything....png)
        context_text = re.sub(r'!\[Image\]\(.*?\.png\)', '', context_text)
        
        # Clean up extra whitespace
        context_text = re.sub(r'\n\s*\n+', '\n\n', context_text)
        
        return context_text.strip()

    def clean_extracted_contexts(self):
        """
        Clean all extracted contexts by removing placeholders.
        """
        if self.article_index is None:
            print("No dataset to clean.")
            return None
        
        context_columns = [col for col in self.article_index.columns if col.startswith('image_context_')]
        
        for col in context_columns:
            for idx in self.article_index.index:
                original_context = self.article_index.at[idx, col]
                if pd.notna(original_context):
                    cleaned_context = self._clean_context_text(original_context)
                    self.article_index.at[idx, col] = cleaned_context
        
        print(f"Cleaned context placeholders.")
        return self.article_index
    
    def save_extracted_images(self, output_dir="extracted_images"):
        """
         Save all extracted images to a single directory with renamed files.
        """
        if self.article_index is None:
            return None
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        copied_count = 0
        image_columns = [col for col in self.article_index.columns if col.startswith('image_path_')]
        
        for idx, row in self.article_index.iterrows():
            article_name = row['article_name']
            
            for col in image_columns:
                image_path = row[col]
                if pd.notna(image_path) and Path(image_path).exists():
                    source_path = Path(image_path)
                    image_number = col.split('_')[-1]
                    new_filename = f"{article_name}_img_{image_number}{source_path.suffix}"
                    dest_path = output_path / new_filename
                    
                    try:
                        shutil.copy2(source_path, dest_path)
                        self.article_index.at[idx, col] = str(dest_path)
                        copied_count += 1
                    except Exception as e:
                        print(f"Error copying {image_path}: {e}")
        
        print(f"Saved {copied_count} images to {output_dir}")
        return self.article_index
    
    def save_dataset(self, filename="dataset.csv"):
        """
        Save the constructed dataset to a CSV file.
        """
        if self.article_index is None:
            print("No dataset to save.")
            return
        
        self.article_index.to_csv(filename, index=False)
        print(f"Dataset saved to {filename} (random_state: {self.random_state})")


if __name__ == "__main__":
    # Example usage:
    # Get the absolute path to the study1 directory
    STUDY1_DIR = Path(__file__).parent.parent
    
    # Define the root directory where processed articles are located.
    # This should point to the output of the ArticleProcessor script.
    PROCESSED_ARTICLES_ROOT = STUDY1_DIR / "articles"
    
    # Define the output paths for the generated dataset and images
    DATA_DIR = STUDY1_DIR / "data"
    DATASET_OUTPUT_PATH = DATA_DIR / "img-context-df.csv"
    SELECTED_IMAGES_OUTPUT_DIR = DATA_DIR / "selected_images"

    # --- How it was used for the experiment ---
    # Initialize the constructor with the absolute path to the processed articles
    constructor = DatasetConstructor(PROCESSED_ARTICLES_ROOT, random_state=42)
    
    # Run the dataset construction steps
    constructor.create_article_index()
    constructor.add_random_images(num_images=1)
    constructor.clean_extracted_contexts()
    
    # Save the final dataset and the selected images to their correct locations
    constructor.save_dataset(DATASET_OUTPUT_PATH)
    constructor.save_extracted_images(SELECTED_IMAGES_OUTPUT_DIR)