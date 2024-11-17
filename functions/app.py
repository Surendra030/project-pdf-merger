from flask import Flask, request, jsonify, send_file, render_template
import os
import time
from PyPDF2 import PdfMerger
from io import BytesIO
from flask_lambda import FlaskLambda

# Initialize Flask app with FlaskLambda for serverless support
app = FlaskLambda(__name__)

# Folder for temporary files (you can use S3 for a production solution)
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Dictionary to track file timestamps
file_timestamps = {}

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    merger = PdfMerger()
    merger.append(pdf1_path)
    merger.append(pdf2_path)
    merger.write(output_path)
    merger.close()

# Delete the merged PDF after 5 minutes
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")

@app.route('/')
def home():
    """
    Render the home page.
    """
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

        # Store the timestamp of when the file was created (for deletion)
        file_timestamps[merged_pdf_path] = time.time()

        # Set a timer to delete the file after 5 minutes (300 seconds)
        # Timer will not work well in serverless, use an external cron job or cleanup mechanism

        # Stream the file back as a response
        response = send_file(
            merged_pdf_path,
            as_attachment=True,
            download_name="merged_output.pdf"
        )

        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check-merged-file', methods=['GET'])
def check_merged_file():
    merged_pdf_path = os.path.join(TEMP_FOLDER, "merged_output.pdf")

    # Check if the file exists and has not been deleted
    if os.path.exists(merged_pdf_path) and time.time() - file_timestamps.get(merged_pdf_path, 0) < 300:
        return send_file(
            merged_pdf_path,
            as_attachment=True,
            download_name="merged_output.pdf"
        )
    else:
        return jsonify({"error": "File has expired or does not exist. Please upload the files again."}), 404

# This is the handler function that will be invoked by Netlify
def lambda_handler(event, context):
    return app.lambda_handler(event, context)

