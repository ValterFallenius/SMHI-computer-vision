import numpy as np
import os
import shutil
import glob
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

print(os.path.abspath(__file__))
path = '../pipeline/label'
path = './validation'
path = '../pipeline/label'
path2=  './washington/data/line_images_normalized'
path3 ='./washington/ground_truth/'
path4 ='./washington/sets/cv1'

list = os.listdir(path)
train = open(os.path.join(path4,"train.txt"),"w")
test = open(os.path.join(path4,"test.txt"),"w")
validation = open(os.path.join(path4,"valid.txt"),"w")
with open(os.path.join(path3,"transcription.txt"), "w") as text_file:
    for name in list[0:]:
        if(name!="temp.png"):
            random = np.random.randint(0,6)
            new_name,label  = convert(name)
            list_file = glob.glob(os.path.join(path2,new_name))
            for file in list_file:
                os.remove(file)
            shutil.copyfile(os.path.join(path,name), os.path.join(path2,new_name))

            text_file.write(new_name[0:-4] +' '+ label + "\n")
            print(new_name)
            if(random in [0,1,2,3]):
                train.write(new_name[0:-4]+ "\n")
            if(random in [0,1,2,3,4,5]):
                test.write(new_name[0:-4]+ "\n")
            if(random in [5]):
                validation.write(new_name[0:-4]+ "\n")
train.close()
test.close()
validation.close()
