import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects.conversion import localconverter
import pandas as pd
import os

def run(args):
    r = ro.r
    r['options'](warn=-1)

    # R package names
    packnames = ('bnlearn', 'gRain', 'reshape2', 'dplyr')

    # R vector of strings
    from rpy2.robjects.vectors import StrVector

    # Selectively install what needs to be installed
    names_to_install = [x for x in packnames if not isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))

    # Now load the libraries
    bnlearn = importr('bnlearn')
    gRain = importr('gRain')
    reshape2 = importr('reshape2')
    dplyr = importr('dplyr')

    r(f'''
        boot = readRDS("{args.input}")
        matrix <- read.csv("{args.presence_absence_matrix}", row.names = 1)

        averaged.network(boot)
        avg.boot = averaged.network(boot, threshold = 0.5)
        arcs(avg.boot) <- directed.arcs(avg.boot)
        
        fitted = bn.fit(avg.boot, matrix_f, method = "bayes")

        data <- read.csv("{args.meta_data}")
        gene_names <- data[, 1]
        valid_genes <- intersect(gene_names, colnames(data)) ##only include genes for query that are in the matrix
        
        matrix_f <- matrix %>% mutate_if(is.numeric, as.factor)
        
        gene_in_db <- function(gene_name) {	
            return(gene_name %in% fitted$gene_names)
        }
        
        
        ''')

    print("\033[35m" + "\nData loaded, fitted network created... " + "\033[0m")

    absodds = r('''
        absodds <- matrix(NA, nrow = length(gene_names), ncol = length(gene_names),
                  dimnames = list(gene_names, gene_names))

        ###Compute pairwise absolute odds ratios
        for (a in seq_along(gene_names)) {
          for (b in seq_along(gene_names)) {
            if (a != b && gene_in_db(gene_names[a]) && gene_in_db(gene_names[b])) {
              exposed = cpquery(fitted, event = eval(parse(text = paste0(gene_names[a], ' == ', 1))),
                                evidence = eval(parse(text = paste0(gene_names[b], ' == ', 1))),
                                n = 10000)
              baseline = cpquery(fitted, event = eval(parse(text = paste0(gene_names[a], ' == ', 1))),
                                 evidence = eval(parse(text = paste0(gene_names[b], ' == ', 0))),
                                 n = 10000)

              absodds[a, b] <- exposed/baseline
            }
          }
        }
        absodds_df <- melt(absodds)
        colnames(absodds_df) <- c('Gene_1', 'Gene_2', 'Absolute_Odds_Ratio')
    ''')

    print("\033[35m" + "\nAbsolute odds ratios calculated... " + "\033[0m")

    probs = r('''
        probs <- matrix(NA, nrow = length(gene_names), ncol = length(gene_names),
                dimnames = list(gene_names, gene_names))

        ###Compute pairwise probabilities
        for (i in seq_along(gene_names)) {
          for (j in seq_along(gene_names)) {
            if (i != j && gene_in_db(gene_names[i]) && gene_in_db(gene_names[j])) {
              # Compute conditional probability
              P_ij <- cpquery(fitted, 
                              event = eval(parse(text = paste0(gene_names[i], ' == ', 1))), 
                              evidence = eval(parse(text = paste0(gene_names[j], ' == ', 1))), 
                              n = 10000)

              # Store result
              probs[i, j] <- P_ij
            }
          }
        }
        probs_df <- melt(probs)
        colnames(probs_df) <- c('Gene_1', 'Gene_2', 'Probability_Score')
    
    merged_df <- merge(probs_df, absodds_df, by = c('Gene_1', 'Gene_2'))
    merged_df <- na.omit(merged_df)
    write.csv(merged_df, 'Scores.csv', row.names = F)

    ''')
    
    print("\033[92m" + "\nConditional Probabilities calculated. Results file created." + "\033[0m")