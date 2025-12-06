# Kaggle Integration Guide

## Setup Kaggle API

### 1. Get Kaggle API Credentials
1. Go to https://www.kaggle.com/account
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json`

### 2. Configure Kaggle API
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Install Kaggle API
```bash
pip install kaggle
```

## Download Datasets

### Skin Type Dataset
```bash
kaggle datasets download -d mahmoudima/skin-types-dataset
unzip skin-types-dataset.zip -d api/MLflow/data/skin_types/
```

### Skin Problems Dataset
```bash
kaggle datasets download -d your-dataset-name
unzip your-dataset-name.zip -d api/MLflow/data/skin_problems/
```

## Train on Kaggle Notebooks

### Option 1: Upload Notebook
1. Go to https://www.kaggle.com/code
2. Click "New Notebook"
3. Upload `api/MLflow/skin-condition-model.ipynb`
4. Enable GPU: Settings → Accelerator → GPU T4 x2
5. Run notebook

### Option 2: Use Kaggle API
```bash
# Create a kernel metadata file
cat > kernel-metadata.json << EOF
{
  "id": "your-username/skin-analysis",
  "title": "Skin Analysis Training",
  "code_file": "api/MLflow/skin-condition-model.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": true,
  "dataset_sources": ["mahmoudima/skin-types-dataset"],
  "competition_sources": [],
  "kernel_sources": []
}
EOF

# Push to Kaggle
kaggle kernels push -p .
```

## Transfer Learning Improvements

### Update Training Script (`api/train.py`)

```python
# Load pre-trained MobileNetV2 with ImageNet weights
base_model = MobileNetV2(
    include_top=False,
    weights='imagenet',  # Use ImageNet pre-trained weights
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Freeze early layers
for layer in base_model.layers[:-20]:
    layer.trainable = False

# Fine-tuning strategy
# Phase 1: Train only heads
model.compile(...)
model.fit(train_data, epochs=10)

# Phase 2: Unfreeze and fine-tune
for layer in base_model.layers:
    layer.trainable = True

model.compile(optimizer=Adam(lr=1e-5), ...)
model.fit(train_data, epochs=20)
```

### Data Augmentation
```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    brightness_range=[0.8, 1.2]
)
```

## MLflow Tracking for Both Tasks

### Current Implementation
The model already tracks BOTH skin type AND skin problems:

```python
# In api/train.py
mlflow.tensorflow.autolog()

# Model has two outputs
out_type = layers.Dense(num_skin_types, activation='softmax', name='skin_type')(x)
out_prob = layers.Dense(num_skin_problems, activation='sigmoid', name='skin_problems')(x)

model = Model(inputs, outputs=[out_type, out_prob])
```

### View in MLflow
```bash
# Start MLflow UI
docker-compose up mlflow

# Or standalone
mlflow ui --port 5001

# Open browser
http://localhost:5001
```

You'll see:
- **Metrics**: Loss for both tasks, accuracy for both tasks
- **Parameters**: Learning rate, batch size, epochs
- **Artifacts**: Saved model, training plots

## Integration with DVC

### Track Kaggle Datasets
```bash
# Add dataset to DVC
dvc add api/MLflow/data/

# Commit to Git
git add api/MLflow/data.dvc .gitignore
git commit -m "Add Kaggle datasets with DVC"

# Push to remote storage
dvc push
```

## Automated Kaggle Training

### GitHub Actions Workflow
```yaml
name: Train on Kaggle

on:
  workflow_dispatch:

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Kaggle
        env:
          KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
          KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}
        run: |
          mkdir -p ~/.kaggle
          echo '{"username":"'$KAGGLE_USERNAME'","key":"'$KAGGLE_KEY'"}' > ~/.kaggle/kaggle.json
          chmod 600 ~/.kaggle/kaggle.json
      
      - name: Push to Kaggle
        run: kaggle kernels push -p .
```

## Best Practices

1. **Version Control**: Use DVC for datasets
2. **Experiment Tracking**: Log all experiments to MLflow
3. **Model Registry**: Register best models in MLflow
4. **Reproducibility**: Pin all package versions
5. **Documentation**: Document dataset sources and preprocessing steps
