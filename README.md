# Image Context Evaluation Study

A research project investigating how textual context influences the quality of AI-generated image descriptions in academic papers.

## Project Overview

This study examines whether providing surrounding textual context from academic documents improves AI-generated image descriptions. The pipeline processes academic papers, extracts images with their contexts, generates descriptions with/without context, and evaluates results through human evaluation.

## Files

### ArticleDownloader.py
Downloads academic papers from online sources for processing.

### ArticleProcessor.py
Converts academic papers (PDF/DOCX) to structured markdown format and extracts images, tables, and text content.

### DatasetConstructor.py
Creates datasets from processed articles by randomly selecting images and extracting their surrounding textual context.

### ResponseGenerator.py
Generates AI descriptions using OpenAI's API, creating both with-context and without-context versions for comparison.

### EvaluationGUI.py
Tkinter-based interface for human evaluation study with blinded comparison of AI-generated descriptions using Likert scales.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set OpenAI API key: `export OPENAI_API_KEY=your_key`
3. For GUI: `sudo apt install python3-tk` (Ubuntu/Debian)

## Usage

Run files in sequence: ArticleDownloader → ArticleProcessor → DatasetConstructor → ResponseGenerator → EvaluationGUI