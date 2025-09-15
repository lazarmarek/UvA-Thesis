## Study 1: Evaluating the role of surrounding textual context on chart interpretive ability of a multimodal large language model (MLLM).

A research project investigating how surrounding textual context from academic papers influences the quality of AI-generated chart interpretations.

## Project Overview

This study investigates the hypothesis that providing surrounding textual context from academic documents improves the quality of AI-generated chart interpretations. The pipeline involves:
1.  **Downloading** research articles as PDFs.
2.  **Processing** them with `docling` to extract chart images and their corresponding contexts.
3.  **Generating** two interpretations for each chart (with and without context) using an MLLM.
4.  **Conducting** a blinded human evaluation to score the outputs on dimensions including accuracy, completeness, relevance, and clarity.

### File Tree

The file structure is designed to separate data, source code, and analysis, promoting a clean and reproducible workflow.

```
study1/
├── data/
│   ├── responses/              # Raw JSON model outputs (one file per generation)
│   ├── img-context-df.csv      # Dataset of image paths and their extracted textual contexts
│   ├── responses.csv           # Aggregated CSV of all generated response texts
│   ├── evaluation_ready.csv    # Final dataset for the evaluation GUI
│   └── evaluation_results.csv  # Raw scores and preferences from human evaluation
├── notebooks/
│   └── data_analysis.ipynb     # Jupyter notebook for statistical analysis and visualization
├── src/
│   ├── ArticleDownloaders.py   # Scripts to download academic papers
│   ├── ArticleProcessor.py     # Processes PDFs using docling
│   ├── dev_message.txt         # System prompt for the language model
│   ├── DatasetConstructor.py   # Builds the image-context dataset
│   ├── ResponseGenerator.py    # Generates interpretations via an LLM API
│   └── EvaluationGUI.py        # Tkinter GUI for human evaluation
├── requirements.txt            # Python package dependencies
└── run.py                      # Main script to orchestrate the pipeline
```

### Files

*   `run.py`: **Main entry point.** Orchestrates the entire pipeline from data acquisition to evaluation via command-line arguments.
*   `src/ArticleDownloader.py`: Downloads academic papers from online sources.
*   `src/ArticleProcessor.py`: Uses `docling` to convert PDFs to a structured format, extracting images and text.
*   `src/DatasetConstructor.py`: Creates the final dataset by pairing selected images with their surrounding textual context.
*   `src/ResponseGenerator.py`: Generates chart interpretations using an LLM API, creating both with-context and without-context versions.
*   `src/EvaluationGUI.py`: A Tkinter-based GUI for the blinded human evaluation, capturing scores on Likert scales.

### Setup

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file:
    ```bash
    touch .env
    ```
    Then, edit the `.env` file with your API keys:
    ```
    OPENAI_API_KEY='your-openai-api-key-goes-here'
    OSF_API_TOKEN='your-osf-api-key-goes-here'
    ```

### Usage

The `run.py` script controls the entire workflow. You can run specific steps or the full pipeline.

```bash
# Run the full pipeline from start to finish
python run.py --step all

# Run only a specific step (e.g., generate responses)
# Steps: download, process, construct, generate, evaluate
python run.py --step generate

# Get help on available commands
python run.py --help
```