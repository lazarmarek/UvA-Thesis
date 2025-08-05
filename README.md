# Image Context Evaluation Study

A research project investigating how surrounding textual context influences the quality of AI-generated chart interpretation - sourcing charts from academic papers.

## Project Overview

This study examines whether providing surrounding textual context from academic documents improves AI-generated chart interpretation. The pipeline downloads research articles as PDFs, processes them using docling to extract images with their relevant contexts, generates descriptions with/without context and utilizes a Tkinter GUI to evaluate (blinded) the two different outputs on factual accuracy, completedness & coherence, 

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

Set-up .env file for OpenAI api key.
TBD

## Usage

Run files in sequence: ArticleDownloader → ArticleProcessor → DatasetConstructor → ResponseGenerator → EvaluationGUI
