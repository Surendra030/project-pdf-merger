import os
import time
from flask import Flask, request, send_file, jsonify, render_template
from PyPDF2 import PdfMerger
from flask_lambda import FlaskLambda

# Create Flask app for Lambda
app = Flask(__name__,template_folder="../templates", static_folder="../public")

# Folder for temporary files
TEMP_FOLDER = "/tmp"  # Use `/tmp` for serverless environments
file_timestamps = {}

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    merger = PdfMerger()
    merger.append(pdf1_path)
    merger.append(pdf2_path)
    merger.write(output_path)
    merger.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs_route():
    try:
        # Get the uploaded files
        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']

        # Save them temporarily
        pdf1_path = os.path.join(TEMP_FOLDER, "pdf1.pdf")
        pdf2_path = os.path.join(TEMP_FOLDER, "pdf2.pdf")
        merged_pdf_path = os.path.join(TEMP_FOLDER, "merged_output.pdf")
        pdf1.save(pdf1_path)
        pdf2.save(pdf2_path)

        # Merge PDFs
        merge_pdfs(pdf1_path, pdf2_path, merged_pdf_path)

        # Track file timestamp
        file_timestamps[merged_pdf_path] = time.time()

        return send_file(merged_pdf_path, as_attachment=True, download_name="merged_output.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check-merged-file', methods=['GET'])
def check_merged_file():
    merged_pdf_path = os.path.join(TEMP_FOLDER, "merged_output.pdf")
    if os.path.exists(merged_pdf_path) and time.time() - file_timestamps.get(merged_pdf_path, 0) < 300:
        return send_file(merged_pdf_path, as_attachment=True, download_name="merged_output.pdf")
    else:
        return jsonify({"error": "File has expired or does not exist. Please upload the files again."}), 404

def handler(event, context):
    return app(event, context)
