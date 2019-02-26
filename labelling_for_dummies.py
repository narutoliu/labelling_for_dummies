from tkinter import * 
from tkinter import filedialog as fd
from tkinter import messagebox as ms

import PIL 
from PIL import Image, ImageTk

class lfd_aabb:
    def __init__(self, canvas, grid_frame):
        self._canvas = canvas
        self._grid_frame = grid_frame
        self._new_bounding_box = None
        self._coordinates_list = []

    def draw_bounding_box(self, start, end, **opts):
        return self._canvas.create_rectangle(*(list(start)+list(end)), **opts)
        

    def bind_controls(self, **opts):
        self._start = None
        self._canvas.bind("<Button-1>"       , self.update, '+')
        self._canvas.bind("<B1-Motion>"      , self.update, '+')
        self._canvas.bind("<ButtonRelease-1>", self.stop  , '+')
        
        self._rectopts = opts
        

    def update(self, event):
        if not self._start:
            print('start(x, y): ({}, {})'.format(event.x - 3, event.y - 3))

            self._start = [event.x, event.y]
            return
        
        # remove duplicated drawings
        if self._new_bounding_box is not None:
            self._canvas.delete(self._new_bounding_box)
        
        self._new_bounding_box = self.draw_bounding_box(self._start, (event.x, event.y), **self._rectopts)


    def stop(self, event):
        print('end(x, y)  : ({}, {})'.format(event.x - 3, event.y - 3))

        self._coordinates_list.append(list(self._start) + [event.x - 3, event.y - 3])
        print(self._coordinates_list)
        self.append_table(self._coordinates_list)

        self._start = None
        self._new_bounding_box  = None


    def append_table(self, coordinates):
        for i in range(len(coordinates)):
            for j in range(len(coordinates[0])):
                coord_str = str(coordinates[i][j])
                Label(self._grid_frame, text=coord_str).grid(row = i + 1, column = j)

            Entry(self._grid_frame, relief = RIDGE).grid(row = i + 1, column = len(coordinates[0]) + 1)


class lfd_window(Frame):
    def __init__(self, master, width = 700, height = 700):
        self._pack_frame = Frame(master)
        self._grid_frame = Frame(master)
        self._pack_frame.pack(side = TOP, fill = X)
        self._grid_frame.pack(side = TOP, fill = X)

        self._master = master
        self._master.title('Labelling for Dummies')
        self._master.geometry('300x300')
        self._master.resizable(False, False)

        self._width  = width
        self._height = height
        self._active_bounding_box = IntVar(0)

        self._menu = Menu(self._pack_frame)
        self._master.config(menu = self._menu)

        lfd_file = Menu(self._menu)
        lfd_file.add_command(label = 'Open...', command = self.display_image)
        lfd_file.add_command(label = 'Open Recent')
        lfd_file.add_separator()

        lfd_edit = Menu(self._menu)
        lfd_edit.add_command(label = 'Undo')
        lfd_edit.add_command(label = 'Redo')
        lfd_edit.add_separator()

        lfd_bounding_box = Menu(self._menu)
        lfd_bounding_box.add_radiobutton(label = 'Axis Aligned Bounding Box'   , 
                                         var = self._active_bounding_box, value = 0)
        lfd_bounding_box.add_radiobutton(label = 'Object Oriented Bounding Box', 
                                         var = self._active_bounding_box, value = 1)

        lfd_help = Menu(self._menu)
        lfd_help.add_command(label = 'Bounding Box Usage')

        self._menu.add_cascade(label = 'File'        , menu = lfd_file)
        self._menu.add_cascade(label = 'Edit'        , menu = lfd_edit)
        self._menu.add_cascade(label = 'Bounding Box', menu = lfd_bounding_box)
        self._menu.add_cascade(label = 'Help'        , menu = lfd_help)

        self._canvas = None
        #self._canvas = Canvas(self._pack_frame, height = 700, width = 700, bg = 'white')
        #self._canvas.pack(fill = BOTH, expand = True)
        #self._lfd_aabb = lfd_aabb(self._canvas)
        #self._lfd_aabb.bind_controls(fill = '', width = 2, outline = 'red')

        self._status = Label(self._master,text = 'Current Image: None',bg = 'white',
                             font = ('Ubuntu', 15), bd = 2, fg = 'black', 
                             relief = 'sunken', anchor = W)
        self._status.pack(side = BOTTOM, fill = X)


    def init_table(self):
        Label(self._grid_frame, text='x_min').grid(row = 0, column = 0)
        Label(self._grid_frame, text='y_min').grid(row = 0, column = 1)
        Label(self._grid_frame, text='x_max').grid(row = 0, column = 2)
        Label(self._grid_frame, text='y_max').grid(row = 0, column = 3)
        Label(self._grid_frame, text='image').grid(row = 0, column = 4)
        Label(self._grid_frame, text='label').grid(row = 0, column = 5)


    def append_table(self, coordinates):
        for i in range(len(coordinates)):
            for j in range(len(coordinates[0])):
                Label(self._grid_frame, text=str(coordinates[i][j])).grid(i + 1, column = j)

            Entry(relief = RIDGE).grid(row = i + 1, column = len(coordinates[0]))


    def resize_image(self, width, height):
        if width >= height:
            new_w = int(self._width  / width * width)
            new_h = int(self._height / width * height)
        else:
            new_w = int(self._width  / height * width)
            new_h = int(self._height / height * height)

        return new_w, new_h


    def display_image(self):
        try:
            img_file = fd.askopenfilename()
            self._pilImage = Image.open(img_file)

            w, h = self._pilImage.size
            new_w, new_h = self.resize_image(w, h)
            resized_img = self._pilImage.resize((new_w, new_h), Image.ANTIALIAS)
            self._image = ImageTk.PhotoImage(resized_img)

            #print('(width, height): ({}, {})'.format(new_w, new_h))
            self._master.geometry(str(new_w) + 'x' + str(new_h + 100))
            if self._canvas is not None:
                self._canvas.destroy()

            self._canvas = Canvas(self._pack_frame, height = new_h, width = new_w, bg = 'white')
            self._canvas.pack(side = TOP, fill = BOTH, expand = True)
            self._canvas.delete(ALL)
            self._canvas.create_image(0, 0, anchor = NW, image = self._image)
            self.init_table()

            self._lfd_aabb = lfd_aabb(self._canvas, self._grid_frame)
            self._lfd_aabb.bind_controls(fill = '', width = 2, outline = 'red')


            self._status['text'] = 'Current Image:' + img_file
        except:
            ms.showerror('Error!','Failed to open file!')


root = Tk()
lfd = lfd_window(root)

root.mainloop()
