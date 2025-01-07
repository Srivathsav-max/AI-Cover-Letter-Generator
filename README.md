# AI-Powered Cover Letter Generator

An intelligent application that generates customized cover letters using NVIDIA's AI model based on your resume and job description. Built with Streamlit and OpenAI/NVIDIA API integration.

## 🌟 Features

- **PDF Resume Upload**: Upload your resume in PDF format
- **Job Description Analysis**: Paste job description for targeted cover letter generation
- **Optional Company Address**: Add company address if available
- **Real-time Generation**: Uses NVIDIA's LLM for intelligent content creation
- **Live Preview & Editing**: Edit generated content before finalizing
- **PDF Export**: Download your cover letter in professional PDF format
- **Current Date**: Automatically includes today's date in proper format
- **Clean Formatting**: Properly structured output with consistent spacing

## 🛠️ Technologies Used

- Python 3.8+
- Streamlit
- OpenAI API (NVIDIA Backend)
- PyPDF2
- FPDF
- python-dotenv

## 📋 Prerequisites

- Python 3.8 or higher
- NVIDIA API key
- Git (for cloning the repository)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-application-automation
   ```

2. **Create and activate virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with:
   ```
   NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
   NVIDIA_API_KEY=your-api-key-here
   MODEL_NAME=meta/llama-3.3-70b-instruct
   ```

## 🖥️ Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Using the Application**
   - Upload your resume (PDF format)
   - Paste the job description
   - (Optional) Add company address
   - Click "Generate Cover Letter"
   - Edit the generated content if needed
   - Click "Finalize and Generate PDF"
   - Download your cover letter

## 📁 Project Structure

```
job-application-automation/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration and API setup
│   ├── pdf_utils.py       # PDF handling functions
│   ├── llm_utils.py       # LLM integration
│   ├── text_utils.py      # Text processing
│   └── ui.py             # Streamlit UI components
├── main.py               # Application entry point
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables
└── README.md            # Project documentation
```

## ⚠️ Important Notes

- Keep your API keys secure and never commit them to version control
- Ensure your resume is in PDF format
- The application requires an active internet connection
- The generated cover letter can be edited before final PDF generation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Made with ❤️ by Srivathsav

## 🙏 Acknowledgments

- NVIDIA for providing the LLM API
- Streamlit for the amazing web framework
- All contributors and users of this project