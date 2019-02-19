#coding=utf-8
import mido

CurrentTime=0   #采用绝对时间计时
SongName="V.K\\Melody of elves"              #待操作音乐名称
path1="data\Commands\Main"      #主旋律指令地址
path2="data\Sequence\Main"      #主旋律序列存放地址
path3="data\Commands\Assistant"      #辅助旋律指令地址
path4="data\Sequence\Entire"      #完整旋律序列存放地址

def compare(s):     #自定义排序函数，根据音符开始的绝对时间对序列降序排列
    time=s.split(' ')
    return int(time[0])

def noteCommand(s):     #将单条指令解析出来
    global CurrentTime
    Info=s.split(' ')
    CurrentTime+=int(Info[4][5:])  #在时间轴上的绝对时间
    if(Info[0][:5]=='note_'):
        return Info[0][5:],int(Info[2][5:]),CurrentTime #返回开关，音高，绝对时间这些信息
    else:
        return '',0,0   #无效指令

'''
- Part1 导出主旋律序列 -
'''
f=open(path1+"\\"+SongName+".txt")  # 加载主旋律指令集
Command=f.readlines()
f.close()
Command=[x[:-1] for x in Command]   # 去除\n
Meta,Play=[x for x in Command if x[:5]=='<meta'],[x for x in Command if x[:5]!='<meta']     #分离meta指令与弹奏指令
OnOff,Note,Time=[''for _ in range(len(Play))],[0 for _ in range(len(Play))],[0 for _ in range(len(Play))]
i=0
for x in Play:
    if(x[:2]!='pr'): #跳过program_change指令
        OnOff[i],Note[i],Time[i]=noteCommand(x)
    i+=1
head,tail=0,0
EntireSequence=[]   #记录完整旋律指令集的列表
f=open(path2+"\\"+SongName+".txt",'w')  #序列输出位置
while(head<len(Note)-1):      #处理同一时间弹奏的多音符
    while(OnOff[head]==''):        #control_change这一类指令，只改变绝对时间
        head+=1
    tail=head
    while(OnOff[tail]!='off'):
        tail+=1
    Sequence=str(Time[head])+" "    #序列格式：开始时间 音符1,音符2,... 结束时间
    SameTime=[Note[x] for x in range(head,tail)]    #同一时刻的音符构成一个列表
    SameTime=sorted(SameTime,reverse=True)                     #按音高降序排列
    for x in SameTime:
        Sequence+=str(x)+","
    Sequence=Sequence[:-1]+" "+str(Time[tail])  #去除多余的','
    if(Time[head]!=Time[tail]):      #排除空音符
        EntireSequence.append(Sequence+" 0")             #将这条指令添加入完整旋律指令集，0代表主旋律音
        f.write(Sequence+"\n")
    while(OnOff[tail]=='off' and tail<len(Note)-1):
        tail+=1
    head=tail
f.close()
print("主旋律序列转化完毕！")

'''
- Part2 导出完整旋律序列 -
'''
CurrentTime=0       #绝对时间清零
f=open(path3+"\\"+SongName+".txt")  # 加载完整旋律指令集
Command=f.readlines()
f.close()
Command=[x[:-1] for x in Command]   # 去除\n
Meta,Play=[x for x in Command if x[:5]=='<meta'],[x for x in Command if x[:4]=='note']     #分离meta指令与弹奏指令
OnOff,Note,Time=[''for _ in range(len(Play))],[0 for _ in range(len(Play))],[0 for _ in range(len(Play))]
i=0
for x in Play:
    OnOff[i],Note[i],Time[i]=noteCommand(x)
    i+=1
head,tail=0,0
while(head<len(Note)-1):      #用和上面完全一样的方法处理辅助旋律序列
    while(OnOff[head]==''):        
        head+=1
    tail=head
    while(OnOff[tail]!='off'):
        tail+=1
    Sequence=str(Time[head])+" "    
    SameTime=[Note[x] for x in range(head,tail)]    
    SameTime=sorted(SameTime,reverse=True)                     
    for x in SameTime:
        Sequence+=str(x)+","
    Sequence=Sequence[:-1]+" "+str(Time[tail])  
    if(Time[head]!=Time[tail]):
        EntireSequence.append(Sequence+" 1")             #将这条指令添加入完整旋律指令集,1代表辅助音
    while(OnOff[tail]=='off' and tail<len(Note)-1):
        tail+=1
    head=tail
f=open(path4+"\\"+SongName+".txt",'w')  #序列输出位置
EntireSequence=sorted(EntireSequence,key=compare)
for x in EntireSequence:
    f.write(x+"\n")
f.close()
print("完整旋律序列转化完毕！")
