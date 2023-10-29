def run(args):
	import pandas as pd
	from mlxtend.frequent_patterns import apriori
	from mlxtend.frequent_patterns import association_rules

	input_file = pd.read_csv(args.input)
	ouput_file = args.output_file

	input_file = input_file.astype('bool')
	input_file = input_file.drop('file', axis=1)

	frequent_itemsets = apriori(input_file, min_support=0.07, use_colnames=True)
	rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

	rules.to_csv(args.output_file, index=False)
