"""
Script to read a CSV setup file and generate three output files:
- {basename}_constant.csv: Constants from the setup
- {basename}_input.vsc: Input variables with RANDOM_UNIFORM distributions
- {basename}_output.lst: Output variables list
"""

import csv
import os
import argparse
import glob


def find_csv_files():
    """Find CSV files in the current directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = glob.glob(os.path.join(script_dir, '*.csv'))
    return sorted(csv_files)


def read_setup_csv(filepath):
    """Read and parse the Setup.csv file."""
    constants = []
    inputs = []
    outputs = []
    
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
            
            if var_type == 'Constant':
                constants.append({
                    'variable': variable,
                    'distribution': distribution,
                    'min': min_val,
                    'max': max_val,
                    'increment': increment
                })
            elif var_type == 'Input':
                inputs.append({
                    'variable': variable,
                    'distribution': distribution,
                    'min': min_val,
                    'max': max_val,
                    'increment': increment
                })
            elif var_type == 'Output':
                outputs.append({
                    'variable': variable
                })
    
    return constants, inputs, outputs


def write_constant_csv(constants, output_path):
    """Write the constant variables to CSV format."""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        for const in constants:
            variable = const['variable']
            min_val = const['min']
            # Write the variable name and its min value
            f.write(f"{variable},{min_val}\n")


def write_input_vsc(inputs, output_path, num_experiments=10):
    """Write the input variables to VSC format with specified distributions."""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header line with number of experiments
        f.write(f"{num_experiments},L,1234,,1 \n")
        
        # Write each input variable with its distribution
        for inp in inputs:
            variable = inp['variable']
            distribution = inp.get('distribution', 'UNIFORM')
            min_val = inp['min']
            max_val = inp['max']
            increment = inp.get('increment', '')
            
            # Format based on distribution type
            if distribution.upper() == 'VECTOR' and increment:
                # VECTOR format: variable=VECTOR(min,max,increment)
                f.write(f"{variable}=VECTOR({min_val},{max_val},{increment}) \n")
            else:
                # Default to RANDOM_UNIFORM
                f.write(f"{variable}=RANDOM_UNIFORM({min_val},{max_val}) \n")


def write_output_lst(outputs, output_path):
    """Write the output variables to LST format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for output in outputs:
            variable = output['variable']
            f.write(f"{variable} \n")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate Vensim sensitivity analysis files from a CSV setup file.'
    )
    parser.add_argument(
        'input_csv',
        nargs='?',
        default=None,
        help='Path to the input CSV file (default: Setup.csv)'
    )
    parser.add_argument(
        '--experiments',
        type=int,
        default=10,
        help='Number of experiments to run (default: 10)'
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
        
        # Generate output file paths in the new directory
        constant_file = os.path.join(output_dir, f'{base_name}_constant.csv')
        input_file_out = os.path.join(output_dir, f'{base_name}_input.vsc')
        output_file = os.path.join(output_dir, f'{base_name}_output.lst')
        
        print(f"Reading {input_file}...")
        
        try:
            # Read and parse the setup file
            constants, inputs, outputs = read_setup_csv(input_file)
            
            print(f"Found {len(constants)} constants, {len(inputs)} inputs, and {len(outputs)} outputs")
            print(f"Output directory: {output_dir}")
            
            # Generate output files
            print(f"\nWriting {os.path.basename(constant_file)}...")
            write_constant_csv(constants, constant_file)
            
            print(f"Writing {os.path.basename(input_file_out)}...")
            write_input_vsc(inputs, input_file_out, args.experiments)
            
            print(f"Writing {os.path.basename(output_file)}...")
            write_output_lst(outputs, output_file)
            
            print("\nAll files generated successfully in:")
            print(f"  {output_dir}")
            print(f"\nFiles created:")
            print(f"  - {os.path.basename(constant_file)}")
            print(f"  - {os.path.basename(input_file_out)}")
            print(f"  - {os.path.basename(output_file)}")
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
