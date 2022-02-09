import numpy as np
import os
import sys
import subprocess
sys.path.insert(1, './pipeline/')
sys.path.append("./Open Source Neural Network/src")
from  create_data import create_case
import data_format_change.change_format
from main_v2 import main as htr_main




def main(path_book,POPPLER_PATH,num_book=0,mode=3):
    '''
    Parameters
    ----------
    path_book : str
        The path to the PDF-book.
    POPPLER_PATH : str
        Local path to poppler
    num_book : int
        Position of book in folder
    mode : int
        Integer that decides what the main function does:

        mode == 0: Label data with numbers with "769.5", "+15.0" etc.
        mode == 1: Label data wind with "NW", "S" etc.
        mode == 2: Train the neural network.
        mode == 3: Transform PDF to JPG for a book.
        mode == 4: Transform the data to a hdf5 file.
    '''

    NUMBER_LABEL_PATH = "./pipeline/label/"
    WIND_LABEL_PATH = "./pipeline/wind/"
    NOLABEL_PATH = "./pipeline/nolabel/"


    if mode==0:
        # Rows and columns to label of table 1 and table 2.
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
    if(mode==2):
        # Select if new training, validation and test sets should be created. If so, specify the sizes.
        new_sets = True
        n_train = 50
        n_val = 40
        n_test = 30
        if new_sets:
            data_format_change.change_format.create_sets(n_train, n_val, n_test)
        # Code to train the network
        # ------ here -------------
    if mode==3:
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

    if mode==4:
        cwd = os.getcwd()
        htr_main("washington", transform="True")



    return 0


if __name__ == "__main__":

    PDF_PATHS = {"Valter": r'C:\Users\valte\Desktop\SMHI jobb\data',
                  "Pierre": r'D:\documents\meteo\data',
                  "Juan": r'C:\Users\daeda\Documents\KTH\Project SMHI\Data'}

    POPPLER_PATHS = {"Valter": r'C:\Program Files\poppler-21.11.0\Library\bin',
                     "Pierre": r'C:\Program Files\poppler-21.11.0\Library\bin',
                     "Juan": r'C:\Users\daeda\Documents\KTH\Project SMHI\poppler-21.11.0\Library\bin'}

    USER = "Juan"
    path_to_books = PDF_PATHS[USER]
    POPPLER_PATH = POPPLER_PATHS[USER]

    name_list = []
    mode = 4

    for k, name in enumerate(os.listdir(path_to_books)):
        if(name[-4:]==".pdf"):
            #file_name_list.append(os.path.join(path_to_books,name))

            name_list.append([k,name])

    for k, name in name_list:
        print(f"Passing to main(): \nBook number {k} \nName {name} \n")
        main(os.path.join(path_to_books,name),POPPLER_PATH,k,mode)
        break