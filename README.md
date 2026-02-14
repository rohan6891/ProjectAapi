# ProjectAapi - Social Media Forensic Investigation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)

> **A comprehensive FastAPI-based backend system for social media forensic investigation and digital evidence collection designed for law enforcement agencies.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Supported Platforms](#-supported-platforms)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**ProjectAapi** is a powerful backend system built with FastAPI that enables law enforcement agencies (NIA, Police, Cybercrime units) to conduct digital forensic investigations across multiple social media platforms. The system automates data collection, generates comprehensive reports in multiple formats, and provides timeline visualization for suspect activities.

### Why ProjectAapi?

- ✅ **Multi-Platform Support** - Scrape data from Instagram, Facebook, X (Twitter), WhatsApp, and Telegram
- ✅ **Dual Report Generation** - PDF for court submissions + JSON for data analysis
- ✅ **Case Management** - Organize evidence by investigation cases
- ✅ **Timeline Visualization** - Cross-platform chronological activity tracking
- ✅ **Secure & Scalable** - JWT authentication, async operations, background processing
- ✅ **Evidence Integrity** - Timestamped, organized, and traceable data collection

---

## ✨ Key Features

### 1. **Automated Social Media Scraping**
- Collect posts, chats, followers, comments, and media
- Selenium-based automation for accurate data extraction
- Background task processing for non-blocking operations

### 2. **Comprehensive Data Collection**

| Platform | Data Types |
|----------|-----------|
| **Instagram** | Posts, Stories, Chats, Followers, Following, Comments, Likes, Saved Posts, Tagged Posts |
| **Facebook** | Posts, Chats, Friends, Personal Information |
| **X (Twitter)** | Tweets, Chats, Followers, Following |
| **WhatsApp** | Chat history (infrastructure ready) |
| **Telegram** | Messages, channels (infrastructure ready) |

### 3. **Dual-Format Report Generation**

#### PDF Reports
- Professional A4 format with title pages
- Organized sections for each data type
- Court-ready evidence documentation

#### JSON Reports
- Machine-readable structured data
- Easy integration with analysis tools
- Preserves all metadata and timestamps

### 4. **Case Management System**
- Create and manage investigation cases
- Link multiple suspects to one case
- Track data sources across platforms
- Officer information tracking (NIA, CIO, EO)
- Case status monitoring (In Progress / Completed)

### 5. **Timeline Visualization**
- Chronological view of all suspect activities
- Cross-platform activity aggregation
- Date-sorted events with context
- Filter by platform and activity type

### 6. **Secure Authentication**
- JWT token-based authentication (7-day expiry)
- Bcrypt password hashing
- Protected API endpoints
- Authorization header validation

### 7. **Background Processing**
- Non-blocking scraping operations
- Immediate API responses
- Parallel task execution
- Efficient resource utilization

---

## 🌐 Supported Platforms

```python
PLATFORM_SCRAPERS = {
    "instagram": Instagram Scraper,
    "facebook": Facebook Scraper,
    "x": Twitter/X Scraper,
    "whatsapp": WhatsApp Scraper (ready),
    "telegram": Telegram Scraper (ready)
}
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │
       │ HTTP/REST API
       ▼
┌─────────────────────────────────┐
│        FastAPI Server           │
│  ┌─────────────────────────┐   │
│  │  Authentication Layer   │   │
│  │    (JWT + bcrypt)       │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │   API Routers           │   │
│  │  • User Management      │   │
│  │  • Case Management      │   │
│  │  • Data Scraping        │   │
│  │  • Report Extraction    │   │
│  │  • Timeline Dashboard   │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │   Business Logic        │   │
│  │  • auth_utils           │   │
│  │  • data_utils           │   │
│  │  • dashboard_utils      │   │
│  │  • extract_utils        │   │
│  └─────────────────────────┘   │
│  ┌─────────────────────────┐   │
│  │  Background Workers     │   │
│  │  • Scraping Engine      │   │
│  │  • Report Generator     │   │
│  └─────────────────────────┘   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│      MongoDB Database           │
│  • user_agents                  │
│  • case_collections             │
│  • data                         │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Platform Scrapers             │
│  • Selenium WebDriver           │
│  • Instagram Module             │
│  • Facebook Module              │
│  • X (Twitter) Module           │
└─────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.0 or higher
- Chrome/Chromium browser (for Selenium)
- ChromeDriver

### Step 1: Clone the Repository

```bash
git clone https://github.com/rohan6891/ProjectAapi.git
cd ProjectAapi
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MongoDB

```bash
# Install MongoDB (Ubuntu example)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=forensic_db

# JWT Configuration
SECRET_KEY=your_super_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

### Step 6: Run the Application

```bash
python main.py
```

The API will be available at `http://127.0.0.1:8000`

---

## ⚙️ Configuration

### Database Configuration

Edit `database.py` to configure MongoDB connection:

```python
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "forensic_db")
```

### JWT Configuration

Edit `utils/jwt_handler.py`:

```python
SECRET_KEY = os.getenv("SECRET_KEY", "your_very_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
```

### Scraper Configuration

Update file paths in scraper modules to match your system:

```python
# app_scrapers/instagram/main.py
folder_path = os.path.join("ScraData", "instagram", folder_name)
```

---

## 📚 API Documentation

### Interactive API Docs

Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Authentication Endpoints

#### Register User
```http
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "officer_john",
  "password": "secure_password"
}
```

#### Login
```http
POST /api/v1/users/login
Content-Type: application/x-www-form-urlencoded

username=officer_john&password=secure_password
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Data Scraping Endpoints

#### Initiate Scraping
```http
POST /api/v1/data/scrape
Authorization: Bearer <token>
Content-Type: multipart/form-data

case: CASE001
title: Cybercrime Investigation
description: Investigation details
nia_officer: Officer Name
cio_officer: CIO Name
eo_officer: EO Name
eo_designation: Senior Officer
platform: instagram
username: suspect_username
password: suspect_password
suspect_name: John Doe
```

#### Get User Data Files
```http
GET /api/v1/data/datafiles
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "name": "John Doe",
    "source": "instagram",
    "status": "Completed",
    "case_id": "CASE001"
  }
]
```

### Report Extraction Endpoints

#### Get Available Case IDs
```http
GET /api/v1/extract/case_ids
```

#### Get Report Options
```http
GET /api/v1/extract/options?case=CASE001
```

### Timeline Dashboard Endpoints

#### Get Timeline Data
```http
GET /api/v1/case_dashboard/timelines
Authorization: Bearer <token>
case: CASE001
```

---

## 💡 Usage Examples

### Complete Workflow Example

```python
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Register/Login
login_data = {
    "username": "officer_john",
    "password": "secure_password"
}
response = requests.post(f"{BASE_URL}/users/login", data=login_data)
token = response.json()["token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Initiate Scraping
scrape_data = {
    "case": "CASE001",
    "title": "Digital Investigation",
    "description": "Social media evidence collection",
    "nia_officer": "Officer John",
    "cio_officer": "CIO Smith",
    "eo_officer": "EO Davis",
    "eo_designation": "Senior Officer",
    "platform": "instagram",
    "username": "suspect_account",
    "password": "suspect_password",
    "suspect_name": "Jane Doe"
}
response = requests.post(f"{BASE_URL}/data/scrape", headers=headers, data=scrape_data)
print(response.json())  # {"message": "Scraping started for instagram in the background."}

# 3. Check Status
response = requests.get(f"{BASE_URL}/data/datafiles", headers=headers)
print(response.json())

# 4. Get Timeline
timeline_headers = {**headers, "case": "CASE001"}
response = requests.get(f"{BASE_URL}/case_dashboard/timelines", headers=timeline_headers)
print(response.json())
```

---

## 📁 Project Structure

```
ProjectAapi/
│
├── main.py                          # FastAPI application entry point
│
├── routers/                         # API route handlers
│   ├── user.py                     # Authentication endpoints
│   ├── data.py                     # Scraping operations
│   ├── extract.py                  # Report extraction
│   └── case_dashboard.py           # Timeline visualization
│
├── models/                          # Pydantic data models
│   ├── user.py                     # User schemas
│   ├── case.py                     # Case schemas
│   └── data.py                     # Data schemas
│
├── utils/                           # Business logic utilities
│   ├── auth_utils.py               # Password hashing & user management
│   ├── jwt_handler.py              # JWT token operations
│   ├── data_utils.py               # Case & data operations
│   ├── dashboard_utils.py          # Timeline formatting
│   ├── extract_utils.py            # Report extraction logic
│   └── pdf_util.py                 # PDF generation utilities
│
├── app_scrapers/                    # Platform-specific scrapers
│   ├── instagram/
│   │   ├── main.py                 # Instagram scraper entry point
│   │   └── FuncScrape/             # Instagram scraping functions
│   ├── facebook/
│   │   ├── main.py                 # Facebook scraper entry point
│   │   └── FuncScrape/             # Facebook scraping functions
│   ├── x/
│   │   ├── main.py                 # Twitter/X scraper
│   │   └── FuncScrape/
│   ├── telegram/
│   └── whatsapp/
│
├── ScraData/                        # Scraped data storage
│   ├── instagram/
│   ├── facebook/
│   └── x/
│
├── database.py                      # MongoDB connection setup
├── config.py                        # Application configuration
├── requirements.txt                 # Python dependencies
└── .env                            # Environment variables (create this)
```

---

## 🔒 Security

### Security Features

1. **Password Security**
   - Bcrypt hashing with salt
   - No plaintext password storage

2. **Authentication**
   - JWT token-based authentication
   - 7-day token expiration
   - Bearer token authorization

3. **Data Protection**
   - Environment variables for sensitive data
   - HTTPS recommended for production
   - Input validation using Pydantic

### Security Best Practices

```python
# ✅ DO: Use environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# ❌ DON'T: Hardcode secrets
SECRET_KEY = "my_secret_key"  # Never do this!
```

### Production Recommendations

1. **Change default SECRET_KEY** in `.env`
2. **Use HTTPS** for all communications
3. **Configure CORS** to allow only trusted origins
4. **Enable rate limiting** to prevent abuse
5. **Regular security audits** of dependencies
6. **Use MongoDB authentication** in production

---

## 🧪 Testing

### Run Tests (Coming Soon)

```bash
pytest tests/
```

### Manual Testing

Use the interactive API documentation at `/docs` to test endpoints.

---

## 📦 Dependencies

```
fastapi          # Modern web framework
uvicorn          # ASGI server
motor            # Async MongoDB driver
pymongo          # MongoDB driver
python-dotenv    # Environment variable management
bcrypt           # Password hashing
pydantic         # Data validation
PyJWT            # JWT token handling
selenium         # Web automation
reportlab        # PDF generation
Pillow           # Image processing
```

---

## 🛠️ Technologies Used

- **Backend Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT + Bcrypt
- **Web Scraping**: Selenium WebDriver
- **PDF Generation**: ReportLab
- **Async Operations**: Python AsyncIO + Motor
- **Data Validation**: Pydantic
- **API Documentation**: OpenAPI (Swagger)

---

## 🚧 Roadmap

- [ ] Add WhatsApp scraper implementation
- [ ] Add Telegram scraper implementation
- [ ] Implement ML-based content analysis
- [ ] Add data export to CSV/Excel
- [ ] Implement real-time scraping status updates (WebSocket)
- [ ] Add multi-language support
- [ ] Create admin dashboard
- [ ] Add automated testing suite
- [ ] Implement data encryption at rest
- [ ] Add audit logging

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide
- Add docstrings to functions
- Update documentation for new features
- Write tests for new functionality

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Rohan** - *Initial work* - [@rohan6891](https://github.com/rohan6891)

---

## 🙏 Acknowledgments

- FastAPI framework for excellent async support
- MongoDB for flexible data storage
- Selenium project for web automation capabilities
- Law enforcement agencies for requirements and feedback

---

## 📞 Support

For support, email rohan6891@example.com or open an issue in the GitHub repository.

---

## ⚠️ Disclaimer

This tool is designed exclusively for legal digital forensic investigations by authorized law enforcement agencies. Unauthorized use of this software to access private social media accounts without proper legal authority is illegal and unethical. Users are responsible for ensuring compliance with all applicable laws and regulations.

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for law enforcement and digital forensics**