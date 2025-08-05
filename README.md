# Diabetes Readmission Prediction Chatbot

A comprehensive healthcare chatbot system built with Rasa framework for predicting diabetes patient readmission risk. This project combines natural language processing with machine learning to provide healthcare professionals with an intuitive interface for patient risk assessment and generates detailed PDF reports.

## Backend Repository

**IMPORTANT**: This project requires a separate backend API server for machine learning predictions and PDF report generation. You must clone and set up the backend repository first before running this chatbot application.

**Backend Repository**: https://github.com/gurmatsinghsour/SweatHogChatBot

### Backend Setup Steps:

1. Clone the backend repository:
   ```bash
   git clone https://github.com/gurmatsinghsour/SweatHogChatBot.git
   cd SweatHogChatBot
   ```

2. Follow the backend setup instructions in its README file

3. Ensure the backend API is running on `http://localhost:8080` before starting this chatbot

### What the Backend Handles:

- Machine learning model inference for diabetes readmission prediction
- PDF report generation with patient analysis and visualizations
- File management and download endpoints
- Data validation and preprocessing
- RESTful API endpoints for the chatbot to consume

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

- Interactive chatbot interface for diabetes patient data collection
- Machine learning-based readmission risk prediction
- PDF report generation with detailed analysis
- Real-time conversation with natural language understanding
- RESTful API integration
- Secure data handling and validation
- Multi-environment support (development, testing, production)

## Architecture

![Architecture Diagram](./architecture_diag/architecture.pdf)

The system consists of four main components:

1. **Rasa Core & NLU**: Handles conversation flow and natural language understanding
2. **Actions Server**: Custom Python actions for ML predictions and API integrations  
3. **Frontend**: React-based web interface for user interactions
4. **Backend API**: Flask-based service for PDF generation and file management (separate repository)

For detailed architectural information, see the [Technical Architecture Guide](./TECHNICAL_ARCHITECTURE_GUIDE.md) and the [Architecture Diagram](./architecture_diag/architecture.pdf).

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.9.23** (exact version required for compatibility)
- **Node.js** (version 16+ recommended)
- **npm** or **yarn**
- **Conda** (Anaconda or Miniconda)
- **Git**
- **Ollama** (for local LLM inference)

### Ollama Setup

This project uses Ollama for local language model inference as a fallback option. You need to install Ollama and download the required model:

1. **Install Ollama**:
   - Visit https://ollama.com and download Ollama for your operating system
   - Follow the installation instructions for your platform

2. **Download the required model**:
   ```bash
   ollama pull llama3.2:1b
   ```

3. **Verify Ollama is running**:
   ```bash
   ollama list
   ```
   You should see `llama3.2:1b` in the list of available models.

The chatbot uses `llama3.2:1b` model for faster responses when generating explanations and handling complex queries.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/gurmatsinghsour/rasa-capstone.git
cd rasa-capstone
```

### Step 2: Create Conda Environment

Create a new conda environment with Python 3.9.23 (exact version required):

```bash
conda create -n rasa-env python=3.9.23
conda activate rasa-env
```

**Note**: Python 3.9.23 is specifically required for compatibility with Rasa 3.6.21 and all dependencies. Using other versions may cause compatibility issues.

### Step 3: Install Python Dependencies

Install the main requirements:

```bash
pip install -r requirements.txt
```

Install actions server dependencies:

```bash
pip install -r requirements-actions.txt
```

### Step 4: Install Spacy Language Model

Download the English language model for Spacy:

```bash
python -m spacy download en_core_web_md
```

### Step 5: Setup Frontend

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
cd ..
```

### Step 6: Train the Rasa Model

Train the initial Rasa model:

```bash
rasa train
```

## Configuration

### Rasa Configuration

The main configuration files are:

- `config.yml`: NLU and Core configuration
- `domain.yml`: Chatbot domain definition
- `endpoints.yml`: External service endpoints
- `credentials.yml`: Channel credentials

## Running the Application

### Method 1: Using the Start Script (Recommended)

Make the start script executable and run it:

```bash
chmod +x start_and_test.sh
./start_and_test.sh
```

### Method 2: Manual Startup

Start each component manually in separate terminals:

#### Terminal 1: Start Rasa Server
```bash
conda activate rasa-env
rasa run --enable-api --cors "*" --port 5005
```

#### Terminal 2: Start Actions Server
```bash
conda activate rasa-env
rasa run actions --port 5055
```

#### Terminal 3: Start Frontend
```bash
cd frontend
npm run dev
```

**Note**: Make sure the backend API server from https://github.com/gurmatsinghsour/SweatHogChatBot is running on `http://localhost:8080` before starting the chatbot.

## Usage

1. **Access the Application**: Open your browser and navigate to `http://localhost:3000`

2. **Start Conversation**: Begin chatting with the bot by typing a greeting

3. **Provide Patient Data**: Follow the bot's prompts to provide patient information:
   - Demographics (age, gender)
   - Medical history
   - Current medications
   - Lab results
   - Hospital stay details

4. **Get Prediction**: The bot will analyze the data and provide a readmission risk assessment

5. **Download Report**: Click the download button to get a detailed PDF report

## API Endpoints

### Rasa Endpoints

- `POST /webhooks/rest/webhook`: Send messages to the bot
- `GET /status`: Check server status
- `GET /model`: Get current model information

### Custom API Endpoints

- `POST /predict_with_report`: Generate prediction and PDF report
- `GET /download_report/{filename}`: Download generated PDF reports

### Frontend API

- `GET /`: Main chat interface
- Static assets served from `/assets/`

## Testing

### Run Rasa Tests

```bash
conda activate rasa-env
rasa test
```

### Test Stories

```bash
rasa test stories
```

### Test NLU

```bash
rasa test nlu
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process using port 5005
   lsof -ti:5005 | xargs kill -9
   ```

2. **Conda Environment Issues**
   ```bash
   # Remove and recreate environment
   conda remove -n rasa-env --all
   conda create -n rasa-env python=3.9.23
   ```

3. **Spacy Model Not Found**
   ```bash
   python -m spacy download en_core_web_md
   ```

4. **Frontend Build Issues**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Log Files

Check the following log files for debugging:

- `rasa_server.log`: Rasa server logs
- `actions_server.log`: Actions server logs
- `frontend.log`: Frontend application logs

## Project Structure

```
rasa-capstone/
├── actions/                    # Custom Rasa actions
│   ├── __init__.py
│   └── actions.py             # Main actions implementation
├── architecture_diag/          # Architecture documentation
│   └── architecture.pdf       # System architecture diagram
├── data/                      # Training data
│   ├── nlu.yml               # NLU training examples
│   ├── rules.yml             # Conversation rules
│   └── stories.yml           # Training stories
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── types/           # TypeScript definitions
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── models/                   # Trained Rasa models
├── tests/                    # Test files
├── config.yml               # Rasa configuration
├── domain.yml               # Chatbot domain
├── endpoints.yml            # External endpoints
├── credentials.yml          # Channel credentials
├── requirements.txt         # Main Python dependencies
├── requirements-actions.txt # Actions server dependencies
└── start_and_test.sh       # Startup script
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is part of a capstone project for educational purposes.

## Support

For support and questions, please contact the development team or create an issue in the repository. 