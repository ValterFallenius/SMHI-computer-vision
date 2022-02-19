import numpy as np
import os
import shutil
import glob
import random

def new_label(label):
    new=''
    for s in label:
        if(s=='-'):
            s='s_mi'
        if(s=='.'):
            s='s_pt'
        if(s==' '):
            s='n'
        new+=s+'-'
    return new[:-1]

def convert(name):
    name = name[:-4]
    new_name =''
    k=0
    while(name[k]!='_'):
        new_name+=name[k]
        k+=1
    new_name+='-0'
    if(len(name[k:])>1):
        label = new_label(name[k+1:])
    else:
        label = 'n'
    label+='-n'
    return new_name+'.png',label

def create_sets(n_train: int, n_val: int, n_test: int,path = '.\pipeline\label') -> None:
    """Creates new train, validation, test and ground truth text files for the HTR network.
    args:
        n_train     int      -- size of training set
        n_val       int      -- size of validation set
        n_test      int      -- size of test set
        path        string   -- data path
    """
    #path = '../pipeline/label'
    #path = './validation'
    # Path to label directory (where the pictures are located).
    # Path to directory where pictures with new labels will be located. Delete old files each time new sets are created.
    path2 =  './data_format_change/washington/data/line_images_normalized'
    for file in os.listdir(path2):
        os.remove(os.path.join(path2, file))
    # Paths to ground truths and sets.
    path3 ='./data_format_change/washington/ground_truth/'
    path4 ='./data_format_change/washington/sets/cv1'

    # List all files in the label directory.
    files = os.listdir(path)
    # Create text files to write names of pictures in each set.
    train = open(os.path.join(path4, "train.txt"),"w")
    test = open(os.path.join(path4,"test.txt"),"w")
    validation = open(os.path.join(path4,"valid.txt"),"w")
    # Create the sets randomly with the specified size. Avoid overlap.
    random.shuffle(files)
    train_files = files[:n_train]
    validation_files = files[n_train : n_train + n_val]
    if n_test == -1:
        test_files = files
    else:
        test_files = files[n_train + n_val : n_train + n_val + n_test]
    files = train_files + validation_files + test_files
    # Write the text files for ground truth, train, validation and test sets.
    with open(os.path.join(path3,"transcription.txt"), "w") as text_file:
        for idx, name in enumerate(files[0:]):
            if(name!="temp.png"):
                #random = np.random.randint(0,6)
                # Get the new name and label of the file.
                new_name,label  = convert(name)
                list_file = glob.glob(os.path.join(path2,new_name))
                for file in list_file:
                    os.remove(file)
                # Copy the picture to the directory with the new names.
                shutil.copyfile(os.path.join(path,name), os.path.join(path2,new_name))
                # Write the ground truth.
                text_file.write(new_name[0:-4] +' '+ label + "\n")
                # Write the train, validation and test text files.
                if n_test==-1:
                    test.write(new_name[0:-4] + "\n")
                else:
                    if idx < n_train:
                        train.write(new_name[0:-4]+ "\n")
                    elif idx < n_train + n_val:
                        validation.write(new_name[0:-4] + "\n")
                    elif idx < n_train + n_val + n_test:
                        test.write(new_name[0:-4] + "\n")
                #print(new_name)
                #if(random in [0,1,2,3]):
                #    train.write(new_name[0:-4]+ "\n")
                #if(random in [0,1,2,3,4,5]):
                #    test.write(new_name[0:-4]+ "\n")
                #if(random in [5]):
                #    validation.write(new_name[0:-4]+ "\n")

    print("New train, validation and test sets have been created.")
    train.close()
    test.close()
    validation.close()
