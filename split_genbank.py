import os
import argparse
from tqdm import tqdm
from Bio import SeqIO 

print("\033[35m" + "\nThis can take several minutes if working with a large multi-genbank file \n" + "\033[0m")

###Define main code
def split_genbank_file(input_file, output_dir):
    records = list(SeqIO.parse(input_file, "genbank"))
    filename_counter = {}
    
    for i, record in tqdm (enumerate(records), total=len(records), desc="Splitting Genbank file"):
        version = record.annotations['accessions'][0] if 'accessions' in record.annotations and record.annotations['accessions'] else f"record_{i+1}"
        
        if version in filename_counter:
            filename_counter[version] += 1
            version = f"{version}_{filenamecounter[version]}"
        else:
            filename_counter[version] = 0
            
        output_filename = os.path.join(output_dir, f"{version}.gbk")
        with open(output_filename, "w") as output_handle:
            SeqIO.write(record, output_handle, "genbank")

def run(args):
    input_file = args.input
    output_dir = args.output_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    split_genbank_file(input_file, output_dir)
    
