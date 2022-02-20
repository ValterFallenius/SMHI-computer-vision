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


def main():

    data_path = r"C:\Users\valte\Desktop\SMHI jobb\project_meteo\preprocessing\label"
    pngs = data_path + "\*.png"
    sample_size = 30
    img_files = glob(pngs)
    chars = {".":0, "-":0, "+":0, "x":0}
    for i in range(10):
        chars[str(i)]=0
    for i,file_name in enumerate(img_files):


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
        for char in label:
            if char ==",":
                print(ID)
            if char in chars.keys():
                chars[char] += 1
            else:
                chars[char] = 1
    print(chars)

    # ---------- plot histogram ---------------
    fig, ax = plt.subplots(1,1)
    ax.bar([str(i) for i in chars.keys()], chars.values())
    fig.suptitle("Spread of dataset")
    ax.set_ylabel("Amount")
    ax.legend()
    plt.show()
    # ---------- plot histogram ---------------


if __name__ == "__main__":
    main()
