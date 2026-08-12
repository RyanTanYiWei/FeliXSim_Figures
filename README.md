# FeliXSim Figures and Validation Materials

This repository contains the code, source data, and supporting materials used to produce the figures for the FeliXSim paper, together with the validation workflow used to check the model outputs.

The repository is organized around three main purposes:

- generating the survey figure from the preliminary questionnaire data
- composing publication figures from screenshot panels
- documenting the validation workflow and exploratory analysis pipeline

## Repository Contents

- [SurveyFigures.py](SurveyFigures.py): builds the preliminary survey figure from [Raw_Sources/PreliminarySurvey.csv](Raw_Sources/PreliminarySurvey.csv)
- [CompositeFigures.py](CompositeFigures.py): composes screenshot panels into the final composite figures saved in [Final_Figures/](Final_Figures/)
- [Raw_Sources/](Raw_Sources/): source assets used to generate figures, including the survey data and screenshot folders
- [Final_Figures/](Final_Figures/): exported figures ready for manuscript use
- [Validation_Test/](Validation_Test/): model validation workflow, Vensim setup, conversion scripts, and exploratory analysis notebook

## Figure Generation

### Preliminary survey figure

Run [SurveyFigures.py](SurveyFigures.py) to generate the survey summary figure from the questionnaire responses stored in [Raw_Sources/PreliminarySurvey.csv](Raw_Sources/PreliminarySurvey.csv). The script produces [Final_Figures/f09.png](Final_Figures/f09.png).

### Composite figures

Run [CompositeFigures.py](CompositeFigures.py) to assemble the screenshot panels stored in [Raw_Sources/Figure5_InterfaceDesign/](Raw_Sources/Figure5_InterfaceDesign/) into publication-ready composite figures. The script writes the final image files to [Final_Figures/](Final_Figures/), including [Final_Figures/f05.png](Final_Figures/f05.png).

## Validation Workflow

The [Validation_Test/](Validation_Test/) folder contains the end-to-end validation and exploratory analysis pipeline:

1. [1_Vensim_Sensitivity_List/](Validation_Test/1_Vensim_Sensitivity_List/) generates Vensim setup files and optional Sobol sampling inputs.
2. [2_Vensim_Runs/](Validation_Test/2_Vensim_Runs/) stores the Vensim model, run configurations, and exported run outputs.
3. [3_Conversion_to_EMA/](Validation_Test/3_Conversion_to_EMA/) converts Vensim output to Exploratory Modeling and Analysis compatible files.
4. [4_Exploratory_Analysis/](Validation_Test/4_Exploratory_Analysis/) contains the exploratory analysis notebook and the converted data used for validation.

The exploratory notebook is [Validation_Test/4_Exploratory_Analysis/ExploratoryAnalysis.ipynb](Validation_Test/4_Exploratory_Analysis/ExploratoryAnalysis.ipynb).

## Requirements

The workflow assumes the following software is available:

- Python 3.11
- Anaconda or Miniconda
- Vensim DSS for running the model sensitivity analyses

Python dependencies for the validation workflow are listed in [Validation_Test/environment.yml](Validation_Test/environment.yml).

## Setup

Create the conda environment from the validation folder:

```bash
conda env create -f Validation_Test/environment.yml
```

If you use the batch files under [Validation_Test/](Validation_Test/), update [Validation_Test/config.bat](Validation_Test/config.bat) so that it points to your local Python executable. The bundled configuration is intended for the original development machine and may not match your setup.

## Reproducing the Figures

1. Activate the conda environment created from [Validation_Test/environment.yml](Validation_Test/environment.yml).
2. Run [SurveyFigures.py](SurveyFigures.py) to regenerate the survey figure.
3. Run [CompositeFigures.py](CompositeFigures.py) to rebuild the composite manuscript figures.
4. Use the scripts and notebook under [Validation_Test/](Validation_Test/) to repeat the validation analysis if needed.