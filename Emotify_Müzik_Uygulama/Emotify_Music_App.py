import cv2 as cv
import random
from deepface import DeepFace
import tkinter as tk
from selenium import webdriver
import os
from gtts import gTTS
from selenium.webdriver.common.by import By
import time
import tkinter.filedialog


#------------------------------------------------------------------------------------------------------------------------------------------------------------------

form = tk.Tk()
form.config(bg='turquoise')
form.title('Emotify')
form.geometry('500x300')
form.resizable(width=False, height=False)


window_width = 600
window_height = 400


screen_width = form.winfo_screenwidth()
screen_height = form.winfo_screenheight()

x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))

form.geometry(f'{window_width}x{window_height}+{x_coordinate}+{y_coordinate}')

etiket = tk.Label(text="Emotify'a Hoşgeldiniz !", font='Arial 20 bold', fg='purple', bg='turquoise', anchor='center')
etiket.place(relx=0.5, rely=0.1, anchor='center')

etiket2 = tk.Label(form, text='Aşağıdaki Seçeneklerden Dileğinize Göre Duygu Tespiti Yapabilirsiniz', fg='black',font='Arial 13 bold', bg='turquoise')
etiket2.place(relx=0.5, rely=0.25, anchor='center')


emotion_counts = {'happy': 0, 'sad': 0, 'angry': 0, 'surprise': 0, 'fear': 0}

def update_emotion_counts(emotion):
    global emotion_counts
    if emotion in emotion_counts:
        emotion_counts[emotion] += 1
    else:
        emotion_counts[emotion] = 1

    
    save_emotion_counts_to_file()

def save_emotion_counts_to_file():
    file_path = "emotions.txt"
    with open(file_path, 'w') as file:
        for emotion, count in emotion_counts.items():
            file.write(f"{emotion}:{count}\n")

def show_emotion_statistics():
    print("Duygu İstatistikleri:")
    for emotion, count in emotion_counts.items():
        print(f"{emotion}: {count}")

#-----------------------------------------------------------------------------------------------

def show_emotion_statistics_window():
    def kapat():
        stats_window.destroy()

    def sifirla():
        global emotion_counts
        emotion_counts = {'happy': 0, 'sad': 0, 'angry': 0, 'surprise': 0, 'fear': 0}
        save_emotion_counts_to_file()
        guncelle() 

    def guncelle():
        file_path = "emotions.txt"
        try:
          with open(file_path, 'r') as file:
            file_content = file.read()

          sayi = 0.2
          for i, line in enumerate(file_content.splitlines(), start=1):
            emotion, count = line.split(":")
            emotion = emotion.strip().upper()
            count = count.strip()
            label_text = f"{emotion}: {count}"
            label = tk.Label(stats_window, text=label_text, bg='turquoise', font='Arial 15 bold')
            sayi += 0.1
            label.place(relx=0.5, rely=sayi, anchor='center')
        except FileNotFoundError:
          tk.messagebox.showerror("Hata", "Dosya bulunamadı: emotions.txt")

    stats_window = tk.Toplevel()
    stats_window.config(bg='turquoise')
    stats_window.title('Duygu İstatistikleri')
    stats_window.resizable(width=False, height=False)

    window_width = 400
    window_height = 300

    screen_width = stats_window.winfo_screenwidth()
    screen_height = stats_window.winfo_screenheight()

    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))

    stats_window.geometry(f'{window_width}x{window_height}+{x_coordinate}+{y_coordinate}')

    update_button = tk.Button(stats_window, text="Güncelle", fg='white', bg='purple', command=guncelle,
                              font='Arial 13 italic bold')
    update_button.place(relx=0.2, rely=0.9, anchor='center')

    sifirla_button = tk.Button(stats_window, text="Sıfırla", fg='white', bg='purple', command=sifirla,
                               font='Arial 13 italic bold')
    sifirla_button.place(relx=0.5, rely=0.9, anchor='center')

    kapat_buton = tk.Button(stats_window, text="Kapat", fg='white', bg='purple', command=kapat,
                              font='Arial 13 italic bold')
    kapat_buton.place(relx=0.8,rely=0.9,anchor='center')

    guncelle()

    

#---------------------------------------------------------------------------------------------------

def save_emotion_counts():
    with open('emotions.txt', 'w') as file:
        for emotion, count in emotion_counts.items():
            file.write(f"{emotion}: {count}\n")

#--------------------------------------------------------------------------------------------------

def load_emotion_counts():
    try:
        with open('emotion_counts.txt', 'r') as file:
            for line in file:
                emotion, count = line.strip().split(': ')
                emotion_counts[emotion] = int(count)
    except FileNotFoundError:
        pass

#------------------------------------------------------------------------------------------------

def sil():
    #save_emotion_counts()
    #show_emotion_statistics()
    form.destroy()

#---------------------------------------------------------------------------------------------------

def foto_cek():
    load_emotion_counts()
    cam = cv.VideoCapture(0)
    cv.namedWindow("TAKE A PHOTO")
    counter = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Kamera Bulunamadı :( ")
            break

        cv.imshow("TAKE A PHOTO", frame)
        key = cv.waitKey(1)
        if key == ord('q'):
            print("Ekran Kapatılıyor...")
            break
        elif key == ord('p'):
            file_name = 'photo/photo_{}.png'.format(counter)
            cv.imwrite(file_name, frame)
            img = cv.imread(file_name)
            face_classifier = cv.CascadeClassifier()
            face_classifier = cv.CascadeClassifier(
                cv.samples.findFile(cv.data.haarcascades + "haarcascade_frontalface_default.xml"))
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray)
            response = DeepFace.analyze(frame, actions=("emotion",), enforce_detection=False)[0]

            for face in faces:
                x, y, w, h = face
                isim = cv.putText(frame, response["dominant_emotion"], (x, y), cv.FONT_HERSHEY_COMPLEX, 1,(255, 255, 0))
                new_frame = cv.rectangle(frame, (x, y), (x + w, y + h), color=(255, 255, 0), thickness=2)
                emotion_counts[response['dominant_emotion']] += 1

            cv.imshow("Emotify - Emotion Catcher", frame)           
            cv.waitKey(3)

            counter += 1

            if response['dominant_emotion'] == 'happy':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_l5vsK_hF93SboJt2sqZ94fLp-aE8aO9Tw"
                driver.get(playlist_url)  
                try:
                    rasgele = random.randint(1,98)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break
                
                

            if response['dominant_emotion'] == 'sad':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_lp8LtelM9GiSwRFGGQjctKaGoHcrgQVEU"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,54)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break    

            if response['dominant_emotion'] == 'angry':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_kb7EBi6y3GrtJri4_ZH56Ms786DFEimbM"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,128)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break                  
        

            if response['dominant_emotion'] == 'surprise':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_l1oO11DBO4FD8U7bOrqUKK5Y_PkISUMQM"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,78)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break           
                

            if response['dominant_emotion'] == 'fear':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_lRX7tRkfO2wmlk0ZMHRz2BYH7RMGJAts0"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,106)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break    

               
    cam.release()
    cv.destroyAllWindows()
    save_emotion_counts_to_file()
    form.mainloop() 

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def tara_canli():
    load_emotion_counts()
    face_classifier = cv.CascadeClassifier()
    face_classifier = cv.CascadeClassifier(cv.samples.findFile(cv.data.haarcascades + "haarcascade_frontalface_default.xml"))
    
    cap = cv.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray)
        response = DeepFace.analyze(frame, actions=("emotion",), enforce_detection=False)[0]

        for face in faces:
            x, y, w, h = face
            cv.putText(frame, response["dominant_emotion"], (x, y), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
            new_frame = cv.rectangle(frame, (x, y), (x + w, y + h), color=(255, 255, 0), thickness=2)
            if response['dominant_emotion'] != 'neutral':
             emotion_counts[response['dominant_emotion']] += 1

       
        cv.imshow("Emotify - Emotion Catcher", frame)          
        
        key = cv.waitKey(1)

        if key == ord('q'):
         print("Programdan Çıkış Yapılıyor...")
         break
       

        if response['dominant_emotion'] == 'happy':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_l5vsK_hF93SboJt2sqZ94fLp-aE8aO9Tw"
                driver.get(playlist_url)  
                try:
                    rasgele = random.randint(1,98)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break

        if response['dominant_emotion'] == 'sad':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_lp8LtelM9GiSwRFGGQjctKaGoHcrgQVEU"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,54)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break    
        
        if response['dominant_emotion'] == 'angry':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_kb7EBi6y3GrtJri4_ZH56Ms786DFEimbM"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,128)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break
               

        if response['dominant_emotion'] == 'surprise':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_l1oO11DBO4FD8U7bOrqUKK5Y_PkISUMQM"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,78)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break
                

        if response['dominant_emotion'] == 'fear':
                time.sleep(1)
                driver = webdriver.Chrome()
                playlist_url = "https://music.youtube.com/playlist?list=RDCLAK5uy_lRX7tRkfO2wmlk0ZMHRz2BYH7RMGJAts0"
                driver.get(playlist_url)
                try:
                    rasgele = random.randint(1,106)
                    time.sleep(1)
                    playlist_items = driver.find_element(By.CSS_SELECTOR,"#contents > ytmusic-responsive-list-item-renderer:nth-child({}) > div.flex-columns.style-scope.ytmusic-responsive-list-item-renderer > div.title-column.style-scope.ytmusic-responsive-list-item-renderer > yt-formatted-string > a".format(rasgele)).click()
                except:
                    pass
                break       
         
                
    cap.release()
    cv.destroyAllWindows()
    save_emotion_counts_to_file()
    form.mainloop()
    
 # -----------------------------------------------------------------------------------------------------------------

button_width = 20
button_height = 2

buton = tk.Button(form, text=' Canlı Tarama', fg='white', bg='purple', command=tara_canli, font='Arial 13 italic bold',
                  anchor='center',width=button_width, height=button_height)
buton.place(relx=0.3, rely=0.45, anchor='center')

buton2 = tk.Button(form, text='Görüntü Tarama', fg='white', bg='purple', command=foto_cek, font='Arial 13 italic bold',
                   anchor='center',width=button_width, height=button_height)
buton2.place(relx=0.7, rely=0.45, anchor='center')

buton3 = tk.Button(form, text="Çıkış", fg='white', bg='purple', command=sil, font='Arial 13 italic bold',
                   anchor='center',width=button_width, height=button_height)
buton3.place(relx=0.7, rely=0.70, anchor='center')

buton4 = tk.Button(form,text='Duygu İstatistikleri',fg='white',bg='purple',command=show_emotion_statistics_window,font='Arial 13 italic bold',anchor='center',width=button_width, height=button_height)
buton4.place(relx=0.3, rely=0.70, anchor='center')

form.mainloop()