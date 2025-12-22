# Data Folder Description

Due to file upload limitations, the model checkpoints, repair results, and training datasets are not directly included in this repository. 

## Download Links

All related files, including:

- **Model Checkpoints**: Fine-tuned `BugCerberus` model weights.
- **Bug Repair Results**: Generated repair patches from the BugCerberus.
- **Training Data**: Sample code contexts used for training.

These files can be downloaded from the following link:

🔗 [Download Data and Checkpoints](https://www.alipan.com/s/wNRpNfF25mm)  

## Generating Additional Data

Users can generate additional training data using the scripts provided in the `Static Analysis` folder. These scripts support extracting code contexts at **file-level**, **function-level**, and **statement-level**, which can be used to create custom training datasets for bug localization and repair tasks.

For more details about the project and training process, please refer to the top-level [README.md](../README.md) file.

