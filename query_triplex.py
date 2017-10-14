import requests
import MySQLdb
import MySQLdb.cursors
import json
import os
import sys
import getopt
import shutil

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

liste_of_genes=".txt"


def get_cli(argv):
    """
    Parses the command line, returning the mandatory parameters.
    """
    global config
    global liste_of_genes
    
    # assign defult configurations (might be overwritten while
    # parsing the provided cli options)
    config[DB_ADDR] = DEFAULT_SERVER_ADDR
    config[DB_PORT] = DEFAULT_DB_PORT


    try:
        opts, args = getopt.getopt(argv, "hl:d:b:u:p:n:a", ['help', 'liste_of_genes=', 'db-addr=', 'db-port=', 'user=', 'password=', 'name='])
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
        elif opt in ( '-l', '--liste_of_genes'):
            liste_of_genes = arg
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
    print('\t-h | --help\t\t\tprint this help and exit')
    print('\t-l  | --liste_of_genes liste_of_genes= \tthe name of the file with the genes to query. One gene name by line')
    print('\t-d  | -db_addr  DB_ADDR\tthe server\'s data-base address')
    print('\t-b  | -db_port  DB_PORT\tthe server\'s data-base port')
    print('\t-u  | --user  DB_USER\t\tthe server\'s data-base user (mandatory)')
    print('\t-p  | -password  DB_PASS\tthe server\'s data-base password (mandatory)')
    print('\t-n  | -name  DB_NAME\t\tthe server\'s data-base name (mandatory)')

    print('\n' + '\t' + 'Where db_addr and db_port have defaults values')


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
    string="Genes present in list of genes:" 
    i=0
    for gene in set_of_genes :
        list_gene="\n"+gene+list_gene
        i=i+1
    string="There is " + str(i) + " genes in this particular pathway" + list_gene
    
    fichier = open("global_report.txt", "w")
    fichier.write(string)
    fichier.close()
    
    return 


def add_rapport_output(gene, count_of_triplexes):
    #addition to the outputfile the number of triplex per genes 
    string="\n" + str(gene) + " : " +str(count_of_triplexes)
    fichier = open("global_report.txt", "a")
    fichier.write(string)
    fichier.close()    
    
    return


def add_header_output(header):
    #addition to the outputfile the number of triplex per genes 
    string="\n"+ header
    fichier = open("global_report.txt", "a")
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




def request_position_triplexes(id_triplex):
    
    #this request the positions of start and end for the two microRNAs binding site for one triplexe
    #the purpose is to filter out the triplexes with the exact same position (provocked by microRNAs of the same familly)
    #this filtering is to avoid an over-estimation of the triplexes that the micro-RNA contribute to

    query = "select gene_start1, gene_end1, gene_start2, gene_end2 from triplets where id=%(s1)s"
    
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(query, {"s1":id_triplex})
        data = cursor.fetchall()      
    except:
        print "error"
         
    cursor.close()
    db.close()


    return data

def request_id_same_position(gene_start1, gene_end1, gene_start2, gene_end2, micro_RNA1, micro_RNA2,):
    
    #prolongation of the previous fonction for filtering, now we look for triplexes to filter
    
    query ="select id from triplets where (gene_start1=" + str(gene_start1) + " or gene_end2=" + str(gene_end1) + ") and (gene_start2=" + str(gene_start2) + " or gene_end2=" + str(gene_end2) + ') and (miR1_name="' + str(micro_RNA1) + '" or mir2_name="' + str(micro_RNA2) +'");'
       
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



def triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, string):
    #the goal here is to filter the triplexes based on the workflow of the triplex database
    #if the seed binding parameter is equal to yes, that's mean that both micro-RNAs are binding and exert a cooperative repression,
    #according to the simulation of the workflow which the RNA database is based on
    
    if pattern == "canonical triplex":
        #string = string + micro_RNA1 + " " + triplexe + " " + micro_RNA2 + "\n"            
               
        if int(triplexe) in list_of_filtering :
            string=string
        else :
            string = string + micro_RNA1 + " " + triplexe + " " + micro_RNA2 + "\n"
        data=request_position_triplexes(id_triplex=triplexe)

        ids_redondant_triplexes=request_id_same_position(int(data[0][0]), int(data[0][1]), int(data[0][2]), int(data[0][3]), micro_RNA1, micro_RNA2)
        for ids in ids_redondant_triplexes:
            holder=int(ids[0])
            list_of_filtering.append(holder)
 


    return string





if __name__ == '__main__':
    
    reload(sys)
    get_cli(sys.argv[1:])

    filin =open(liste_of_genes)
    set_of_genes=set()
    lines=filin.readlines()
    
    if os.path.exists("Output_files_of_the_triplexdatabase_query" + str(liste_of_genes)):
    
        shutil.rmtree("Output_files_of_the_triplexdatabase_query" + str(liste_of_genes))
    if not os.path.exists("Output_files_of_the_triplexdatabase_query" + str(liste_of_genes)):
        os.mkdir("Output_files_of_the_triplexdatabase_query" + str(liste_of_genes))
   
    os.chdir("Output_files_of_the_triplexdatabase_query" + str(liste_of_genes))
    

    for line in lines :
        line=line.replace("\n", "")
        set_of_genes.add(line)
    
    write_rapport_ouput(set_of_genes)

    
    add_header_output("Genes and the number of their triplexes")   
    triplexes_whole_list_of_gene=""   #string for output a sif file for the all query
    
    for gene in set_of_genes :
        
        global list_of_filtering
        list_of_filtering=[]
        
        json_gene=jasoooooon(gene)
        list_of_genes_without_triplexes=[]
        
        string=""
        count_of_triplex=0
        for dictionnary in json_gene :
            micro_RNA1, micro_RNA2, triplexe, pattern=json_read(dictionnary)
            string = triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, string)
            triplexes_whole_list_of_gene = triplex_pattern_control(pattern, micro_RNA1, micro_RNA2, triplexe, triplexes_whole_list_of_gene)  #filter also redondant triplexes
            count_of_triplex = pattern_control_for_count(pattern, count_of_triplex)
        
        #the following function do more behing the door than the return suggest
        list_of_genes_without_triplexes=output_manager(string, gene, count_of_triplex, list_of_genes_without_triplexes) 
        
                
    write_sif_output(liste_of_genes, triplexes_whole_list_of_gene)

    gene_without_triplexes_reporter(list_of_genes_without_triplexes)











