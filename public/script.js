document.getElementById('pdfForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData();
    const pdf1 = document.getElementById('pdf1').files[0];
    const pdf2 = document.getElementById('pdf2').files[0];
    const downloadBtn = document.getElementById('downloadBtn');
    const responseDiv = document.getElementById('response');

    if (!pdf1 || !pdf2) {
        alert("Please select both PDF files.");
        return;
    }

    formData.append('pdf1', pdf1);
    formData.append('pdf2', pdf2);

    // Update download button to indicate "processing"
    downloadBtn.style.display = 'inline-block';
    downloadBtn.style.backgroundColor = 'red';
    downloadBtn.textContent = 'Processing...';
    downloadBtn.disabled = true;

    responseDiv.textContent = '';

    try {
        const response = await fetch('/.netlify/functions/merge_pdfs', { // Updated URL
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Update the download button for ready status
            downloadBtn.style.backgroundColor = 'green';
            downloadBtn.textContent = 'Download Merged PDF';
            downloadBtn.disabled = false;

            // Set up the download behavior
            downloadBtn.onclick = () => {
                const link = document.createElement('a');
                link.href = url;
                link.download = 'merged.pdf';
                link.click();
            };

            responseDiv.textContent = "PDFs merged successfully!";
        } else {
            const errorData = await response.json();
            responseDiv.textContent = `Error: ${errorData.error}`;
            downloadBtn.style.display = 'none'; // Hide download button if error occurs
        }
    } catch (error) {
        responseDiv.textContent = `Error: ${error.message}`;
        downloadBtn.style.display = 'none'; // Hide download button if error occurs
    }
});
