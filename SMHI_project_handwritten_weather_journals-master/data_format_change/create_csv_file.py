import csv
import sys
import os
sys.path.insert(1, '../pipeline/')
from ID import decode
from datetime import datetime
year = "1927"

path_result = "../Open Source Neural Network/output/washington/flor"
result=[]
with open(os.path.join(path_result,'result.txt'),'r') as f:
    for line in f:
        liste   = line.split()
        if(len(liste)==2):
            result.append(liste)


header = ['Timme', 'Term. Pa Barom.', 'Barom.',
          'Torraterm.','Vataterm.','slag','mangd','hogre slag','total mangd',
          'Rikning','Beaufort','m/sek.','Sikt','Sjogang'
          ]
all_data =  []
for k in range(2,367):
    day_num = str(k-1)
    day_num.rjust(3 + len(day_num), '0')
    res = str(datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y"))

    data = [
        ['2 fm']+ ['' for k in range(len(header)-1)],
        ['8 fm']+ ['' for k in range(len(header)-1)],
        ['2 em']+ ['' for k in range(len(header)-1)],
        ['7 em']+ ['' for k in range(len(header)-1)],
        ['9 em']+ ['' for k in range(len(header)-1)],
        ['date',str(res)]
    ]
    for r in result:
        if (decode(int(r[0]),False)[1]==k):
            position = decode(int(r[0]),False)[-3:]
            position = list(position)
            if(position[2]==1):
                position[1]+=9
            if(position[0]<=5 and position[1]<=14):
                data[position[0]-1][position[1]]=r[1]
    all_data.extend(data)


with open('../result.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(all_data)
