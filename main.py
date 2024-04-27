from tkinter import *
import os
import ctypes
from PIL import Image, ImageFilter, ImageColor, ImageDraw
from PIL import ImageTk
from PIL import ImageOps
import imghdr
from collections import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import threading
def drawOnImage(canvas):
    style = ttk.Style()
    style.map("C.TButton",foreground=[('pressed', 'red'), ('active', 'blue')],background=[('pressed', '!disabled', 'black'), ('active', 'white')])
    style.configure('TButton', font=('calibri', 23, 'bold'),borderwidth='1')
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = True
    drawWindow = Toplevel(canvas.data.mainWindow)
    drawWindow.title = "Draw"
    drawFrame = Frame(drawWindow)
    redButton = ttk.Button(drawFrame, bg="red", width=2,command=lambda: colourChosen(drawWindow, canvas, "red"))
    redButton.grid(row=0, column=0)
    blueButton = ttk.Button(drawFrame, bg="blue", width=2, command=lambda: colourChosen(drawWindow, canvas, "blue"))
    blueButton.grid(row=0, column=1)
    greenButton = Button(drawFrame, bg="green", width=2, command=lambda: colourChosen(drawWindow, canvas, "green"))
    greenButton.grid(row=0, column=2)
    magentaButton = Button(drawFrame, bg="magenta", width=2, command=lambda: colourChosen(drawWindow, canvas, "magenta"))
    magentaButton.grid(row=1, column=0)
    cyanButton = Button(drawFrame, bg="cyan", width=2, command=lambda: colourChosen(drawWindow, canvas, "cyan"))
    cyanButton.grid(row=1, column=1)
    yellowButton = Button(drawFrame, bg="yellow", width=2, command=lambda: colourChosen(drawWindow, canvas, "yellow"))
    yellowButton.grid(row=1, column=2)
    orangeButton = Button(drawFrame, bg="orange", width=2, command=lambda: colourChosen(drawWindow, canvas, "orange"))
    orangeButton.grid(row=2, column=0)
    purpleButton = Button(drawFrame, bg="purple", width=2,command=lambda: colourChosen(drawWindow, canvas, "purple"))
    purpleButton.grid(row=2, column=1)
    brownButton = Button(drawFrame, bg="brown", width=2, command=lambda: colourChosen(drawWindow, canvas, "brown"))
    brownButton.grid(row=2, column=2)
    blackButton = Button(drawFrame, bg="black", width=2, command=lambda: colourChosen(drawWindow, canvas, "black"))
    blackButton.grid(row=3, column=0)
    whiteButton = Button(drawFrame, bg="white", width=2, command=lambda: colourChosen(drawWindow, canvas, "white"))
    whiteButton.grid(row=3, column=1)
    grayButton = Button(drawFrame, bg="gray", width=2,command=lambda: colourChosen(drawWindow, canvas, "gray"))
    grayButton.grid(row=3, column=2)
    drawFrame.pack(side=BOTTOM)
def colourChosen(drawWindow, canvas, colour):
    if canvas.data.image != None:
        canvas.data.drawColour = colour
        canvas.data.mainWindow.bind("<B1-Motion>",lambda event: drawDraw(event, canvas))
    drawWindow.destroy()
def drawDraw(event, canvas):
    if canvas.data.drawOn == True:
        x = int(round((event.x - canvas.data.imageTopX) * canvas.data.imageScale))
        y = int(round((event.y - canvas.data.imageTopY) * canvas.data.imageScale))
        draw = ImageDraw.Draw(canvas.data.image)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=canvas.data.drawColour,outline=None)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def closeHistWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.histWindowClose = True
def histogram(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    histWindow = Toplevel(canvas.data.mainWindow)
    histWindow.title("Histogram")
    canvas.data.histCanvasWidth = 350
    canvas.data.histCanvasHeight = 475
    histCanvas = Canvas(histWindow, width=canvas.data.histCanvasWidth,height=canvas.data.histCanvasHeight)
    histCanvas.pack()
    redSlider = Scale(histWindow, from_=-100, to=100, orient=HORIZONTAL, label="R")
    redSlider.pack()
    blueSlider = Scale(histWindow, from_=-100, to=100, orient=HORIZONTAL, label="B")
    blueSlider.pack()
    greenSlider = Scale(histWindow, from_=-100, to=100, orient=HORIZONTAL, label="G")
    greenSlider.pack()
    OkHistFrame = Frame(histWindow)
    OkHistButton = Button(OkHistFrame, text="OK", command=lambda: closeHistWindow(canvas))
    OkHistButton.grid(row=0, column=0)
    OkHistFrame.pack(side=BOTTOM)
    initialRGB = (0, 0, 0)
    changeColours(canvas, redSlider, blueSlider,greenSlider, histWindow, histCanvas, initialRGB)
def changeColours(canvas, redSlider, blueSlider,greenSlider, histWindow, histCanvas, previousRGB):
    if canvas.data.histWindowClose == True:
        histWindow.destroy()
        canvas.data.histWindowClose = False
    else:
        if canvas.data.image != None and histWindow.winfo_exists():
            R, G, B = canvas.data.image.split()
            sliderValR = redSlider.get()
            (previousR, previousG, previousB) = previousRGB
            scaleR = (sliderValR - previousR) / 100.0
            R = R.point(lambda i: i + int(round(i * scaleR)))
            sliderValG = greenSlider.get()
            scaleG = (sliderValG - previousG) / 100.0
            G = G.point(lambda i: i + int(round(i * scaleG)))
            sliderValB = blueSlider.get()
            scaleB = (sliderValB - previousB) / 100.0
            B = B.point(lambda i: i + int(round(i * scaleB)))
            canvas.data.image = Image.merge(canvas.data.image.mode, (R, G, B))
            canvas.data.imageForTk = makeImageForTk(canvas)
            drawImage(canvas)
            displayHistogram(canvas, histWindow, histCanvas)
            previousRGB = (sliderValR, sliderValG, sliderValB)
            canvas.after(200, lambda: changeColours(canvas, redSlider,blueSlider, greenSlider, histWindow, histCanvas, previousRGB))
def displayHistogram(canvas, histWindow, histCanvas):
    histCanvasWidth = canvas.data.histCanvasWidth
    histCanvasHeight = canvas.data.histCanvasHeight
    margin = 50
    if canvas.data.image != None:
        histCanvas.delete(ALL)
        im = canvas.data.image
        # x-axis
        histCanvas.create_line(margin - 1, histCanvasHeight - margin + 1,margin - 1 + 258, histCanvasHeight - margin + 1)
        xmarkerStart = margin - 1
        for i in range(0, 257, 64):
            xmarker = "%d" % (i)
            histCanvas.create_text(xmarkerStart + i,histCanvasHeight - margin + 7, text=xmarker)
        histCanvas.create_line(margin - 1,histCanvasHeight - margin + 1, margin - 1, margin)
        ymarkerStart = histCanvasHeight - margin + 1
        for i in range(0, histCanvasHeight - 2 * margin + 1, 50):
            ymarker = "%d" % (i)
            histCanvas.create_text(margin - 1 - 10,ymarkerStart - i, text=ymarker)
        R, G, B = im.histogram()[:256], im.histogram()[256:512],im.histogram()[512:768]
        for i in range(len(R)):
            pixelNo = R[i]
            histCanvas.create_oval(i + margin,histCanvasHeight - pixelNo / 100.0 - 1 - margin, i + 2 + margin,histCanvasHeight - pixelNo / 100.0 + 1 - margin,fill="red", outline="red")
        for i in range(len(G)):
            pixelNo = G[i]
            histCanvas.create_oval(i + margin, \
                                   histCanvasHeight - pixelNo / 100.0 - 1 - margin, i + 2 + margin,histCanvasHeight - pixelNo / 100.0 + 1 - margin,fill="green", outline="green")
        for i in range(len(B)):
            pixelNo = B[i]
            histCanvas.create_oval(i + margin, \
                                   histCanvasHeight - pixelNo / 100.0 - 1 - margin, i + 2 + margin,histCanvasHeight - pixelNo / 100.0 + 1 - margin,fill="blue", outline="blue")
def colourPop(canvas):
    canvas.data.cropPopToHappen = False
    canvas.data.colourPopToHappen = True
    canvas.data.drawOn = False
    messagebox.showinfo(title="Colour Pop", message="Click on a part of the image which you want in colour",parent=canvas.data.mainWindow)
    if canvas.data.cropPopToHappen == False:
        canvas.data.mainWindow.bind("<ButtonPress-1>", lambda event: getPixel(event, canvas))
def getPixel(event, canvas):
    try:
        if canvas.data.colourPopToHappen == True and \
                canvas.data.cropPopToHappen == False and canvas.data.image != None:
            data = []
            canvas.data.pixelx = \
                int(round((event.x - canvas.data.imageTopX) * canvas.data.imageScale))
            canvas.data.pixely = \
                int(round((event.y - canvas.data.imageTopY) * canvas.data.imageScale))
            pixelr, pixelg, pixelb = \
                canvas.data.image.getpixel((canvas.data.pixelx, canvas.data.pixely))
            tolerance = 60
            for y in range(canvas.data.image.size[1]):
                for x in range(canvas.data.image.size[0]):
                    r, g, b = canvas.data.image.getpixel((x, y))
                    avg = int(round((r + g + b) / 3.0))
                    if (abs(r - pixelr) > tolerance or
                            abs(g - pixelg) > tolerance or
                            abs(b - pixelb) > tolerance):
                        R, G, B = avg, avg, avg
                    else:
                        R, G, B = r, g, b
                    data.append((R, G, B))
            canvas.data.image.putdata(data)
            save(canvas)
            canvas.data.undoQueue.append(canvas.data.image.copy())
            canvas.data.imageForTk = makeImageForTk(canvas)
            drawImage(canvas)
    except:
        pass
    canvas.data.colourPopToHappen = False
def crop(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.drawOn = False
    canvas.data.cropPopToHappen = True
    messagebox.showinfo(title="Crop",message="Draw cropping rectangle and press Enter",parent=canvas.data.mainWindow)
    if canvas.data.image != None:
        canvas.data.mainWindow.bind("<ButtonPress-1>", lambda event: startCrop(event, canvas))
        canvas.data.mainWindow.bind("<B1-Motion>", lambda event: drawCrop(event, canvas))
        canvas.data.mainWindow.bind("<ButtonRelease-1>", lambda event: endCrop(event, canvas))
def startCrop(event, canvas):
    # detects the start of the crop rectangle
    if canvas.data.endCrop == False and canvas.data.cropPopToHappen == True:
        canvas.data.startCropX = event.x
        canvas.data.startCropY = event.y
def drawCrop(event, canvas):
    if canvas.data.endCrop == False and canvas.data.cropPopToHappen == True:
        canvas.data.tempCropX = event.x
        canvas.data.tempCropY = event.y
        canvas.create_rectangle(canvas.data.startCropX, canvas.data.startCropYcanvas.data.tempCropX, canvas.data.tempCropY, fill="gray", stipple="gray12", width=0)
def endCrop(event, canvas):
    if canvas.data.cropPopToHappen == True:
        canvas.data.endCrop = True
        canvas.data.endCropX = event.x
        canvas.data.endCropY = event.y
        canvas.create_rectangle(canvas.data.startCropX, canvas.data.startCropYcanvas.data.endCropX, canvas.data.endCropY, fill="gray", stipple="gray12", width=0)
        canvas.data.mainWindow.bind("<Return>",lambda event: performCrop(event, canvas))
def performCrop(event, canvas):
    canvas.data.image = \
        canvas.data.image.crop((int(round((canvas.data.startCropX - canvas.data.imageTopX) * canvas.data.imageScale)),
             int(round((canvas.data.startCropY - canvas.data.imageTopY) * canvas.data.imageScale)),
             int(round((canvas.data.endCropX - canvas.data.imageTopX) * canvas.data.imageScale)),
             int(round((canvas.data.endCropY - canvas.data.imageTopY) * canvas.data.imageScale))))
    canvas.data.endCrop = False
    canvas.data.cropPopToHappen = False
    save(canvas)
    canvas.data.undoQueue.append(canvas.data.image.copy())
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)
def rotateFinished(canvas, rotateWindow, rotateSlider, previousAngle):
    if canvas.data.rotateWindowClose == True:
        rotateWindow.destroy()
        canvas.data.rotateWindowClose = False
    else:
        if canvas.data.image != None and rotateWindow.winfo_exists():
            canvas.data.angleSelected = rotateSlider.get()
            if canvas.data.angleSelected != None and canvas.data.angleSelected != previousAngle:
                canvas.data.image = canvas.data.image.rotate(float(canvas.data.angleSelected))
                canvas.data.imageForTk = makeImageForTk(canvas)
                drawImage(canvas)
        canvas.after(200, lambda: rotateFinished(canvas,rotateWindow, rotateSlider, canvas.data.angleSelected))
def closeRotateWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.rotateWindowClose = True
def rotate(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    rotateWindow = Toplevel(canvas.data.mainWindow)
    rotateWindow.title("Rotate")
    rotateSlider = Scale(rotateWindow, from_=0, to=360, orient=HORIZONTAL)
    rotateSlider.pack()
    OkRotateFrame = Frame(rotateWindow)
    OkRotateButton = Button(OkRotateFrame, text="OK", command=lambda: closeRotateWindow(canvas))
    OkRotateButton.grid(row=0, column=0)
    OkRotateFrame.pack(side=BOTTOM)
    rotateFinished(canvas, rotateWindow, rotateSlider, 0)
def closeBrightnessWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.brightnessWindowClose = True
def changeBrightness(canvas, brightnessWindow, brightnessSlider, previousVal):
    if canvas.data.brightnessWindowClose == True:
        brightnessWindow.destroy()
        canvas.data.brightnessWindowClose = False
    else:
        if canvas.data.image != None and brightnessWindow.winfo_exists():
            sliderVal = brightnessSlider.get()
            scale = (sliderVal - previousVal) / 100.0
            canvas.data.image = canvas.data.image.point(lambda i: i + int(round(i * scale)))
            canvas.data.imageForTk = makeImageForTk(canvas)
            drawImage(canvas)
            canvas.after(200,lambda: changeBrightness(canvas, brightnessWindow,brightnessSlider, sliderVal))
def brightness(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    brightnessWindow = Toplevel(canvas.data.mainWindow)
    brightnessWindow.title("Brightness")
    brightnessSlider = Scale(brightnessWindow, from_=-100, to=100,orient=HORIZONTAL)
    brightnessSlider.pack()
    OkBrightnessFrame = Frame(brightnessWindow)
    OkBrightnessButton = Button(OkBrightnessFrame, text="OK",command=lambda: closeBrightnessWindow(canvas))
    OkBrightnessButton.grid(row=0, column=0)
    OkBrightnessFrame.pack(side=BOTTOM)
    changeBrightness(canvas, brightnessWindow, brightnessSlider, 0)
    brightnessSlider.set(0)
def reset(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = canvas.data.originalImage.copy()
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def mirror(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.mirror(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def flip(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.flip(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def transpose(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        imageData = list(canvas.data.image.getdata())
        newData = []
        newimg = Image.new(canvas.data.image.mode, (canvas.data.image.size[1], canvas.data.image.size[0]))
        for i in range(canvas.data.image.size[0]):
            addrow = []
            for j in range(i, len(imageData), canvas.data.image.size[0]):
                addrow.append(imageData[j])
            addrow.reverse()
            newData += addrow
        newimg.putdata(newData)
        canvas.data.image = newimg.copy()
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def covertGray(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        data = []
        for col in range(canvas.data.image.size[1]):
            for row in range(canvas.data.image.size[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                avg = int(round((r + g + b) / 3.0))
                R, G, B = avg, avg, avg
                data.append((R, G, B))
        canvas.data.image.putdata(data)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def sepia(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        sepiaData = []
        for col in range(canvas.data.image.size[1]):
            for row in range(canvas.data.image.size[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                avg = int(round((r + g + b) / 3.0))
                R, G, B = avg + 100, avg + 50, avg
                sepiaData.append((R, G, B))
        canvas.data.image.putdata(sepiaData)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def invert(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.invert(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def solarize(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    solarizeWindow = Toplevel(canvas.data.mainWindow)
    solarizeWindow.title("Solarize")
    solarizeSlider = Scale(solarizeWindow, from_=0, to=255, orient=HORIZONTAL)
    solarizeSlider.pack()
    OkSolarizeFrame = Frame(solarizeWindow)
    OkSolarizeButton = Button(OkSolarizeFrame, text="OK",command=lambda: closeSolarizeWindow(canvas))
    OkSolarizeButton.grid(row=0, column=0)
    OkSolarizeFrame.pack(side=BOTTOM)
    performSolarize(canvas, solarizeWindow, solarizeSlider, 255)
def performSolarize(canvas, solarizeWindow, solarizeSlider, previousThreshold):
    if canvas.data.solarizeWindowClose == True:
        solarizeWindow.destroy()
        canvas.data.solarizeWindowClose = False
    else:
        if solarizeWindow.winfo_exists():
            sliderVal = solarizeSlider.get()
            threshold_ = 255 - sliderVal
            if canvas.data.image != None and threshold_ != previousThreshold:
                canvas.data.image = ImageOps.solarize(canvas.data.image,threshold=threshold_)
                canvas.data.imageForTk = makeImageForTk(canvas)
                drawImage(canvas)
            canvas.after(200, lambda: performSolarize(canvas,solarizeWindow, solarizeSlider, threshold_))
def closeSolarizeWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.solarizeWindowClose = True
def posterize(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    posterData = []
    if canvas.data.image != None:
        for col in range(canvas.data.imageSize[1]):
            for row in range(canvas.data.imageSize[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                if r in range(32):
                    R = 0
                elif r in range(32, 96):
                    R = 64
                elif r in range(96, 160):
                    R = 128
                elif r in range(160, 224):
                    R = 192
                elif r in range(224, 256):
                    R = 255
                if g in range(32):
                    G = 0
                elif g in range(32, 96):
                    G = 64
                elif g in range(96, 160):
                    G = 128
                elif r in range(160, 224):
                    g = 192
                elif r in range(224, 256):
                    G = 255
                if b in range(32):
                    B = 0
                elif b in range(32, 96):
                    B = 64
                elif b in range(96, 160):
                    B = 128
                elif b in range(160, 224):
                    B = 192
                elif b in range(224, 256):
                    B = 255
                posterData.append((R, G, B))
        canvas.data.image.putdata(posterData)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
def keyPressed(canvas, event):
    if event.keysym == "z":
        undo(canvas)
    elif event.keysym == "y":
        redo(canvas)
def undo(canvas):
    if len(canvas.data.undoQueue) > 0:
        lastImage = canvas.data.undoQueue.pop()
        canvas.data.redoQueue.appendleft(lastImage)
    if len(canvas.data.undoQueue) > 0:
        canvas.data.image = canvas.data.undoQueue[-1]
    save(canvas)
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)
def redo(canvas):
    if len(canvas.data.redoQueue) > 0:
        canvas.data.image = canvas.data.redoQueue[0]
    save(canvas)
    if len(canvas.data.redoQueue) > 0:
        lastImage = canvas.data.redoQueue.popleft()
        canvas.data.undoQueue.append(lastImage)
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)
def saveAs(canvas):
    if canvas.data.image != None:
        filename = asksaveasfilename(defaultextension=".jpg")
        im = canvas.data.image
        im.save(filename)
def save(canvas):
    if canvas.data.image != None:
        im = canvas.data.image
        im.save(canvas.data.imageLocation)
def newImage(canvas):
    def call():
        while True:
            name = str(input("Name of the Photo : "))
            if name:
                imageName = name
                filetype = ""
                # make sure it's an image file
                try:
                    filetype = imghdr.what(imageName)
                except:
                    messagebox.showinfo(title="Image File",message="Choose an Image File!", parent=canvas.data.mainWindow)
                # restrict filetypes to .jpg, .bmp, etc.
                if filetype in ['jpeg', 'bmp', 'png', 'tiff']:
                    canvas.data.imageLocation = imageName
                    im = Image.open(name)
                    canvas.data.image = im
                    canvas.data.originalImage = im.copy()
                    canvas.data.undoQueue.append(im.copy())
                    canvas.data.imageSize = im.size  # Original Image dimensions
                    canvas.data.imageForTk = makeImageForTk(canvas)
                    drawImage(canvas)
                else:
                    messagebox.showinfo(title="Image File",message="Choose an Image File!", parent=canvas.data.mainWindow)
    threading.Thread(target=call).start()
def makeImageForTk(canvas):
    im = canvas.data.image
    if canvas.data.image != None:
        imageWidth = canvas.data.image.size[0]
        imageHeight = canvas.data.image.size[1]
        if imageWidth > imageHeight:
            resizedImage = im.resize((canvas.data.width,int(round(float(imageHeight) * canvas.data.width / imageWidth))))
            canvas.data.imageScale = float(imageWidth) / canvas.data.width
        else:
            resizedImage = im.resize((int(round(float(imageWidth) * canvas.data.height / imageHeight)),canvas.data.height))
            canvas.data.imageScale = float(imageHeight) / canvas.data.height
        canvas.data.resizedIm = resizedImage
        return ImageTk.PhotoImage(resizedImage)
def drawImage(canvas):
    if canvas.data.image != None:
        # make the canvas center and the image center the same
        canvas.create_image(canvas.data.width / 2.0 - canvas.data.resizedIm.size[0] / 2.0,
                            canvas.data.height / 2.0 - canvas.data.resizedIm.size[1] / 2.0,
                            anchor=NW, image=canvas.data.imageForTk)
        canvas.data.imageTopX = int(round(canvas.data.width / 2.0 - canvas.data.resizedIm.size[0] / 2.0))
        canvas.data.imageTopY = int(round(canvas.data.height / 2.0 - canvas.data.resizedIm.size[1] / 2.0))
def desktopBk(canvas):
    if canvas.data.image != None:
        new = canvas.data.image.copy()
        newLocation = os.path.dirname( \
            canvas.data.imageLocation) + "/desktopPhoto.bmp"
        new.save(newLocation)
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, str(newLocation), 0)
def init(root, canvas):
    buttonsInit(root, canvas)
    menuInit(root, canvas)
    canvas.data.image = None
    canvas.data.angleSelected = None
    canvas.data.rotateWindowClose = False
    canvas.data.brightnessWindowClose = False
    canvas.data.brightnessLevel = None
    canvas.data.histWindowClose = False
    canvas.data.solarizeWindowClose = False
    canvas.data.posterizeWindowClose = False
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.endCrop = False
    canvas.data.drawOn = True
    canvas.data.undoQueue = deque([], 10)
    canvas.data.redoQueue = deque([], 10)
    canvas.pack()
def buttonsInit(root, canvas):
    style = ttk.Style()
    style.map("C.TButton",
              foreground=[('pressed', 'red'), ('active', 'blue')],
              background=[('pressed', '!disabled', 'black'), ('active', 'white')])
    style.configure('TButton', font=('Comic Sans MS', 15),borderwidth='0.5')
    buttonWidth = 14
    buttonHeight = 2
    toolKitFrame = Frame(root)
    cropButton = ttk.Button(toolKitFrame, text="Crop", command=lambda: crop(canvas))
    cropButton.grid(row=0, column=0)
    rotateButton = ttk.Button(toolKitFrame, text="Rotate",command=lambda: rotate(canvas))
    rotateButton.grid(row=1, column=0)
    brightnessButton = ttk.Button(toolKitFrame, text="Brightness",command=lambda: brightness(canvas))
    brightnessButton.grid(row=2, column=0)
    histogramButton = ttk.Button(toolKitFrame, text="Histogram",command=lambda: histogram(canvas))
    histogramButton.grid(row=3, column=0)
    colourPopButton = ttk.Button(toolKitFrame, text="Colour Pop",command=lambda: colourPop(canvas))
    colourPopButton.grid(row=4, column=0)
    mirrorButton = ttk.Button(toolKitFrame, text="Mirror",command=lambda: mirror(canvas))
    mirrorButton.grid(row=5, column=0)
    flipButton = ttk.Button(toolKitFrame, text="Flip",command=lambda: flip(canvas))
    flipButton.grid(row=6, column=0)
    transposeButton = ttk.Button(toolKitFrame, text="Transpose",command=lambda: transpose(canvas))
    transposeButton.grid(row=7, column=0)
    drawButton = ttk.Button(toolKitFrame, text="Draw",command=lambda: drawOnImage(canvas))
    drawButton.grid(row=8, column=0)
    resetButton = ttk.Button(toolKitFrame, text="Reset",command=lambda: reset(canvas))
    resetButton.grid(row=9, column=0)
    toolKitFrame.pack(side=LEFT)
def menuInit(root, canvas):
    menubar = Menu(root)
    menubar.add_command(label="New", command=lambda: newImage(canvas))
    menubar.add_command(label="Save", command=lambda: save(canvas))
    menubar.add_command(label="Save As", command=lambda: saveAs(canvas))
    ## Edit pull-down Menu
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo   Z", command=lambda: undo(canvas))
    editmenu.add_command(label="Redo   Y", command=lambda: redo(canvas))
    menubar.add_cascade(label="Edit", menu=editmenu)
    root.config(menu=menubar)
    filtermenu = Menu(menubar, tearoff=0)
    filtermenu.add_command(label="Black and White", command=lambda: covertGray(canvas))
    filtermenu.add_command(label="Sepia", command=lambda: sepia(canvas))
    filtermenu.add_command(label="Invert", command=lambda: invert(canvas))
    filtermenu.add_command(label="Solarize", command=lambda: solarize(canvas))
    filtermenu.add_command(label="Posterize", command=lambda: posterize(canvas))
    menubar.add_cascade(label="Filter", menu=filtermenu)
    root.config(menu=menubar)
def run():
    root = Tk()
    root.title("Ignora")
    canvasWidth = 500
    canvasHeight = 500
    canvas = Canvas(root, width=canvasWidth, height=canvasHeight,background="#ffffff")
    class Struct: pass
    canvas.data = Struct()
    canvas.data.width = canvasWidth
    canvas.data.height = canvasHeight
    canvas.data.mainWindow = root
    init(root, canvas)
    root.bind("<Key>", lambda event: keyPressed(canvas, event))
    root.mainloop()
run()









