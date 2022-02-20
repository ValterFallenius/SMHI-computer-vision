import os, io
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import matplotlib.pyplot as plt
from glob import glob
import csv
from tkinter import PhotoImage
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def feeder(image):
    # Sends a request to the Google Vision API and returns the predicted text.
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'serviceAccountToken.json'
    client = vision_v1.ImageAnnotatorClient()
    image = vision_v1.types.Image(content=image)
    response = client.document_text_detection(image=image,image_context={"language_hints": ["ko"]})
    docText = response.full_text_annotation.text
    return docText

def partially_correct(label,guess):
    # Determines the partial score of a guess. Guess: "2", label: "20" returns partial_score = 0.5.
    if len(guess)==0:
        if len(label)==0:
            return 1
        return 0
    if len(guess)>len(label):
        return 0
    partial_score = 0
    for letter in guess:
        if letter in label:
            partial_score +=1
    return partial_score/len(label)

def absolut_score(after,label):
    try:
        return 1- ((float(after)-float(label))/float(label))
    except:
        return 0
        #print(f"not integer, after: {after}, label: {label}")

def reformat(string):
    # WARNING: This is very ugly and hardcoded.
    #Converts google string to restricted character string. Example "4, 8" should be "4.8"
    start = string[:]
    accepted = ["1","2","3","4","5","6","7", "8", "9", "0", "-", ".", "x"]
    string = string.replace(" ", "") #remove spaces
    string = string.replace("\n", "") #removes new lines
    string = string.replace("\t", "") #removes tabs
    string = string.replace("S", "5") #replaces S with 5
    string = string.replace(",", ".") #replaces , with .
    string = string.replace("/", "1") #replaces / with 1
    string = string.replace("\\", "1") #replaces \ with 1
    string = string.replace("_", "-") #replaces _ with -
    string = string.replace("Y", "4") #replaces Y with 4
    string = string.replace("y", "4") #replaces y with 4
    string = string.replace("o", "0") #replaces o with 0
    string = string.replace("O", "0") #replaces O with 0
    string = string.replace("I", "1") # etc...
    string = string.replace("i", "1")
    string = string.replace("l", "1")
    string = string.replace("i", "1")
    string = string.replace("!", "1")
    string = string.replace("A", "4")
    string = string.replace("X", "x")
    string = string.replace("Z", "7")
    string = string.replace("z", "7")
    string = string.replace("]", "3")

    if "." in string: # removes . if solo or misplaced "4." becomes "4" and ".3" becomes "3" or "4.1" stays the same
        split = string.split(".")
        temp = ""
        past = False
        for i in split:

            if len(i)>0:
                if past:
                    temp +="."
                temp += i
                past = True
        string = temp
    temp = ""
    #removes all non-wanted letters
    for letter in string:
        if letter in accepted:
            temp += letter
        else:
            print("Removed: ", letter.encode("utf-8"), letter.encode("utf-8").decode("latin1"))
    string = temp
    if len(string)==3 or len(string)==4:
        if "." not in string:
            string = string[:-1]+"."+string[-1]

    if "." in string: #fixes 25.25 to 25.2, allow only 1 decimal place
        splitted = string.split(".")
        if len(splitted[1])>1:
            string = splitted[0] + "." + splitted[1][0]

    try: #if number is larger than 10 and has no decimal points, we add decimal point. Fixes 34 to 3.4, which is more likely than 34 since 34 would have been written as 34.0
        if np.abs(float(string))>10 and len(string)==2:
            string = string[0] + "." + string[1]

    except: pass

    #print("final string = ", string," with starting string: ", start)
    return string

def print_table(labels, befores, afters, partials,abses, IDs):
    #Prints an evaluation table in the terminal.
    spaced = " "*20
    dashed = "-"*65
    print(dashed,"CORRECT",dashed)
    print(f"{spaced[:-5]}label     {spaced[:-6]}before     {spaced[:-5]}after     {spaced[:-7]}partial     {spaced[:-5]}abses     {spaced[:-2]}ID")
    for label,before,after,partial,abs,ID in zip(labels, befores, afters, partials,abses,IDs):
        l = repr(label)
        b = repr(before)
        a = repr(after)
        p = repr(partial)
        ab = repr(abs)
        if str(a)!=str(l):
            continue
        print(f"{spaced[:-len(l)]}{l}     {spaced[:-len(b)]}{b}     {spaced[:-len(a)]}{a}     {spaced[:-len(p)]}{p}     {spaced[:-len(ab)]}{ab}     {spaced[:-len(ID)]}{ID}")
    print(dashed,"INCORRECT",dashed)
    print(f"{spaced[:-5]}label     {spaced[:-6]}before     {spaced[:-5]}after     {spaced[:-7]}partial     {spaced[:-5]}abses     {spaced[:-2]}ID")
    for label,before,after,partial,abs,ID in zip(labels, befores, afters, partials,abses,IDs):
        l = repr(label)
        b = repr(before)
        a = repr(after)
        p = repr(partial)
        ab = repr(abs)
        if str(a)==str(l):
            continue
        print(f"{spaced[:-len(l)]}{l}     {spaced[:-len(b)]}{b}     {spaced[:-len(a)]}{a}     {spaced[:-len(p)]}{p}     {spaced[:-len(ab)]}{ab}     {spaced[:-len(ID)]}{ID}")

def main():
    
    data_path = r"C:\Users\valte\Desktop\SMHI jobb\project_meteo\preprocessing\label"
    pngs = data_path + "\*.png"
    sample_size = 30
    print(pngs)
    img_files = glob(pngs)
    correct = 0
    incorrect = 0
    partials = []
    labels = []
    google_before = []
    google_after = []
    abses = []
    IDs = []
    count = 0
    for i,file_name in enumerate(img_files):
        if i<837: continue

        assert ".png" in file_name

        file_path = os.path.join(data_path, file_name)
        name = file_name.replace(".png", "").split("label")[-1]
        name = name[1:]
        splitted = name.split("_")
        if len(splitted) == 1:
            ID, label = splitted[0], ""

        elif len(splitted) == 2:
            ID, label = splitted
        if label == "": continue
        label = label.replace("+", "") #remove + signs for correct evaluation
        #print(f"ID {ID}, label {label}")
        with io.open(file_path, "rb") as image_file:
            content = image_file.read()
        IDs.append(ID)
        labels.append(label)
        google_text = feeder(content) # Get image recognized
        google_before.append(google_text)
        google_text_processed = reformat(google_text) # Get image reformatted to allowed characters.
        google_after.append(google_text_processed)
        abs = absolut_score(google_text_processed,label)
        abses.append(abs)
        # ---- Evaluation -----
        if google_text_processed == label:
            correct +=1
            partials.append(1)
        else:
            incorrect +=1
            partial_score = partially_correct(label,google_text_processed)
            partials.append(partial_score)
        print(f"For image {ID} we get google text {repr(google_text)} when true label is {repr(label)}")

        count+=1
        if count>sample_size: break
        #img = mpimg.imread(file_path)
        #imgplot = plt.imshow(img, cmap = "gray")
        #plt.show()
        # ---- Evaluation -----

    print_table(labels, google_before, google_after, partials,abses,IDs)
    print(f"We got: \n Accuracy: {correct/(correct+incorrect)}  \n Correct: {correct} \n Incorrect: {incorrect} \n Average partial score of incorrect samples: {np.mean(partials)}")

    print("FINAL: ", i)



if __name__ == "__main__":
    main()
