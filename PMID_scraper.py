#Programme pulls out PMIDs from a text file

x = 'PMID: '
a = []
i = 0

with open('India Alliance 2017.txt') as infile, open('output1.txt','w') as outfile:
    for line in infile:
        if line.strip():
            outfile.write(line)
         
f = open('output1.txt')
for line in f:
    if x in line:
        print(line[(line.find(x)+len(x)):((line.find(x)+len(x))+8)])
    else:
        a.append(i)
    i+=1
print ("check following lines:", a)
  
    
    

