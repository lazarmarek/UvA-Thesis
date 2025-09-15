import typer
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Define project paths
# This assumes run.py is in the 'study1' directory.
BASE_DIR = Path(__file__).parent.resolve()
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"

# Add src to the Python path to allow for direct imports
sys.path.append(str(SRC_DIR))

# --- App Definition ---
app = typer.Typer(
    name="study1-pipeline",
    help="Orchestrates the full data processing and evaluation pipeline for Study 1.",
    add_completion=False
)

def _run_script(script_name: str, *args):
    """Helper function to run a Python script from the src directory."""
    script_path = SRC_DIR / script_name
    if not script_path.exists():
        typer.secho(f"Error: Script '{script_path}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    command = [sys.executable, str(script_path), *args]
    typer.secho(f"Running: {' '.join(command)}", fg=typer.colors.YELLOW)
    
    try:
        # Using subprocess.run to wait for completion
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        typer.secho(f"Successfully ran {script_name}.", fg=typer.colors.GREEN)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Error running {script_name}:", fg=typer.colors.RED)
        typer.secho(e.stderr, fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def download():
    """1. Downloads articles from online sources."""
    typer.secho("--- Step 1: Downloading Articles ---", bold=True)
    _run_script("ArticleDownloaders.py")

@app.command()
def process():
    """2. Processes downloaded PDFs with docling to extract images and text."""
    typer.secho("--- Step 2: Processing Articles ---", bold=True)
    _run_script("ArticleProcessor.py")

@app.command()
def construct():
    """3. Constructs the image-context dataset from processed articles."""
    typer.secho("--- Step 3: Constructing Dataset ---", bold=True)
    _run_script("DatasetConstructor.py")

@app.command()
def generate():
    """4. Generates chart interpretations using the LLM API."""
    typer.secho("--- Step 4: Generating Responses ---", bold=True)
    _run_script("ResponseGenerator.py")

@app.command()
def evaluate():
    """5. Launches the Tkinter GUI for human evaluation."""
    typer.secho("--- Step 5: Launching Evaluation GUI ---", bold=True)
    # GUIs are often run directly without capturing output
    script_path = SRC_DIR / "EvaluationGUI.py"
    if not script_path.exists():
        typer.secho(f"Error: Script '{script_path}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    command = [sys.executable, str(script_path)]
    typer.secho(f"Running: {' '.join(command)}", fg=typer.colors.YELLOW)
    subprocess.run(command)
    typer.secho("GUI closed.", fg=typer.colors.GREEN)

@app.command(name="all")
def run_all():
    """Runs the entire pipeline sequentially (download -> process -> construct -> generate -> evaluate)."""
    typer.secho("--- Running Full Pipeline ---", bold=True, fg=typer.colors.CYAN)
    download()
    process()
    construct()
    generate()
    evaluate()
    typer.secho("--- Full Pipeline Complete ---", bold=True, fg=typer.colors.CYAN)

if __name__ == "__main__":
    app()