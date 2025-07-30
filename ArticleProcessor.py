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
            
            articles = os.listdir(input_path)
            if not articles:
                logging.error(f"No articles found in {input_path}.")
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
    # Example usage for a single directory with articles
    processor = ArticleProcessor()
    input_path = "./your/path/to/directory/of/articles"  # Replace with your actual path
    processor.process_articles(input_path)

    # # Example usage for multiple directories with articles
    # directories_list = os.listdir("./tbp_articles")

    # processor = ArticleProcessor()
    # for directory in directories_list:
    #     input_path = "./tbp_articles" + f"/{directory}"
    #     processor.process_articles(input_path=input_path)
