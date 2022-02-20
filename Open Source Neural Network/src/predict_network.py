import tensorflow as tf
import os
import datetime
import string
from data.generator import DataGenerator


         
# define parameters
source = "washington"
arch = "flor"
epochs = 1000
batch_size = 16

# define paths
source_path = os.path.join("..", "data", f"{source}.hdf5")
output_path = os.path.join("..", "output", source, arch)
target_path = os.path.join(output_path, "checkpoint_weights.hdf5")
os.makedirs(output_path, exist_ok=True)

# define input size, number max of chars per line and list of valid chars
input_size = (1024, 128, 1)
max_text_length = 128
charset_base = string.printable[:95] # all possible characters if training character are unknow
charset_base = "0123456789n.-+x" # possible character "nswe" for wind



print("source:", source_path)
print("output", output_path)
print("target", target_path)
print("charset:", charset_base)

dtgen = DataGenerator(source=source_path,
                      batch_size=batch_size,
                      charset=charset_base,
                      max_text_length=max_text_length)

print(f"Train images: {dtgen.size['train']}")
print(f"Validation images: {dtgen.size['valid']}")
print(f"Test images: {dtgen.size['test']}")
from network.model import HTRModel

# create and compile HTRModel
model = HTRModel(architecture=arch,
                  input_size=input_size,
                  vocab_size=dtgen.tokenizer.vocab_size,
                  beam_width=10,
                  stop_tolerance=20,
                  reduce_tolerance=15)

model.compile(learning_rate=0.001)
model.summary(output_path, "summary.txt")

# get default callbacks and load checkpoint weights file (HDF5) if exists
model.load_checkpoint(target=target_path)

callbacks = model.get_callbacks(logdir=output_path, checkpoint=target_path, verbose=1)

from data import preproc as pp

start_time = datetime.datetime.now()

# predict() function will return the predicts with the probabilities
predicts, AA = model.predict(x=dtgen.next_test_batch(),
                            steps=dtgen.steps['test'],
                            ctc_decode=True,
                            verbose=1)

# decode to string
predicts = [dtgen.tokenizer.decode(x[0]) for x in predicts]
ground_truth = [x.decode() for x in dtgen.dataset['test']['gt']]

total_time = datetime.datetime.now() - start_time

# mount predict corpus file
with open(os.path.join(output_path, "predict.txt"), "w") as lg:
    for pd, gt in zip(predicts, ground_truth):
        lg.write(f"TE_L {gt}\nTE_P {pd}\n")
   
for i, item in enumerate(dtgen.dataset['test']['dt'][:400]):
    print("=" * 10, "\n")
    print(ground_truth[i])
    print(predicts[i], "\n")
    print("certainty ", AA[i],"\n")
     

dico = {}
result = []
with open('../raw/washington/sets/cv1/test.txt','r') as f:
    for line in f:
        for Word in line.split():
            dico[Word] =""
           
k = -1
with open('../raw/washington/ground_truth/transcription.txt','r') as f:
    for line in f:
        liste   = line.split()
        if liste[0] in dico:
            k+=1
            if(k<len(predicts)):
                new_value = predicts[k].replace("n","")
                result.append([liste[0][:-2],new_value])
    
with open("../output/washington/flor/result.txt",'w') as f:
    for r in result:
        f.write(r[0]+ " "+ r[1]+ "\n")
            