import os
import json
import re

def parse_pessession_file(filepath):
    """
    Parses a PSSESSION file and extracts potential and current data for all scans.
    """
    all_scans = []  # Will hold all scan data
    print(f"Parsing file: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-16') as file:
            content = file.read()
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # Find the first complete JSON object
            start_idx = content.find('{')
            if start_idx == -1:
                print("No JSON content found")
                return []
            
            # Find matching closing brace
            brace_count = 1
            end_idx = start_idx + 1
            
            while brace_count > 0 and end_idx < len(content):
                if content[end_idx] == '{':
                    brace_count += 1
                elif content[end_idx] == '}':
                    brace_count -= 1
                end_idx += 1
            
            if brace_count > 0:
                print("Incomplete JSON content")
                return []
            
            # Extract and parse JSON content
            json_content = content[start_idx:end_idx]
            data = json.loads(json_content)
            
            if 'Measurements' in data and len(data['Measurements']) > 0:
                # Process each measurement
                for measurement_idx, measurement in enumerate(data['Measurements']):
                    print(f"\nProcessing measurement {measurement_idx + 1}")
                    
                    # Look for curves in the measurement
                    if 'Curves' in measurement:
                        # Process each curve in the measurement
                        for curve_idx, curve in enumerate(measurement['Curves']):
                            print(f"Processing curve {curve_idx + 1}")
                            potential = []
                            current = []
                            
                            # Extract potential values
                            if 'XAxisDataArray' in curve and 'DataValues' in curve['XAxisDataArray']:
                                potential = [point['V'] for point in curve['XAxisDataArray']['DataValues']]
                                print(f"Found {len(potential)} potential points")
                            
                            # Extract current values
                            if 'YAxisDataArray' in curve and 'DataValues' in curve['YAxisDataArray']:
                                current = [point['V'] for point in curve['YAxisDataArray']['DataValues']]
                                print(f"Found {len(current)} current points")
                            
                            if len(potential) > 0 and len(current) > 0:
                                if len(potential) != len(current):
                                    print("WARNING: Mismatch between potential and current data points!")
                                else:
                                    all_scans.append({
                                        'scan_number': curve_idx + 1,
                                        'potential': potential,
                                        'current': current
                                    })
                    else:
                        print("No Curves found in measurement")
            else:
                print("No Measurements found in file")
            
            print(f"Total scans found: {len(all_scans)}")
            return all_scans
            
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
        return []

def convert_pessession_to_text(folder_path):
    """
    Scans the specified folder for PSSESSION files and converts them to .txt
    """
    print(f"\nScanning folder: {folder_path}")
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return

    # Create output folder for all text files
    output_folder = os.path.join(folder_path, "Converted_Data")
    os.makedirs(output_folder, exist_ok=True)
    print(f"Saving all converted files to: {output_folder}")

    # Get list of .pssession files (case-insensitive)
    pessession_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pssession")]
    
    if not pessession_files:
        print("No .pssession files found in the specified folder")
        return
    
    print(f"Found {len(pessession_files)} .pssession files")

    # Process each file
    for filename in pessession_files:
        print(f"\nProcessing: {filename}")
        filepath = os.path.join(folder_path, filename)

        try:
            # Extract potential and current data for all scans
            all_scans = parse_pessession_file(filepath)

            if not all_scans:
                print(f"Skipping {filename} - no data extracted")
                continue

            # Create output file with same name but .txt extension
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_filepath = os.path.join(output_folder, output_filename)

            # Write all scans to the file side by side
            with open(output_filepath, 'w') as output_file:
                # Write headers for all scans
                header_line = ""
                for scan_num in range(len(all_scans)):
                    header_line += f"Scan {scan_num + 1}\t\t\t\t"
                output_file.write(header_line + "\n")

                # Write column headers for all scans
                header_line = ""
                for _ in range(len(all_scans)):
                    header_line += "Potential(V)\tCurrent(A)\t\t"
                output_file.write(header_line + "\n")

                # Find the maximum number of data points across all scans
                max_points = max(len(scan['potential']) for scan in all_scans)

                # Write data points side by side
                for i in range(max_points):
                    line = ""
                    for scan in all_scans:
                        if i < len(scan['potential']):
                            line += f"{scan['potential'][i]}\t{scan['current'][i]}\t\t"
                        else:
                            line += "\t\t\t"  # Empty space for missing data points
                    output_file.write(line + "\n")

            print(f"Created: {output_filename} with {len(all_scans)} scans")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

# Specify the folder containing PSSESSION files
folder_path = r"YOUR_PATH_HERE"
print("Starting PSSESSION file conversion...")
convert_pessession_to_text(folder_path)
print("Conversion complete!")
