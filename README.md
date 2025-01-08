# Image Registration Pipeline

## Overview
This project provides a pipeline for registering medical images (MRI and CT) to fixed templates using ITK and elastix. The pipeline includes:

1. Registering MRI image and CT image to a standard templates.
2. Registering CT to MRI.

## Features
- Automatic MRI and CT image registration.
- Overlay functionality to create larger, standardized images.
- Two-stage elastix non-deformable registration.

## Requirements
Install the required dependencies by running:
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
This project is open-source under the Apashe 2.0 License.

