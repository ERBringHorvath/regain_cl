def simplify_gene_names(gene_name):
    gene_name = gene_name.replace("'", "p")  # Replace single quote with p
    gene_name = gene_name.replace('"', "pp")  # Replace double quote with p
    gene_name = gene_name.replace(".", "_")  # Replace dot with underscore
    gene_name = gene_name.replace("(", "")  # Remove left parenthesis
    gene_name = gene_name.replace(")", "")  # Remove right parenthesis
    gene_name = gene_name.replace("-", "_")  # Replace hyphen with underscore
    gene_name = gene_name.replace("/", "_") # Replace forward slash with underscore
    return gene_name

def run(args):
    import os
    import glob
    import pandas as pd
    import csv

    path = args.directory
    
    output_directory = os.path.join(path, 'ReGAIN_Dataset')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Modify file paths to use output_directory
    args.search_output = os.path.join(output_directory, os.path.basename(args.search_output))
    args.output = os.path.join(output_directory, os.path.basename(args.output))
    args.search_strings_output = os.path.join(output_directory, os.path.basename(args.search_strings_output))

    # Step 1: Combine CSV files
    filename = os.path.basename(args.search_output).split('.')[0]

    os.chdir(path)

    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

    valid_dfs = []

    for f in all_filenames:
        try:
            df = pd.read_csv(f, sep='\t', na_filter=False)
            if not df.empty and list(df.columns) != []:
                valid_dfs.append(df)
            else:
                print(f"Skipping file {f} because it is empty or has no header row.")
        except Exception as e:
            print(f"Skipping file {f} due to an error while reading: {str(e)}")

    if valid_dfs:  # check if the list is not empty
        combined_csv = pd.concat(valid_dfs)
    else:
        raise ValueError("No valid CSV files found to concatenate")

    gene_type = args.gene_type.lower()

    if gene_type == 'resistance':
        combined_csv = combined_csv[(combined_csv['Element subtype'] == 'AMR') | (combined_csv['Element subtype'] == 'METAL') | (combined_csv['Element subtype'] == 'BIOCIDE') | (combined_csv['Element subtype'] == 'POINT')]
    elif gene_type == 'virulence':
        combined_csv = combined_csv[combined_csv['Element type'] == 'VIRULENCE']

    # drop duplicates from the column named 'Gene symbol'
    combined_csv = combined_csv.drop_duplicates(subset=['Gene symbol'])

    output_file_path = os.path.join(output_directory, filename + '.csv')
    combined_csv.to_csv(output_file_path, sep='\t', index=False, encoding='utf-8-sig')

    print("Step complete: combined CSV file has been created and placed in " + output_file_path)

    # Prepare input for Step 2
    df = pd.read_csv(output_file_path, sep='\t')
    search_strings_df = df[['Gene symbol', 'Class']].copy()
    search_strings_df.columns = ['Gene', 'GeneClass']
    search_strings_df['GeneClass'] = search_strings_df['GeneClass'].fillna('virulence')
    search_strings_df['GeneClass'] = search_strings_df['GeneClass'].astype(str).str.title()  # convert to proper format
   
    # define the path for the metadata file
    #search_strings_file = os.path.join(output_directory, 'search_strings.csv')
    search_strings_file = os.path.join(output_directory, args.search_strings_output)

    # save the search strings dataframe to a csv file
    search_strings_df.to_csv(search_strings_file, index=False, header=True)

    if args.simplify_gene_names:
        ###Copy search strings file
        metadata_df = search_strings_df.copy() 
        metadata_df.columns = ['Gene', 'GeneClass']
        metadata_df['Gene'] = metadata_df['Gene'].apply(simplify_gene_names)

        metadata_file = os.path.join(output_directory, 'metadata.csv')
        metadata_df.to_csv(metadata_file, index = False, header = True)

    # Step 2: Search for strings and filter columns by sum
    csv_dir = path
    search_output_path = args.search_output

    with open(search_strings_file, 'r') as ref_file:
        reader = csv.reader(ref_file)
        search_strings = [row[0] for row in reader]

    csv_files = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith('.csv')]

    with open(search_output_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        headers = ['file']
        headers.extend(search_strings)
        writer.writerow(headers)

        for f in csv_files:
            row = [os.path.basename(f)]
            with open(f, 'r') as csv_file:
                counts = [0] * len(search_strings)
                for line in csv_file:
                    for i, search_str in enumerate(search_strings):
                        if search_str in line:
                            counts[i] = 1
                row.extend(counts)
            writer.writerow(row)

    input_file = search_output_path
    required_min = args.min
    required_max = args.max

    df = pd.read_csv(input_file)

    sums_df = pd.DataFrame(columns=['variable', 'sum'])
    sums_df['variable'] = df.columns[1:]

    for col in df.columns[1:]:
        sums_df.loc[sums_df['variable'] == col, 'sum'] = df[col].sum()

    filter_output_path = args.output

    cols_to_keep = list(sums_df[(sums_df['sum'] >= required_min) & (sums_df['sum'] <= required_max)]['variable'])
    cols_to_keep.insert(0, 'file')
    df_filtered = df[cols_to_keep]

    if args.simplify_gene_names:
        df_filtered.columns = [simplify_gene_names(col) if col != 'file' 
    else col for col in df_filtered.columns]

    df_filtered.to_csv(filter_output_path, index=False)