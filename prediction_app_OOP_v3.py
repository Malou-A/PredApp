#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 12:32:36 2021

@author: malou
"""

from tkinter import Tk, Scale, SUNKEN, RAISED, LEFT, IntVar, PhotoImage, DISABLED, ACTIVE, Label, Frame, Listbox, Scrollbar, HORIZONTAL, Button, Checkbutton, END
from tkinter import filedialog
import os
from PIL import ImageTk,Image
import skimage
import skimage.io
from skimage import img_as_float, img_as_ubyte
import skimage.morphology
from skimage.transform import resize
from skimage.color import rgb2lab, label2rgb, rgb2gray
from skimage import exposure
import tkinter.messagebox
import skimage.segmentation
import numpy as np
from skimage.draw import disk
from scipy import ndimage


class MainWindow:
    def __init__(self, root):
        self.root = root
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.ImageLab = Label(self.root, text = "Images in choosen directory")
        self.ImageLab.place(x = 25 + int(w*0.35/2), y = 40, anchor = "center")

        # Create a frame for listbox to be able to include scrollbar.
        self.Listframe = Frame(self.root)
        self.Listframe.place(x = 25, y = int(h*0.08), width = int(w*0.35), height =  im_frame_height)
            
        self.ImageList = Listbox(self.Listframe, bg = "white")
        self.ImageList.pack(side = "left", fill = "both", expand = True)
        
        if image_path:
            self.PopListBox(image_path) 
            
        self.scrollbar = Scrollbar(self.Listframe, orient="vertical")
        self.scrollbar.config(command=self.ImageList.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.ImageList.config(yscrollcommand=self.scrollbar.set)
        self.ImageList.bind("<<ListboxSelect>>", self.callback)
   
        # Creating the "label" that will contain the image preview.
        self.panel = Label(self.root, width = im_frame_width, height = im_frame_height)
        self.panel.place(x=int(w*0.4), y = int(h*0.08))
        
        self.B1 = Button(self.root, text = "Select Image directory", command = self.open_dir)
        self.B1.place(x = 15 + int(w*0.35/2), y = int(30+ h*0.88), anchor = "center", width = 300)

        # Create frame to align buttons nicely with image panel.
        self.button_frame = Frame(self.root)
        self.button_frame.place(x = int(w*0.4), y = int(h*0.88), width = im_frame_width, height = int(h*0.08))

        x_step = (im_frame_width - 450)/3
        x_step = x_step + 150

        self.B2 = Button(self.button_frame, text = "Nuclei model", command = lambda: self.get_channel('nuclei'))
        self.B2.place(x = 20, y = 20 , width = 150)
        self.B3 = Button(self.button_frame, text = "Cell model", command = lambda: self.get_channel('cell'))
        self.B3.place(x = x_step+20, y = 20, width = 150)
        self.B4 = Button(self.button_frame, text = "Lysosome model", command = lambda: self.get_channel('lysosome'))
        self.B4.place(x = 2*x_step +20 , y = 20, width = 150) 
    
    def PopListBox(self, image_path): 
        if image_path != "/":
            images = os.listdir(image_path)    
        else:    
            image_path = self.old_image_path           
            images = os.listdir(image_path)
        # Populate the image list from the selected or default folder
        for image in images:
            if image.endswith(".png"):
                self.ImageList.insert(END,image)
        
    def open_dir(self):
        global image_path, images
        if image_path:
            self.ImageList.delete(0,END)
        self.old_image_path = image_path
        image_path = filedialog.askdirectory(initialdir = root_dir) + "/"
        # Action to keep previous image path if non is choosen.
        self.PopListBox(image_path)
    
    def get_channel(self, channel):

        SecondFrame(self.root, channel, self.img)
    
    def callback(self, event):
        global image, imframeX
        # Gives selection object, which contain the index.
        selection = event.widget.curselection()
        if selection:
            # If a selection is made, the selection[0] retrieves the name in the list corresponding to the index from selection.
            image = event.widget.get(selection[0])
            # Open the image and also resize it to the same size as "panel" which is containing the image.
            self.img = skimage.io.imread(image_path + image)
            imframeX = self.img.shape[0]
            imagewindow = PanelWindow(self.root, self.panel, self.img)
            imagewindow.panel_config()

class SecondFrame:
    def __init__(self, root, channel, img):
        global pred_path
        self.img = img
        self.root = root
        self.channel = channel
        pred_path = channels[self.channel]
        w = 1000
        h = 700
        im_frame_width = int(h*0.8)
        im_frame_height = int(h*0.8)
        
        self.root.geometry("{}x{}+{}+{}".format(w, h, int(x), int(y)))
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.panel = Label(self.root, width = im_frame_width, height = im_frame_height)
        self.panel.place(x=int(w*0.65), y = int(h*0.5), anchor = "center")
        
        self.imagewindow = PanelWindow(self.root, self.panel, self.img, self.channel)#, self.var1, self.var2, self.var3, self.var4)
        
        self.circle = Checkbutton(self.root, text = "Mark with circles", variable = self.imagewindow.var1, command = self.imagewindow.check_function)
        self.circle.place(x = 0.1*w, y = h*0.2)
    
        if self.channel == "nuclei" or self.channel == "cell":
            self.circle.config(state=DISABLED)
        else:
            self.circle.config(state=ACTIVE)
    
        self.labels = Checkbutton(self.root, text = "Add labels", variable = self.imagewindow.var2, command = self.imagewindow.check_function)
        self.labels.place(x = 0.1*w, y = h*0.2 + 20)
    
        self.brighten = Checkbutton(self.root, text = "Brighten image", variable = self.imagewindow.var3, command = self.imagewindow.check_function)
        self.brighten.place(x = 0.1*w, y = h*0.2 + 40)
    
        self.boundaries = Checkbutton(self.root, text = "Mark boundaries", variable = self.imagewindow.var4, command = self.imagewindow.check_function)
        self.boundaries.place(x = 0.1*w, y = h*0.2 + 60)
    
        self.B1 = Button(self.root, text = "Back", command = lambda: MainWindow(self.root))
        self.B1.place(x = int(w*0.20/2), y = int(35+ h*0.88), anchor = "center", width = 150)
        
        self.B2 = Button(self.root, text = "Edit annotation", 
                         command = lambda: ThirdFrame(self.root, self.imagewindow.img, self.imagewindow.x0, self.imagewindow.x1, self.imagewindow.y0, self.imagewindow.y1,
                                                                                           self.imagewindow.x0s, self.imagewindow.x1s, self.imagewindow.y0s, self.imagewindow.y1s, self.channel ))
        self.B2.place(x=int(w*0.65), y = int(35+ h*0.88), anchor = "center", width = 150)
        
        self.B3 = Button(self.root, text = "Exit", command = self.root.destroy)
        self.B3.place(x = 160 + int(w*0.20/2), y = int(35+ h*0.88), anchor = "center", width = 150)
            
        self.ImNameLab = Label(root, text = image, width = im_frame_width, height = 5)
        self.ImNameLab.place(x=int(w*0.65), y = 30, anchor = "center")
 
        self.root.bind('<Left>', self.left)
        self.root.bind('<Right>', self.right)
        """Bind arrows to get next or previous image"""
    def left(self, event):
        global image
        images = os.listdir(image_path)
        im_index = images.index(image)-1
        image = images[im_index]
        self.img = skimage.io.imread(image_path + image)
        self.imagewindow.check_function()
        self.ImNameLab.configure(text = image)
            
    def right(self, event):
        global image
        images = os.listdir(image_path)
        im_index = images.index(image)+1
        image = images[im_index]
        self.img = skimage.io.imread(image_path + image)
        self.imagewindow.check_function()
        self.ImNameLab.configure(text = image)
        
class ThirdFrame:
    def __init__(self, root, img, x0, x1, y0, y1,x0s,x1s,y0s,y1s, channel):
        global w, h, im_frame_width, im_frame_height
        self.root = root
        w = 800
        h = 800
        self.root.geometry("{}x{}+{}+{}".format(w, h, int(x), int(y)))
        self.img = img
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.x0s = x0s
        self.x1s = x1s
        self.y0s = y0s
        self.y1s = y1s
        self.channel = channel
        
        if self.img.shape[0] != im_frame_width:
            self.img = resize(self.img,(im_frame_width, im_frame_height),anti_aliasing=False,order=0, preserve_range=True)     
            
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.B1 = Button(self.root, text = "Back", command = lambda: SecondFrame(self.root, self.channel, self.img))
        self.B1.place(x = int(w*0.30/2), y = int(55+ h*0.88), anchor = "center", width = 150)
        
        self.B3 = Button(self.root, text = "Exit", command = self.root.destroy)
        self.B3.place(x = 160 + int(w*0.30/2), y = int(55+ h*0.88), anchor = "center", width = 150)
            
        global undo, pencil, wand, eraser, zoomin, pensize, brighten, labels, recompile
        
        self.buttonframe = Frame(self.root ,width = im_frame_width , height = int(im_frame_height/4))
        self.buttonframe.place(x=int(w*0.5), y = int(h*0.40 + (im_frame_height/2) + (im_frame_height/6)), anchor = "center")
         
              
        self.panel = Label(self.root, width = im_frame_width, height = im_frame_height)
        self.panel.place(x=int(w*0.5), y = int(h*0.40), anchor = "center")       
        
        self.imagewindow = PanelWindow(self.root, self.panel, 
                                       self.img, x0 = self.x0, 
                                       x1 = self.x1, y0 = self.y0, 
                                       y1 = self.y1, x0s = self.x0s, 
                                       x1s = self.x1s, y0s = self.y0s, 
                                       y1s = self.y1s, channel = self.channel)
        #self.imagewindow.panel_config()
 
        
        
        self.pencil_im = PhotoImage(file = "icons/pencil.png")
        self.undo_im = PhotoImage(file = "icons/undo.png")
        self.wand_im = PhotoImage(file = "icons/wand.png")
        self.eraser_im = PhotoImage(file = "icons/eraser.png")
        self.zoomin_im = PhotoImage(file = "icons/zoomIn.png")
        self.download_im = PhotoImage(file = "icons/download.png")
        self.recompile_im = PhotoImage(file = "icons/recompile.png")
        #self.zoomout_im = PhotoImage(file = icon_dir + "zoomOut.png")
        
        
        
        
        labels = Checkbutton(self.root, text = "Hide labels", variable = self.imagewindow.var5, command = self.imagewindow.check_function)
        labels.place(x = 0.7*w, y = int(h*0.40 + (im_frame_height/2) + 10))
        
        brighten = Checkbutton(self.root, text = "Brighten image", variable = self.imagewindow.var3, command = self.imagewindow.check_function)
        brighten.place(x = 0.5*w, y = int(h*0.40 + (im_frame_height/2) + 10))
        
        circle = Checkbutton(self.root, text = "Add circles", variable = self.imagewindow.var1, command = self.imagewindow.check_function)
        circle.place(x = 0.3*w, y = int(h*0.40 + (im_frame_height/2) + 10))
        if self.channel == "nuclei" or self.channel == "cell":
            circle.config(state=DISABLED)
        
        pensize = IntVar()
        self.pensize_slider = Scale(self.root, variable = pensize, from_=1, to = 20, command = self.imagewindow.set_pensize, orient = HORIZONTAL)
        self.pensize_slider.set(5)
        self.pensize_slider.place(x = int(w*0.2),  y = int(h*0.40 + (im_frame_height/2) + 20), anchor = "center")
        
            
        
        undo = Button(self.buttonframe, width = 50, height = 50, image = self.undo_im, command = self.imagewindow.undo)
        undo.image = self.undo_im
        #undo.grid(row = 0, column = 1)
        undo.pack(side = LEFT)
        
              
        pencil = Button(self.buttonframe, image = self.pencil_im, command = self.imagewindow.pencil_draw)
        pencil.image = self.pencil_im
        pencil.pack(side = LEFT)
        #pencil.grid(row = 1, column = 2)
        
        wand = Button(self.buttonframe, image = self.wand_im, command = self.imagewindow.edit_label)
        wand.image = self.wand_im
        wand.pack(side = LEFT)
        
        eraser = Button(self.buttonframe, image = self.eraser_im, command = self.imagewindow.erase)
        eraser.image = self.eraser_im
        eraser.pack(side = LEFT)
        
        zoomin = Button(self.buttonframe, image = self.zoomin_im, command = self.imagewindow.zoom_on)
        zoomin.image = self.zoomin_im
        zoomin.pack(side = LEFT)
        
        download = Button(self.buttonframe, image = self.download_im, command = self.imagewindow.download)
        download.image = self.download_im
        download.pack(side = LEFT)
        
        recompile = Button(self.buttonframe, image = self.recompile_im, command = self.imagewindow.recompile)
        recompile.image = self.recompile_im
        recompile.pack(side = LEFT)
        self.imagewindow.draw()
        #zoomout = Button(self.buttonframe, image = self.zoomout_im)
        #zoomout.image = self.zoomout_im
        #zoomout.pack(side = LEFT)
        #self.B1.place(x = int(w*0.20/2), y = int(h*0.88), anchor = "center", width = 150)
        
            
            

class PanelWindow:
    def __init__(self, root, panel, img, channel = None, x0 = 0, x1 = 0, y0 = 0, y1 = 0, x0s = [], x1s = [], y0s = [], y1s = []):
        self.root = root
        self.panel = panel
        self.image = image
        self.image_path = image_path
        self.img = img
        self.x0s = x0s
        self.x1s = x1s
        self.y0s = y0s
        self.y1s = y1s
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.imshapeX = imframeX
        if self.img.shape[0] != im_frame_width:
            self.img = resize(self.img,(im_frame_width, im_frame_height),anti_aliasing=False,order=0, preserve_range=True)
        #self.reset_vars()
        self.var1 = IntVar()
        self.var2 = IntVar()
        self.var3 = IntVar()
        self.var4 = IntVar()
        self.var5 = IntVar()
        self.channel = channel
        self.DRAW = False
        self.check_function()
        self.zoom_bind()
        
    def panel_config(self):        

        if isinstance(self.img, np.ndarray):
            if ((self.channel == "nuclei" or self.channel == "cell") and self.var2.get() == True) or self.var4.get() == True:
                PIL_img = Image.fromarray(self.img,"RGB").resize((im_frame_width, im_frame_height))
            else:
                PIL_img =  Image.fromarray(self.img).resize((im_frame_width, im_frame_height))      
        else:
            PIL_img = self.img
            
        img = ImageTk.PhotoImage(PIL_img)
        self.panel.configure(image=img)
        self.panel.image = img  
    
    def get_label(self):
        global pred_path
        if not os.path.isfile(pred_path + image):
            tkinter.messagebox.showinfo("Error", "Labels are missing, please select another image")
            MainWindow(self.root)
            return
        label_im = skimage.io.imread(pred_path + image)
        #print(np.unique(label_im))
        #label_im = img_as_float(label_im)

        if len(label_im.shape) > 2:
            label_im = rgb2lab(label_im)
            label_im = label_im[:,:,0]
        label_im = skimage.morphology.label(label_im)
        #label_im = label_im/(len(np.unique(label_im)))
        #print(np.unique(label_im))
        
        return label_im            
    
    def crop_im(self, im,x0,x1,y0,y1):
        im = im[y0:y1,x0:x1]
        im = resize(im,(im_frame_width, im_frame_height),anti_aliasing=False,order=0, preserve_range=True)
        return(im)
    
    def get_boundaries(self, label_im, cell_im):
        boundaries = skimage.segmentation.find_boundaries(label_im)

        if len(cell_im.shape) > 2:
            pass
        else:
            cell_im =  np.dstack((cell_im,)*3)

        cell_im[boundaries == 1, 0] = 1
        cell_im[boundaries == 1, 1] = 0
        cell_im[boundaries == 1, 2] = 0
        return(cell_im)
    
    def image_configure(self, image):
        
        if any([self.x0,self.x1,self.y0,self.y1]):
            image = self.crop_im(image, self.x0,self.x1,self.y0,self.y1)
        
        self.img = resize(image,(im_frame_width, im_frame_height),anti_aliasing=False,order=0, preserve_range=True)      
        self.img = img_as_ubyte(self.img)
        self.panel_config()
        
    def check_function(self):

        cell_im = skimage.io.imread(image_path + image)
        cell_im = img_as_float(cell_im)   

        if self.var3.get() == True:    
            v_min, v_max = np.percentile(cell_im, (2.2, 97.8))
            cell_im = exposure.rescale_intensity(cell_im, in_range = (v_min, v_max))       
                
        if not self.var5.get() and self.DRAW:
            cell_im = self.draw_im.copy()
            #if self.lab_color == 0:
            #    cell_im[self.mask_im]
            if self.lab_color != 0:
                cell_im[self.mask_im == 1 ] = self.lab_color
                cell_im[self.filled_im == 1] = self.lab_color  
            
        if self.var1.get():  
            label_im = self.get_label()
            circle_im = skimage.transform.hough_circle(label_im, radius = 10, normalize = True)
            circle_im = circle_im[0]
            cell_im[circle_im > 0] = 0.5
            
        if self.var2.get():
            label_im = self.get_label()
            if self.channel == "lysosome":
                cell_im[label_im > 0] = 1
            else:
                cell_im = label2rgb(label_im, image = cell_im, bg_label=0)
            
        if self.var4.get():
            label_im = self.get_label()
            cell_im = self.get_boundaries(label_im, cell_im)
        
        self.image_configure(cell_im)
        
      
    def reset_vars(self):  
        self.x0s = []
        self.x1s = []
        self.y0s = []
        self.y1s = []
        self.x0 = 0
        self.x1 = 0
        self.y0 = 0
        self.y1 = 0
        
    def zoom_in(self,eventorigin):
        x = eventorigin.x
        y = eventorigin.y
        
        self.x0,self.x1,self.y0,self.y1 = self.get_coords(x,y)
        
        self.check_function()
        
    def zoom_out(self,eventorigin):
        self.reset_vars()
        self.check_function()
        
    def zoom_bind(self):
        self.panel.bind("<Button 1>", self.zoom_in)
        self.panel.bind("<Button 3>", self.zoom_out)
    
    def zoom_unbind(self):
        self.panel.unbind("<Button 1>")
        self.panel.unbind("<Button 3>")
        
    def get_coords(self,x,y):
        multiplyerX = (self.imshapeX/im_frame_width)
        wwidth = self.imshapeX
        wheight = self.imshapeX
        cropsize =round(150*multiplyerX)
        cropfrac = (2*cropsize)/self.imshapeX
        x = round(x*multiplyerX)
        y = round(y*multiplyerX)
        
        if y < cropsize + 1:
            y0 = 0
            y1 = 2*cropsize + 1
        elif wheight-y < cropsize + 1:
            y1 = wheight
            y0 = wheight-(2*cropsize)
        else:
            y0 = y - cropsize
            y1 = y + cropsize
        if x < cropsize + 1:
            x0 = 0
            x1 = 2*cropsize + 1
        elif wwidth-x < cropsize + 1:
            x1 = wwidth
            x0 = wwidth-(2*cropsize)
        else:
            x0 = x - cropsize
            x1 = x + cropsize
        exponent = len(self.x0s)
        x0 = x0*(cropfrac**(exponent))
        x1 = x1*(cropfrac**(exponent))
        y0 = y0*(cropfrac**(exponent))
        y1 = y1*(cropfrac**(exponent))
        
        self.x0s.append(x0)
        self.x1s.append(x1)
        self.y0s.append(y0)
        self.y1s.append(y1)
        
        x0 = int(sum(self.x0s))
        y0 = int(sum(self.y0s))
        x1 = int(round(x0 + (self.x1s[-1]-self.x0s[-1])))
        y1 = int(round(y0 + (self.y1s[-1]-self.y0s[-1])))
        
        return x0, x1, y0, y1
            
        
    def motion(self, event):       
        

        xmult, ymult = self.get_multi() 
            
        rr, cc = disk((int(event.y*ymult) + self.y0, int(event.x*xmult) + self.x0), self.pensize)
      
            
        rr[rr < 0] = 0
        rr[rr > self.imshapeX - 1] = self.imshapeX-1
        cc[cc < 0] = 0
        cc[cc > self.imshapeX - 1] = self.imshapeX-1
        
        if self.Eraser:
            
            self.draw_im[rr,cc] = self.orig_im[rr,cc]
            self.label_im[rr,cc] = 0
            self.check_function()
            
        else:
            self.mask_im[rr,cc] = 1
            self.check_function()
   
    def fill_holes(self, event):
        self.old_im = self.filled_im.copy()
        
        self.filled_im = ndimage.binary_fill_holes(self.mask_im)
        self.check_function()
        
        if self.lab_color != 0:
            self.label_im[self.mask_im == 1] = self.lab_color
            self.label_im[self.filled_im == 1] = self.lab_color
       
        
        
    def undo(self, event = None):

        if self.Eraser:
            self.draw_im = self.old_draw.copy()
            self.label_im = self.old_lab.copy()
        self.filled_im = self.old_im.copy()
        self.mask_im = self.old_im.copy()
        
        self.check_function()
        
        
    def zoom_on(self, event=None):
        if self.zoom == False:
            zoomin.config(relief = SUNKEN)
            self.raise_buttons(zoomin)
            self.zoom = True
            self.zoom_bind()
            self.panel.unbind('<B1-Motion>')
            self.panel.unbind("<ButtonRelease-1>")
            self.panel.config(cursor = "plus")

    def reset_mask(self):
        if self.lab_color != 0:
            self.draw_im[self.filled_im == 1] = self.lab_color
        self.mask_im[self.filled_im == 1] = 0 
        self.filled_im = self.mask_im.copy()
           
    def get_multi(self):
        if any([self.x0,self.x1,self.y0,self.y1]):
            xcrop = self.x1-self.x0
            ycrop = self.y1-self.y0
            xmult = xcrop/im_frame_width
            ymult = ycrop/im_frame_height
        else:
            xmult = self.imshapeX/im_frame_width
            ymult = self.imshapeX/im_frame_height
        return xmult, ymult
    
    def get_color(self,event):
        xmult, ymult = self.get_multi()   
        
        x = round(event.x*xmult + self.x0)
        y = round(event.y*ymult + self.y0)
        if self.lab_color != self.label_im[y,x]:
            self.reset_mask()
            self.lab_color = self.label_im[y,x]                  
            #self.check_function()
        
    def edit_label(self, event = None):
        if self.Edit == False:
            wand.config(relief = SUNKEN)
            self.raise_buttons(wand)
            self.Edit = True
            self.panel.bind("<Button-1>", self.get_color)

    def raise_buttons(self, button):
        buttonlist = [undo, pencil, wand, eraser, zoomin]
        buttonlist.remove(button)
        for b in buttonlist:
            b.config(relief = RAISED)
        self.Eraser = False
        self.Edit = False
        self.panel.unbind("<Button-1>")
        self.zoom = False
        self.zoom_unbind()
        self.panel.bind('<B1-Motion>', self.motion)
        self.panel.bind("<ButtonRelease-1>", self.fill_holes)
        self.panel.config(cursor = "dot")
    def save_old_im(self, event):
        #pass
        # self.reset_mask()
        self.old_draw = self.draw_im.copy()
        self.old_lab = self.label_im.copy()
        # print("saved old")

    def set_pensize(self, event):    
        self.pensize = pensize.get()
        
    def erase(self, event = None):
        if self.Eraser == False:
            self.reset_mask()
            eraser.config(relief = SUNKEN)
            self.raise_buttons(eraser)
            self.panel.bind("<Button-1>", self.save_old_im)
            self.old_lab = self.label_im.copy()
            self.Eraser = True
        else:
            self.panel.unbind("<Button-1>")
    def pencil_draw(self, event = None):
        self.reset_mask()
        self.lab_color = 1
        pencil.config(relief = SUNKEN)
        self.raise_buttons(pencil)
        self.panel.bind('<B1-Motion>', self.motion)
        self.panel.bind("<ButtonRelease-1>", self.fill_holes)
    def recompile(self):
        
        #self.label_im[self.filled_im == 1] = self.lab_color
        self.reset_mask()
        self.check_function()
        new_label_im = self.label_im.copy()
        new_label_im[self.filled_im == 1] = self.lab_color
        new_label_im = img_as_ubyte(new_label_im)
        labels = skimage.morphology.label(new_label_im)
        self.label_im = labels/len(np.unique(new_label_im))
       
        self.draw_im = img_as_float(skimage.io.imread(image_path + image))
        self.draw_im[self.label_im > 0] = 0
        self.draw_im = self.draw_im.copy() + self.label_im.copy()
        #self.reset_mask()
        self.check_function()
    
    def download(self):
        if self.channel != "lysosome":
            self.recompile()
        
        skimage.io.imsave("new_labels/" + self.channel + "/" + image,self.label_im)

    
    def hide_labels(self, event):
        labels.toggle()
        self.check_function()
        
    def toggle_bright(self, event):
        brighten.toggle()
        self.check_function()
        
    def draw(self): 
        self.DRAW = True
        self.Edit = False
        self.Eraser = False
        self.mask_im = np.zeros((self.imshapeX,self.imshapeX), dtype=np.uint8)
        #self.label_im = self.mask_im.copy() 
        self.filled_im = self.mask_im.copy()
        self.panel.bind('<B1-Motion>', self.motion)
        self.panel.bind("<ButtonRelease-1>", self.fill_holes)
        self.zoom = False
        self.zoom_unbind()
        
        
        self.label_im = skimage.io.imread(pred_path + image)
        if self.channel != "lysosome":
            self.label_im = rgb2gray(self.label_im)    
            self.label_im = img_as_ubyte(self.label_im)
            self.label_im = skimage.morphology.label(self.label_im)
            self.label_im = self.label_im/len(np.unique(self.label_im))
        else:
            self.label_im = img_as_float(self.label_im)
            wand.config(state = DISABLED, relief = SUNKEN)
            recompile.config(state = DISABLED, relief = SUNKEN)
        self.old_label = self.label_im.copy()
        self.lab_color = 1
        self.draw_im = img_as_float(skimage.io.imread(image_path + image))
        
        self.orig_im = self.draw_im.copy()
        self.draw_im[self.label_im > 0] = 0
        self.draw_im = self.draw_im.copy() + self.label_im.copy()
        self.old_im = self.filled_im.copy()
        self.old_draw = self.draw_im.copy()
        #self.old_draw = self.draw_im.copy()
        
        self.panel.bind("<z>", self.zoom_on)
        self.panel.bind("<c>", self.pencil_draw)        
        self.panel.bind("<h>", self.hide_labels)
        self.panel.bind("<b>", self.toggle_bright)
        self.panel.bind("<d>", self.erase)
        self.panel.bind("<q>", self.undo)
        self.panel.bind("<v>", self.edit_label)
        
        self.panel.config(cursor = "dot")
        #self.panel.bind("<KeyRelease-z>", self.zoom_off)
        self.panel.focus_set()
        self.check_function()


root_dir = os.getcwd()

image_path = root_dir + '/images/nuclei/'

cell_path = root_dir + '/predictions/cell/'
lysosome_path = root_dir + '/predictions/lysosome/'
nuclei_path = root_dir + '/predictions/nuclei/'    

savedir_nuc = root_dir + "/new_labels/nuclei/"
savedir_cell = root_dir + "/new_labels/cell/"
savedir_lysosome = root_dir + "/new_labels/lysosome/"
os.makedirs(savedir_nuc, exist_ok = True)
os.makedirs(savedir_cell, exist_ok = True)
os.makedirs(savedir_lysosome, exist_ok = True)

channels = {"nuclei": nuclei_path, "cell": cell_path, "lysosome":lysosome_path}

#x = (screen_width/2) - (w/2)
#y = (screen_height/2) - (h/2)
w = 1000
h = 700
im_frame_width = int(h*0.8)
im_frame_height = int(h*0.8)

cropsize = 150

def main(): 
    global screen_width, screen_height, x, y 
    root = Tk()
    root.title("Prediction App")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width/2) - (w/2)
    y = (screen_height/2) - (h/2)
    root.geometry("{}x{}+{}+{}".format(w, h, int(x), int(y)))
    root.resizable(False, False)
    
    MainWindow(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()