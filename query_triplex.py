import requests
import MySQLdb
import MySQLdb.cursors
import json
import os
import sys
import getopt
import time
# This is a set of function to call the triplexRNA,org database with sql query and json call, part of an internship
# The goal of this funtions is to output data in a form usable for cytoscape, a logicial to represent graph from various output, here .sif
# This output is a transformation of data to target the micro-RNAs involved in the most triplexes, which can be easely visuluable 


config = {}
DB_ADDR="address"
DB_PORT="port"
DB_USER="user"
DB_PASS="password"
DB_NAME="name"

DEFAULT_SERVER_ADDR="localhost"
DEFAULT_DB_PORT=3306
DEFAULT_PATHWAYS="hsa05218"

id_pathways="pathways_in_triplex"
BIAS='bias'


def get_cli(argv):
    """
    Parses the command line, returning the mandatory parameters.
    """
    global config
    global id_pathways

    # assign defult configurations (might be overwritten while
    # parsing the provided cli options)
    config[DB_ADDR] = DEFAULT_SERVER_ADDR
    config[DB_PORT] = DEFAULT_DB_PORT
    id_pathways=DEFAULT_PATHWAYS

    try:
        opts, args = getopt.getopt(argv, "hi:d:b:u:p:n:a", ['help', 'id-pathways=', 'db-addr=', 'db-port=', 'user=', 'password=', 'name=', 'bias_analysis'])
    except getopt.GetoptError as err:
        print_help()
        print str(err)
        sys.exit(1)
    
    # parse the provided cli options
    for opt, arg in opts:
        print opt, arg
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif opt in ( '-i', '--id_pathways'):
            id_pathways = arg
        elif opt in ('-d', '--db_addr'):
            config[DB_ADDR] = arg
        elif opt in ('-b', '--db_port'):
            config[DB_PORT] = arg
        elif opt in ('-u', '--user'):
            config[DB_USER] = arg
        elif opt in ('-p', '--password'):
            config[DB_PASS] = arg
        elif opt in ('-n', '--name'):
            config[DB_NAME] = arg
        elif opt in ('-a', '--bias_analysis'):
            config[BIAS] = True
            
    # check wether or not all mandatory parameters have been provided
    if ( (DB_USER not in config.keys())
        or (DB_PASS not in config.keys())
        or (DB_NAME not in config.keys())):
        print_help()
        print "key missing"
        print config 
        sys.exit(1)
        
    return



def print_help():
    
    #Prints the help/usage
    
    print('\t This function, ' + os.path.basename(sys.argv[0]) + ', take as arguments:' + '\n')
    print('\t-help\t\t\tprint this help and exit')
    print('\t-id_pathways id_pathways \tthe pathway id to query inside the sql table Pathways')
    print('\t-db_addr  DB_ADDR\tthe server\'s data-base address')
    print('\t-db_port  DB_PORT\tthe server\'s data-base port')
    print('\t-user  DB_USER\t\tthe server\'s data-base user (mandatory)')
    print('\t-password  DB_PASS\tthe server\'s data-base password (mandatory)')
    print('\t-name  DB_NAME\t\tthe server\'s data-base name (mandatory)')
    print('\t-bias_analysis BIAS \t initiate a different behavior, query all the genes and functionnal triplexes inside the sql pathways table, \n \t\t\t\t and output a .sif file, and exit. This option does not require arguments')

    print('\n' + '\t' + 'Where db_addr and db_port and id_pathways have defaults values')


def get_db():
     # The function to get the connection to the database is called get_db,
    db = MySQLdb.connect(
            host=config[DB_ADDR],
            port=config[DB_PORT],
            user=config[DB_USER],
            passwd=config[DB_PASS],                         
            db=config[DB_NAME],
                     
            cursorclass = MySQLdb.cursors.SSCursor)
    
    return db


def request_pathways_component(id_pathways):

    query = "select miR1_name, miR2_name, triplexes, targets from pathways where pathways.id=%(s1)s"

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(query, {"s1":id_pathways})
        data = cursor.fetchall()      
    except:
        print "error"
         
    cursor.close()
    db.close()
        
    return data

def merging_micro_RNA():
    #miRNAs with nearly identical sequences except for one or two nucleotides are
    #annotated with an additional lower case letter. For example, miR-124a is closely related to miR-124b.
    #the goal of the function is to regroup them under one name for the further graph construction
    
    return 



def triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, string):
    #the goal here is to filter the triplexes based on the workflow of the triplex database
    #if the seed binding parameter is equal to yes, that's mean that both micro-RNAs are binding and exert a cooperative repression,
    #according to the simulation of the workflow which the RNA database is based on
    
    #here I take the seed binding parameter, but the triplexe pattern can also be taken
    
    if pattern == "canonical triplex":
            string= string + micro_RNA1 + " " + triplexe + " " + micro_RNA2 + "\n"


    return string


def jasoooooon(gene):
    print gene
    response = requests.get("http://www.sbi.uni-rostock.de/triplexrna/JSON/Human/gene/" + gene )
    if response.status_code == 200:
        results = json.loads(response.content) # results can be now accessed as a Python dictionary

    return results 

def write_sif_output(gene, string):

    fichier = open(gene + ".sif", "w")
    fichier.write(string)
    fichier.close()

    return 


def write_rapport_ouput(set_of_genes):
    #here is the printing function for the global output of the sfi test creation, number of genes, etc
    string=""
    list_gene=""    
    string="Genes present in the melanoma pathways - from the triplex RNA database, id_pathways=hsa05218 - are :" 
    i=0
    for gene in set_of_genes :
        list_gene="\n"+gene+list_gene
        i=i+1
    string="There is " + str(i) + " genes in this particular pathway" + list_gene
    
    fichier = open("global_report_melanoma_pathways.txt", "w")
    fichier.write(string)
    fichier.close()
    
    return 


def add_rapport_output(gene, count_of_triplexes):
    #addition to the outputfile the number of triplex per genes 
    string="\n" + str(gene) + " : " +str(count_of_triplexes)
    fichier = open("global_report_melanoma_pathways.txt", "a")
    fichier.write(string)
    fichier.close()    
    
    return


def add_header_output(header):
    #addition to the outputfile the number of triplex per genes 
    string="\n"+ header
    fichier = open("global_report_melanoma_pathways.txt", "a")
    fichier.write(string)
    fichier.close()    
    
    return


def pattern_control_for_count(pattern, count_of_triplex):
    #the goal here is to count the number of valid triplexes per genes
    #if the pattern parameter is equal to "canonical triplex", that's mean that both micro-RNAs are binding and exert a cooperative repression,
    #according to the simulation of the workflow which the triplex RNA database is based on
    
    #here I take the triplex pattern as the seed pattern doesn't seem reliable on that matter, cf TRIPLEX ID : 596935
    
    if pattern == "canonical triplex":
        return count_of_triplex+1
    else:
        return count_of_triplex 


def functionnal_triplexes_pathway_table(set_of_genes):
    count_of_triplex=0
    triplexes_whole_pathways=""
    for gene in set_of_genes :
        json_gene=jasoooooon(gene)
        for dictionnary in json_gene :
            micro_RNA1 = dictionnary['miRNA1 ID']
            micro_RNA2 = dictionnary['miRNA2 ID']
            #micro_RNA1 = merging_micro_RNA(micro_RNA1)
            #micro_RNA2 = merging_micro_RNA(micro_RNA2)
            triplexe = dictionnary['Triplex ID']
            pattern = dictionnary['Pattern']
            triplexes_whole_pathways = triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, triplexes_whole_pathways)
            count_of_triplex = pattern_control_for_count(pattern, count_of_triplex)


    write_sif_output("pathway_biais", triplexes_whole_pathways)
    print count_of_triplex
    return 



def request_all_genes():
    #this function request everything in the target column of the table pathways
    #the main purpose of it is to query every single genes
    #this will be used to query every functionnal triplexes, to further estimate the enrichment biais in the triplexe database
    #i.e. to compare the enrichment biais of the base to the triplexes composition of a genes
    
    query = "select targets from pathways"

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(query)
        data = cursor.fetchall()      
    except:
        print "error"
         
    cursor.close()
    db.close()
        
    return data


def gene_reader_sql_output(results, column):
    #column in the number of the column to lok for genes in the result
    set_of_genes=set()
    for result in results :

        genes=result[column]

        if "/" in genes:
            genes = genes.split("/")
            for gene in genes:
                set_of_genes.add(gene)
        else:
            set_of_genes.add(genes)

    return set_of_genes

def main_biais_analysis():
    result = request_all_genes()
    set_of_genes=gene_reader_sql_output(result,0)


    #len(set_of_genes)
    #1851
    functionnal_triplexes_pathway_table(set_of_genes)
    return 

def json_read(dictionnary):
    
    micro_RNA1 = dictionnary['miRNA1 ID']
    micro_RNA2 = dictionnary['miRNA2 ID']
    #micro_RNA1 = merging_micro_RNA(micro_RNA1)
    #micro_RNA2 = merging_micro_RNA(micro_RNA2)
    triplexe = dictionnary['Triplex ID']
    pattern = dictionnary['Pattern']

    return micro_RNA1, micro_RNA2, triplexe, pattern


        
def output_manager(string, gene, count_of_triplex, list_of_genes_without_triplexes):
    
    #this functiom return list_of_genes_without_triplexes because it is a global variable
    #otherwise, the function write the various output files in sif format for visualisation in cytoscape
    #the function also writte some information in a another file which resume the global process (number of genes, triplexes per genes)
    
    
    if len(string)>1 :   #to avoid output of empty text files
        write_sif_output(gene, string)
        add_rapport_output(gene, count_of_triplex)
    else :
        list_of_genes_without_triplexes.append(gene)

    return  list_of_genes_without_triplexes



def gene_without_triplexes_reporter(list_of_genes_without_triplexes):
    count_of_triplexes=0        #and supposed to remain the same, it's just for the call of the function to writte into the rapport fil
    if len(list_of_genes_without_triplexes)>0:
        for gene in list_of_genes_without_triplexes:
            add_header_output("Genes without triplexes")
            add_rapport_output(gene, count_of_triplexes)    
    return 



if __name__ == '__main__':
    
    reload(sys)
    get_cli(sys.argv[1:])
    
    if config[BIAS] == True :
        
        print "\t This option is an override of the normal behavior of the executable script"
        print "\t In 60 secondes this executable will query all the triplexes inside the pathways table of the triplexRNA"
        print "\t This query is about 1800 jason call, so it will take time"
        print "\t This script will output a dedicated file call 'pathways biais' and will exit after, even with a pathways put as argument"
        time.sleep(60) 
        #main_biais_analysis()
        sys.exit(2)
    

    
    if not os.path.exists("Output_files_of_the_triplexdatabase_query"):
        os.mkdir("Output_files_of_the_triplexdatabase_query")
    os.chdir("Output_files_of_the_triplexdatabase_query")
    results=request_pathways_component(id_pathways)       
    set_of_genes=set()
    set_of_genes=gene_reader_sql_output(results, 3)
    write_rapport_ouput(set_of_genes)

    
    add_header_output("Genes and the number of their triplexes")   
    triplexes_whole_pathways=""   #string for output a sif file for the all pathway
    
    for gene in set_of_genes :
        json_gene=jasoooooon(gene)
        list_of_genes_without_triplexes=[]
        
        string=""
        count_of_triplex=0
        for dictionnary in json_gene :
            micro_RNA1, micro_RNA2, triplexe, pattern=json_read(dictionnary)
            string = triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, string)
            triplexes_whole_pathways = triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, triplexes_whole_pathways)
            count_of_triplex = pattern_control_for_count(pattern, count_of_triplex)
        
        #the following function do more behing the door than the return suggest
        list_of_genes_without_triplexes=output_manager(string, gene, count_of_triplex, list_of_genes_without_triplexes) 
        
                
    write_sif_output("melanoma_pathway", triplexes_whole_pathways)

    gene_without_triplexes_reporter(list_of_genes_without_triplexes)
    


























