# Image Registration Pipeline

## Overview
This project provides a pipeline for registering brain(head) medical images (MRI and CT) to MNI152 space using fixed templates using ITK and elastix. The pipeline includes:

1. Registering MRI image and CT image to a standard templates.
2. Registering CT to MRI.

## What's special
- Automatic MRI and CT image registration with *larger* images (including neck).
- *Two-stage* non-deformable registration to ensure the best possible solution.

## Requirements
Install the required dependencies by running (feel free to use conda or anything else):
```bash
pip install -r requirements.txt
```

## Usage

### Input Data Structure
Organize the input directory as follows:
```
data/mri_ct/
    └── Subject1/
        ├── image_MR.nii.gz
        ├── image_CT.nii.gz
    └── Subject2/
        ├── ...
```


Run the script:
```bash
python register.py
```


## License
This project is open-source under the Apache-2.0 license 

