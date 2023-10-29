from rpy2.robjects import r

def run(args):
    network_output = args.network_output if args.network_output.endswith('.html') else args.network_output + '.html'
    
    r(f'''
    ###Install required packages, if necessary
    if (!require(bnlearn)) {{install.packages('bnlearn')}}
    if (!require(dplyr)) {{install.packages('dplyr')}}
    if (!require(visNetwork)) {{install.packages('visNetwork')}}
    if (!require(igraph))  {{install.packages('igraph')}}
    if (!require(RColorBrewer)) {{install.packages('RColorBrewer')}}
    
    boot = readRDS("{args.boot_input}")
    
    data = read.csv("{args.presence_absence_matrix}", row.names = 1)
    d_fact <- data %>% mutate_if(is.numeric, as.factor)
    metadata <- read.csv("{args.meta_data}")
    
    ###Set sig threshold at 0.5
    averaged.network(boot)
    avg.boot = averaged.network(boot, threshold = 0.5)
    
    arcs(avg.boot) <- directed.arcs(avg.boot)
    
    fitted = bn.fit(avg.boot, d_fact, method = "bayes")
    
    ###Construct network
    net <- igraph.from.graphNEL(as.graphNEL(fitted))
    visZach <- toVisNetworkData(net)
    
    nodes <- visZach$nodes
    nodes = nodes[order(nodes$id),]
    
    edges <- visZach$edges
    
    metadata = metadata[order(metadata$Gene, decreasing = F),]
    met_data = metadata[metadata$Gene %in% nodes$id,]
    
    ###Add class column for node coloring
    nodes$group = met_data$GeneClass
    
    ###Def colors
    grp <- as.numeric(as.factor(nodes$group))
    n <- length(unique(grp))
    colors <- brewer.pal.info[brewer.pal.info$colorblind == T, ]
    col_vec <- unlist(mapply(brewer.pal, colors$maxcolors, rownames(colors)))
    colSide <- sample(col_vec, n)[grp]
    
    nodes$color <- colSide
    
    ###Dataframe for network legend
    ledges <- data.frame(color = unique(nodes$color),
                         label = unique(nodes$group),
                         arrows = 'none',
                         font.align = 'top',
                         shape = 'dot',
                         width = 3)
    
    lnodes <- data.frame(color = unique(nodes$color),
                         label = unique(nodes$group),
                         font.color = 'white')
    
    network <- visNetwork(nodes = nodes, edges = edges, width = '100%', height = 900) %>%
        visNodes(size = 20, color = list(highlight = 'yellow'), font = list(size = 25)) %>%
        visEdges(arrows = 'to', smooth = list(enabled = T, type = 'diagonalCross', roundness = 0.1),
            physics = F, color = "black") %>%
        visIgraphLayout(layout = "layout_with_fr", type = 'full') %>%
        visOptions(highlightNearest = list(enabled = T, degree = 1, hover = T, labelOnly = T),
            nodesIdSelection = T) %>%
        visLegend(addNodes = lnodes, width = 0.1, position = 'left', main = 'Gene Class', ncol = 2, useGroups = F)
        
    
    visSave(network, file = "{args.network_output}", background = "#F5F4F4")
    ''')