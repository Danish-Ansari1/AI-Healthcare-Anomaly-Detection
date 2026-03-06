import pandas as pd
import numpy as np
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
# Neural Network for Autoencoder
class PatientAutoencoder(nn.Module):
    def __init__(self, input_dim=5):
        super(PatientAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.Tanh(),
            nn.Linear(8, 4),
            nn.Tanh()
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.Tanh(),
            nn.Linear(8, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def generate_training_data(n_samples=5000):
    """Generate synthetic normal patient vitals for initial training."""
    np.random.seed(42)
    # Target Normal ranges
    # HR: 60-100, SpO2: 95-100, Temp: 36.1-37.2, Sys: 90-120, Dia: 60-80
    data = {
        'heart_rate': np.random.normal(80, 10, n_samples),
        'spo2': np.random.normal(97.5, 1.5, n_samples),
        'temperature': np.random.normal(36.6, 0.3, n_samples),
        'blood_pressure_systolic': np.random.normal(110, 8, n_samples),
        'blood_pressure_diastolic': np.random.normal(70, 5, n_samples)
    }
    
    # Clip to realistic normal bounds
    df = pd.DataFrame(data)
    df['spo2'] = df['spo2'].clip(95, 100)
    return df

def train_models():
    print("Generating synthetic training data...")
    df = generate_training_data()
    feature_cols = ['heart_rate', 'spo2', 'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic']
    X = df[feature_cols].values

    # Fit Scaler
    print("Fitting StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest
    print("Training Isolation Forest...")
    iso_forest = IsolationForest(contamination=0.01, random_state=42)
    iso_forest.fit(X_scaled)

    # Train Autoencoder
    print("Training Autoencoder...")
    autoencoder = PatientAutoencoder(input_dim=5)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(autoencoder.parameters(), lr=0.01)

    X_tensor = torch.FloatTensor(X_scaled)
    epochs = 50
    batch_size = 64

    for epoch in range(epochs):
        permutation = torch.randperm(X_tensor.size()[0])
        total_loss = 0
        for i in range(0, X_tensor.size()[0], batch_size):
            indices = permutation[i:i+batch_size]
            batch_x = X_tensor[indices]
            
            optimizer.zero_grad()
            outputs = autoencoder(batch_x)
            loss = criterion(outputs, batch_x)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        if (epoch+1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(X_tensor):.4f}")

    # Create artifacts directory if needed
    os.makedirs('models', exist_ok=True)

    # Save Models
    print("Saving models to standard files...")
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    with open('models/isolation_forest.pkl', 'wb') as f:
        pickle.dump(iso_forest, f)

    torch.save(autoencoder.state_dict(), 'models/autoencoder.pth')
    print("Models saved successfully in 'models/' directory.")

if __name__ == "__main__":
    train_models()
