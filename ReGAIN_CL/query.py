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
    packnames = ('bnlearn', 'gRain', 'doParallel', 'foreach')

    # R vector of strings
    from rpy2.robjects.vectors import StrVector

    # Selectively install what needs to be installed
    names_to_install = [x for x in packnames if not isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))

    # Now load the libraries
    bnlearn = importr('bnlearn')
    gRain = importr('gRain')
    doParallel = importr('doParallel')
    foreach = importr('foreach')

    r(f'''
        load("{args.input}")
        data <- read.csv("{args.meta_data}")
        gene <- data$Gene
        n.cores <- {args.threads}
        registerDoParallel(cores = n.cores)
        ''')

    relodds = r('''
        relodds <- foreach(x = gene, .combine = rbind, .packages = c("bnlearn", "gRain")) %dopar% {
          temp2 <- foreach(y = gene, .combine = rbind, .packages = c("bnlearn", "gRain")) %do% {
            if (x != y) {
              exposed = querygrain(setEvidence(database, nodes = c(x),
                                               states = c("1"), propagate = T),
                                   nodes = y)[[1]][2]
              baseline = querygrain(database, nodes = c(y),
                                    type = "marginal")[[1]][2]
              
              relative_odds <- exposed/baseline
              
              c(Gene_1 = x, Gene_2 = y, Relative_Odds_Ratio = relative_odds)
            } else {
              NULL
            }
          }
          temp2
        }
        data.frame(relodds)
    ''')

    probs = r('''
        probs <- foreach(x = gene, .combine = rbind, .packages = c("bnlearn", "gRain")) %dopar% {
          temp2 <- foreach(y = gene, .combine =rbind, .packages = c("bnlearn", "gRain")) %do% {
            if (x != y) {
              exposed = querygrain(setEvidence(database, nodes = c(x),
                                               states = c("1"), propagate = T),
                                   nodes = y)[[1]][2]
              
              c(Gene_1 = x, Gene_2 = y, Probability = exposed)
            } else {
              NULL
            }
          }
          temp2
        }
        data.frame(probs)
    ''')

    with localconverter(ro.default_converter + pandas2ri.converter):
        relodds_df = ro.conversion.rpy2py(relodds)
        probs_df = ro.conversion.rpy2py(probs)

    merged_df = pd.merge(relodds_df, probs_df, on=['Gene_1', 'Gene_2'])

    merged_df.to_csv(args.output, index=False)
