#coding=utf-8
import keras
import numpy as np
import mido
from mido import MidiTrack,MidiFile,Message

Artist="V.K"    #待迁入风格的音乐家
Length=50       #音符序列长度
Track,Music=MidiTrack(),MidiFile()

def Normalize(x):       #标准化辅助音符数据，>=0.5记作标签1，否则记作标签0
    if(x>=0.5):
        return 1
    else:
        return 0

speed=12.5       #音乐放慢的系数
Model=keras.models.load_model(r"data\\Networks\\%s.h5"%(Artist))  #预加载神经网络
Notes=[69,72,70,72,70,72,70,69,67,60,74,72,72,70,72,70,69,67,66,62,60,58,57,58,62,69,67,62,65,69,69,70,69,81,82,84,62,65,72,62,65,72,62,72,70,69,64,67,65,69]
Notes=np.array(Notes)
Notes=np.reshape(Notes,(1,1,Length))        #转化为标准输入格式
Result=Model.predict([Notes,Notes,Notes,Notes])
Assistant=[Normalize(Result[0][0][x]) for x in range(Length,Length*2)]  #读取辅助音符数据
Start=[int(abs(Result[0][0][x]*speed)) for x in range(Length*2,Length*3)] #读取音符开始延时数据
Finish=[int(abs(Result[0][0][x]*speed)) for x in range(Length*3,Length*4)]   #读取音符结束延时数据
for x in range(Length):
    if(Assistant[x]==0):    #含有辅助音符
        Track.append(Message("note_on",note=Notes[0][0][x],velocity=80,channel=0,time=Start[x])) #加入note_on 指令
        Track.append(Message("note_on",note=Notes[0][0][x]-6,velocity=80,channel=0,time=0))
        Track.append(Message("note_off",note=Notes[0][0][x],velocity=64,channel=0,time=Finish[x])) #加入note_off 指令
        Track.append(Message("note_off",note=Notes[0][0][x]-6,velocity=64,channel=0,time=0))        
    else:
        Track.append(Message("note_on",note=Notes[0][0][x],velocity=80,channel=0,time=Start[x]))
        Track.append(Message("note_off",note=Notes[0][0][x],velocity=64,channel=0,time=Finish[x]))
Music.tracks.append(Track)
Music.save("output.mid")
print("Midi音频输出完成！")

