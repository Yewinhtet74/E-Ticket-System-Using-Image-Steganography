# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 20:29:29 2024

@author: User
"""

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont

def ticket_image(data):
    
    font_color2=(66,66,66)
    img=np.array(Image.open('images/sample ticket.png'))
    '''
    logo=np.array(Image.open('images/utycclogo.png'))
    logo=cv.resize(logo,logo_size)
    logo=logo[:,:,:3]
    mask = np.all(logo==[0,0,0], axis=2)
    logo[mask] = [255,255,255]
    img[60:60+logo_size[0],60:60+logo_size[1]]=logo
    '''
    img=Image.fromarray(img)
    draw=ImageDraw.Draw(img)
    def writeinimage(msg,strt_wd,height,align_center,color,size):
        x1,y1,x2,y2 = draw.textbbox((0,0),msg,font=ImageFont.truetype('arial.ttf', size))
        w=x2
        draw.text(([strt_wd,strt_wd-w/2][align_center],height), msg,font=ImageFont.truetype('arial.ttf', size), fill =color)
    
    
    writeinimage(data['name'], 145,290,1,font_color2,20)
    writeinimage(data['passport'], 450,290,1,font_color2,20)
    writeinimage(f"{(data['ticket_no']):0>8}", 750,290,1,font_color2,20)
    
    writeinimage(data['depart_code'], 98,390,0,font_color2,25)
    writeinimage('('+data['depart_name']+')', 158,397,0,font_color2,15)
    writeinimage(data['arrive_code'], 708,390,0,font_color2,25)
    writeinimage('('+data['arrive_name']+')', 768,397,0,font_color2,15)
    writeinimage(data['depart_date'], 98,430,0,font_color2,15)
    writeinimage(data['arrive_date'], 708,430,0,font_color2,15)
    writeinimage(data['depart_time']+' (local)', 98,455,0,font_color2,15)
    writeinimage(data['arrive_time']+' (local)', 708,455,0,font_color2,15)
    
    
    writeinimage(data['flight_no'], 145,540,1,font_color2,20)
    writeinimage(data['class'], 450,540,1,font_color2,20)
    writeinimage(data['flight_time'], 750,540,1,font_color2,20)
    
    
    #plt.imshow(img,cmap='gray')
    
    img=np.array(img)
    '''
    img2=cv.cvtColor(img, cv.COLOR_RGB2BGR)
    cv.imshow('',img2)
    cv.waitKey(0)
    cv.destroyAllWindows()
    '''
    return img
    #cv.imwrite('images/e_ticket8.png',img2)