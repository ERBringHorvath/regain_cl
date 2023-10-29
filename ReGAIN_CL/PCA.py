import subprocess
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

def install_r_package(package_name):
    utils = importr('utils')
    utils.chooseCRANmirror(ind=1)
    utils.install_packages(package_name)

def run(args):
    # Check and install rpy2 if necessary
    try:
        import rpy2
    except ImportError:
        print("Installing rpy2 package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rpy2"])

    # Set up R environment and check/install R packages
    r_required_packages = ["vegan", "ggplot2", "tidyr", "dplyr", "RColorBrewer"]
    r_installed_packages = robjects.r("installed.packages()[,1]")

    for package in r_required_packages:
        if package not in r_installed_packages:
            print(f"Installing R package: {package}")
            install_r_package(package)

    # Read input file
    robjects.r(f'data <- read.csv("{args.input}", row.names=1)')

    # Execute R script
    robjects.r(f'''
        library(vegan)
        library(ggplot2)
        library(tidyr)
        library(dplyr)
        library(RColorBrewer)

	data_T <- setNames(data.frame(t(data[,-1])), data[,1])
        pca <- prcomp(data_T)

        clusters <- kmeans(pca$x, centers={args.centers})
        cluster_table <- data.frame(sample=rownames(data_T), cluster=clusters$cluster)

        colors <- c("red", "blue", "green", "orange", "violet", "aquamarine",
            "navy", "firebrick", "cyan4", "purple")

        plot(pca$x, type="n", xlab="PCA1", ylab="PCA2")
        points(pca$x, col="black", bg=colors[clusters$cluster], pch=21, cex=2.5)
        text(pca$x, labels=rownames(data_T), pos=2, cex=0.5)
    ''')
    
    output_format = args.output.split('.')[-1]
    robjects.r(f'''
        {output_format}("{args.output}")
        plot(pca$x, type="n", xlab="PCA1", ylab="PCA2")
        points(pca$x, col="black", bg=colors[clusters$cluster], pch=21, cex=2.5)
        text(pca$x, labels=rownames(data_T), pos=2, cex=0.5)
        dev.off()
    ''')
        

    # Save cluster table as CSV
    robjects.r('write.csv(cluster_table, file="PCA_GeneClusters.csv", row.names=F)')
