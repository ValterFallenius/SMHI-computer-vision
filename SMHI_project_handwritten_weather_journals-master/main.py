import numpy as np
import os
import sys
sys.path.insert(1, './pipeline/')
from  create_data import create_case
import data_format_change.change_format as change_format
# Required for mode 4:
sys.path.append("./Open Source Neural Network/src")
#from main_v2 import main as htr_main   # HTR Network's main script but made into a single function
import shutil
import unidecode


def compare_name(name1,name2):
    print(name2)
    name1_new = unidecode.unidecode(name1)
    name2_new = unidecode.unidecode(name2[0])
    name1_new = name1_new.split(" ")
    name2_new=name2_new.split(" ")
    try:
        if(name1_new[1]==name2_new[0]) and (name1_new[3][:-4]==name2_new[2]):
            return [[int(name2[2]),int(name2[3])],[int(name2[2]),int(name2[4][:-2])]]
    except:
        return 0
    return 0

def main(path_book,POPPLER_PATH,num_book=0,mode=3,size_tables= [[9,10],[9,10]]):
    '''
    Parameters
    ----------
    path_book: str
        The path to the PDF book.
    POPPLER_PATH : str
        Local path to poppler
    num_book : int
        Position of book in folder
    mode : int
        Integer that decides what the main function does:

        mode == 0: Label data with numbers with "769.5", "+15.0" etc.
        mode == 1: Label data wind with "NW", "S" etc.
        mode == 2: create prediction data (whithout label for number)
        mode == 3: Create new training, validation and test sets for training and train
        mode == 4: Create new test sets for prediction and predict
        mode == 5: save predict data into csv file
        mode == 6: extract position cases
    '''

    NUMBER_LABEL_PATH = "./pipeline/label/"
    WIND_LABEL_PATH = "./pipeline/wind/"
    NOLABEL_PATH = "./pipeline/nolabel/"

    if mode == 6:
        pdf_name = path_book.split("\\")[-1]
        directory = os.path.join(NOLABEL_PATH,pdf_name[:-4])
        #make directory if not exist:
        if not os.path.exists(directory):
            os.makedirs(directory)
        choose_cases=[[],[],[],[]]
        size_case =[2,2,2,2] # size of each case [2,2,2,2] is the standard case
        create_case(path_book,POPPLER_PATH,directory,size_tables,choose_cases,size_case,num_book,[2,-1],False , True)

    if mode==0:
        # Rows and columns to the label of table 1 and table 2.
        row_1=np.array([2,3,4,5])
        row_2=np.array([3,4,5,6])
        col_1=np.array([1,2,3,4,5,6,7,8])
        col_2=np.array([1,2,3,4])
        choose_cases=[row_1[:, None],col_1,row_2[:, None],col_2]
        size_case =[2,1.2,2,1.5] # size of each case [2,2,2,2] is the standard case
        create_case(path_book,POPPLER_PATH,NUMBER_LABEL_PATH,choose_cases,size_case ,num_book,pages=[2,-1])
    if mode==1:
        row_1=np.array([])
        col_1=np.array([])
        row_2=np.array([2,3,4,5])
        col_2=np.array([0])
        choose_cases=[row_1[:, None],col_1,row_2[:, None],col_2]
        size_case =[2,1.2,2,1.5] # size of each case [2,2,2,2] is the standard case
        create_case(path_book,POPPLER_PATH,WIND_LABEL_PATH,choose_cases,size_case ,num_book,pages=[2,-1])

    if mode==2:
        pdf_name = path_book.split("\\")[-1]
        directory = os.path.join(NOLABEL_PATH,pdf_name[:-4])
        #make directory if not exist:
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Rows and columns to extract:
        row_1=np.array([1,2,3,4,5])
        row_2=np.array([2,3,4,5,6])
        col_1=np.array([1,2,3,4,5,6,7,8])
        col_2=np.array([1,2,3,4])
        choose_cases=[row_1[:, None],col_1,row_2[:, None],col_2]
        size_case =[2,1.2,2,1.5] # size of each case [2,2,2,2] is the standard case
        create_case(path_book,POPPLER_PATH,directory,choose_cases,size_case ,num_book,pages=[2,-1], LABELLING=False)





    if(mode==3):
        # Select if new training, validation and test sets should be created. If so, specify the sizes.
        new_sets = True
        n_train = 10
        n_val = 10
        n_test = 10
        if new_sets:
            change_format.create_sets(n_train, n_val, n_test,NUMBER_LABEL_PATH)
            PATH_DATA_WASHINGTON_FORMAT_OLD = ".\\data_format_change\\washington"
            PATH_DATA_WASHINGTON_FORMAT_NEW = ".\\Open Source Neural Network\\raw\\washington"
            shutil.rmtree(PATH_DATA_WASHINGTON_FORMAT_NEW)
            shutil.copytree(PATH_DATA_WASHINGTON_FORMAT_OLD, PATH_DATA_WASHINGTON_FORMAT_NEW)
            cwd = os.getcwd()
            # Changing directories might be necessary to fix paths and imports in main_v2.py. However, other problems arise.
            new_cwd = r"./Open Source Neural Network/src"
            print("CWD:", os.getcwd())
            os.chdir(new_cwd)
            print("New CWD:", os.getcwd())
            #htr_main("washington", transform="True")
            os.system("python main.py --source=washington --transform")
            os.system("python train_network.py")
    if mode==4:
        # Select if new prediction test sets should be created. If so, specify the sizes.
        new_sets = True
        n_train = 0
        n_val = 0
        n_test = -1
        path = NOLABEL_PATH + "/DAGBOK  Bjuröklubb Station Jan-Dec 1927"
        if new_sets:
            change_format.create_sets(n_train, n_val, n_test,path)
            PATH_DATA_WASHINGTON_FORMAT_OLD = ".\\data_format_change\\washington"
            PATH_DATA_WASHINGTON_FORMAT_NEW = ".\\Open Source Neural Network\\raw\\washington"
            shutil.rmtree(PATH_DATA_WASHINGTON_FORMAT_NEW)
            shutil.copytree(PATH_DATA_WASHINGTON_FORMAT_OLD, PATH_DATA_WASHINGTON_FORMAT_NEW)
            cwd = os.getcwd()
            # Changing directories might be necessary to fix paths and imports in main_v2.py. However, other problems arise.
            new_cwd = r"./Open Source Neural Network/src"
            print("CWD:", os.getcwd())
            os.chdir(new_cwd)
            print("New CWD:", os.getcwd())
            #htr_main("washington", transform="True")
            os.system("python main.py --source=washington --transform")
            os.system("python predict_network.py")
    if mode==5:
        new_cwd = r"./data_format_change/"
        print("CWD:", os.getcwd())
        os.chdir(new_cwd)
        print("New CWD:", os.getcwd())
        os.system("python create_csv_file.py")


    return 0


if __name__ == "__main__":
    FORMAT_PATHS = "./format_book/"

    PDF_PATHS = {"Valter": r'C:\Users\valte\Desktop\SMHI jobb\data',
                  "Pierre": r'D:\documents\meteo\data',
                  "Juan": r'C:\Users\daeda\Documents\KTH\Project SMHI\Data'}

    POPPLER_PATHS = {"Valter": r'C:\Program Files\poppler-21.11.0\Library\bin',
                     "Pierre": r'C:\Program Files\poppler-21.11.0\Library\bin',
                     "Juan": r'C:\Users\daeda\Documents\KTH\Project SMHI\poppler-21.11.0\Library\bin'}

    USER = "Pierre"
    path_to_books = PDF_PATHS[USER]
    POPPLER_PATH = POPPLER_PATHS[USER]

    name_list = []
    mode = 6
    size_tables= [[9,10],[9,10]]
    for k, name in enumerate(os.listdir(path_to_books)):
        if(name[-4:]==".pdf"):
            #file_name_list.append(os.path.join(path_to_books,name))

            name_list.append([k,name])
    print(name_list)
    format_list = open(os.path.join(FORMAT_PATHS,'table_formats.csv'))
    format_list2 = []
    for row in format_list:
        format_list2.append(row.split(";"))
        #print(row)
    for k, name in name_list[:]:
        print(name)
        for row in format_list2:
            if compare_name(name,row)!=0:
                size_tables= compare_name(name,row)
        print(f"Passing to main(): \nBook number {k} \nName {name} \n")
        print("size",size_tables)
        main(os.path.join(path_to_books,name),POPPLER_PATH,k,mode,size_tables)
        break

