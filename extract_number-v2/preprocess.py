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

def simply_order(tot_p):
    """sort tables from top to bottom and left to right
        Parameters
        ----------
        tot_p : list
            each element of the list contains the position and size of each cell of a table
        Returns
        -------
        tot_p : list
            each element of the list contains the position and size of each cell of a table,
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
def get_pos(binary1, only_top_table=False):
    """get position and size for every cases in every element of each tab
        Parameters
        ----------
        binary1 : array 2D
            binary image of an empty one-page table
        only_top_table : boolean
            contains elements that can be sorted
        Returns
        -------
        list_pos3 : list
            each element of this list is a list containing the inflormations of each box of a table.
            The format of the information is:
            [vertical position [int], horizontal position [int], width [int], height [int]])
            the position is defined in relation to the position on the whole page and not in relation to the relative position of the table
        l_size3 : list
        list of size of tables (same order than list_pos3
        """
    l_size3=[[] for k in range(5)]
    list_pos3=[[] for k in range(5)]
    binary1  = skimage.morphology.erosion(binary1, skimage.morphology.square(10))# increase size of line
    a = label(~binary1) # inverse image and separate non connected objects
    l_tab = [] # l_tab list to contain list of tab
    for k in range(1,a[1]+1):# for every objects detected
        object= np.where(a[0]==k)
        if(len(object[0])>400): # if object are not to small in term of pixel
            tab=np.ones(a[0].shape,dtype=np.int16) # create a white image (dtype = int16 in order to reduce memory place)
            tab[object]=0 # add black element
            l_tab.append(tab) # add the image with only one object in l_tab
    l_sensibility = [1.1,1.2,1.4,1.6,1.8,2,2.2,2.4,2.6,2.8,3]
    for sensibility in l_sensibility:
        gc.collect()
        list_pos=[] # list position of element for one tab
        l_size=[] # size of a tab
        order =[]
        list_pos_tab=[]
        for kk in range(len(l_tab)): # for every object
            tab=1-l_tab[kk] # invere the image
            proj_x=np.sum(tab,1) # projection_1
            proj_y=np.sum(tab,0) # projection_2
            # sometime edge of tab don't appear, this code can create edge in this case
            bord=False
            for k in range(1,len(proj_x)-1):
                if(bord==False and proj_x[k]>0 and proj_x[k-1]<1): # if we not yet in the tab but we have big evolution
                    bord=True # we detected edge
                    proj_x[k]=np.max(proj_x) #we add edge to the projection
                if(bord==True and proj_x[k]>0 and proj_x[k+1]<1): # we add final edge
                    proj_x[k]=np.max(proj_x)
            bord=False
            for k in range(1,len(proj_y)-1): # same for the other projection
                if(bord==False and proj_y[k]>0 and proj_y[k-1]<1):
                    bord=True
                    proj_y[k]=np.max(proj_y)
                if(bord==True and proj_y[k]>0 and proj_y[k+1]<1):
                    proj_y[k]=np.max(proj_y)
            proj_x = proj_x > int(np.max(proj_x)/sensibility) # we binaries projection
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
                l_size.append([len(x_pos),len(y_pos)])
            # for k in range(len(tot)):
            #     tab[tot[k][0],tot[k][1]]=5
        list_pos_tab = simply_order(list_pos_tab)
        order=[]
        for k in range(len(list_pos_tab)):
            order.append(3000*list_pos_tab[k][0]+list_pos_tab[k][1])
        list_pos=sort_insertion(list_pos,order)
        l_size=sort_insertion(l_size,order)
        print("real_size:",l_size)
        accepted_dims = [[6, 9], [7, 9], [3, 1], [5, 3], [5, 5],[8, 9]]

        if l_size[1] == [7,10]:
            print("[7,10] anamoly, fixing...")


            copy = list_pos[1][:]
            for i in range(7):


                list_pos[1].remove(copy[i*10])

            l_size[1] = [7,9]

        if(len(l_size)>len(accepted_dims)):
            list_pos2=[]
            l_size2 = []
            for k,dim in enumerate(l_size):
                if dim in accepted_dims:
                    #accepted_dims.remove(dim) # discard duplicates
                    list_pos2.append(list_pos[k])
                    l_size2.append(dim)
            list_pos2=list_pos2[:5]
            l_size2=l_size2[:5]
        else:
            list_pos2=list_pos
            l_size2 = l_size

        for ii in range(len(l_size2)):
            if((l_size2[ii]==accepted_dims[ii]) and l_size3[ii]==[]):
                l_size3[ii]=l_size2[ii]
                list_pos3[ii]=list_pos2[ii]
        if(len(l_size2)>1):
            if((l_size2[0]==accepted_dims[1]) and l_size3[0]==[]):
                l_size3[0]=accepted_dims[0]
                list_pos3[0]=list_pos2[0][9:]
            if((l_size2[0]==accepted_dims[-1]) and l_size3[0]==[]):
                l_size3[0]=accepted_dims[0]
                list_pos3[0]=list_pos2[0][9*2:]
            if((l_size2[1]==accepted_dims[-1]) and l_size3[1]==[]):
                l_size3[1]=accepted_dims[1]
                list_pos3[1]=list_pos2[1][9:]

        # If we only care about table 0 and 1 (which we do):
        if only_top_table:
            if l_size3[0] == [6, 9] and l_size3[1] == [7, 9]:
                print("Good enough: ", l_size3)
                return list_pos3,l_size3

        if((l_size3 == [[6, 9], [7, 9], [3, 1], [5, 3], [5, 5]]) or (l_size3 == [[6,18], [3, 1], [5, 3], [5, 5]])):
            return list_pos3,l_size3

    #print("error")
    return list_pos3,l_size3

    if (len(list_pos2)==len(l_size2)):
        pass

    else:
        print("error!!!")
        return None

def corr_rotate(image):
    image=np.max(image)-image
    image=image.astype(np.float32)
    thresh=threshold_otsu(image)
    binary = image> thresh
    shape_im=image.shape
    im1=image[:,:shape_im[1]//2]
    im2=image[:,shape_im[1]//2:]
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
    im=np.concatenate((im1,im2),1)
    im=np.max(im)-im
    shape_im = list(shape_im)
    im2 = np.ones((shape_im[0]+60,shape_im[1]+60))*np.max(im)
    im2[30:-30,30:-30] = im
    return im2

def debug_plotter(image_filter,pos_list,size_list, printer = False):
    fig, axs = plt.subplots(1,1)
    axs.imshow(image_filter)
    axs.set_title("image_filtered")


    for num_figure in range(len(pos_list)):
        print("a ",size_list[num_figure][0])
        print("b ",size_list[num_figure][1])
        print("pos_list", len(pos_list[num_figure]))
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
    with open('test.npy', 'rb') as f:
        line = np.load(f)
    print(line.shape)
    plt.figure()
    plt.subplot(221)
    plt.title("line")
    thresh=threshold_otsu(line)
    binary1 =line > thresh
    result = get_pos(binary1)
