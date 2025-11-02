# TerraReviewBot - AI-Powered Terraform Plan Validator

TerraReviewBot is a modern Flask web application that validates Terraform plan files and provides AI-powered analysis using NVIDIA's Llama 3.1 Nemotron model. Upload your Terraform plans to get intelligent insights, security assessments, and actionable recommendations.

## 🚀 Features

- **🤖 AI-Powered Analysis**: Intelligent plan review using NVIDIA Llama 3.1 Nemotron
- **📝 Multi-format Support**: JSON (.json) and text (.txt) Terraform plan files
- **🔐 Session Management**: API keys stored securely in browser sessions
- **🎨 Modern UI**: Clean, responsive interface with drag-and-drop upload
- **✅ Smart Validation**: Automatic format detection and structure validation
- **📊 Plan Summary**: Detailed resource changes with visual statistics
- **🛡️ Security Assessment**: AI-powered security and risk analysis
- **💰 Cost Impact**: Infrastructure cost implications and recommendations

## 📋 Prerequisites

- Python 3.7 or higher
- Modern web browser

## 🛠️ Quick Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd TerraReviewBot
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5001
   ```

## 🔑 AI Setup

1. **Get your free NVIDIA API key:**
   - Visit [NVIDIA Build](https://build.nvidia.com/)
   - Sign up for a free account
   - Navigate to "API Keys" section
   - Generate a new API key

2. **Enter your API key:**
   - On the TerraReviewBot home page, enter your API key
   - It will be stored securely in your browser session
   - No need to re-enter for subsequent uploads

## 📖 Usage

### 1. Generate Terraform Plan Files

**JSON Format (Recommended):**
```bash
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
```

**Text Format:**
```bash
terraform plan > plan.txt
```

### 2. Upload and Analyze

1. **Enter API Key** (first time only)
2. **Upload File**: Drag & drop or click to browse
3. **Get Results**: View validation status and AI analysis
4. **Review Insights**: 
   - Resource changes summary
   - Security risk assessment
   - Cost impact analysis
   - Next steps recommendations

## 📊 What You Get

- **📈 Plan Summary**: Visual statistics of resource changes
- **🎯 AI Analysis**: 
  - Overview of planned changes
  - Detailed resource breakdown
  - Security and risk assessment
  - Cost implications
  - Actionable next steps
- **🔍 Validation**: Confirms proper Terraform plan format
- **🗂️ Complete Resource Table**: All changes excluding no-op actions

## 🔒 Security & Privacy

- **🗂️ No Data Storage**: Files are processed and immediately deleted
- **🔐 Session-only API Keys**: Stored securely in browser sessions only
- **✅ File Validation**: Prevents malicious uploads
- **📏 Size Limits**: 16MB maximum file size
- **🛡️ Secure Processing**: All operations happen server-side with proper validation

## 📁 Project Structure

```
TerraReviewBot/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template with styling
│   ├── index.html     # Home page with upload form
│   └── result.html    # Results display page
└── .venv/             # Virtual environment
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Open source project. Feel free to modify and distribute as needed.

---

**TerraReviewBot** - Making Terraform plan analysis smarter with AI! 🤖✨
