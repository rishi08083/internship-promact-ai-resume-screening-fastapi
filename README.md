## Setup Instructions

1. Clone the repository: `git clone <repo-url>`
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. To set up **pytesseract** for Optical Character Recognition (OCR) on your system, follow these steps:

**a. Install Tesseract OCR Engine:**

   - **Windows:**
     - Download the Tesseract installer from the official repository:
     - Run the installer and follow the on-screen instructions. By default, it installs to `C:\Program Files\Tesseract-OCR`.
     - Ensure that the Tesseract executable is added to your system's PATH during installation. If not, you can manually add it:
       - Open the Start Menu, search for "Environment Variables," and select "Edit the system environment variables."
       - In the System Properties window, click on "Environment Variables."
       - Under "System variables," find and select "Path," then click "Edit."
       - Click "New" and add `C:\Program Files\Tesseract-OCR`.
       - Click "OK" to apply the changes.
   - **macOS:**
     - Use Homebrew to install Tesseract:
       ```bash
       brew install tesseract
       ```
   - **Linux (Ubuntu/Debian):**
     - Install Tesseract using apt:
       ```bash
       sudo apt update
       sudo apt install tesseract-ocr
       ```

**b. Install Python Dependencies:**

   - Ensure you're using Python 3.6 or higher.
   - Install the required Python packages using pip:
     ```bash
     pip install pytesseract Pillow
     ```

**c. Configure pytesseract in Your Python Script:**

   - In your Python script, specify the path to the Tesseract executable if it's not in your system's PATH:
     ```python
     import pytesseract

     # For Windows users, specify the path explicitly
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

**d. Add Installation Instructions to Your Markdown Documentation:**

   - To document the installation process in your Markdown file, include the following sections:

     ```markdown
     # Installing pytesseract OCR

     To set up pytesseract for OCR on your system, follow these steps:

     ## 1. Install Tesseract OCR Engine

     - **Windows:**
       1. Download the Tesseract installer from the official repository.
       2. Run the installer and follow the on-screen instructions. By default, it installs to `C:\Program Files\Tesseract-OCR`.
       3. Ensure that the Tesseract executable is added to your system's PATH during installation. If not, manually add `C:\Program Files\Tesseract-OCR` to your PATH environment variable.

     - **macOS:**
       1. Install Homebrew if it's not already installed.
       2. Use Homebrew to install Tesseract:
          ```bash
          brew install tesseract
          ```

     - **Linux (Ubuntu/Debian):**
       1. Update your package list:
          ```bash
          sudo apt update
          ```
       2. Install Tesseract:
          ```bash
          sudo apt install tesseract-ocr
          ```

     ## 2. Configure pytesseract in Your Python Script

     - In your Python script, specify the path to the Tesseract executable if it's not in your system's PATH:
       ```python
       import pytesseract

       # For Windows users, specify the path explicitly
       pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
       ```

     For more detailed information, refer to the [pytesseract GitHub repository](https://github.com/madmaze/pytesseract).
     ```

By following these steps, you'll have pytesseract installed and configured for OCR tasks on your system. 
6. Run the app: `uvicorn main:app --reload`
