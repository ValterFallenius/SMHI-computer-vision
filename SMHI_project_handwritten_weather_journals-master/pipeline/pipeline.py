import numpy as np
from pdf2image import*
import skimage.morphology
from skimage.filters import threshold_otsu,threshold_mean,threshold_li,threshold_triangle,threshold_isodata,threshold_yen
from pdf2image import *
import matplotlib.pyplot as plt
import skimage.exposure
from skimage.filters import threshold_minimum,threshold_local
from scipy.ndimage import label
import gc
import copy as CP
from scipy.ndimage import rotate
import csv
from matplotlib import patches


def convert_format(list):
    format = [10,10]
    new_list = np.zeros((format[0],format[1],4),dtype =np.int)
    for i,line in enumerate(list,0):
        for j,v in enumerate(line,0):
            new_list[i,j,:] = np.array([v[0]-v[2]//2,v[1]-v[3]//2,v[0]+v[2]//2,v[1]+v[3]//2],dtype=np.int)

    test_im=np.zeros((2000,2000))
    for i,line in enumerate(new_list,0):
        for j,v in enumerate(line,0):
            test_im[v[0],v[1]]=4
            test_im[v[2],v[3]]=1
    # plt.figure()
    # plt.imshow(test_im)
    # plt.show()
    return np.array(new_list)







def remove_col(l_size,size_tables,list_pos,n_table =  0,nb_remove = 1):
    #print(f"table {n_table} list_pos shape before {np.array(list_pos[n_table][:]).shape}")
    #if l_size[n_table][1] == size_tables[n_table][1]+nb_remove:
    if True:

        copy = np.array(list_pos[n_table][:]).reshape((l_size[n_table][0],l_size[n_table][1],4))

        copy2 =  copy[:,nb_remove:,:].reshape(-1,4)


        l_size[n_table][1] = l_size[n_table][1]-nb_remove
        list_pos[n_table] = copy2
        #print(f"table {n_table} list_pos shape after {np.array(list_pos[n_table][:]).shape}")
    #     for i in range(l_size[n_table][0]*nb_remove):
    #         list_pos[n_table].remove(copy[i*l_size[n_table][1]])
    #         l_size[n_table][1] = size_tables[n_table][1]

    return list_pos,l_size

def remove_line(l_size,size_tables,list_pos,n_table =  0,nb_remove = 1):
    #if l_size[n_table][0] == size_tables[n_table][0]+nb_remove:
    if True:
        copy = np.array(list_pos[n_table][:]).reshape((l_size[n_table][0],l_size[n_table][1],4))
        copy2 =  copy[nb_remove:,:,:].reshape(-1,4)
        l_size[n_table][0] = l_size[n_table][0] - nb_remove
        list_pos[n_table] = copy2
        # list_pos[n_table] = list_pos[n_table][nb_remove*l_size[n_table][1]:]
        # l_size[n_table][0] = size_tables[n_table][0]
    return list_pos,l_size
def add_edge(proj):
    """Add the vertical or horizontal edges of a table
        Parameters
        ----------
        proj: array 1D
            horizontal or vertical projection of a binary table
        Returns
        -------
        proj : array 1D
            horizontal or vertical projection of a binary table, edge add with the max value
        """
    edge=False #edge is equal to false if we have not yet scanned the first element of the table
    for k in range(1,len(proj)-1):
        if(edge==False and proj[k]>0 and proj[k-1]<1): # if we go from no tables to tables elements
            edge=True # we detected edge
            proj[k]=np.max(proj) #if we go from elements to no more elements then we leave the table and we can add an edge
        if(edge==True and proj[k]>0 and proj[k+1]<1): # we add final edge
            proj[k]=np.max(proj)
    return proj


def simply_order(tot_p):
    """simplify the position of tables to avoid random position.
        Parameters
        ----------
        tot_p : list
            list of position of every tables
        Returns
        -------
        tot_p : list
            list of position of every tables
            this list is ordered
        """
    equal1=0
    equal2=0
    PRECISION  = 100 #if there is rotation, an table can end up on top of another in some case, this value takes this uncertainty into account
    for i in range(len(tot_p)-1):
        equal1=tot_p[i][0]
        equal2=tot_p[i][1]
        for j in range(i,len(tot_p)):
            if (equal1+PRECISION >tot_p[j][0]) and (tot_p[j][0]> equal1-PRECISION):
                tot_p[j][0]=equal1
            if (equal2+PRECISION >tot_p[j][1]) and (tot_p[j][1]> equal2-PRECISION):
                tot_p[j][1]=equal2
    return tot_p

def get_position(proj_x):
    """determines the position of the maximums of a projection of an array (on x or y)
        therefore determine the position of the rows of a table
        Parameters
        ----------
        proj_x: array 1D
            horizontal or vertical projection of a binary table
        Returns
        -------
        x_pos : list of int
            list of position of the middle between 2 lines.
        x_len : list of int
            list of distance between line
        """
    len_x=0
    MIN_VALUE = 20 # minimum distance to be considered as 2 different lines
    not_in=True # if not in the tab yet
    x_pos=[]
    x_len =[]
    for k in range(len(proj_x)):
        if(proj_x[k]==0 and not_in==False): # if we are inside a table but not in a line
            len_x+=1
        if(proj_x[k]==1 and proj_x[k-1]==0): # if we are in a line
            not_in=False
            if(len_x>MIN_VALUE): # if the distance between 2 lines in not too small
                x_pos.append(k-len_x//2) # x_pos is te middle between 2 line
                x_len.append(len_x)
                len_x=0
    return x_pos,x_len


def sort_insertion(L,LL):
    """sort tables according to LL
        Parameters
        ----------
        L : list
            same len than LL
        LL : list
            contains elements that can be sorted
        Returns
        -------
        L : list
            contains L sorted elements
        """
    L2=np.copy(LL)
    N = len(L)
    for n in range(1,N):
        cle= L[n]
        cle2 = L2[n]
        j = n-1
        while j>=0 and L2[j] > cle2:
            L2[j+1] = L2[j] # decalage
            L[j+1] = L[j]
            j = j-1
        L2[j+1] = cle2
        L[j+1] = cle
    return L
# get position for every tab for every element of each tab
#input binary of every line of the image
def get_pos(binary_tables,size_tables, only_top_table=False, original_image = None):
    """get position and size for every cases in every element of each tab
        Parameters
        ----------
        binary_tables : array 2D
            binary image of an empty one-page table
        only_top_table : boolean
            if True return only 2 first tables
        Returns
        -------
        list_pos3 : list
            each element of this list is a list containing the informations of each box of a table.
            The format of the information is:
            [vertical position [int], horizontal position [int], width [int], height [int]])
            the position is defined in relation to the position on the whole page and not in relation to the relative position of the table
        l_size3 : list
        list of size of tables (same order than list_pos3
        """
    NB_TABLES = 5 # total expected number of tables
    MIN_NB_PIXELS = 400 # minimum number of pixels that an array must have to be considered as such
    L_SENSIBILITY = [1.1,1.2,1.4,1.6,1.8,2,2.2,2.4,2.6,2.8,3]# different sensitivities tested to obtain the right dimension of tables, sensitivity of 1 means very little sensitive (detected few lines) and >1 higher sensitivity (detected more lines)
    GOOD_DIMS =  size_tables # expected table dimensions


    l_size3=[[] for k in range(NB_TABLES)]
    list_pos3=[[] for k in range(NB_TABLES)]
    binary_tables  = skimage.morphology.erosion(binary_tables, skimage.morphology.square(10))# increase size of line
    a = label(~binary_tables) # inverse image and separate non connected objects
    l_tab = [] # l_tab list to contain list of tab
    for k in range(1,a[1]+1):# for every objects detected
        object= np.where(a[0]==k)
        if(len(object[0])>MIN_NB_PIXELS): # if object are not to small in term of pixel
            tab=np.ones(a[0].shape,dtype=np.int16) # create a white image (dtype = int16 in order to reduce memory place)
            tab[object]=0 # add black element
            l_tab.append(tab) # add the image with only one object in l_tab
    for sensibility in L_SENSIBILITY:
        gc.collect()
        list_pos=[] # list position of element for one tab
        l_size=[] # size of a tab
        order =[]
        list_pos_tab=[]
        for kk in range(len(l_tab)): # for every object
            tab=1-l_tab[kk] # invere the image
            proj_x=np.sum(tab,1) # projection_1
            proj_y=np.sum(tab,0) # projection_2
            # sometime edge of tab don't appear, this code can create edge in this case:
            proj_x =  add_edge(proj_x)
            proj_y = add_edge(proj_y)
            proj_x = proj_x > int(np.max(proj_x)/sensibility) # we get binaries projection
            proj_y = proj_y > int(np.max(proj_y)/sensibility)
            x_pos,x_len = get_position(proj_x) # we get position for projection
            y_pos,y_len = get_position(proj_y)
            tot  = []
            # we combine data from projection to create data for all te tab
            for i in range(len(x_pos)):
                for j in range(len(y_pos)):
                    tot.append([x_pos[i],y_pos[j],x_len[i],y_len[j]])
            if(len(tot)>1): # if tab is not only on case
                list_pos.append(tot)
                list_pos_tab.append([tot[0][0],tot[0][1]])
                #order.append(tot[0][0]*20000+tot[0][1])
                l_size.append([len(x_pos),len(y_pos)])
            # for k in range(len(tot)):
            #     tab[tot[k][0],tot[k][1]]=5
        list_pos_tab = simply_order(list_pos_tab)
        order=[]
        for k in range(len(list_pos_tab)):
            order.append(3000*list_pos_tab[k][0]+list_pos_tab[k][1])
        list_pos=sort_insertion(list_pos,order)
        l_size=sort_insertion(l_size,order)
        #print("real_size:",l_size)
        #print("wanted: ", GOOD_DIMS)
        if len(l_size)>0:
            list_pos,l_size = remove_col(l_size,size_tables,list_pos,n_table =  0,nb_remove = 1) #Remove leading column
            list_pos,l_size = remove_line(l_size,size_tables,list_pos,n_table =  0,nb_remove = 1) #Remove top row
        if len(l_size)>1:
            list_pos,l_size = remove_line(l_size,size_tables,list_pos,n_table =  1,nb_remove = 2) #Remove top two rows
        if len(l_size)>3:
            if l_size[3][1] == GOOD_DIMS[3][1]+1:
                list_pos,l_size = remove_col(l_size,size_tables,list_pos,n_table =  3,nb_remove = 1)
            if l_size[3][0] == GOOD_DIMS[3][0]+1:
                list_pos,l_size = remove_line(l_size,size_tables,list_pos,n_table =  3,nb_remove = 1)
        if len(l_size)>4:
            if l_size[4][0] == GOOD_DIMS[4][0]+1:
                list_pos,l_size = remove_line(l_size,size_tables,list_pos,n_table =  4,nb_remove = 1)

        #print("after remove:",l_size)




        if(len(l_size)>len(GOOD_DIMS)):

            #print("hej len(l_size)>len(GOOD_DIMS)")
            #debug_plotter(original_image,list_pos,l_size, printer = False)
            list_pos2=[]
            l_size2 = []
            for k,dim in enumerate(l_size):
                if dim in GOOD_DIMS:
                    #ACCEPTED_DIMS.remove(dim) # discard duplicates
                    list_pos2.append(list_pos[k])
                    l_size2.append(dim)
            list_pos2=list_pos2[:len(GOOD_DIMS)]
            l_size2=l_size2[:len(GOOD_DIMS)]
        else:
            list_pos2=list_pos
            l_size2 = l_size

        # save only correct dimension tables in list_pos3 and l_size3
        for ii in range(len(l_size2)):
            if((l_size2[ii]==GOOD_DIMS[ii]) and l_size3[ii]==[]):
                l_size3[ii]=l_size2[ii]
                list_pos3[ii]=list_pos2[ii]

        # If we only care about table 0 and 1 (which we do):
        if only_top_table:
            if l_size3[0] == size_tables[0] and l_size3[1] == size_tables[1]:
                print("Success! final size:",l_size3)


                if original_image is not None:
                    debug_plotter(original_image,list_pos3,l_size3, printer = False)
                else:
                    debug_plotter(binary_tables,list_pos3,l_size3, printer = False)
                return list_pos3,l_size3

        if(l_size3 == GOOD_DIMS):
            return list_pos3,l_size3
    return list_pos3,l_size3

def corr_rotate(image, middle = None):
    """rotate the image if necessary to align with the horizontal
        Parameters
        ----------
       image : array 2D
            grey image of a page
        Returns
        -------
        im : array 2D (bigger)
            image but alligned and with more white margins on the sides and in the middle

        """
    MARGIN=30#margin size
    image=np.max(image)-image
    image=image.astype(np.float32)
    thresh=threshold_otsu(image)
    binary = image> thresh
    shape_im=image.shape
    if middle is not None:
        MIDDLE = middle
    else:
        MIDDLE = shape_im[1]//2 #Not good enough, needs improvement.
    im1=image[:,:MIDDLE]
    im2=image[:,MIDDLE:]
    bin1=binary[:shape_im[0]//4,:shape_im[1]//2]
    bin2=binary[:shape_im[0]//4,shape_im[1]//2:]
    shape_im1=im1.shape
    shape_im2=im2.shape
    angles=[(k-10)/4 for k in range(20)]
    best_1=0
    best_2=0
    maxx1=0
    for angle in angles:
        rotated=rotate(bin1,angle)
        maxx2=np.std(np.sum(rotated,1))
        if (maxx2>=maxx1):
            maxx1=maxx2
            best_1=angle
    maxx1=0
    for angle in angles:
        rotated=rotate(bin2,angle)
        maxx2=np.max(np.sum(rotated,1))
        if (maxx2>=maxx1):
            maxx1=maxx2
            best_2=angle
    im1=rotate(im1,best_1)[:shape_im1[0],-shape_im1[1]:]
    im2=rotate(im2,best_2)[:shape_im2[0],-shape_im2[1]:]
    shape_im1=im1.shape
    shape_im2=im2.shape
    im1_middle_marge = np.ones((shape_im1[0]+MARGIN*2,shape_im1[1]+MARGIN*2))*np.max(image)
    im1_middle_marge[MARGIN:-MARGIN,MARGIN:-MARGIN] = im1
    im2_middle_marge = np.ones((shape_im2[0]+MARGIN*2,shape_im2[1]+MARGIN*2))*np.max(image)
    im2_middle_marge[MARGIN:-MARGIN,MARGIN:-MARGIN] = im2
    im=np.concatenate((im1,im2),1)
    im=np.max(im)-im
    return im

def debug_plotter(image_filter,pos_list,size_list, printer = False):
    """plot image for debug
        Parameters
        ----------
        image_filter : array 2D
            grey image of a page without background noise
        pos_list : list
            each element of this list is a list containing the inflormations of each box of a table.
            The format of the information is:
            [vertical position [int], horizontal position [int], width [int], height [int]])
            the position is defined in relation to the position on the whole page and not in relation to the relative position of the table
        size_list : list
            list of the size of tables
            """
    fig, axs = plt.subplots(1,1)
    axs.imshow(image_filter)
    axs.set_title("image_filtered")


    #for num_figure in range(len(pos_list)):
    for num_figure in range(len(pos_list)):
        try:
            print("a ",size_list[num_figure][0])
            print("b ",size_list[num_figure][1])
            print("pos_list", len(pos_list[num_figure]))
        except IndexError:
            print("Raised index error, likely due to empty list of tables. Skipping these...")
            continue
        for k in range(size_list[num_figure][0]*size_list[num_figure][1]):
            if printer ==True:

                print("Size: ",size_list)
                print("positions length: ", len(pos_list))

                print("num_fig: ", num_figure)
                print("k: ", k)
                print("positions[numfig] length: ", len(pos_list[num_figure]))

            position = pos_list[num_figure][k]

            rect = patches.Rectangle((int(position[1]-position[3]/2),int(position[0]-position[2]/2)),position[3], position[2], edgecolor='r', facecolor="none")
            axs.add_patch(rect)

    plt.show()

if __name__ == "__main__":
    all_pdfs = r"C:/Users/valte/Desktop/Python/SMHI-computer-vision/ScannedObsCorrected/"
    table_formats = r"C:/Users/valte/Desktop/SMHI jobb/All data/ScannedObs/table_formats.csv"
    with open(table_formats, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for i,csv_line in enumerate(datareader):
            if i==0: continue
            year, station, measure_times, rows, table1_cols, table2_cols = csv_line
            pdf_path = os.path.join(all_pdfs,station.upper(),station+"_"+year+"_mod.pdf")

    '''with open('test.npy', 'rb') as f:
        line = np.load(f)
    print(line.shape)
    plt.figure()
    plt.subplot(221)
    plt.title("line")
    thresh=threshold_otsu(line)
    binary_tables =line > thresh
    result = get_pos(binary_tables)'''
