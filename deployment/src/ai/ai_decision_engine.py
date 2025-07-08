"""
AI Decision Engine for Forex Trading Bot
Implements machine learning models and ensemble methods for trading decisions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

class AIDecisionEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.feature_columns = []
        self.min_confidence_threshold = self.config.get('MIN_CONFIDENCE', 70)
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize machine learning models"""
        # Random Forest for pattern recognition
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Logistic Regression for linear relationships
        self.models['logistic'] = LogisticRegression(
            random_state=42,
            max_iter=1000
        )
        
        # SVM for non-linear patterns
        self.models['svm'] = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        
        # Ensemble model combining all approaches
        self.models['ensemble'] = VotingClassifier(
            estimators=[
                ('rf', self.models['random_forest']),
                ('lr', self.models['logistic']),
                ('svm', self.models['svm'])
            ],
            voting='soft'
        )
        
        # Initialize scalers for each model
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
    
    def prepare_features(self, df):
        """Prepare features for machine learning models"""
        if df.empty or len(df) < 50:
            return None
        
        features = pd.DataFrame()
        
        # Technical indicators
        features['rsi'] = df.get('RSI', 50)
        features['ema_short'] = df.get('EMA_Short', df['close'])
        features['ema_long'] = df.get('EMA_Long', df['close'])
        features['atr'] = df.get('ATR', 0)
        features['macd'] = df.get('MACD', 0)
        features['macd_signal'] = df.get('MACD_Signal', 0)
        features['bb_upper'] = df.get('BB_Upper', df['close'])
        features['bb_lower'] = df.get('BB_Lower', df['close'])
        features['bb_middle'] = df.get('BB_Middle', df['close'])
        
        # Price-based features
        features['price_change'] = df['close'].pct_change()
        features['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        features['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        features['volume_ratio'] = df.get('volume', 1) / df.get('volume', 1).rolling(20).mean()
        
        # Trend features
        features['ema_trend'] = (features['ema_short'] - features['ema_long']) / features['ema_long']
        features['price_vs_ema'] = (df['close'] - features['ema_short']) / features['ema_short']
        features['bb_position'] = (df['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # Momentum features
        features['rsi_momentum'] = features['rsi'].diff()
        features['price_momentum'] = df['close'].diff()
        features['volume_momentum'] = features['volume_ratio'].diff()
        
        # Volatility features
        features['atr_ratio'] = features['atr'] / df['close']
        features['price_volatility'] = df['close'].rolling(20).std() / df['close'].rolling(20).mean()
        
        # Market structure features
        features['golden_cross'] = df.get('Golden_Cross', pd.Series([False] * len(df))).astype(int)
        features['death_cross'] = df.get('Death_Cross', pd.Series([False] * len(df))).astype(int)
        features['bos_bullish'] = df.get('BOS_Bullish', pd.Series([False] * len(df))).astype(int)
        features['bos_bearish'] = df.get('BOS_Bearish', pd.Series([False] * len(df))).astype(int)
        features['bullish_ob'] = df.get('Bullish_OB', pd.Series([False] * len(df))).astype(int)
        features['bearish_ob'] = df.get('Bearish_OB', pd.Series([False] * len(df))).astype(int)
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def create_labels(self, df, lookahead_periods=5, profit_threshold=0.001):
        """Create labels for supervised learning"""
        if df.empty or len(df) < lookahead_periods + 1:
            return None
        
        labels = []
        
        for i in range(len(df) - lookahead_periods):
            current_price = df.iloc[i]['close']
            future_prices = df.iloc[i+1:i+1+lookahead_periods]['close']
            
            max_future_price = future_prices.max()
            min_future_price = future_prices.min()
            
            # Calculate potential profit/loss
            buy_profit = (max_future_price - current_price) / current_price
            sell_profit = (current_price - min_future_price) / current_price
            
            # Determine label based on best opportunity
            if buy_profit > profit_threshold and buy_profit > sell_profit:
                labels.append(1)  # BUY
            elif sell_profit > profit_threshold and sell_profit > buy_profit:
                labels.append(-1)  # SELL
            else:
                labels.append(0)  # HOLD
        
        # Pad with zeros for the last periods
        labels.extend([0] * lookahead_periods)
        
        return np.array(labels)
    
    def train_models(self, historical_data, retrain=False):
        """Train machine learning models on historical data"""
        if not retrain and self.is_trained:
            return True
        
        print("Training AI models...")
        
        # Prepare features and labels
        features = self.prepare_features(historical_data)
        if features is None:
            print("Insufficient data for training")
            return False
        
        labels = self.create_labels(historical_data)
        if labels is None:
            print("Could not create labels for training")
            return False
        
        # Ensure features and labels have same length
        min_length = min(len(features), len(labels))
        features = features.iloc[:min_length]
        labels = labels[:min_length]
        
        # Store feature columns for later use
        self.feature_columns = features.columns.tolist()
        
        # Split data for training and validation
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train each model
        for model_name, model in self.models.items():
            print(f"Training {model_name}...")
            
            # Scale features
            X_train_scaled = self.scalers[model_name].fit_transform(X_train)
            X_test_scaled = self.scalers[model_name].transform(X_test)
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"{model_name} accuracy: {accuracy:.3f}")
        
        self.is_trained = True
        print("AI models training completed!")
        return True
    
    def predict_signal(self, current_data, symbol, timeframe):
        """Generate AI-enhanced trading signal"""
        if not self.is_trained:
            print("Models not trained yet")
            return None
        
        # Prepare features
        features = self.prepare_features(current_data)
        if features is None:
            return None
        
        # Get the latest features
        latest_features = features.iloc[-1:][self.feature_columns]
        
        # Get predictions from all models
        predictions = {}
        probabilities = {}
        
        for model_name, model in self.models.items():
            # Scale features
            features_scaled = self.scalers[model_name].transform(latest_features)
            
            # Get prediction and probability
            prediction = model.predict(features_scaled)[0]
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features_scaled)[0]
                probabilities[model_name] = proba
            else:
                probabilities[model_name] = [0.33, 0.34, 0.33]  # Default uniform
            
            predictions[model_name] = prediction
        
        # Calculate ensemble confidence
        ensemble_proba = probabilities['ensemble']
        
        # Determine signal based on ensemble prediction
        ensemble_prediction = predictions['ensemble']
        
        # Calculate confidence score
        if ensemble_prediction == 1:  # BUY
            confidence = ensemble_proba[2] * 100  # Probability of BUY class
            signal_type = "BUY"
        elif ensemble_prediction == -1:  # SELL
            confidence = ensemble_proba[0] * 100  # Probability of SELL class
            signal_type = "SELL"
        else:  # HOLD
            confidence = ensemble_proba[1] * 100  # Probability of HOLD class
            signal_type = "HOLD"
        
        # Create AI signal
        ai_signal = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': pd.Timestamp.now(),
            'signal_type': signal_type,
            'confidence': round(confidence, 2),
            'model_predictions': predictions,
            'model_probabilities': {k: v.tolist() for k, v in probabilities.items()},
            'feature_importance': self._get_feature_importance(),
            'meets_threshold': confidence >= self.min_confidence_threshold
        }
        
        return ai_signal
    
    def _get_feature_importance(self):
        """Get feature importance from Random Forest model"""
        if 'random_forest' not in self.models or not self.is_trained:
            return {}
        
        rf_model = self.models['random_forest']
        importance_dict = dict(zip(
            self.feature_columns,
            rf_model.feature_importances_
        ))
        
        # Sort by importance
        sorted_importance = dict(sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return sorted_importance
    
    def enhance_signal(self, traditional_signal, ai_signal):
        """Enhance traditional signal with AI insights"""
        if not ai_signal or not traditional_signal:
            return traditional_signal
        
        enhanced_signal = traditional_signal.copy()
        
        # Combine confidence scores
        traditional_confidence = traditional_signal.get('confidence_score', 0)
        ai_confidence = ai_signal.get('confidence', 0)
        
        # Weighted average (70% traditional, 30% AI for safety)
        combined_confidence = (traditional_confidence * 0.7) + (ai_confidence * 0.3)
        
        # Check signal agreement
        traditional_type = traditional_signal.get('signal_type', 'NONE')
        ai_type = ai_signal.get('signal_type', 'HOLD')
        
        # Only proceed if signals agree or AI is neutral
        if traditional_type != 'NONE' and ai_type in [traditional_type, 'HOLD']:
            enhanced_signal['confidence_score'] = round(combined_confidence, 2)
            enhanced_signal['ai_enhancement'] = {
                'ai_signal_type': ai_type,
                'ai_confidence': ai_confidence,
                'model_agreement': ai_type == traditional_type,
                'feature_importance': ai_signal.get('feature_importance', {}),
                'model_predictions': ai_signal.get('model_predictions', {})
            }
            
            # Boost confidence if AI agrees
            if ai_type == traditional_type:
                enhanced_signal['confidence_score'] = min(100, combined_confidence * 1.2)
        
        elif traditional_type != 'NONE' and ai_type not in [traditional_type, 'HOLD']:
            # AI disagrees - reduce confidence significantly
            enhanced_signal['confidence_score'] = traditional_confidence * 0.5
            enhanced_signal['ai_enhancement'] = {
                'ai_signal_type': ai_type,
                'ai_confidence': ai_confidence,
                'model_agreement': False,
                'warning': 'AI model disagrees with traditional signal'
            }
        
        return enhanced_signal
    
    def save_models(self, filepath_prefix='ai_models'):
        """Save trained models to disk"""
        if not self.is_trained:
            print("No trained models to save")
            return False
        
        try:
            # Save models
            for model_name, model in self.models.items():
                joblib.dump(model, f"{filepath_prefix}_{model_name}.pkl")
            
            # Save scalers
            for scaler_name, scaler in self.scalers.items():
                joblib.dump(scaler, f"{filepath_prefix}_scaler_{scaler_name}.pkl")
            
            # Save metadata
            metadata = {
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained,
                'min_confidence_threshold': self.min_confidence_threshold
            }
            joblib.dump(metadata, f"{filepath_prefix}_metadata.pkl")
            
            print("Models saved successfully")
            return True
        
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def load_models(self, filepath_prefix='ai_models'):
        """Load trained models from disk"""
        try:
            # Load metadata
            metadata = joblib.load(f"{filepath_prefix}_metadata.pkl")
            self.feature_columns = metadata['feature_columns']
            self.is_trained = metadata['is_trained']
            self.min_confidence_threshold = metadata['min_confidence_threshold']
            
            # Load models
            for model_name in self.models.keys():
                self.models[model_name] = joblib.load(f"{filepath_prefix}_{model_name}.pkl")
            
            # Load scalers
            for scaler_name in self.scalers.keys():
                self.scalers[scaler_name] = joblib.load(f"{filepath_prefix}_scaler_{scaler_name}.pkl")
            
            print("Models loaded successfully")
            return True
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def get_model_performance(self):
        """Get performance metrics of trained models"""
        if not self.is_trained:
            return None
        
        performance = {
            'is_trained': self.is_trained,
            'feature_count': len(self.feature_columns),
            'feature_columns': self.feature_columns,
            'min_confidence_threshold': self.min_confidence_threshold,
            'models': list(self.models.keys())
        }
        
        return performance

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='H')
    
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 102,
        'low': np.random.randn(1000).cumsum() + 98,
        'close': np.random.randn(1000).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 1000)
    })
    
    # Add some technical indicators (simplified)
    sample_data['RSI'] = np.random.uniform(20, 80, 1000)
    sample_data['EMA_Short'] = sample_data['close'].rolling(20).mean()
    sample_data['EMA_Long'] = sample_data['close'].rolling(50).mean()
    sample_data['ATR'] = np.random.uniform(0.5, 2.0, 1000)
    sample_data['MACD'] = np.random.randn(1000)
    sample_data['MACD_Signal'] = sample_data['MACD'].rolling(9).mean()
    sample_data['BB_Upper'] = sample_data['close'] + 2 * sample_data['close'].rolling(20).std()
    sample_data['BB_Lower'] = sample_data['close'] - 2 * sample_data['close'].rolling(20).std()
    sample_data['BB_Middle'] = sample_data['close'].rolling(20).mean()
    sample_data['Golden_Cross'] = sample_data['EMA_Short'] > sample_data['EMA_Long']
    sample_data['Death_Cross'] = sample_data['EMA_Short'] < sample_data['EMA_Long']
    sample_data['BOS_Bullish'] = np.random.choice([True, False], 1000, p=[0.1, 0.9])
    sample_data['BOS_Bearish'] = np.random.choice([True, False], 1000, p=[0.1, 0.9])
    sample_data['Bullish_OB'] = np.random.choice([True, False], 1000, p=[0.1, 0.9])
    sample_data['Bearish_OB'] = np.random.choice([True, False], 1000, p=[0.1, 0.9])
    
    # Test AI Decision Engine
    ai_engine = AIDecisionEngine()
    
    # Train models
    success = ai_engine.train_models(sample_data)
    if success:
        print("Training successful!")
        
        # Test prediction
        ai_signal = ai_engine.predict_signal(sample_data, "EURUSD", "1H")
        print("AI Signal:", ai_signal)
        
        # Test model performance
        performance = ai_engine.get_model_performance()
        print("Model Performance:", performance)
    else:
        print("Training failed!")

