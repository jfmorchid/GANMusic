#coding=utf-8
path1="data\Sequence\Main"      #主旋律序列存放地址
path2="data\TrainingDataset"    #切分后序列存放地址
SongName="V.K\\Melody of elves"             #待操作音乐名称
CutLength=50              #切分的长度

f=open(path1+"\\"+SongName+".txt")
Command=f.readlines()
Command=[x[:-1] for x in Command]   #去除"\n"
f.close()
Pieces=len(Command)//CutLength
for x in range(Pieces):
    f=open(path2+"\\"+SongName+"_part%d.txt"%(x+1),'w')
    for i in range(CutLength*x,CutLength*(x+1)):
        f.write(Command[i]+"\n")
    f.close()
print("序列切分完成！")
        
