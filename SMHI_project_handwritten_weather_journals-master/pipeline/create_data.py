#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from pdf2image import convert_from_path, pdfinfo_from_path
import skimage.morphology
from skimage.filters import threshold_otsu,threshold_mean,threshold_li,threshold_triangle,threshold_isodata,threshold_yen
import gc
import matplotlib.pyplot as plt
import skimage.exposure
from skimage.filters import threshold_minimum,threshold_local

import os
from cv2 import imencode
from tkinter import *
from tkinter import ttk
import numpy as np
import imageio
import os
import glob
import datetime
# ----- LOCAL MODULES ----------
from pipeline import *
from ID import encode, decode
# ----- LOCAL MODULES ----------

def get_date(start_date, page_number, initial_page=2):
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%y")
    end_date = start_date + datetime.timedelta(days=page_number - initial_page)
    return end_date

def save_data(entry1,key_name,root,path_label):
    x1 = entry1.get() # get the input (so the value of the case)
    name=key_name + str(x1)+".png"
    name_all=key_name+"*"+".png"
    list_file = glob.glob(os.path.join(path_label,name_all))
    for file in list_file:
        os.remove(file)
    os.rename(os.path.join(path_label,"temp.png"),os.path.join(path_label, name))
    root.destroy() # destroy the windows

def create_case(filename,poppler_path,path_label,size_tables,size_case,compt_book,pages=[0,-1],LABELLING = True, ONLY_POSITION =False, skip = {"tables": [], "rows": [[],[],[],[],[]] , "cols": [[],[],[],[],[]] }):
    page_counter = 0
    success_counter = [0,0,0,0,0]

    if "vaderbod" in filename: #where to split the image, hardcoded!!!!!!!!!!
        MIDDLE = 1295
    else: MIDDLE = None
    info = pdfinfo_from_path(filename, userpw=None, poppler_path=poppler_path)
    maxPages = info["Pages"]
    if pages[1]==-1 or pages[1]>maxPages:
        pages[1]=maxPages
    if pages[0]>=maxPages:
        pages[0]=0
    only_page = np.random.randint(365)
    for pagenumber in range(pages[0],pages[1]):
        if pagenumber != only_page:
            continue
        print(f"filename: {filename}, page: {pagenumber}")
        images = convert_from_path(filename,poppler_path=poppler_path,first_page=pagenumber,last_page=pagenumber+1)

        image = np.array(images[0],dtype=np.int16)# get a array of the page

        #plt.imshow(image)
        #plt.show()
        image=np.sum(image,2)# convert to black and white

        ##remove background
        image_background = skimage.morphology.dilation(image, skimage.morphology.disk(6)) #dilation remove black letter of the page
        image_background = skimage.morphology.erosion(image_background, skimage.morphology.disk(6)) # erosion increase background but not black letter
        image_filter=image-image_background #remove background
        image_filter = image_filter-np.min(image_filter) #normalize min=0
        ## correction rotation
        image_filter=corr_rotate(image_filter, middle = MIDDLE) # correction rotation image
        og_image = np.copy(image_filter)
        ##get lines of the table
        mask_x = np.ones((1,36)) #mask for horizontal lines
        mask_y =np.ones((36,1)) #mask for vertical lines
        ligne_x  = skimage.morphology.dilation(image_filter, mask_x)
        ligne_x  = skimage.morphology.erosion(ligne_x, np.ones((1,40)))
        ligne_y = skimage.morphology.dilation(image_filter, mask_y)
        ligne_y  = skimage.morphology.erosion(ligne_y, np.ones((40,1)))
        ligne = ligne_x+ligne_y
        image_background = skimage.morphology.dilation(ligne, skimage.morphology.disk(3))
        image_background = skimage.morphology.erosion(image_background, skimage.morphology.disk(3))
        ligne_filter=ligne-image_background
        ligne_filter = ligne_filter-np.min(ligne_filter)
        thresh=threshold_otsu(ligne_filter)
        binary_line =ligne_filter > thresh
        ## get image without lines and background
        fin = image_filter-ligne_filter
        fin =fin-np.min(fin)
        p2, p98 = np.percentile(fin, (1, 99))
        fin = skimage.exposure.rescale_intensity(fin,in_range=(p2, p98)) #increase saturation
        fin-=np.min(fin)
        fin=(255*fin/np.max(fin)).astype(np.uint8) #normalize between 0 to 255
        gc.collect()
        ##get position of cases for every tables
        l_position,l_size = get_pos(binary_line,size_tables, only_top_table = True, original_image = og_image) #only pop first two tables
        table1_pos,table2_pos = l_position[0:2] # only care about 2 first tables
        table1_size,table2_size = l_size[0:2]
        #print("size----------------",l_size, size_tables)
        page_counter += 1
        for table_n, table_size in enumerate(l_size):
            if table_n in skip["tables"]:
                continue
            table_n_pos = l_position[table_n]

            if table_size == size_tables[table_n]:
                success_counter[table_n] += 1

                table_pos = np.array(table_n_pos).reshape((table_size[0],table_size[1],4))

                if ONLY_POSITION == False:


                    for row in range(table_size[0]):
                        if row in skip["rows"][table_n]:
                            continue
                        for col in range(table_size[1]):
                            if col in skip["cols"][table_n]:
                                continue
                            position = table_pos[row,col]
                            number = fin[int(position[0]-position[2]/size_case[0]):int(position[0]+position[2]/size_case[1]),int(position[1]-position[3]/size_case[2]):int(position[1]+position[3]/size_case[3])]
                            key_name=encode(compt_book,pagenumber,row,col,table_n) + "_"
                            #print(key_name)
                            im=number

                            if LABELLING == False: #if we are not labelling the image
                                image_path = os.path.join(path_label,key_name+"nolabel"+".png")

                                if os.path.exists(image_path):
                                    continue
                                imageio.imwrite(image_path,im.astype(np.uint8))

                                continue #Save image and continue

                            imageio.imwrite(os.path.join(path_label,"temp.png"),im.astype(np.uint8)) # save the image in a temporary file
                            root = Tk()
                            root.geometry('300x300+0+0') # position and size of the windows
                            canvas = Canvas(root, width = 300, height = 300)
                            canvas.pack()
                            img = PhotoImage(file=os.path.join(path_label,"temp.png")) # open the temporary image
                            canvas.create_image(20,20, anchor=NW, image=img) # show the image
                            entry1 = Entry(root) # get input
                            canvas.create_window(100, 200, window=entry1) # position of the input button
                            button1 = Button(text='put value', command=lambda: save_data(entry1,key_name,root,path_label)) # call save_data
                            canvas.create_window(100, 250, window=button1) # position of the button "put_value"

                            mainloop()
                    #plt.imshow(im)
                    #plt.show()
            else:
                print(f"Size for table {table_n} does not match wanted size: {table_size} vs. {size_tables[table_n]}")
                #save to CSV to correct manually later.
    return page_counter, success_counter
