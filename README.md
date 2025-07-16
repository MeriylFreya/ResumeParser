# Resume Parser

## Project Overview
The Resume Parser is a web application designed to streamline the recruitment process by automatically extracting key candidate information from uploaded resumes. Using advanced parsing technology, the tool extracts contact details such as emails and phone numbers, as well as sample text from resumes, enabling faster and smarter hiring decisions.
https://resumeparser-3ag5.onrender.com

## Features
- Upload PDF or DOCX resumes for parsing.
- Extracts contact information including emails and phone numbers.
- Displays a sample of the extracted text for quick review.
- Clean and modern user interface styled with Tailwind CSS.
- Responsive design for usability across devices.

## Technology Stack
- Backend: Python (Flask) for handling file uploads and parsing logic.
- Frontend: HTML templates with Tailwind CSS for styling.
- File handling and parsing logic implemented in `app.py`.
- Static assets served from the `static/` directory.

## Usage
1. Run the Flask application (`app.py`).
2. Open the web interface in a browser.
3. Upload a resume file (PDF or DOCX).
4. View the parsed details displayed on the page.

## Project Structure
- `app.py`: Main application script handling routes and parsing.
- `templates/`: HTML templates for the web pages.
- `static/`: Static files such as images and stylesheets.
- `uploads/`: Directory for storing uploaded resume files.

## Future Improvements
- Support for additional resume formats.
- Enhanced parsing accuracy with NLP techniques.
- Export parsed data to CSV or JSON formats.
- User authentication and resume management.

## License
This project is open source and available under the MIT License.
