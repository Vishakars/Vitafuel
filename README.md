# VitaFuel - Health and Fitness Tracking Web Application

VitaFuel is a comprehensive health and fitness tracking web application that helps users monitor their nutrition, activities, and overall wellness. Built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend.

## 🚀 Features

### ✅ Implemented Features

#### 🔐 User Authentication
- **Secure Registration**: Username, email, and hashed password registration
- **Login System**: Email-based authentication with JWT tokens
- **Password Reset**: Forgot password functionality with email reset tokens
- **Session Management**: Secure JWT-based session handling

#### 👤 User Profile Management
- **Profile Creation**: Age, gender, weight, height, fitness goals
- **Avatar Uploads**: Per-account avatar uploads with file storage
- **Health Domains**: Selection and management of health tracking areas
- **Profile Updates**: Real-time profile information updates

#### 🍎 Nutrition Tracking
- **Food Diary**: Log meals with detailed nutritional information
- **Daily Intake Tracking**: Calories, proteins, carbohydrates, fats
- **Food Database**: Searchable food database with nutritional data
- **Water Tracking**: Daily water intake monitoring
- **Nutrition Goals**: Set and track daily nutritional targets
- **Meal Planning**: Organize meals by type (breakfast, lunch, dinner, snacks)

#### 🏃‍♂️ Activity & Fitness Tracking
- **Activity Logging**: Log various physical activities and workouts
- **Metrics Tracking**: Duration, distance, calories burned
- **Activity Types**: Running, walking, cycling, swimming, weight training, yoga, etc.
- **Intensity Levels**: Low, moderate, high intensity tracking
- **Fitness Goals**: Set and track fitness objectives
- **Workout Plans**: Create and manage custom workout routines

#### 📊 Dashboard & Analytics
- **Personal Dashboard**: Daily health metrics overview
- **Data Visualization**: Interactive charts and graphs
- **Progress Tracking**: Visual progress indicators
- **Health Trends**: Historical data analysis
- **Insights**: AI-powered health recommendations
- **Weekly/Monthly Reports**: Comprehensive activity summaries

#### 🎨 User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, intuitive interface with warm color scheme
- **Real-time Updates**: Live data synchronization
- **Notifications**: Success/error feedback system
- **Accessibility**: Keyboard navigation and screen reader support

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Passlib with bcrypt
- **File Storage**: Local file system for avatars
- **Server**: Uvicorn ASGI server

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styling with CSS variables
- **JavaScript**: Vanilla ES6+ with async/await
- **Charts**: Chart.js for data visualization
- **Icons**: Emoji-based iconography

### Development Tools
- **Package Management**: pip with requirements.txt
- **Code Quality**: Built-in linting and type hints
- **API Documentation**: Auto-generated FastAPI docs

## 📁 Project Structure

```
VitaFuel/
├── client/                 # Frontend files
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Main dashboard
│   ├── profile.html       # User profile management
│   ├── nutrition.html     # Nutrition tracking
│   ├── activity.html      # Activity tracking
│   ├── analytics.html     # Analytics and charts
│   ├── style.css          # Main stylesheet
│   └── logo/              # Application logos
├── server/                # Backend files
│   ├── main.py           # FastAPI application entry point
│   ├── config/           # Configuration files
│   │   ├── db.py
        ├── atlas_config.py # Database configuration
│   │   └── settings.py   # Application settings
│   ├── routes/           # API route handlers
│   │   ├── auth.py       # Authentication routes
│   │   ├── profile.py    # Profile management routes
│   │   ├── nutrition.py  # Nutrition tracking routes
│   │   ├── activity.py   # Activity tracking routes
│   │   └── health.py     # Health data routes
│   ├── models/           # Data models
│   └── utils/            # Utility functions
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

### Port Configuration
VitaFuel uses the following default ports:
- **Backend API**: Port 8005 (FastAPI server)
- **Frontend**: Port 3000 (HTTP server for client files)
- **MongoDB**: Port 27017 (default MongoDB port)

All API calls in the frontend are configured to use port 8005. Make sure no other services are using these ports.

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VitaFuel
   ```

2. **Set up the virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   .\venv\Scripts\activate.bat  # Windows Command Prompt
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ## Environment Setup
   Environment variables can be configured either via a `.env` file or directly in the configuration files under `server/config/`(depending on deployment environment).

5. **Start MongoDB**
   Make sure MongoDB is running on your system:
   ```bash
   mongod
   ```

### 🔗 Direct Access Links

Once the servers are running, you can access these pages directly:

- **🏠 Home Page**: http://127.0.0.1:3000/
- **🔐 Login Page**: http://127.0.0.1:3000/login.html
- **📝 Registration**: http://127.0.0.1:3000/register.html
- **📊 Dashboard**: http://127.0.0.1:3000/dashboard.html
- **🩸 Anemia Tracker**: http://127.0.0.1:3000/anemia.html
- **🦋 Thyroid Tracker**: http://127.0.0.1:3000/thyroid.html
- **🍎 Nutrition Tracker**: http://127.0.0.1:3000/nutrition.html
- **🏃‍♂️ Activity Tracker**: http://127.0.0.1:3000/activity.html
- **📈 Analytics**: http://127.0.0.1:3000/analytics.html
- **👤 Profile**: http://127.0.0.1:3000/profile.html

### Manual Server Startup

If you prefer to start servers manually:

1. **Start the backend server**
   ```bash
   cd server
   python -m uvicorn main:app --host 127.0.0.1 --port 8005 --reload
   ```

2. **Start the frontend server** (in a new terminal)
   ```bash
   cd client
   python -m http.server 3000
   ```

3. **Access the application**
   Open your browser and go to: http://127.0.0.1:3000

## 📖 API Documentation

Once the server is running, you can access the interactive API documentation at:
- **Swagger UI**: http://127.0.0.1:8005/docs
- **ReDoc**: http://127.0.0.1:8005/redoc
- **Backend API Base URL**: http://127.0.0.1:8005

### Key API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation
- `GET /auth/me` - Get current user info

#### Profile Management
- `GET /api/profile/me` - Get user profile
- `POST /api/profile/` - Create/update profile
- `PATCH /api/profile/{email}/avatar` - Upload avatar
- `PATCH /api/profile/{email}/domains` - Update health domains

#### Nutrition Tracking
- `GET /api/nutrition/{email}/nutrition/{date}` - Get daily nutrition
- `POST /api/nutrition/{email}/nutrition/{date}/meal` - Log meal
- `PATCH /api/nutrition/{email}/nutrition/{date}/water` - Log water intake
- `GET /api/nutrition/food-database` - Search food database

#### Activity Tracking
- `GET /api/activity/activity-types` - Get activity types
- `POST /api/activity/{email}/activities` - Log activity
- `GET /api/activity/{email}/activities/summary` - Get activity summary
- `GET /api/activity/{email}/stats/weekly` - Get weekly stats

## 🎯 Usage Guide

### 1. Getting Started
1. **Register**: Create a new account with email and password
2. **Login**: Access your personalized dashboard
3. **Complete Profile**: Add your basic information and health goals
4. **Select Health Domains**: Choose areas you want to track

### 2. Daily Tracking
1. **Log Meals**: Add breakfast, lunch, dinner, and snacks
2. **Track Water**: Monitor daily water intake
3. **Log Activities**: Record workouts and physical activities
4. **Update Metrics**: Track weight, mood, and other health indicators

### 3. Analytics & Insights
1. **View Dashboard**: See daily progress and key metrics
2. **Check Analytics**: Review trends and patterns
3. **Set Goals**: Create and track fitness objectives
4. **Get Insights**: Receive personalized recommendations

## 🔧 Configuration

### Database Configuration
The application uses MongoDB for data storage. Configure the connection in `server/config/db.py`:

```python
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "vitafuel"
```

### Security Settings
Configure JWT settings in `server/config/settings.py`:

```python
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## 🧪 Testing

### Manual Testing
1. **Authentication Flow**: Test registration, login, and password reset
2. **Profile Management**: Test profile creation and avatar upload
3. **Nutrition Tracking**: Test meal logging and water tracking
4. **Activity Tracking**: Test activity logging and goal setting
5. **Analytics**: Test chart rendering and data visualization
6. **Health Trackers**: Test anemia and thyroid tracking functionality

### API Testing
Use the interactive API documentation at `/docs` to test endpoints directly.

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
If you get "port already in use" errors:
```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Or kill specific processes by port
netstat -ano | findstr :3000
taskkill /F /PID <PID_NUMBER>
```

#### 404 File Not Found Errors
If you get 404 errors when accessing HTML files:
- Make sure the frontend server is running from the `client` directory
- Use the provided startup scripts: `.\start_servers.bat` or `.\start_servers.ps1`

#### Backend Server Won't Start
If the backend server fails to start:
- Make sure you're in the `server` directory
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure MongoDB is running on port 27017

#### VS Code Live Server Conflicts
If VS Code Live Server is interfering:
- Disable the Live Server extension temporarily
- Use the provided startup scripts instead
- Make sure no other servers are running on ports 3000 or 8005

### Port Configuration Issues
- **Frontend**: Must run on port 3000 from the `client` directory
- **Backend**: Must run on port 8005 from the `server` directory
- **MongoDB**: Must run on port 27017

### Virtual Environment Issues
If you have virtual environment path issues:
```bash
# Create a new virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Set production environment variables
2. **Database**: Use MongoDB Atlas or production MongoDB instance
3. **Static Files**: Configure proper static file serving
4. **Security**: Enable HTTPS and secure headers
5. **Monitoring**: Set up logging and error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the code comments and inline documentation
- Create an issue in the repository

## 🔮 Future Enhancements

- **Mobile App**: React Native or Flutter mobile application
- **Social Features**: Friend connections and challenges
- **Wearable Integration**: Fitbit, Apple Health, Google Fit
- **AI Recommendations**: Machine learning-powered insights
- **Barcode Scanning**: Food item recognition
- **Meal Planning**: Weekly meal planning and shopping lists
- **Health Reports**: PDF export of health data
- **Multi-language Support**: Internationalization

---

**VitaFuel** - Empowering Healthy Lives Through Technology 🏃‍♂️💪🍎

## Team Members
- Misha T Shekhar
- Shravana N
- Varsha A Hajare
- Vishaka R S 

