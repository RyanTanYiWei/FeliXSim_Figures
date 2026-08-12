"""
Script to convert Vensim CSV output to EMA-compatible format.
Reads a Vensim sensitivity analysis CSV file and converts it to the format
expected by EMA Workbench for analysis.
"""

import os
import argparse
import importlib
import vensim_output_to_ema
import glob


def find_vensim_csv_files():
    """Find CSV files in the Vensim_Exported_Results directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    vensim_results_dir = os.path.join(parent_dir, '3_Conversion_to_EMA', 'Vensim_Exported_Results')
    
    if not os.path.exists(vensim_results_dir):
        return []
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(vensim_results_dir, '*.csv'))
    return csv_files


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Convert Vensim CSV output to EMA-compatible format.'
    )
    parser.add_argument(
        'vensim_csv',
        nargs='?',
        default=None,
        help='Path to the Vensim CSV file (optional - will auto-detect if not provided)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory name (default: {basename}_EMA)'
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
    vensim_csv_file = args.vensim_csv
    
    # Find all CSV files
    csv_files = find_vensim_csv_files()
    
    if not csv_files:
        print("Error: No CSV files found in Vensim_Exported_Results directory!")
        return
    
    # Sort files for consistent numbering
    csv_files.sort()
    
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
    elif vensim_csv_file is None:
        # Auto-detect - use first file by default
        print("Searching for Vensim CSV files in 3_Conversion_to_EMA/Vensim_Exported_Results...")
        
        if len(csv_files) == 1:
            files_to_process = [csv_files[0]]
            print(f"Found: {os.path.basename(csv_files[0])}")
        else:
            print(f"\nFound {len(csv_files)} CSV files:")
            for i, f in enumerate(csv_files, 1):
                print(f"  {i}. {os.path.basename(f)}")
            print("\nUsing first file by default.")
            files_to_process = [csv_files[0]]
    else:
        # Single file specified directly
        if not os.path.exists(vensim_csv_file):
            print(f"Error: {vensim_csv_file} not found!")
            return
        files_to_process = [vensim_csv_file]
    
    # Process each file
    for idx, vensim_csv_file in enumerate(files_to_process, 1):
        if len(files_to_process) > 1:
            print(f"\n{'='*60}")
            print(f"Processing file {idx}/{len(files_to_process)}: {os.path.basename(vensim_csv_file)}")
            print(f"{'='*60}")
        
        # Get the base name without extension
        file_name = os.path.basename(vensim_csv_file)
        base_name = os.path.splitext(file_name)[0]
        
        # Determine output directory
        if args.output_dir:
            output_directory = args.output_dir
        else:
            # Create output directory in 4_Exploratory_Analysis folder
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            analysis_dir = os.path.join(parent_dir, '4_Exploratory_Analysis')
            output_directory = os.path.join(analysis_dir, f'{base_name}_EMA')
        
        print(f"Reading {vensim_csv_file}...")
        print(f"Output directory: {output_directory}")
        
        # Reload the module to get latest changes
        importlib.reload(vensim_output_to_ema)
        from vensim_output_to_ema import convert_vensim_to_ema
        
        # Convert and save results
        print("\nConverting Vensim output to EMA format...")
        try:
            experiments_df, outcomes_dict, metadata = convert_vensim_to_ema(
                vensim_csv_file, 
                output_directory
            )
            
            print(f"\n{'='*60}")
            print(f"Conversion complete for {os.path.basename(vensim_csv_file)}!")
            print(f"{'='*60}")
            print(f"Experiments shape: {experiments_df.shape}")
            print(f"Number of outcomes: {len(outcomes_dict)}")
            print(f"Outcome names: {list(outcomes_dict.keys())[:5]}...")  # Show first 5
            print(f"\nResults saved to directory:")
            print(f"  {output_directory}")
            print(f"\nDirectory contains:")
            print(f"  - experiments.csv")
            print(f"  - {len(outcomes_dict)} outcome CSV files")
            print(f"  - metadata.json")
        except Exception as e:
            print(f"\nError processing {os.path.basename(vensim_csv_file)}: {str(e)}")
            if len(files_to_process) > 1:
                print("Continuing with next file...")
            else:
                raise
    
    if len(files_to_process) > 1:
        print(f"\n{'='*60}")
        print(f"All conversions complete! Processed {len(files_to_process)} files.")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
