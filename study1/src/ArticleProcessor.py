import logging
from pathlib import Path
import time
import os

from docling_core.types.doc.document import ImageRefMode
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)

class ArticleProcessor:
    """
    Processes articles using the docling library to extract text and images from PDFs.
    """
    def process_articles(self, input_path: str, pipeline_options = PdfPipelineOptions()):
        """ 
        Processes articles from the specified input path, converting them to a structured format
        with OCR and table structure analysis. The results are saved in a specified output directory. 

        Args:
        input_path (str): The path to the directory containing articles to process.
        pipeline_options (PdfPipelineOptions): Options for the document processing pipeline.
        """
        _log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Validate input path
        input_path = Path(input_path)
        if not input_path.exists():
            logging.error(f"Input path {input_path} does not exist.")
            return None
        
        articles = list(input_path.glob('**/*.pdf'))
        if not articles:
            logging.warning(f"No PDF articles found in {input_path} or its subdirectories.")
            return None
        
        # Preconfigure pipeline options
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        pipeline_options.ocr_options.lang = ["en"]
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_picture_images = True
        pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
        )

        # Initialize the document converter with the specified options
        doc_converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.DOCX],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.DOCX: WordFormatOption(pipeline_options=pipeline_options),
            }
        )

        # Process individual articles in the input directory
        _log.info(f"Processing articles in {input_path}...")
        
        # Convert each article
        _log.info(f"Converting articles: {articles}")
        for article in articles:
            # Start timing the conversion
            start_time = time.time()
            article_path = input_path / article
            conv_result = doc_converter.convert(article_path)
            end_time = time.time() - start_time
            _log.info(f"{article} converted in {end_time:.2f} seconds.")
        
            ## Export results
            _log.info(f"Exporting results for {article}...")
            output_dir = Path(input_path) / "processed_articles"
            output_dir.mkdir(parents=True, exist_ok=True)
            doc_filename = conv_result.input.file.stem

            # Save markdown with externally referenced pictures
            md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
            conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)
            _log.info(f"{article} successfully processed and saved to {md_filename}.")
        _log.info("All articles processed successfully.")

if __name__ == "__main__":
    # # # -- How it was used for the experiment -- ##
    # # Example usage for multiple directories with articles
    # directories_list = os.listdir("./tbp_articles")

    # processor = ArticleProcessor()
    # for directory in directories_list:
    #     input_path = "./tbp_articles" + f"/{directory}"
    #     processor.process_articles(input_path=input_path)

    # Example usage
    STUDY1_DIR = Path(__file__).parent.parent
    
    # Define the parent directory where raw articles were downloaded
    # This should match the output location from ArticleDownloader.py
    ARTICLES_PARENT_DIR = STUDY1_DIR / "articles"

    # --- How it was used for the experiment ---
    # Check if the parent directory exists
    if not ARTICLES_PARENT_DIR.exists():
        logging.error(f"Articles directory not found at: {ARTICLES_PARENT_DIR}")
        logging.error("Please run the 'download' step first.")
    else:
        # Get the list of subdirectories (e.g., 'arxiv_downloads', 'osf_downloads')
        # We use a generator expression to filter for directories only
        directories_list = (d for d in ARTICLES_PARENT_DIR.iterdir() if d.is_dir())

        processor = ArticleProcessor()
        for directory_path in directories_list:
            # The 'directory_path' is already an absolute Path object
            logging.info(f"--- Processing directory: {directory_path.name} ---")
            processor.process_articles(input_path=directory_path)