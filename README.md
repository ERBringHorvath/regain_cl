# **Installation and User guide for ReGAIN** #

**Prerequisites**

Ensure that you have the following prerequisites installed on your system:
Python (version 3.8 or higher)
R (version 4 or higher)
NCBI AMRfinderPlus

**Suggested to install all prerequisites within a Conda environment**

Create Conda environment and nstall NCBI AMRfinderPlus

`conda create -y -c conda-forge -c bioconda regain ncbi-amrfinderplus`

Activate the environement

`source activate amrfinder`

Download ARMfinderPlus Database

`amrfinder -u`

Install Python dependencies

`pip install tqdm pandas`

Download ReGAIN to preferred directory

`git clone https://github.com/ERBringHorvath/ReGAIN_CL.git`

Add ReGAIN to your PATH

For Unix/Linux/macOS:

`export PATH="$PATH:/path/to/your-program-directory"`

Verify installation:

`regain --version`

use `-h`, `--help`, to bring up the help menu

`regain --help`
 
Programs and example usage

Resistance and virulence gene identification (Module 1, `regain AMR`):

`-d`, `--directory`, path to directory containing FASTA files to analyze

`-O`, `--organism`, specify what organism (if any) you want to analyze (optional flag)

`-T`, `--threads`, number of cores to dedicate

`-o`, `--output-dir`, output directory to store AMRfinder results

Currently supported organisms and how they should be input,
Acinetobacter_baumannii, 
Burkholderia_cepacia
Burkholderia_pseudomallei
Campylobacter
Clostridioides_difficile
Enterococcus_faecalis
Enterococcus_faecium
Escherichia
Klebsiella
Neisseria
Pseudomonas_aeruginosa
Salmonella
Staphylococcus_aureus
Staphylococcus_pseudintermedius
Streptococcus_agalactiae
Streptococcus_pneumoniae
Streptococcus_pyogenes
Vibrio_cholerae

Module 1 example usage:
                                       
`regain AMR -d path/to/directory -O Pseudomonas_aruginosa -T 8 -o output_directory`

Dataset creation (Module 2, `regain matrix`)
                                       
`-d`, `--directory`, path to AMRfinder results in CSV format

`-s`, `--search-strings-output`, name of output file where gene names will be stored

`--gene-type`, searches for `resistance` or `virulence` genes

`-f`, `--search-output`, presence/absence matrix with all genes in your dataset

`--min`, minimum desired occurrence of genes across genomes

`--max`, maximum allowed occurrence of genes (should be less than number of genomes, as genes occurring across all genomes can significantly slow down Bayesian analysis.

`--simplify-gene-names`, gets rid of special characters in gene names, i.e., aph(3’’)-Ib becomes aph3pp_Ib. This is required for the Bayesian network structure learning module

`-o`, `--output`, output of final cleaned up presence/absence matrix

Module 2 example usage:
                                            
`regain matrix -d path/to/directory -s search_strings --simplify-gene-names --gene-type resistance -f matrix.csv --min 5 --max 500 -o matrix_final.csv`

NOTE: all results are saved in the 'ReGAIN_Dataset', folder which will be generated within the directory defined by --directory

Bayesian network structure learning (Module 3, `regain bnL` or `regain bnS`)
                                            
`-i`, `--input`, input file in CSV format

`-M`, `--metadata`, file containing gene names and descriptions

`-o`, `--output_boot`, output bootstrap file

`-T`, `--threads`, number of cores to dedicate

`-n`, `--number_of_boostraps`, how many bootstraps to run (suggested 300-500)

`-r`, `--number-of-resamples`, how many data resamples you want to use (suggested 100)

Bayesian Network example usage:

`bnS`, Bayesian network structure learning analysis for less than 100 genes

`bnL`, Bayesian network structure learning analysis for 100 genes or greater

`###For less than 100 genes
regain bnS regain bnS -i matrix.csv -M metadata.csv -o boot -T 8 -n 3 -r 3`
                                            
`###For 100 or more genes     
regain bnL -i matrix.csv -M metadata.csv -o boot -T 8 -n 3 -r 3`

For multidimensional analyses (Optional Module 4, `regain MVA`)

Currently supported measures of distance: `manhattan`, `euclidean`, `canberra`, `clark`, `bray`, 
                                          `kulczynski`, `jaccard`, `gower`, `altGower`, `morisita`, 
                                          `horn`, `mountford`, `raup`, `binomial`, `chao`, `cao`, `mahalanobis`, 
                                          `chisq`, `chord`, `hellinger`
                                           
`-i`, `--input`, input file in CSV format

`-m`, `--method`, measure of distance method

`-c`, `--centers`, how many centers you want for your multidimensional analysis (1-10)

`-C`, `--confidence`, confidence interval for ellipses
                                       
Module 4 example usage

`$ regain MVA -i matrix.csv -m jaccard -c 3 -C 0.75`

NOTE: the MVA analysis with generate 2 files: a PNG and a PDF of the plot   
<<<<<<< HEAD

=======
>>>>>>> cbaf8d32823a95a254078172d8000eab83b875c8
