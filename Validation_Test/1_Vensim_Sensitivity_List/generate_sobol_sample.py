"""
Script to read a CSV setup file and generate Sobol samples for sensitivity analysis.
Outputs a tab-delimited file with sampled parameter values and noise seeds.
"""

import csv
import os
import argparse
import numpy as np
from SALib.sample import sobol
import glob


def find_csv_files():
    """Find CSV files in the current directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = glob.glob(os.path.join(script_dir, '*.csv'))
    return sorted(csv_files)


def read_setup_csv(filepath):
    """Read and parse the Setup.csv file to extract input variables."""
    inputs = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows
            if not row.get('Type'):
                continue
            
            var_type = row['Type'].strip()
            variable = row.get('Variable', '').strip()
            distribution = row.get('Distribution', '').strip()
            min_val = row.get('Min', '').strip()
            max_val = row.get('Max', '').strip()
            increment = row.get('Increment', '').strip()
            
            # Skip rows with empty variable names
            if not variable:
                continue
            
            # Only process Input type variables
            if var_type == 'Input':
                try:
                    min_float = float(min_val)
                    max_float = float(max_val)
                    increment_float = float(increment) if increment else None
                    
                    inputs.append({
                        'name': variable,
                        'min': min_float,
                        'max': max_float,
                        'distribution': distribution,
                        'increment': increment_float
                    })
                except ValueError:
                    print(f"Warning: Could not convert min/max/increment to float for {variable}, skipping")
                    continue
    
    return inputs


def generate_sobol_samples(inputs, num_samples=1024, calc_second_order=False):
    """
    Generate Sobol samples for the input variables.
    For VECTOR distributions, samples are rounded to discrete values based on increment.
    
    Args:
        inputs: List of input variable dictionaries with 'name', 'min', 'max', 'distribution', 'increment'
        num_samples: Number of samples to generate (default: 1024)
        calc_second_order: Whether to calculate second-order indices (default: False)
    
    Returns:
        Numpy array of samples with shape (N, num_vars)
    """
    # Define the problem for SALib
    problem = {
        'num_vars': len(inputs),
        'names': [inp['name'] for inp in inputs],
        'bounds': [[inp['min'], inp['max']] for inp in inputs]
    }
    
    # Generate Sobol samples
    samples = sobol.sample(problem, num_samples, calc_second_order=calc_second_order)
    
    # Post-process VECTOR distributions to discrete values
    for i, inp in enumerate(inputs):
        if inp.get('distribution', '').upper() == 'VECTOR' and inp.get('increment') is not None:
            increment = inp['increment']
            min_val = inp['min']
            # Round to nearest discrete value: min + round((value - min) / increment) * increment
            samples[:, i] = min_val + np.round((samples[:, i] - min_val) / increment) * increment
            # Ensure values stay within bounds
            samples[:, i] = np.clip(samples[:, i], inp['min'], inp['max'])
    
    return samples


def write_sobol_output(samples, variable_names, output_path):
    """
    Write the Sobol samples to a tab-delimited file.
    
    Format:
    var1<tab>var2<tab>var3
    1.36<tab>12.2<tab>5.5
    1.5<tab>13.7<tab>6.1
    ...
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header line
        header = '\t'.join(variable_names) + '\n'
        f.write(header)
        
        # Write each sample
        for i, sample in enumerate(samples):
            # Format each value to a reasonable precision
            values = [f"{val:.6g}" for val in sample]
            line = '\t'.join(values) + '\n'
            f.write(line)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate Sobol samples from a CSV setup file for sensitivity analysis.'
    )
    parser.add_argument(
        'input_csv',
        nargs='?',
        default=None,
        help='Path to the input CSV file (default: Setup.csv)'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=1024,
        help='Number of Sobol samples to generate (default: 1024)'
    )
    parser.add_argument(
        '--second-order',
        action='store_true',
        help='Calculate second-order Sobol indices (increases sample size)'
    )
    parser.add_argument(
        '--numbers',
        default=None,
        help='Comma-separated list of file numbers to process (e.g., "1,2,3")'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all CSV files found'
    )
    
    args = parser.parse_args()
    
    # Find all CSV files
    csv_files = find_csv_files()
    
    if not csv_files:
        print("Error: No CSV files found in current directory!")
        return
    
    # Determine which files to process
    files_to_process = []
    
    if args.all:
        # Process all files
        files_to_process = csv_files
        print(f"Processing all {len(csv_files)} CSV files...")
    elif args.numbers:
        # Process selected file numbers
        try:
            numbers = [int(n.strip()) for n in args.numbers.split(',')]
            for num in numbers:
                if 1 <= num <= len(csv_files):
                    files_to_process.append(csv_files[num - 1])
                else:
                    print(f"Warning: Number {num} is out of range (1-{len(csv_files)}), skipping...")
            
            if not files_to_process:
                print("Error: No valid file numbers provided!")
                return
                
            print(f"Processing {len(files_to_process)} selected file(s)...")
        except ValueError:
            print("Error: Invalid number format. Please use comma-separated numbers like '1,2,3'")
            return
    elif args.input_csv is not None:
        # Single file specified directly
        input_file = args.input_csv
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found!")
            return
        files_to_process = [input_file]
    else:
        # Default to Setup.csv
        default_file = 'Setup.csv'
        if os.path.exists(default_file):
            files_to_process = [default_file]
        elif csv_files:
            print(f"Setup.csv not found. Using first file: {os.path.basename(csv_files[0])}")
            files_to_process = [csv_files[0]]
        else:
            print("Error: No CSV files found!")
            return
    
    # Process each file
    for idx, input_file in enumerate(files_to_process, 1):
        if len(files_to_process) > 1:
            print(f"\n{'='*60}")
            print(f"Processing file {idx}/{len(files_to_process)}: {os.path.basename(input_file)}")
            print(f"{'='*60}")
        
        # Get the base name without extension
        file_name = os.path.basename(input_file)
        base_name = os.path.splitext(file_name)[0]
        
        # Create output directory: 2_Vensim_Runs/{base_name}/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        output_dir = os.path.join(parent_dir, '2_Vensim_Runs', base_name)
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output file path in the new directory
        output_file = os.path.join(output_dir, f'{base_name}_sobol.txt')
        
        print(f"Reading {input_file}...")
        
        try:
            # Read and parse the setup file
            inputs = read_setup_csv(input_file)
            
            if not inputs:
                print("Error: No input variables found in the CSV file!")
                if len(files_to_process) > 1:
                    print("Continuing with next file...")
                    continue
                return
            
            print(f"Found {len(inputs)} input variables")
            print(f"Variables: {', '.join([inp['name'] for inp in inputs])}")
            
            # Generate Sobol samples
            print(f"\nGenerating {args.samples} Sobol samples...")
            if args.second_order:
                print("(Including second-order indices - this will generate more samples)")
            
            samples = generate_sobol_samples(inputs, args.samples, args.second_order)
            
            print(f"Generated {len(samples)} samples")
            
            # Write output file
            print(f"\nWriting {os.path.basename(output_file)}...")
            variable_names = [inp['name'] for inp in inputs]
            write_sobol_output(samples, variable_names, output_file)
            
            print("\nSobol samples generated successfully in:")
            print(f"  {output_dir}")
            print(f"\nFile created:")
            print(f"  - {os.path.basename(output_file)}")
            print(f"  Samples: {len(samples)}")
            print(f"  Variables: {len(variable_names)}")
        except Exception as e:
            print(f"\nError processing {os.path.basename(input_file)}: {str(e)}")
            if len(files_to_process) > 1:
                print("Continuing with next file...")
            else:
                raise
    
    if len(files_to_process) > 1:
        print(f"\n{'='*60}")
        print(f"All processing complete! Processed {len(files_to_process)} files.")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
