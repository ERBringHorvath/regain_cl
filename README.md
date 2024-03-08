# <ins>**ReGAIN Installation and User guide**</ins> 

<img src="https://github.com/ERBringHorvath/regain_cl/assets/97261650/931d3268-89c3-41e0-99f6-23530fe2f8ac" alt="image" width="363" height="418"/>

_________________________________________________________________________________

**Prerequisites**

Ensure that you have the following prerequisites installed on your system:

Python (version 3.8 or higher)

R (version 4 or higher)

NCBI AMRfinderPlus

[Install R](https://www.r-project.org/)

_________________________________________________________________________________


**It is suggested that ReGAIN and all prerequisites are installed within a Conda environment**

Download [miniforge](https://github.com/conda-forge/miniforge/)

Create Conda environment and install [NCBI AMRfinderPlus](https://github.com/ncbi/amr/wiki/Install-with-bioconda)

`conda create -n regain python=3.10`

`conda activate regain`

Install AMRfinderPlus

`conda install -y -c conda-forge -c bioconda ncbi-amrfinderplus`

Check installation

`amrfinder -h`

Download ARMfinderPlus Database

`amrfinder -u`

Download ReGAIN to preferred directory

`git clone https://github.com/ERBringHorvath/regain_cl`

Install Python dependencies

`pip install -r requirements.txt` or `pip3 install -r requirements.txt`

Add ReGAIN to your PATH

Add this line to the end of `.bash_profile` (Linux/Unix) or `.zshrc` (macOS):

`export PATH="$PATH:/path/to/regain/bin"`

Replace `/path/to/regain/bin` with the actual path to the directory containing the executable. <br />
Whatever the initial directory, this path should end with `/regain/bin`

Save the file and restart your terminal or run `source ~/.bash_profile` or `source ~/.zshrc`

Verify installation:

`regain --version`

use `-h`, `--help`, to bring up the help menu

`regain --help`

_________________________________________________________________________________

# <ins>**Programs and Example Usage**</ins> 

## **Resistance and Virulence Gene Identification** 

Module 1.1 `regain AMR`

`-d`, `--directory`, path to directory containing FASTA files to analyze <br />
`-O`, `--organism`, specify what organism (if any) you want to analyze (optional flag) <br />
`-T`, `--threads`, number of cores to dedicate <br />
`-o`, `--output-dir`, output directory to store AMRfinder results

**Currently supported organisms and how they should be called:**

`Acinetobacter_baumannii` <br />
`Burkholderia_cepacia` <br />
`Burkholderia_pseudomallei` <br />
`Campylobacter` <br />
`Clostridioides_difficile` <br />
`Enterococcus_faecalis` <br />
`Enterococcus_faecium` <br />
`Escherichia` <br />
`Klebsiella` <br />
`Neisseria` <br />
`Pseudomonas_aeruginosa` <br />
`Salmonella` <br />
`Staphylococcus_aureus` <br />
`Staphylococcus_pseudintermedius` <br />
`Streptococcus_agalactiae` <br />
`Streptococcus_pneumoniae` <br />
`Streptococcus_pyogenes` <br />
`Vibrio_cholerae`

**Module 1.1 example usage:**

Organism specific:

`regain AMR -d path/to/FASTA/files -O Pseudomonas_aruginosa -T 8 -o path/to/output/directory`

Organism non-specific:

`regain AMR -d path/to/FASTA/files -T 8 -o path/to/output/directory`

_________________________________________________________________________________

## **Dataset Creation** 

**NOTE**: variable names <ins>**cannot**</ins> contain special characters–but don't worry, we've taken care of that! <br />
To replace special characters during dataset creation, include `--simplify-gene-names` in the command!

Module 1.2 `regain matrix`
                                       
`-d`, `--directory`, path to AMRfinder results in CSV format <br />
`-s`, `--search-strings-output`, name of output file where gene names will be stored <br />
`--gene-type`, searches for `resistance` or `virulence` genes <br />
`-f`, `--search-output`, presence/absence matrix of all genes in your dataset, regardless of `--min`/`--max` values <br />
`--min`, minimum gene occurrence cutoff <br />
`--max`, maximum gene occurrence cutoff (should be less than number of genomes, see NOTE below) <br />
`--simplify-gene-names`, replaces special characters in gene names, i.e., aph(3’’)-Ib becomes aph3pp_Ib. This is <ins>**required**</ins> for the Bayesian network structure learning module <br />
`-o`, `--output`, output of final curated presence/absence matrix

**Module 1.2 example usage**

NOTE: Discrete Bayesian network anlyses requires all variables to exist in at least two states. For ReGAIN, these two states are 'present' and 'absent'. Ubiquitously occurring genes will break the analysis. 
Best practice is for *N* genomes, `--max` should MINIMALLY be defined as *N* - 1. Keep in mind that removing very low and very high abundance genes can reduce noise in the network.
                                            
`regain matrix -d path/to/AMRfinder/results -s search_strings --simplify-gene-names --gene-type` <br />
`resistance -f matrix.csv --min 5 --max 500 -o matrix_final.csv`

**NOTE: all results are saved in the 'ReGAIN_Dataset' folder, which will be generated within the directory defined by** `-d`

_________________________________________________________________________________

## **Bayesian Network Structure Learning** 

Module 2 `regain bnL` or `regain bnS`
                                            
`-i`, `--input`, input file in CSV format <br />
`-M`, `--metadata`, file containing gene names and descriptions <br />
`-o`, `--output_boot`, output bootstrap file <br />
`-T`, `--threads`, number of cores to dedicate <br />
`-n`, `--number_of_boostraps`, how many bootstraps to run (suggested 300-500) <br />
`-r`, `--number-of-resamples`, how many data resamples you want to use (suggested 100) <br />

**Module 2 example usage:**

**NOTE: We suggest using between 300 and 500 bootstraps and minimum 100 resamples**

`bnS`, Bayesian network structure learning analysis for less than 100 genes <br />
`bnL`, Bayesian network structure learning analysis for 100 genes or greater

For less than 100 genes:

`regain bnS regain bnS -i matrix.csv -M metadata.csv -o bootstrapped_network -T 8 -n 500 -r 100`
                                            
For 100 or more genes:

`regain bnL -i matrix.csv -M metadata.csv -o bootstrapped_network -T 8 -n 500 -r 100`

_________________________________________________________________________________

## **Multidimensional Analyses**

Optional Module 3 `regain MVA`

**Currently supported measures of distance:**

`manhattan`, `euclidean`, `canberra`, `clark`, `bray`, `kulczynski`, `jaccard`, `gower`, <br />
`horn`, `mountford`, `raup`, `binomial`, `chao`, `cao`, `mahalanobis``altGower`, `morisita`, <br />
`chisq`, `chord`, `hellinger`
                                           
`-i`, `--input`, input file in CSV format <br />
`-m`, `--method`, measure of distance method <br />
`-c`, `--centers`, how many centers you want for your multidimensional analysis (1-10) <br />
`-C`, `--confidence`, confidence interval for ellipses <br />
                                       
**Module 3 example usage:**

`regain MVA -i matrix.csv -m jaccard -c 3 -C 0.75`

**NOTE: the MVA analysis will generate 2 files: a PNG and a PDF of the plot**

_________________________________________________________________________________

## **Formatting External Data**

Bayesian network analysis requires both data matrix and metadata files. MVA analysis requires only a data matrix file.

<img src="https://github.com/ERBringHorvath/regain_cl/assets/97261650/906de456-8368-4872-97c1-df3c9978d535" alt="image">

_________________________________________________________________________________

# Citing ReGAIN

Resistance Gene Association and Inference Network (ReGAIN): A Bioinformatics Pipeline for Assessing Probabilistic Co-Occurrence Between Resistance Genes in Bacterial Pathogens
Elijah R. Bring Horvath, Mathew G. Stein, Matthew A Mulvey, Edgar Javier Hernandez, Jaclyn M. Winter
*bioRxiv* 2024.02.26.582197; doi: https://doi.org/10.1101/2024.02.26.582197
