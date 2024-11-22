from flask import Flask, request, jsonify, send_file, render_template
import os
import time
from PyPDF2 import PdfFileMerger

# Folder for temporary files
TEMP_FOLDER = "/tmp"  # Use '/tmp' for temporary storage on Vercel
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Dictionary to track file timestamps
file_timestamps = {}

# Initialize Flask app
app = Flask(__name__,
            static_folder=os.path.join(os.getcwd(), 'public'),
            template_folder=os.path.join(os.getcwd(), 'templates'))

def merge_pdfs(pdf1_path, pdf2_path, output_path):
    merger = PdfFileMerger()
    merger.append(pdf1_path)
    merger.append(pdf2_path)
    merger.write(output_path)
    merger.close()

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

        # Stream the file back as a response
        return send_file(
            merged_pdf_path,
            as_attachment=True,
            download_name="merged_output.pdf"
        )
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

if __name__ == '__main__':
    app.run(debug=True)
