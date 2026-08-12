"""
Convert abc.csv (Vensim output format) to EMA Workbench format
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
import re


def convert_vensim_to_ema(input_csv, output_dir):
    """
    Convert Vensim output CSV to EMA workbench format.
    
    The input CSV has the structure:
    - First column: Variable names
    - Remaining columns: Simulation runs (1, 2, 3, ...)
    - Rows without time prefix (T0, T1, etc.): Uncertainty variables
    - Rows with "T# Variable Name": Time series outcomes at timestep T#
    
    Parameters:
    -----------
    input_csv : str
        Path to the input CSV file (abc.csv format)
    output_dir : str
        Directory to save the output files
        
    Returns:
    --------
    experiments_df : DataFrame
        The experiments dataframe with uncertainties
    outcomes_dict : dict
        Dictionary of outcome DataFrames (one per outcome variable)
    metadata : dict
        The metadata dictionary
    """
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Identify uncertainty variables and time series rows
    # Pattern: "T<number> <variable_name>" indicates time series at that timestep
    uncertainty_vars = []
    timeseries_data = {}  # {outcome_name: {timestep: row_idx}}
    
    for idx, row in df.iterrows():
        var_name = row.iloc[0]  # First column is variable name
        
        # Check if variable name is a time series marker (T followed by digit and space)
        match = re.match(r'T(\d+)\s+(.+)', var_name)
        if match:
            timestep = int(match.group(1))
            outcome_name = match.group(2)
            
            if outcome_name not in timeseries_data:
                timeseries_data[outcome_name] = {}
            timeseries_data[outcome_name][timestep] = idx
        else:
            uncertainty_vars.append(var_name)
    
    # Extract uncertainty data (rows before time series)
    uncertainty_data = df.iloc[:len(uncertainty_vars), 1:].T  # Transpose to get runs as rows
    uncertainty_data.columns = uncertainty_vars
    
    # Get number of simulations
    n_sims = len(uncertainty_data)
    
    # Create experiments.csv with scenario, policy, model columns
    experiments_df = uncertainty_data.copy()
    experiments_df['scenario'] = range(n_sims)
    experiments_df['policy'] = None
    experiments_df['model'] = 'FelixVensim'
    
    # Reorder columns to match EMA format
    cols = list(uncertainty_vars) + ['scenario', 'policy', 'model']
    experiments_df = experiments_df[cols]
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save experiments.csv
    experiments_df.to_csv(output_path / 'experiments.csv', index=False)
    print(f"Saved experiments.csv with {n_sims} runs and {len(uncertainty_vars)} uncertainties")
    print(f"Uncertainty variables: {uncertainty_vars}")
    
    # Process each outcome variable
    outcomes_dict = {}
    outcome_metadata = []
    
    for outcome_name, timestep_dict in timeseries_data.items():
        # Sort timesteps
        sorted_timesteps = sorted(timestep_dict.keys())
        
        # Extract data for each timestep and build outcome dataframe
        # Each row = one scenario, each column = one timestep
        outcome_data = []
        for timestep in sorted_timesteps:
            row_idx = timestep_dict[timestep]
            # Get values for this timestep across all simulations
            values = df.iloc[row_idx, 1:].values
            outcome_data.append(values)
        
        # Transpose so rows = scenarios, columns = timesteps
        outcome_df = pd.DataFrame(outcome_data).T
        outcome_df.columns = sorted_timesteps  # Use timestep numbers directly (0, 1, 2, ...)
        
        # Create outcome name for dictionary key (replace brackets with underscores)
        outcome_key = outcome_name.replace('[', '_').replace(']', '')
        outcome_filename = f"{outcome_key}.csv"
        
        # Save outcome CSV with timesteps as headers
        outcome_df.to_csv(output_path / outcome_filename, index=False, header=True)
        print(f"Saved {outcome_filename} with {n_sims} scenarios and {len(sorted_timesteps)} time steps")
        
        # Store in dictionary using the cleaned name
        outcomes_dict[outcome_key] = outcome_df
        
        # Add to metadata using the cleaned name
        outcome_metadata.append([
            "TimeSeriesOutcome", 
            outcome_key, 
            outcome_filename
        ])
    
    # Create metadata.json
    metadata = {
        "version": 0.1,
        "outcomes": outcome_metadata,
        "experiments": {
            **{var: "float64" for var in uncertainty_vars},
            "scenario": "category",
            "policy": "category",
            "model": "category"
        }
    }
    
    with open(output_path / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata.json with {len(outcome_metadata)} outcomes")
    
    print(f"\nConversion complete! Files saved to: {output_path}")
    print(f"Total outcomes: {len(outcomes_dict)}")
    return experiments_df, outcomes_dict, metadata


def load_vensim_ema_results(results_dir):
    """
    Load EMA Workbench format results from a directory.
    
    Reads experiments.csv and all outcome CSV files from the specified directory.
    
    Parameters:
    -----------
    results_dir : str
        Directory containing the EMA format files
        
    Returns:
    --------
    experiments_df : DataFrame
        The experiments dataframe with uncertainties
    outcomes_dict : dict
        Dictionary of outcome DataFrames (one per outcome variable)
    """
    results_path = Path(results_dir)
    
    # Load experiments
    experiments_df = pd.read_csv(results_path / 'experiments.csv')
    print(f"Loaded experiments: {experiments_df.shape}")
    
    # Load metadata to get outcome file names
    with open(results_path / 'metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Load all outcome CSV files based on metadata
    outcomes_dict = {}
    for outcome_info in metadata['outcomes']:
        outcome_type, outcome_name, outcome_file = outcome_info
        outcome_df = pd.read_csv(results_path / outcome_file)
        outcomes_dict[outcome_name] = outcome_df
        print(f"Loaded outcome '{outcome_name}': {outcome_df.shape}")
    
    print(f"\nTotal outcomes loaded: {len(outcomes_dict)}")
    return experiments_df, outcomes_dict


if __name__ == "__main__":
    # Convert the abc.csv file
    input_file = r"c:\Users\tanryan\Desktop\WBF_Paper\FeliX_Vensim_Run\abc.csv"
    output_directory = r"c:\Users\tanryan\Desktop\WBF_Paper\3_Analysis\converted_results"
    
    experiments, outcomes_dict, metadata = convert_vensim_to_ema(
        input_file, 
        output_directory
    )
    
    print(f"\nExperiments shape: {experiments.shape}")
    print(f"Number of outcomes: {len(outcomes_dict)}")
    for outcome_name, outcome_df in outcomes_dict.items():
        print(f"  {outcome_name}: {outcome_df.shape}")
    print(f"\nFirst few rows of experiments:")
    print(experiments.head())
