from tkinter import *
from tkinter import ttk
import random
import math
import cv2
import numpy as np
import mss

display_window = Tk()
display_window.geometry("600x600")
display_window.resizable(False, False)
display_title = display_window.title("Drone Usage for Gas Detection")

house = Canvas(display_window, width=600, height=600, bg="black")
house.pack()

def areaofBubbles(canbas):
    x = canbas.winfo_rootx()
    y = canbas.winfo_rooty()
    w = canbas.winfo_width()
    h = canbas.winfo_height()
    
    if w <= 1 or h <= 1:
        return 0, 0, 0, 0, "None", 0, 0, 0, 0

    with mss.MSS() as sct:
        monitor = {"top": y, "left": x, "width": w, "height": h}
        img = np.array(sct.grab(monitor))

    b, g, r = img[:,:,0], img[:,:,1], img[:,:,2]
   
    yellow_mask = (r > 200) & (g > 200) & (b < 150)
    yellowmask = np.sum(yellow_mask)
    
    pink_mask = (r > 200) & (b > 150) & (g < 150)
    pinkpixels = np.sum(pink_mask)
    
    blue_mask = (b > 200) & (r < 100) & (g < 100)
    bluepixels = np.sum(blue_mask)

    fullmask = pink_mask | yellow_mask | blue_mask

    top_left_quad  = fullmask[0:200, 0:200]
    top_right_quad = fullmask[0:200, 200:400]
    bot_left_quad  = fullmask[200:400, 0:200]
    bot_right_quad = fullmask[200:400, 200:400]

    tl_area = np.sum(top_left_quad)
    tr_area = np.sum(top_right_quad)
    bl_area = np.sum(bot_left_quad)
    br_area = np.sum(bot_right_quad)

    maximummm = int(max(tl_area, tr_area, bl_area, br_area))

    corners = {
        "Top-Left": tl_area,
        "Top-Right": tr_area,
        "Bottom-Left": bl_area,
        "Bottom-Right": br_area
    }
    highest_corner = max(corners, key=corners.get)
    if corners[highest_corner] == 0:
        highest_corner = "None"

    return pinkpixels, yellowmask, bluepixels, maximummm, highest_corner, tl_area, tr_area, bl_area, br_area


popup_open = False

def startGas(canbas, popup_win):
    particles = []

    data = Toplevel(popup_win)
    data.title("Analytics")
    data.resizable(False, False)
    data.geometry("300x175")
    data.transient(popup_win)
    data.attributes("-topmost", True)

    overview_label = Label(data, text="Carbon Monoxide/Yellow: %", font=("Arial", 12, "bold"))
    overview_label.pack(pady=5)
    overview1_label = Label(data, text="Methane/Blue", font=("Arial", 12, "bold"))
    overview1_label.pack(pady=5)
    overview2_label = Label(data, text="Radon/Pink: %", font=("Arial", 12, "bold"))
    overview2_label.pack(pady=5)
    overview3_label = Label(data, text="Highest Concentration: %", font=("Arial", 12, "bold"))
    overview3_label.pack(pady=5)
    

    sourcex = random.choice(range(80, 320))
    sourcey = random.choice(range(80, 320))
    max_radius = 200



    def run_loop():
        # Safety Check: If the user closed the window, stop looping immediately
        if not popup_win.winfo_exists():
            if data.winfo_exists():
                data.destroy()
            return
            
        if random.random() < 0.5:
            radius = random.randint(10, 20)
            spawn_x = random.randint(sourcex, sourcex + 25)
            spawn_y = random.randint(sourcey - 25, sourcey)

            randcolor = random.choice(["#FFFF00", "#FF69B4", "#0000FF"])

            p_id = canbas.create_oval(spawn_x - radius, spawn_y - radius, spawn_x + radius, spawn_y + radius, fill=randcolor, outline="", tags="bubble")
            
            dx = random.uniform(-1, 1)  # Slight side drift
            dy = random.uniform(-1,0) # Float UP
            life = random.randint(150,200) # Frames to survive
            
            particles.append({"id": p_id, "dx": dx, "dy": dy,})

    
        for p in particles[:]:
            canbas.move(p["id"], p["dx"], p["dy"])

            coords =  canbas.coords(p["id"])
            if coords:
                current_x = (coords[0]+ coords[2]) / 2
                current_y = (coords[1]+ coords[3]) / 2

                distancesource = math.sqrt((current_x - sourcex) ** 2 + (current_y - sourcey) ** 2)

                if distancesource > max_radius: 
                    canbas.delete(p["id"])
                    particles.remove(p)

        
        canbas.tag_raise("bubble")

        pinkpixels, yellowmask, bluepixels, maximummm, highest_corner, tl, tr, bl, br = areaofBubbles(canbas)
        
        pinkpercent = (pinkpixels / 160000)
        yellowpercent = (yellowmask / 160000)
        bluepercent = (bluepixels / 160000)

        if data.winfo_exists():
            overview_label.config(text=f"Carbon Monoxide/Yellow: {yellowpercent:.2%}")
            overview1_label.config(text=f"Methane/Blue: {bluepercent:.2%}")
            overview2_label.config(text=f"Radon/Pink: {pinkpercent:.2%}")
            overview3_label.config(text=f"Highest Concentration: {highest_corner}")

        popup_win.after(30, run_loop)

    run_loop()

        
       



def reset_popup_tracker():
    global popup_open
    popup_open = False

def open_attic(event):
    global popup_open
    if popup_open == True: return
    popup_open = True

    window = Toplevel(display_window)
    window.title("Attic")
    canbas = Canvas(window, width=400, height=400, bg="black")
    window.geometry("400x400")
    canbas.pack()   
    window.resizable(False, False) 
    x = random.randint(100,300)

    canbas.create_line(0, x, random.randint(100, 250), x, width = 2)
    canbas.create_line(x, 400, x, random.randint(100, 250), width = 2)

    startGas(canbas, window)

    window.bind("<Destroy>", lambda e: reset_popup_tracker())


def open_floor1(event):
    global popup_open
    if popup_open == True: return
    popup_open = True

    window = Toplevel(display_window)
    window.title("Floor 1")
    window.geometry("400x400")
    window.resizable(False, False) 
    canbas = Canvas(window, width=400, height=400, bg="black")
    canbas.pack()
    x = random.randint(10,200)
    y= random.randint(230,390)
    
    canbas.create_line(0, x, random.randint(100, 250), x, width = 2)
    canbas.create_line(x, 400, x, random.randint(100, 250), width = 2)
    canbas.create_line(y, random.randint(100, 250), y, 400, width = 2)

    startGas(canbas, window)

    window.bind("<Destroy>", lambda e: reset_popup_tracker())

def open_floor2(event):
    global popup_open
    if popup_open == True: return
    popup_open = True

    window = Toplevel(display_window)
    window.title("Floor 2")
    window.geometry("400x400")
    window.resizable(False, False) 
    canbas = Canvas(window, width=400, height=400, bg="black")
    canbas.pack()

    x = random.randint(10,200)
    y= random.randint(230,390)
        
    canbas.create_line(0, x, random.randint(100, 250), x, width = 2)
    canbas.create_line(x, 400, x, random.randint(100, 250), width = 2)
    canbas.create_line(y, random.randint(100, 250), y, 400, width = 2)

    startGas(canbas, window)


    window.bind("<Destroy>", lambda e: reset_popup_tracker())

def open_basement(event):
    global popup_open
    if popup_open == True: return
    popup_open = True

    window = Toplevel(display_window)
    window.title("Basement")
    window.geometry("400x400")
    window.resizable(False, False) 
    canbas = Canvas(window, width=400, height=400, bg="black")
    canbas.pack()
    
    x = random.randint(10,200)
    y= random.randint(230,390)
            
    canbas.create_line(0, x, random.randint(100, 250), x, width = 2)
    canbas.create_line(x, 400, x, random.randint(100, 250), width = 2)
    canbas.create_line(y, random.randint(100, 250), y, 400, width = 2)

    startGas(canbas, window)

    window.bind("<Destroy>", lambda e: reset_popup_tracker())


def hover_in_attic(event):
    house.itemconfig(attic, fill="#A19595")
def hover_out_attic(event):
    house.itemconfig(attic, fill="brown")

def hover_in_floor2(event):
    house.itemconfig(floor2, fill="#A19595")
def hover_out_floor2(event):
    house.itemconfig(floor2, fill="brown")

def hover_in_floor1(event):
    house.itemconfig(floor1, fill="#A19595")
def hover_out_floor1(event):
    house.itemconfig(floor1, fill="brown")

def hover_in_basement(event):
    house.itemconfig(basement, fill="#A19595")
def hover_out_basement(event):
    house.itemconfig(basement, fill="brown")


floor2 = house.create_rectangle(200, 150, 450, 250, fill="brown", width=4, outline="white")
floor1 = house.create_rectangle(200, 250, 450, 350, fill="brown", width=4, outline="white")
basement = house.create_rectangle(200, 350, 450, 475, fill="brown", width=5, outline="white")

triangle_points = [450, 150, 325, 100, 200, 150]
attic = house.create_polygon(triangle_points, fill="brown", width=3, outline="white")

house.tag_bind(attic, "<Button-1>", open_attic)
house.tag_bind(floor2, "<Button-1>", open_floor2)
house.tag_bind(floor1, "<Button-1>", open_floor1)
house.tag_bind(basement, "<Button-1>", open_basement)

house.tag_bind(attic, "<Enter>", hover_in_attic)
house.tag_bind(attic, "<Leave>", hover_out_attic)

house.tag_bind(floor2, "<Enter>", hover_in_floor2)
house.tag_bind(floor2, "<Leave>", hover_out_floor2)

house.tag_bind(floor1, "<Enter>", hover_in_floor1)
house.tag_bind(floor1, "<Leave>", hover_out_floor1)

house.tag_bind(basement, "<Enter>", hover_in_basement)
house.tag_bind(basement, "<Leave>", hover_out_basement)


attic_text = house.create_text(325, 125, anchor = "center", text = "Attic", font=("Arial", 12))
floor2_text = house.create_text(325, 200, anchor = "center", text = "Upstairs", font=("Arial", 12))
floor1_text = house.create_text(325, 300, anchor = "center", text = "Downstairs", font=("Arial", 12))
basement_text = house.create_text(325, 412, anchor = "center", text = "Basement", font=("Arial", 12))


coord_text = house.create_text(20, 20, text="X: 0, Y: 0", fill="white", anchor="w", font=("Arial", 12))

def track_cursor():
    globalx = house.winfo_pointerx()
    globaly = house.winfo_pointery()

    window_x = globalx - house.winfo_rootx()
    window_y = globaly - house.winfo_rooty()

    house.itemconfig(coord_text, text=f"Cursor Position -> X: {window_x}, Y: {window_y}")

    display_window.after(20,track_cursor)

track_cursor()


display_window.mainloop()
