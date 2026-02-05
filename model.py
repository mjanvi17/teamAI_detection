import numpy as np
import librosa
import warnings
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

# --------------------------------- 
# Configuration
# --------------------------------- 

MODEL_PATH = "voice_classifier_model.pkl"
SCALER_PATH = "voice_scaler.pkl"

# --------------------------------- 
# Feature Extraction
# --------------------------------- 

def extract_features(path):
    """
    Extract audio features using librosa for AI vs Human classification.
    Features include MFCC, spectral characteristics, and prosodic features.
    
    Returns:
        np.array: Feature vector of shape (48,)
    """
    try:
        # Load audio at 16kHz
        y, sr = librosa.load(path, sr=16000, duration=10)
        
        # MFCC (Mel-frequency cepstral coefficients) - 20 coefficients
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        
        # Spectral features
        spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spec_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # Temporal features
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma)
        
        # Combine all features (48 total features)
        features = np.hstack([
            mfcc_mean,                           # 20 features
            mfcc_std,                            # 20 features
            np.mean(spec_centroid),              # 1 feature
            np.std(spec_centroid),               # 1 feature
            np.mean(spec_rolloff),               # 1 feature
            np.std(spec_rolloff),                # 1 feature
            np.mean(spec_bandwidth),             # 1 feature
            np.mean(zero_crossing_rate),         # 1 feature
            np.std(zero_crossing_rate),          # 1 feature
            chroma_mean                          # 1 feature
        ])
        # Total: 20 + 20 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 = 48 features
        
        return features
        
    except Exception as e:
        raise Exception(f"Feature extraction failed: {str(e)}")


# --------------------------------- 
# Model Training (for initial setup)
# --------------------------------- 

def train_model(X_train, y_train):
    """
    Train the Random Forest classifier.
    
    Args:
        X_train: Training features (n_samples, 48)
        y_train: Training labels (n_samples,) - 0 for HUMAN, 1 for AI_GENERATED
    
    Returns:
        tuple: (trained_model, scaler)
    """
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train Random Forest classifier
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Save model and scaler
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"Model trained and saved to {MODEL_PATH}")
    print(f"Scaler saved to {SCALER_PATH}")
    
    return model, scaler


def create_synthetic_training_data():
    """
    Create synthetic training data for initial model.
    In production, replace this with real labeled dataset.
    
    Returns:
        tuple: (X_train, y_train)
    """
    np.random.seed(42)
    
    # Simulate 100 samples (50 AI, 50 Human)
    n_samples = 100
    n_features = 48
    
    X_train = []
    y_train = []
    
    # Generate synthetic AI-generated voice features
    # AI voices tend to have: lower variance, more uniform patterns
    for i in range(n_samples // 2):
        # MFCC mean (more centered)
        mfcc_mean = np.random.normal(0, 10, 20)
        # MFCC std (lower variance)
        mfcc_std = np.random.uniform(0.5, 3, 20)
        # Spectral features (more uniform) - 7 features
        spec_features = np.random.uniform(500, 2000, 7)
        # Zero crossing rate features - 1 feature
        zcr_std = np.random.uniform(0.05, 0.15, 1)
        
        features = np.hstack([mfcc_mean, mfcc_std, spec_features, zcr_std])
        X_train.append(features)
        y_train.append(1)  # AI_GENERATED
    
    # Generate synthetic human voice features
    # Human voices have: higher variance, more natural irregularities
    for i in range(n_samples // 2):
        # MFCC mean (more varied)
        mfcc_mean = np.random.normal(0, 15, 20)
        # MFCC std (higher variance)
        mfcc_std = np.random.uniform(3, 8, 20)
        # Spectral features (more varied) - 7 features
        spec_features = np.random.uniform(300, 3000, 7)
        # Zero crossing rate features - 1 feature
        zcr_std = np.random.uniform(0.08, 0.25, 1)
        
        features = np.hstack([mfcc_mean, mfcc_std, spec_features, zcr_std])
        X_train.append(features)
        y_train.append(0)  # HUMAN
    
    return np.array(X_train), np.array(y_train)


def initialize_model():
    """
    Initialize the model with synthetic data if no trained model exists.
    In production, replace with real training data.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        print("No trained model found. Creating initial model with synthetic data...")
        print("WARNING: For production use, train with real labeled data!")
        X_train, y_train = create_synthetic_training_data()
        train_model(X_train, y_train)


# --------------------------------- 
# Model Loading and Prediction
# --------------------------------- 

def load_model():
    """
    Load the trained model and scaler.
    
    Returns:
        tuple: (model, scaler)
    """
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        
        return model, scaler
    
    except FileNotFoundError:
        raise Exception(
            "Model files not found. Please train the model first using train_model() "
            "or run initialize_model() to create an initial model."
        )


def predict_voice(path):
    """
    Classify audio as AI-generated or Human using trained ML model.
    
    Args:
        path: Path to audio file
    
    Returns:
        tuple: (label, confidence) where label is 'AI_GENERATED' or 'HUMAN'
               and confidence is between 0.0 and 1.0
    """
    try:
        # Initialize model if it doesn't exist
        initialize_model()
        
        # Load trained model and scaler
        model, scaler = load_model()
        
        # Extract features from audio
        features = extract_features(path)
        
        # Reshape for prediction
        features = features.reshape(1, -1)
        
        # Standardize features
        features_scaled = scaler.transform(features)
        
        # Get prediction and probability
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        # Get confidence score
        confidence = float(max(probabilities))
        
        # Map prediction to label
        if prediction == 1:
            label = "AI_GENERATED"
        else:
            label = "HUMAN"
        
        return label, confidence
        
    except Exception as e:
        raise Exception(f"Prediction failed: {str(e)}")


# --------------------------------- 
# Feature Importance (Explainability)
# --------------------------------- 

def get_feature_importance():
    """
    Get feature importance from the trained model for explainability.
    
    Returns:
        dict: Feature names and their importance scores
    """
    try:
        model, _ = load_model()
        
        feature_names = [
            *[f"mfcc_mean_{i}" for i in range(20)],
            *[f"mfcc_std_{i}" for i in range(20)],
            "spec_centroid_mean", "spec_centroid_std",
            "spec_rolloff_mean", "spec_rolloff_std",
            "spec_bandwidth_mean",
            "zcr_mean", "zcr_std",
            "chroma_mean"
        ]
        
        importances = model.feature_importances_
        
        feature_importance = dict(zip(feature_names, importances))
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return feature_importance
        
    except Exception as e:
        raise Exception(f"Could not get feature importance: {str(e)}")


# --------------------------------- 
# Model Evaluation Metrics
# --------------------------------- 

def evaluate_model(X_test, y_test):
    """
    Evaluate model performance on test data.
    
    Args:
        X_test: Test features
        y_test: Test labels
    
    Returns:
        dict: Evaluation metrics (accuracy, precision, recall, f1)
    """
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    try:
        model, scaler = load_model()
        
        X_test_scaled = scaler.transform(X_test)
        predictions = model.predict(X_test_scaled)
        
        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions),
            "recall": recall_score(y_test, predictions),
            "f1_score": f1_score(y_test, predictions)
        }
        
        return metrics
        
    except Exception as e:
        raise Exception(f"Model evaluation failed: {str(e)}")