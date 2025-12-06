"""
Improved training script with transfer learning and MLflow tracking.
Tracks BOTH skin type AND skin problems as required.
"""
import os
import yaml
import json
import mlflow
import mlflow.tensorflow
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load parameters
with open('api/params.yaml', 'r') as f:
    params = yaml.safe_load(f)

# Configuration
IMG_SIZE = params.get('img_size', 224)
BATCH_SIZE = params.get('batch_size', 32)
EPOCHS = params.get('epochs', 50)
LEARNING_RATE = params.get('learning_rate', 0.001)

# Data paths
DATA_DIR = Path('api/data')
SKIN_TYPES = ['Dry', 'Normal', 'Oily']
SKIN_PROBLEMS = ['Acne', 'Dark_Spots', 'Wrinkles']

def load_data():
    """Load and preprocess data."""
    logger.info("Loading data...")
    
    # Load images and labels
    X_type, y_type = [], []
    X_prob, y_prob = [], []
    
    # Load skin type data
    for skin_type in SKIN_TYPES:
        type_dir = DATA_DIR / skin_type
        if type_dir.exists():
            for img_path in type_dir.glob('*.jpg'):
                try:
                    img = tf.keras.preprocessing.image.load_img(
                        img_path, target_size=(IMG_SIZE, IMG_SIZE)
                    )
                    img_array = tf.keras.preprocessing.image.img_to_array(img)
                    X_type.append(img_array)
                    y_type.append(SKIN_TYPES.index(skin_type))
                except Exception as e:
                    logger.warning(f"Error loading {img_path}: {e}")
    
    # Load skin problems data
    for problem in SKIN_PROBLEMS:
        prob_dir = DATA_DIR / problem
        if prob_dir.exists():
            for img_path in prob_dir.glob('*.jpg'):
                try:
                    img = tf.keras.preprocessing.image.load_img(
                        img_path, target_size=(IMG_SIZE, IMG_SIZE)
                    )
                    img_array = tf.keras.preprocessing.image.img_to_array(img)
                    X_prob.append(img_array)
                    # Multi-label: one-hot encode
                    label = [0] * len(SKIN_PROBLEMS)
                    label[SKIN_PROBLEMS.index(problem)] = 1
                    y_prob.append(label)
                except Exception as e:
                    logger.warning(f"Error loading {img_path}: {e}")
    
    # Convert to numpy arrays
    X_type = np.array(X_type) / 255.0
    y_type = tf.keras.utils.to_categorical(y_type, len(SKIN_TYPES))
    X_prob = np.array(X_prob) / 255.0
    y_prob = np.array(y_prob)
    
    logger.info(f"Loaded {len(X_type)} skin type images, {len(X_prob)} skin problem images")
    
    return X_type, y_type, X_prob, y_prob

def create_model_with_transfer_learning():
    """
    Create multi-task model with transfer learning.
    Uses ImageNet pre-trained MobileNetV2.
    """
    logger.info("Creating model with transfer learning...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        include_top=False,
        weights='imagenet',  # Use ImageNet weights
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        pooling='avg'
    )
    
    # Freeze early layers for initial training
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    # Input
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    
    # Shared backbone
    x = base_model(inputs, training=False)
    x = layers.Dropout(0.3)(x)
    
    # Task 1: Skin Type Classification (multi-class)
    skin_type_branch = layers.Dense(128, activation='relu', name='type_dense')(x)
    skin_type_branch = layers.Dropout(0.2)(skin_type_branch)
    skin_type_output = layers.Dense(
        len(SKIN_TYPES), 
        activation='softmax', 
        name='skin_type'
    )(skin_type_branch)
    
    # Task 2: Skin Problems Classification (multi-label)
    skin_prob_branch = layers.Dense(128, activation='relu', name='prob_dense')(x)
    skin_prob_branch = layers.Dropout(0.2)(skin_prob_branch)
    skin_prob_output = layers.Dense(
        len(SKIN_PROBLEMS), 
        activation='sigmoid',  # Sigmoid for multi-label
        name='skin_problems'
    )(skin_prob_branch)
    
    # Create model
    model = Model(
        inputs=inputs,
        outputs=[skin_type_output, skin_prob_output],
        name='multitask_skin_model'
    )
    
    return model, base_model

def train_model():
    """Train model with MLflow tracking."""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5001")
    mlflow.set_experiment("skin-analysis-transfer-learning")
    
    with mlflow.start_run(run_name="transfer_learning_v1"):
        # Log parameters
        mlflow.log_params({
            'img_size': IMG_SIZE,
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE,
            'transfer_learning': True,
            'backbone': 'MobileNetV2',
            'pretrained_weights': 'ImageNet'
        })
        
        # Load data
        X_type, y_type, X_prob, y_prob = load_data()
        
        # Split data
        X_type_train, X_type_val, y_type_train, y_type_val = train_test_split(
            X_type, y_type, test_size=0.2, random_state=42
        )
        X_prob_train, X_prob_val, y_prob_train, y_prob_val = train_test_split(
            X_prob, y_prob, test_size=0.2, random_state=42
        )
        
        # Create model
        model, base_model = create_model_with_transfer_learning()
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE),
            loss={
                'skin_type': 'categorical_crossentropy',
                'skin_problems': 'binary_crossentropy'
            },
            metrics={
                'skin_type': ['accuracy'],
                'skin_problems': ['accuracy', 'AUC']
            }
        )
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
        ]
        
        # Enable MLflow autologging
        mlflow.tensorflow.autolog()
        
        # Phase 1: Train with frozen backbone
        logger.info("Phase 1: Training with frozen backbone...")
        history1 = model.fit(
            X_type_train,
            {'skin_type': y_type_train, 'skin_problems': y_prob_train},
            validation_data=(
                X_type_val,
                {'skin_type': y_type_val, 'skin_problems': y_prob_val}
            ),
            epochs=EPOCHS // 2,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        
        # Phase 2: Fine-tune entire model
        logger.info("Phase 2: Fine-tuning entire model...")
        for layer in base_model.layers:
            layer.trainable = True
        
        model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE / 10),  # Lower LR for fine-tuning
            loss={
                'skin_type': 'categorical_crossentropy',
                'skin_problems': 'binary_crossentropy'
            },
            metrics={
                'skin_type': ['accuracy'],
                'skin_problems': ['accuracy', 'AUC']
            }
        )
        
        history2 = model.fit(
            X_type_train,
            {'skin_type': y_type_train, 'skin_problems': y_prob_train},
            validation_data=(
                X_type_val,
                {'skin_type': y_type_val, 'skin_problems': y_prob_val}
            ),
            epochs=EPOCHS // 2,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        results = model.evaluate(
            X_type_val,
            {'skin_type': y_type_val, 'skin_problems': y_prob_val},
            verbose=0
        )
        
        # Log final metrics
        mlflow.log_metrics({
            'final_skin_type_accuracy': results[3],
            'final_skin_problems_accuracy': results[4],
            'final_skin_problems_auc': results[5]
        })
        
        # Save model
        model_path = 'api/multitask_skin_model.h5'
        model.save(model_path)
        mlflow.log_artifact(model_path)
        
        # Save metrics
        metrics = {
            'skin_type_accuracy': float(results[3]),
            'skin_problems_accuracy': float(results[4]),
            'skin_problems_auc': float(results[5])
        }
        
        with open('api/metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        mlflow.log_artifact('api/metrics.json')
        
        logger.info(f"Training complete! Metrics: {metrics}")
        logger.info(f"Model saved to {model_path}")
        
        return model

if __name__ == '__main__':
    train_model()
