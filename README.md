# Circular RNA design

This script is part of a workflow developped at the Systems Biology and Bioinformatics department, Universität Rostock, as an extension of the TriplexRNA database, https://triplexrna.org/, a database of cooperating microRNAs and their mutual target.

This script query a local instance of the TriplexRNA, not the web instance.


# How to use it

The script take as input a the name of a file containing a list of genes (see below), the name of the user, the password of the user and the name of the base on the machine.

The file much contain the names of the genes from which the user want to recollect all the canonical triplexes. This file is a txt file with just the name of the genes, one per line.

# Example

The script is provided with a example files :  liste_gene.txt


	python python query_triplex.py -h

To see the help and how to pass arguments.

# About

This script has been developped at the Systems Biology and Bioinformatics department - Universität Rostock, by E. Rolland and A. Bagnacani, under the supervision of the Dr S. Gupta and the Pr O. Wolkenhauer.
