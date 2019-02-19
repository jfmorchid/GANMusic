#coding=utf-8
import mido
from mido import MidiTrack,MidiFile,Message

CurrentTime=0   #绝对时间轴
Track,Music=MidiTrack(),MidiFile()
SongName="Pianoboy\\105 days"              #待操作音乐名称
path1="data\Sequence\Main"      #主旋律序列存放地址
path2="output.mid"              #输出音乐存放地址

def addNote(StartTime,Notes,FinishTime):
    global CurrentTime,Track
    if(StartTime-FinishTime>0 or StartTime<CurrentTime):
        print(1)
    Track.append(Message("note_on",note=int(Notes[0]),velocity=80,channel=0,time=StartTime-CurrentTime)) #加入note_on 指令
    if(len(Notes)>1):
        for x in range(1,len(Notes)):
            Track.append(Message("note_on",note=int(Notes[x]),velocity=80,channel=0,time=0))
    Track.append(Message("note_off",note=int(Notes[0]),velocity=64,channel=0,time=FinishTime-StartTime)) #加入note_off 指令
    if(len(Notes)>1):
        for x in range(1,len(Notes)):
            Track.append(Message("note_off",note=int(Notes[x]),velocity=64,channel=0,time=0))    
    CurrentTime=FinishTime


Track.append(mido.MetaMessage("set_tempo",tempo=714280,time=0)) #设定默认的四分音符拍速
#f=open(path1+"\\"+SongName+".txt")
f=open('water.txt')
Command=f.readlines()
Command=[x[:-1] for x in Command]   #去除"\n"
StartTime,Notes,FinishTime=["" for _ in range(len(Command))],["" for _ in range(len(Command))],["" for _ in range(len(Command))] #初始化开始时间，音符与结束时间这三个列表
for x in range(len(Command)):
    StartTime[x],Notes[x],FinishTime[x]=Command[x].split(" ")
Notes=[x.split(',') for x in Notes]
for x in range(len(Command)):       #将每条指令写入mid文件
    addNote(int(StartTime[x]),Notes[x],int(FinishTime[x]))
Music.tracks.append(Track)
Music.save(path2)
print("Midi音频输出完成！")