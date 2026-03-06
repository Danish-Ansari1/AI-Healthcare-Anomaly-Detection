# AI Healthcare Anomaly Detection 🏥🚑

This project is a real-time health monitoring system that uses Machine Learning to detect anomalies in patient data.

## 🚀 Features
- **Real-time Detection:** Monitors vitals and detects irregularities instantly.
- **Advanced ML Models:** Uses Autoencoders and Isolation Forest.
- **Interactive Dashboard:** Visual interface for monitoring patients.

## 🛠️ Tech Stack
- **Language:** Python
- **ML Libraries:** Scikit-learn, PyTorch
- **Backend:** Flask
- **Data Pipeline:** Kafka

## 📁 Project Structure
- `app.py`: Main Flask application.
- `models/`: Pre-trained AI models.
- `templates/`: Frontend HTML files.

## ⚙️ How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run app: `python app.py`
3.Set up Virtual Environment:
  # Create environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Linux/Mac)
source venv/bin/activate

4.Install Dependencies:
pip install -r requirements.txt

5.Run the App:
python app.py

6.🐳 Docker Support
If you have Docker installed, you can run the entire stack with a single command:
docker-compose up --build