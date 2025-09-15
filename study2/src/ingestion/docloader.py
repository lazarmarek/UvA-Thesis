from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
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
import logging
from typing import List



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader():

    def __init__(self):
        pass

    def load_doc(self, file_path, pipeline_options=PdfPipelineOptions(), tokenizer="BAAI/bge-base-en-v1.5") -> List:
        """Load document using LangChain's DoclingLoader.
            Currently supports PDF and Word documents."""

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

        converter = DocumentConverter(
                allowed_formats=[InputFormat.PDF, InputFormat.DOCX],
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                    InputFormat.DOCX: WordFormatOption(pipeline_options=pipeline_options),
                }
            )

        # Initialize Docling Loader for PDF
        loader = DoclingLoader(
            file_path=file_path,
            converter=converter,
            export_type=ExportType.DOC_CHUNKS,
            chunker=HybridChunker(tokenizer=tokenizer)
        )
        
        documents = loader.load()
        return documents

if __name__ == "__main__":

    # Example usage
    file_path = "/home/mlazar/projects/thesis/study2/data/tbp_articles/arxiv_articles/2507.08637v1.pdf"
    doc_loader = DocumentLoader()
    documents = doc_loader.load_doc(file_path)
    for doc in documents:
        print(doc.page_content)