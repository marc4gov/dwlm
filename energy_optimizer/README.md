# Energy Optimizer for Pump Profiles

Optimize pump schedules based on energy prices using reinforcement learning.

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Generate synthetic training data:
```bash
python generate_synthetic_data.py
```

3. Train the model:
```bash
python train_model.py
```

4. Optimize new profiles:
```bash
python optimize_profile.py
```

## Directory Structure
```
energy_optimizer/
├── README.md
├── requirements.txt
├── energy_policy.py      # Model architecture
├── train_model.py        # Training script
├── generate_synthetic_data.py  # Data generation
├── optimize_profile.py   # Profile optimization
└── pump_profiles/        # Data directory
    ├── katwijk_profile.csv
    └── prices_profile.csv
```

## Features
- Dynamic price-based optimization
- 30% maximum increase in cheap hours
- 10% maximum decrease in expensive hours
- 3-hour balance compensation window
- Synthetic data generation for training