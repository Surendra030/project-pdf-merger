# functions/handler.py
import os
from flask import Flask, jsonify, request, send_file
from PyPDF2 import PdfMerger
from io import BytesIO

app = Flask(__name__)

@app.route("/merge-pdfs", methods=["POST"])
def merge_pdfs_route():
    # Assuming files are uploaded in a `files[]` field
    try:
        files = request.files.getlist("files[]")
        if len(files) < 2:
            return jsonify({"error": "At least two files are required."}), 400
        
        pdf_merger = PdfMerger()

        # Merge PDFs
        for file in files:
            pdf_merger.append(file)

        # Save the merged PDF into a BytesIO object
        merged_pdf = BytesIO()
        pdf_merger.write(merged_pdf)
        merged_pdf.seek(0)

        # Send the merged file back as response
        return send_file(
            merged_pdf,
            as_attachment=True,
            download_name="merged_output.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(request, context):
    from werkzeug.serving import run_simple
    from werkzeug.wrappers import Request, Response

    # Make Flask app callable as a Netlify Function
    return app(request, context)
