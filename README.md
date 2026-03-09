# LABEL ME!

**LABEL ME!** is an interactive installation that explores the tension between social labeling and personal identity in an algorithmically mediated society. It transforms psychological data into a "branded" beverage identity using Generative AI, prompting a reflection on the commodification of the self.

## 🛠 Tech Stack

- **Backend:** Flask (Python 3.13.7)
- **Frontend:** Vanilla JavaScript, CSS
- **AI Integration:** - **OpenAI GPT-4o:** Brand Strategist (Text Generation)
  - **Google Vertex AI Imagen:** Visual Identity (Image Generation)
- **Image Processing:** Custom PIL (Python Imaging Library) engine for high-resolution label composition (2717x768px).

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.13.7**
- Google Cloud CLI (authenticated for Vertex AI)
- OpenAI API Account

### 2. Clone the Repository
```bash
git clone [https://github.com/your-username/label-me.git](https://github.com/your-username/label-me.git)
cd label-me
```

### 3. Setup Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration (.env)
Create a .env file in the root directory and add your credentials. This file is used to manage sensitive API keys and environment-specific settings.
```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud Project Settings
GOOGLE_CLOUD_PROJECT_ID=your_project_id_here
GOOGLE_CLOUD_LOCATION=us-central1
```

## 💻 Running the Application
1. **Start the Server:**
   ```bash
   # Run on port 5001
   python app.py
   ```
2. **Access the Interface:** `http://localhost:5001`
  
## 🍾 Physicalization Workflow
This project incorporates human labor and physical assembly to bridge the digital-physical divide:

- Printing: A staff member operates the host PC to trigger high-resolution printing onto OHP (Overhead Projector) film via an inkjet printer.
- Cutting: The printed film is manually cut using scissors.
- Application: The visitor applies the label to a 500ml PET bottle using tape glue.
- Placement: The finished "product" is placed in a refrigerator, completing the metaphor of self-commodification.


## 📄 License
This project is for academic/artistic exhibition purposes.
