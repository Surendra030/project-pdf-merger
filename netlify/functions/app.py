from flask import Flask, request, jsonify, send_file
from flask_serverless import FlaskServerless
import os
from PyPDF2 import PdfMerger
from io import BytesIO

# Initialize Flask app
app = Flask(__name__,
static_folder=os.path.join(os.getcwd(), 'public')),              static_folder="../../public")
template_folder=os.path.join(os.getcwd(), 'templates')
# Use /tmp for temporary files in serverless functions
TEMP_FOLDER = "/tmp"

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    merger = PdfMerger()
    merger.append(pdf1_path)
    merger.append(pdf2_path)
    merger.write(output_path)
    merger.close()

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs_route():
    try:
        # Get the uploaded files
        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']

        # Save them temporarily to /tmp
        pdf1_path = os.path.join(TEMP_FOLDER, "pdf1.pdf")
        pdf2_path = os.path.join(TEMP_FOLDER, "pdf2.pdf")
        merged_pdf_path = os.path.join(TEMP_FOLDER, "merged_output.pdf")
        pdf1.save(pdf1_path)
        pdf2.save(pdf2_path)

        # Merge PDFs
        merge_pdfs(pdf1_path, pdf2_path, merged_pdf_path)

        # Stream the file back as a response
        return send_file(
            merged_pdf_path,
            as_attachment=True,
            download_name="merged_output.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
