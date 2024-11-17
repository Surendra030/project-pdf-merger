from PyPDF2 import PdfMerger

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    """
    Merges two PDF files into one.

    Args:
        pdf1_path (str): Path to the first PDF file.
        pdf2_path (str): Path to the second PDF file.
        output_path (str): Path to save the merged PDF.

    Returns:
        str: Path to the merged PDF.
    """
    try:
        # Create a PdfMerger object
        merger = PdfMerger()

        # Append PDFs
        merger.append(pdf1_path)
        merger.append(pdf2_path)

        # Write the merged PDF
        merger.write(output_path)
        merger.close()

        return output_path
    except Exception as e:
        raise RuntimeError(f"Error merging PDFs: {e}")
