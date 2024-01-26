def run(args):
    from Bio import SeqIO
    from tqdm import tqdm
    
    input_file = args.input
    output_dir = args.output_dir

    total_records = sum(1 for record in SeqIO.parse(input_file, "fasta"))

    with tqdm(total=total_records, desc="Processing") as pbar:
        for record in SeqIO.parse(input_file, "fasta"):
            output_file = f"{output_dir}/{record.id}.fasta"
            SeqIO.write(record, output_file, "fasta")
            pbar.update(1)