#coding=utf-8
import keras
from keras import layers
import numpy as np
import os
import random

path1="data\TrainingDataset"  #数据集地址
Artist='V.K'        #风格迁移的对象

def takeNotesApart(s):   #分离主音符、辅助音符
    L=s.split(',')
    if(len(L)==1):  #缺省辅助音符，用0表示；有辅助音符，用1表示
        return int(L[0]),0
    else:
        return int(L[0]),1

'''
数据预加载：这段代码的功能是将先前处理好的序列读取，并处理成我们需要的各种样子。
其中用到的数据有：音符的起始时间（相对前一音符的差），主音，辅音，终止时间（也是相对时间）
'''
SongList=os.listdir(path1+"\\"+Artist)      #音乐目录
SongNum=len(SongList)   #音乐数目

Main,Assistant,Start,Finish=[[] for _ in range(SongNum)],[[] for _ in range(SongNum)],[[] for _ in range(SongNum)],[[] for _ in range(SongNum)]
for u in range(SongNum):
    f=open(path1+"\\%s\\"%(Artist)+SongList[u])
    Command=f.readlines()
    Command=[x[:-1]for x in Command]           #去除"\n"
    StartTime,Notes,Finishtime=[0 for _ in range(len(Command))],['' for _ in range(len(Command))],[0 for _ in range(len(Command))]
    for i in range(len(Command)):
        StartTime[i],Notes[i],Finishtime[i]=Command[i].split(' ')   #分离起始时间、音符和中止时间
        MainNote,AssisNote=[0 for _ in range(len(Command))],[0 for _ in range(len(Command))]   #主音符、辅助音符列表
    for i in range(len(Command)):
        MainNote[i],AssisNote[i]=takeNotesApart(Notes[i])  #从所有音符中分离主音符和辅助音符
    Starting,Finishing=[0 for _ in range(len(Command))],[int(Finishtime[i])-int(StartTime[i]) for i in range(len(Command))]   #相对时间轴列表
    for i in range(1,len(Command)):
        Starting[i]=int(StartTime[i])-int(Finishtime[i-1])       #计算相对时间
    Main[u],Assistant[u]=MainNote,AssisNote
    Start[u],Finish[u]=Starting,Finishing
    f.close()

'''
第一个生成函数：音符叠加
它的功能是对于输入的纯粹音符，生成具有一定风格的叠音。
比如1 78,76 15中，78与76就是叠音。这样子的话主音听起来就会更像人弹出来的。
'''
Length=50   #输入序列长度
Generator1Input=keras.Input(shape=(None,Length))
gen1=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(Generator1Input)#套上两层一维卷积层
gen1=layers.LeakyReLU()(gen1)
gen1=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(gen1)
gen1=layers.LeakyReLU()(gen1)
gen1=layers.Dense(Length,activation='sigmoid')(gen1)    #标签分类，以0.5为界
Generator1=keras.models.Model(Generator1Input,gen1)
Generator1.compile(loss='mse',optimizer='rmsprop')


'''
第2，3个生成函数：起始、中止相对时间
它的功能是对于输入的纯粹音符，生成具有一定风格的节奏。
'''
Length=50   #输入序列长度
Generator2Input=keras.Input(shape=(None,Length))
gen2=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(Generator2Input)#训练起始节奏
gen2=layers.LeakyReLU()(gen2)
gen2=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(gen2)
gen2=layers.LeakyReLU()(gen2)
Generator2=keras.models.Model(Generator2Input,gen2)
Generator2.compile(loss='mse',optimizer='rmsprop')
Generator3Input=keras.Input(shape=(None,Length))
gen3=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(Generator3Input)#训练中止节奏
gen3=layers.LeakyReLU()(gen3)
gen3=layers.Conv1D(filters=Length,kernel_size=5,use_bias=True,padding='same')(gen3)
gen3=layers.LeakyReLU()(gen3)
Generator3=keras.models.Model(Generator3Input,gen3)
Generator3.compile(loss='mse',optimizer='rmsprop')


'''
鉴别器：和三个生成器共同组成生成式对抗网络。
通过训练，它能鉴别一组数据是真实数据还是由生成器生成的。
'''
DiscriminatorInput=layers.Input(shape=(None,4*Length))
disc=layers.Conv1D(filters=Length*4,kernel_size=5,use_bias=True,padding='same')(DiscriminatorInput)
disc=layers.LeakyReLU()(disc)
disc=layers.Conv1D(filters=Length*4,kernel_size=5,use_bias=True,padding='same')(disc)
disc=layers.LeakyReLU()(disc)
disc=layers.Dropout(0,3)(disc)
disc=layers.Dense(Length*2,activation='relu')(disc)
disc=layers.Dense(1,activation='sigmoid')(disc)
Opt=keras.optimizers.RMSprop(lr=0.005, clipvalue=1.0, decay=2e-8)    #自定义优化器
discriminator=keras.models.Model(DiscriminatorInput, disc)

'''
GAN：生成式对抗网络。
利用前几步构建的生成器和鉴别器，组成模型主体。
'''
discriminator.trainable=False   #在对抗过程中，冻结鉴别器
discriminator.compile(optimizer=Opt, loss='binary_crossentropy')
NoteInput=layers.Input(shape=(None,Length))
OutputNetwork=keras.layers.Concatenate()([NoteInput,gen1,gen2,gen3])  #添加一个合并层
gan=discriminator(OutputNetwork)   #连接生成器与鉴别器
Model=keras.models.Model([NoteInput,Generator1Input,Generator2Input,Generator3Input],gan)   #本质上，四个输入都是音符序列
Model.compile(optimizer='rmsprop',loss='binary_crossentropy')

'''
数据处理与模型训练：将真实数据与生成器生成的数据进行混合。
通过鉴别器鉴别，提高生成器造假能力。
'''
TrainingTime=50   #训练次数
FakeNum=100 # 训练鉴别器时一次生成的数据个数
FightNum=100    #训练生成器时一次生成的数据个数
FakeData=np.array([[0 for _ in range(Length*4)] for _ in range(FakeNum)])   #存储生成数据的集合
RealData=np.array([[0 for _ in range(Length*4)] for _ in range(SongNum)])   #存储真实数据的集合
FightData=np.array([[0 for _ in range(Length*4)] for _ in range(FightNum)]) #存储对抗时生成数据的集合
label=np.concatenate([np.ones((1,SongNum)),np.zeros((1,FakeNum))],axis=-1)
label+=0.04*np.random.random(label.shape)       #引入随机噪声
label=np.reshape(label[0],(len(label[0]),1,1))
Fight=np.ones((1,FightNum))
Fight=np.reshape(Fight[0],(len(Fight[0]),1,1))
for x in range(SongNum):
    RealData[x]=np.concatenate((np.array(Main[x]),np.array(Assistant[x]),np.array(Start[x]),np.array(Finish[x])))
for u in range(TrainingTime):
    print("这是第%d个训练周期："%(u+1))
    for x in range(FakeNum):    #训练鉴别器
        RandomNote=np.array(random.choice(Main))  #随机选择一串音符作为“造假”基础
        RandomNote=np.reshape(RandomNote,(1,1,Length)) #处理成标准输入格式
        Gen1Output,Gen2Output,Gen3Output=Generator1.predict(RandomNote),Generator2.predict(RandomNote),Generator3.predict(RandomNote)   #使用生成器生成数据
        FakeData[x]=np.concatenate((RandomNote,Gen1Output,Gen2Output,Gen3Output),axis=-1)   #生成一组假数据
    CombinedData=np.concatenate([RealData,FakeData])
    CombinedData=np.reshape(CombinedData,(len(CombinedData),1,4*Length))
    discriminator.fit(CombinedData,label,epochs=15)
    print('鉴别器训练完毕！')
    FightNote=[[] for _ in range(FightNum)]
    for x in range(FightNum):   #训练生成器        
        FightNote[x]=random.choice(Main)  #同样基于随机的音符序列生成
    FightNote=np.array(FightNote)
    FightNote=np.reshape(FightNote,(FightNum,1,Length)) #处理成标准数据格式
    Model.fit([FightNote,FightNote,FightNote,FightNote],Fight,epochs=15)
    print('生成器训练完毕！')
f=open("water.txt",'w')
Output=keras.models.Model([NoteInput,Generator1Input,Generator2Input,Generator3Input],OutputNetwork)
GG=Output.predict([RandomNote,RandomNote,RandomNote,RandomNote])
Output.save('data\\Networks\\%s.h5'%(Artist))      #保存网络权重
print('%s风格的网络保存完毕！'%(Artist))