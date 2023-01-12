import cv2
from PIL import Image
from requests import post
from datetime import datetime

img_name={'left.jpg':('350','430','350','430'),'right.jpg':('410','465','1610','1680')} # имя картинки и x,y как кропнуть
name_cond={'left.jpg':('левому','левом','левый'),'right.jpg':('правому','правом','правый')} 
bot_api=''
chat_id='' 
tg_request=f'{bot_api}/sendMessage?chat_id={chat_id}&text='

# Send_foto
def send_tg(name):
    files = {'photo': open(f"full.jpg", 'rb')}
    data={'chat_id':{chat_id},'caption':f'Атеншен {name_cond[name][0]} плохо!!!! Просьба позвонить охране по номеру '} 
    post(f"{bot_api}/sendPhoto", files=files, data=data)
    
#пишем в лог
def wr_log(data):
    file = open('rtsp_cam.log','a+')
    file.write(f'{datetime.now().strftime("%d-%b-%Y %H:%M")}: {data}')   
    file.close()    

#Читаем файл
def read_dic():
    fail_conunt={}
    try:
        with open('fail_conunt') as inp:
            for i in inp.readlines():
                key,val=i.strip().split(':')
                fail_conunt[key]=int(val)
    except:
        fail_conunt={'left.jpg':0,'right.jpg':0}
    return fail_conunt

#Пишем в файл
def wr_dic(fail_conunt):
    with open('fail_conunt', 'w') as out:
        for key,val in fail_conunt.items():
            out.write(f'{key}:{val}\n')    

#Сравниваем пиксели
def compare_pixel(name):
    fail_conunt=read_dic()
    try:
        stok=Image.open('stok_'+name)     
        new=Image.open(name)
    except FileNotFoundError as err:
        wr_log(f'ФАЙЛ stok_+{err.filename} НЕ НАЙДЕН \n')
        return
    stok_load=stok.load()
    new_load=new.load()
    x1,y1 = stok.size    
    i = 0 # Счетчик пикселей, которые не совпадают
    compare_num=0 # различия между пикселями 
    for x in range(0,x1):
        for y in range(0,y1):
            for z in range(0,3): #RGB
                compare_num=abs(stok_load[x,y][z]-new_load[x,y][z])
            if compare_num>50:
                i+=1
    if i>=1000 and fail_conunt[name]==0:
        send_tg(name)
        fail_conunt[name]+=1
    elif i>=1000 and fail_conunt[name]>0:
        post(f"{tg_request}{name_cond[name][0]} всё ещё плохо")
        fail_conunt[name]+=1
    elif i<1000 and fail_conunt[name]>0:
        post(f"{tg_request}{name_cond[name][2]} починили спустя ~ {fail_conunt[name]*10} минут")
        fail_conunt[name]=0               
    wr_log(f'Кол-во различных пикселей в {name_cond[name][1]} = {i}\n')
    wr_dic(fail_conunt)

cam_pass=''
cam_ip='0'
# Get&SaveVideo
cap = cv2.VideoCapture(f"rtsp://{cam_pass}@{cam_ip}:554/live/main")
ret, frame = cap.read()
if ret:
    cv2.imwrite(f'full.jpg',frame)
    for name in img_name.keys():
        cv2.imwrite(f'{name}',frame[int(img_name[name][0]):int(img_name[name][1]),int(img_name[name][2]):int(img_name[name][3])]) #выглядит страшно но так надо
        compare_pixel(name)
else:
    wr_log('Не получилось подключиться к камере!!!! \n')