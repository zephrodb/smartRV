#! /usr/bin/python3
import paho.mqtt.client as mqtt #import the client1
from tkinter import *
from PIL import ImageTk, Image
import os
import string

#Get the window and set the size
window = Tk()
window.geometry('800x600')
window.title("Glass Control Panel")


def rvEnable():
        button0.configure(bg='green')
        #button0.pack(pady=10, padx=10)
def kitchenLight():
        button1.configure(bg='green')
        #button1.pack(pady=10, padx=10)
def genStart():
        button2.configure(bg='green')
        #button2.pack(pady=10, padx=10)
def outsideLights():
        button3.configure(bg='green')
        #button3.pack(pady=10, padx=10)
def waterHeater():
        button4.configure(bg='green')
        #button4.pack(pady=10, padx=10)
def waterPump():
        button5.configure(bg='green')
        #button5.pack(pady=10, padx=10)
def step():
        button6.configure(bg='green')
        #button6.pack(pady=10, padx=10)
def porchLight():
        button7.configure(bg='green')
        #button7.pack(pady=10, padx=10)
def inverter():
        button8.configure(bg='green')
        #button8.pack(pady=10, padx=10)
def acStart():
        button9.configure(bg='green')
        #button9.pack(pady=10, padx=10)
def acDown():
        button10.configure(bg='green')
        #button10.pack(pady=10, padx=10)
def acUp():
        button11.configure(bg='green')
        #button11.pack(pady=10, padx=10)



#panel = Label(window, text="Just a freggin test, OK?")
#panel.pack(side = "top", fill = "y", expand = "yes")
T = Text(window, height = 1, width = 17)
def Button_Size():
   button0.configure(font=('Calibri 28 bold'))
def Button_Size():
   button1.configure(font=('Calibri 28 bold'))
def Button_Size():
   button2.configure(font=('Calibri 28 bold'))
def Button_Size():
   button3.configure(font=('Calibri 28 bold'))
def Button_Size():
   button4.configure(font=('Calibri 28 bold'))
def Button_Size():
   button5.configure(font=('Calibri 28 bold'))
def Button_Size():
   button6.configure(font=('Calibri 28 bold'))
def Button_Size():
   button7.configure(font=('Calibri 28 bold'))
def Button_Size():
   button8.configure(font=('Calibri 28 bold'))
def Button_Size():
   button9.configure(font=('Calibri 28 bold'))
def Button_Size():
   button10.configure(font=('Calibri 28 bold'))
def Button_Size():
   button11.configure(font=('Calibri 28 bold'))
def Button_Size():
   button12.configure(font=('Calibri 28 bold'))


button0=Button(window, text="RV Enable",
command=rvEnable, height = 5, width = 15).grid(row=1,column=0)
#button0.pack(pady=10, padx=10)

button1=Button(window, text="Kitchen Light",
command=kitchenLight, height = 5, width = 15).grid(row=1,column=1)
#button1.pack(pady=10, padx=10)

button2=Button(window, text="Generator Start",
command=genStart, height = 5, width = 15)
button2.grid(row=1,column=2)
#button2.pack(pady=10, padx=10)

button3=Button(window, text="Exterior Lights",
command=outsideLights, height = 5, width = 15)
button3.grid(row=1,column=3)
#button3.pack(pady=10, padx=10)

button4=Button(window, text="Water Heater",
command=waterHeater, height = 5, width = 15)
#button4.pack(pady=10, padx=10)
button4.grid(row=2,column=0)

button5=Button(window, text="Water Pump",
command=waterPump, height = 5, width = 15)
button5.grid(row=2,column=1)
#button5.pack(pady=10, padx=10)

button6=Button(window, text="Step",
command=step, height = 5, width = 15)
button6.grid(row=2,column=2)
#button6.pack(pady=10, padx=10)

button7=Button(window, text="Porch Light",
command=porchLight, height = 5, width = 15)
button7.grid(row=2,column=3)
#button7.pack(pady=10, padx=10)

button8=Button(window, text="Inverter",
command=inverter, height = 5, width = 15)
button8.grid(row=3,column=0)
#button8.pack(pady=10, padx=10)

button9=Button(window, text="A/C Start",
command=acStart, height = 5, width = 15)
button9.grid(row=4,column=1)
#button9.pack(pady=10, padx=10)

button10=Button(window, text="Temp Down",
command=acDown, height = 5, width = 15)
button10.grid(row=4,column=2)
#button10.pack(pady=10, padx=10)

button11=Button(window, text="Temp Up",
command=acUp, height = 5, width = 15)
button11.grid(row=4,column=3)
#button11.pack(pady=10, padx=10)


button12=Button(window, text="::LOADING::", height = 5, width = 15)
button12.grid(row=4,column=0)

# This is the event handler method that receives the Mosquito messages
def on_message(client, userdata, message, button12):
    msg = str(message.payload.decode("utf-8"))
    #print("message received " , msg)
    if "HI=" in msg:
        hi = msg.split("=")[2]
        hi =  hi.strip(" '")
        #button12.delete("1.0","end")
        buttonTxt = "Heat Index = {}".format(hi)

        print(buttonTxt)
        button12=Button(text=buttonTxt)
        #button12.update()

broker_address="127.0.0.1"
print("creating new instance")
client = mqtt.Client() #create new instance
client.username_pw_set("dale", "paleale")
client.on_message=on_message #attach function to callback

print("connecting to broker")
client.connect(broker_address) #connect to broker

print("Subscribing to topic","/feeds/stats")
client.subscribe("/feeds/stats")

 #Start the MQTT Mosquito process loop
client.loop_start() 

window.mainloop()