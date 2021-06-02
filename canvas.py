# Original author:  Michelle Weck

from tkinter import *  
from PIL import ImageTk,Image
import cv2  
import numpy as np
import os
import csv


ROOTDIR = os.path.abspath("imdir")
RESDIR = os.path.abspath("resultDir")
#print(ROOTDIR)
#print(RESDIR)

RESULT_CSV = os.path.abspath("result.csv")
#print(RESULT_CSV)

image_cnt = 0
scaleWidth = 0
scaleHeight = 0
sameimgcount = 0
imageLeft = 0
dirimages = []
update_list = []
showimages = []
polypoints = []

scalefactor = 0

mask = []
invertedMask = []

csv_file = open(RESULT_CSV, mode='r')
csv_reader = csv.reader(csv_file, delimiter=',')
for row in csv_reader:
    update_list.append(row[0])
csv_file.close()

for dirName, subdirList, fileList in os.walk(ROOTDIR):
    for fname in fileList:
        if (not fname.endswith(".pdf") and not fname.endswith(".mp4") and not fname.endswith(".PDF") and not fname.endswith(".MP4") and not fname.endswith(".tmp") and not fname.endswith(".db") and not fname in update_list):
            dirimages.append(dirName + "\\" +fname)
#print(dirimages)

imageLeft = len(dirimages)

root = Tk()
root.title("Beste App aller Zeiten")

###
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
maxScreenWidth = screenWidth*0.95
maxScreenHeight = screenHeight*0.85

##Fullscreen
root.state("zoomed")

def restartDrawing():
    canvas.delete('points')
    polypoints.clear()

    maskButton["state"] = DISABLED
    saveButton["state"] = DISABLED

def lastImage():
    global image_cnt
    global scalefactor
    global scaleWidth
    global scaleHeight
    global imageLeft
    global sameimgcount
    global mask
    global invertedMask
    global back

    maskButton["state"] = DISABLED
    saveButton["state"] = DISABLED
    backButton["state"] = DISABLED

    image_cnt -= 1

    ##Refresh
    canvas.delete('points')
    polypoints.clear()
    sameimgcount = 100
    outputSameImgCount.configure(text="Anzahl einzelner Masken zum jetzigen Bild: " + str(sameimgcount))
    mask = []
    invertedMask = []

    imageLeft += 1
    outputPicturesLeft.configure(text="Anzahl noch zu maskierenden Bildern: " + str(imageLeft))

    ##Load image
    img_pil = Image.open(dirimages[image_cnt])

    image_ratio = (img_pil.size[0]/img_pil.size[1])
    canvas_ratio = (maxScreenWidth/ maxScreenHeight)
    ##resize to screen length 
    if image_ratio > canvas_ratio:
        scalefactor = (maxScreenWidth/img_pil.size[0])
        print("Scalefactor: ", scalefactor)
        img_pil = img_pil.resize((round(img_pil.size[0]*scalefactor), round(img_pil.size[1]*scalefactor)), Image.ANTIALIAS)
    else:
        scalefactor = (maxScreenHeight/img_pil.size[1])
        print("Scalefactor: ", scalefactor)
        scaleHeight = round(img_pil.size[0]*scalefactor)
        scaleWidth = round(img_pil.size[1]*scalefactor)
        img_pil = img_pil.resize((scaleHeight, scaleWidth), Image.ANTIALIAS)

    ##Convert to PhotoImage (for tkinter)
    img = ImageTk.PhotoImage(img_pil) 
    showimages.append(img)

    ##Redraw Image in Canvas
    canvas.itemconfig(image_id, image=showimages[image_cnt])
        

def nextImage():
    global image_cnt
    global scalefactor
    global scaleWidth
    global scaleHeight
    global imageLeft
    global sameimgcount
    global mask
    global invertedMask

    maskButton["state"] = DISABLED
    saveButton["state"] = DISABLED
    backButton["state"] = NORMAL

    with open(RESULT_CSV, 'a', newline='') as file:
            writer = csv.writer(file,quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writeFile = os.path.split(dirimages[image_cnt])
            writer.writerow([writeFile[1]])

    image_cnt += 1

    if image_cnt < len(dirimages):
        ##Refresh
        canvas.delete('points')
        polypoints.clear()
        sameimgcount = 0
        outputSameImgCount.configure(text="Anzahl einzelner Masken zum jetzigen Bild: " + str(sameimgcount))
        mask = []
        invertedMask = []

        imageLeft -= 1
        outputPicturesLeft.configure(text="Anzahl noch zu maskierenden Bildern: " + str(imageLeft))

        ##Load image
        img_pil = Image.open(dirimages[image_cnt])

        image_ratio = (img_pil.size[0]/img_pil.size[1])
        canvas_ratio = (maxScreenWidth/ maxScreenHeight)
        ##resize to screen length 
        #print(image_ratio, canvas_ratio)
        if image_ratio > canvas_ratio:
            scalefactor = (maxScreenWidth/img_pil.size[0])
            print("Scalefactor: ", scalefactor)
            img_pil = img_pil.resize((round(img_pil.size[0]*scalefactor), round(img_pil.size[1]*scalefactor)), Image.ANTIALIAS)
        else:
            scalefactor = (maxScreenHeight/img_pil.size[1])
            print("Scalefactor: ", scalefactor)
            scaleHeight = round(img_pil.size[0]*scalefactor)
            scaleWidth = round(img_pil.size[1]*scalefactor)
            img_pil = img_pil.resize((scaleHeight, scaleWidth), Image.ANTIALIAS)
        
        ##Convert to PhotoImage (for tkinter)
        img = ImageTk.PhotoImage(img_pil) 
        showimages.append(img)

        ##Redraw Image in Canvas
        canvas.itemconfig(image_id, image=showimages[image_cnt]) 
    else:
        frame.destroy()
        canvas.destroy()
        endscreen = Label(root, text="Du bist fertig! ^^", font="50")
        endscreen.pack(side=TOP, expand=YES, fill=BOTH)
        print("Du bist fertig!")

def getxy(event):
    global scalefactor
    global scaleWidth
    global scaleHeight

    if event.x <= scaleHeight and event.y <= scaleWidth:
        polypoints.append((round(event.x/scalefactor), round(event.y/scalefactor)))
        #print(polypoints)
        x1, y1 = (event.x - 2), (event.y - 2)
        x2, y2 = (event.x + 2), (event.y + 2)
        canvas.create_oval(x1, y1, x2, y2, fill="#FF0000", tags = 'points')
        if len(polypoints) >= 2:
            canvas.create_line(polypoints[-1][0]*scalefactor, polypoints[-1][1]*scalefactor, polypoints[-2][0]*scalefactor, polypoints[-2][1]*scalefactor, tags = 'points')

        maskButton["state"] = NORMAL

def maskImage():
    global mask
    global invertedMask
    global scaleHeight
    global scaleWidth

    imgToMask = cv2.imread(dirimages[image_cnt])

    mask = imgToMask.copy()
    mask[:]= [0,0,0]

    ppt = np.array(polypoints, np.int32)
    ppt = ppt.reshape((-1, 1, 2))
    cv2.fillPoly(mask, [ppt], (255, 255, 255), 8)
    mask= cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    invertedMask = cv2.bitwise_not(mask)
    mask = cv2.bitwise_and(imgToMask,imgToMask,mask = mask)
    invertedMask= cv2.cvtColor(invertedMask, cv2.COLOR_GRAY2BGR)
    invertedMask = mask+invertedMask

    #Resize for show
    maskS = cv2.resize(mask, (img_pil.size[0],img_pil.size[1]))

    cv2.imshow("mask", maskS)

    saveButton["state"] = NORMAL

def saveImage():
    global mask
    global invertedMask
    global sameimgcount

    cv2.destroyWindow("mask")

    file = os.path.split(dirimages[image_cnt])
    path = file[0]
    filename = file[1]

    cv2.imwrite(RESDIR + '\\' + filename[:6] + '_' + str(sameimgcount+1) +'_'+ 'mask_0' + filename[6:], mask)
    cv2.imwrite(RESDIR + '\\' + filename[:6] + '_' + str(sameimgcount+1) +'_'+ 'mask_1' + filename[6:], invertedMask)

    #with open(RESULT_CSV, 'a', newline='') as file:
    #    writer = csv.writer(file,quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #    writer.writerow([filename[:6] + '_' + str(sameimgcount+1) +'_'+ 'mask_0' + filename[6:]])
    #    writer.writerow([filename[:6] + '_' + str(sameimgcount+1) +'_'+ 'mask_1' + filename[6:]])

    print('Sucessfully saved masked images!')

    sameimgcount += 1
    outputSameImgCount.configure(text="Anzahl einzelner Masken zum jetzigen Bild: " + str(sameimgcount))

    canvas.delete('points')
    polypoints.clear()

    maskButton["state"] = DISABLED
    saveButton["state"] = DISABLED

canvas = Canvas(root, height = maxScreenHeight, width = maxScreenWidth)
canvas.bind('<Button-1>', getxy)
canvas.pack(expand=1, fill=BOTH)

##Buttons
frame = Frame(root, relief=RAISED, borderwidth=1)
frame.pack(fill=BOTH, expand=True)

backButton = Button(frame, text='Zurück', state=DISABLED, command=lastImage)
backButton.pack(side=LEFT, padx=50, pady=5)

restartButton = Button(frame, text='Punkte löschen', command=restartDrawing)
restartButton.pack(side=LEFT, padx=50, pady=5)

maskButton = Button(frame, text='Maskieren', state=DISABLED, command=maskImage)
maskButton.pack(side=LEFT, padx=50, pady=5)

saveButton = Button(frame, text='Speichern', state=DISABLED,command=saveImage)
saveButton.pack(side=LEFT)

nextButton = Button(frame, text='Nächstes Bild', command=nextImage)
nextButton.pack(side=LEFT,padx=50, pady=5)

##Anzeige
outputPicturesLeft = Label(frame, text='Noch zu maskieren: ' + str(imageLeft))
outputPicturesLeft.pack(side=RIGHT, padx=50, pady=5)

outputSameImgCount = Label(frame, text='Masken zum jetzigen Bild: ' + str(sameimgcount))
outputSameImgCount.pack(side=RIGHT, padx=25, pady=5)

###First image
if not dirimages:
    frame.destroy()
    canvas.destroy()
    endscreen = Label(root, text="Du hast noch keine Bilder zum Maskieren im imdir Ordner hinterlegt!", font="50")
    endscreen.pack(side=TOP, expand=YES, fill=BOTH)
else:
    img_pil = Image.open(dirimages[image_cnt])


#print ("Image Dimensions (Width, Height): ", img_pil.size)
#print("Image Ratio: " , img_pil.size[0]/img_pil.size[1])
#print("Canvas Ratio: ", maxScreenWidth / maxScreenHeight)
#print("Screen Height: ", maxScreenHeight)

    image_ratio = (img_pil.size[0]/img_pil.size[1])
    canvas_ratio = (maxScreenWidth / maxScreenHeight)
    ##resize to screen length 
    if image_ratio > canvas_ratio:
        scalefactor = (maxScreenWidth/img_pil.size[0])
        print("Scalefactor: ", scalefactor)
        scaleHeight = round(img_pil.size[0]*scalefactor)
        scaleWidth = round(img_pil.size[1]*scalefactor)
        img_pil = img_pil.resize((round(img_pil.size[0]*scalefactor), round(img_pil.size[1]*scalefactor)), Image.ANTIALIAS)
    else:
        scalefactor = (maxScreenHeight/img_pil.size[1])
        print("Scalefactor: ", scalefactor)
        scaleHeight = round(img_pil.size[0]*scalefactor)
        scaleWidth = round(img_pil.size[1]*scalefactor)
        img_pil = img_pil.resize((scaleHeight, scaleWidth), Image.ANTIALIAS)

    ##Convert to PhotoImage (for tkinter)
    img = ImageTk.PhotoImage(img_pil) 
    showimages.append(img)
    image_id = canvas.create_image((0,0),anchor=NW, image=showimages[image_cnt])


root.mainloop()