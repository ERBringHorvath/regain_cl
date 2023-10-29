from rpy2.robjects import r

def run(args):
    # append .rds and .RData to output file names if not already present
    output_boot = args.output_boot if args.output_boot.endswith('.rds') else args.output_boot + '.rds'
    database_output = args.database_output if args.database_output.endswith('.RData') else args.database_output + '.RData'

    r(f'''
    # Install required packages if not already installed
    if (!require(bnlearn)) {{install.packages('bnlearn')}}
    if (!require(dplyr)) {{install.packages('dplyr')}}
    if (!require(parallel)) {{install.packages('parallel')}}
    if (!require(pbapply)) {{install.packages('pbapply')}}
    if (!require(BiocManager)) {{install.packages('BiocManager')}}
    if (!require(gRain)) {{BiocManager::install('gRain')}}
    
    # Read in CSV presence/absence matrix
    data <- read.csv("{args.input}", row.names = 1)

    # Convert all columns to factors (required for bnlearn package)
    d_fact <- data %>% mutate_if(is.numeric, as.factor)

    # Run boostrapping in parallel. Run between 300 and 500 bootstraps.
    n.cores <- {args.threads} 
    cl = parallel::makeCluster(n.cores)
    clusterSetRNGStream(cl, 12345)
    boot = boot.strength(data = d_fact, R={args.number_of_bootstraps}, algorithm = "hc",
                         algorithm.args = list(score="bde", iss=10), cluster = cl)

    # Save the bootstrapped object to create a static Bayes Net
    saveRDS(boot, file = "{output_boot}")

    # Read the Bayes Net created in previous step
    boot = readRDS(file = "{output_boot}")

    # Determine significance threshold
    averaged.network(boot)

    # Remove poorly supported pairs, example given is threshold of 0.5
    avg.boot = averaged.network(boot, threshold = 0.5)

    arcs(avg.boot) <- directed.arcs(avg.boot)

    # Created object needed for both visualized network and queryable network
    fitted = bn.fit(avg.boot, d_fact, method = "bayes")

    # Save fitted as RData object

    parallel::stopCluster(cl)

    library(gRain)
    database = compile(bnlearn::as.grain(fitted), propagate = T)
    save(database, file = "{database_output}")
    ''')
