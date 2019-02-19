#coding=utf-8
from mido import MidiFile,MidiTrack,Message
import mido

SongName="V.K\\Melody of elves"              #待操作音乐名称

Song=MidiFile("data\Midi\\"+SongName+".mid")
for i, track in enumerate(Song.tracks):
    if(i==1):
        Main=track
    if(i==2):
        Assistant=track
f=open('data\Commands\Main\\'+SongName+'.txt','w',encoding='utf-8')       #导出主旋律指令
for x in Main:
    f.write(str(x)+"\n")
f.close()
f=open('data\Commands\Assistant\\'+SongName+'.txt','w',encoding='utf-8')       #导出辅助旋律指令
for x in Assistant:
    f.write(str(x)+"\n")
f.close()
print('旋律指令导出完毕!')