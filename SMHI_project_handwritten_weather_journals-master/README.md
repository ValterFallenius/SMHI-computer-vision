# project_meteo
Digitize weather data written by hand.
the main.Py file controle everything
-----------------------------------------------------------
data are save in different formats:
-------------
Format 1: 
format with png image of different case, the names of images are ID-label 
ID is a number with binary data inside : the number of the book, the number of the page and the position of the case in the page
Save in SMHI_project_handwritten_weather_journals-master\pipeline
label : is data labeled with mode0
old_label : is already labeled data for training
wind : labeled data create with mode 1
no_label : is data create with mode 3
-------------
Format 2:
The Format 2 is the same format than the Washinghton data_set (https://fki.tic.heia-fr.ch/databases/washington-database)
this format is save in SMHI_project_handwritten_weather_journals-master\Open Source Neural Network\raw
-------------
Format 3:
this format is save into 
SMHI_project_handwritten_weather_journals-master\Open Source Neural Network\data
the data come from SMHI_project_handwritten_weather_journals-master\Open Source Neural Network\raw
-------------

network : 
After training the network is save in Open Source Neural Network/output/washington/flor.checkpoint_weights.hdf5
to use a already train network, best_weights.hdf5 need to be rename checkpoint_weights.hdf5
--------------------------------------
modes in main :
        mode == 0: Label data with numbers with "769.5", "+15.0" etc.
        mode == 1: Label data wind with "NW", "S" etc.
        mode == 2: create prediction data (whithout label for number)
        mode == 3: Create new training, validation and test sets for training and train
        mode == 4: Create new test sets for prediction and predict
        mode == 5: save predict data into csv file


exemple of use :
     mode 0 (label the training data)
---> mode 3 (train the network)
---> mode 2(creat prediction data with a book)
---> mode 4(predict) 
---> mode 5(get final file CSV file for the selected book)
