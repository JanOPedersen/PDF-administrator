""" The combined MVC pattern, where we have moved the MySQL stuff to backend.py"""
from tkinter import Listbox,Tk,Label,Entry,StringVar,Scrollbar,RIGHT,Y,Button,IntVar,Checkbutton
import tkinter.messagebox as MessageBox
import webbrowser
import backend

class ModelMySQL():
    """This is just a wrapper class for the static stuff in the backend.py file"""

    def __init__(self):
        self._connection = backend.connect_to_db()

    def __del__(self):
        backend.disconnect_from_db(self._connection)

    @property
    def connection(self):
        """The connection to the MySQL database"""
        return self._connection

    def insert(self, filename, filepath):
        """insert a filename,filepath pair into the database"""
        backend.mySQLinsert(self._connection, filename, filepath)

    def delete(self, _id):
        """delete entry identified by id from the database"""
        backend.mySQLdelete(self._connection, _id)

    def update(self, _id, flags):
        """given the database entry identified by id update the flags field"""
        backend.mySQLupdate(self._connection, _id, flags)

    def get_selected(self, filename):
        """given a filename, retrieve the matching row from the database"""
        return backend.mySQLgetSelected(self._connection, filename)

    def get_from_id(self, _id):
        """given an id, retrieve the matching row from the database"""
        return backend.get_from_id(self._connection, _id)

    def get_from_keywords(self, keywords, flags, ret_all):
        """given keywords find entries with the keywords present in the filename
           in the order given in the keyword list. The ret_all variable tells if we want
           to include the flags also in the searh query"""
        return backend.get_from_keywords(self._connection, keywords, flags, ret_all)

    def get_from_filepath(self, filepath, flags, ret_all):
        """given a filepath find all files that are in folders below that path.
           The ret_all variable tells if we want to include the flags also
           in the searh query"""
        return backend.get_from_filepath(self._connection, filepath, flags, ret_all)

    def get_from_flags(self, flags):
        """given flags, retrieve the matching rows from the database. By this
           is meant rows that have at least these flags set"""
        return backend.get_from_flags(self._connection, flags)

    def update_numbers(self):
        """update the numbers for rows that have newly got the status printed"""
        backend.update_numbers(self._connection)


class view_controller():
    """ In a sense a GUI framework like Tk acts as both a viewer and controller
        so bundle it into one class, and leave it as a future exercise to
        distill it into two classes (View + Controller)"""

    def add_list_box(self, width, height, x, y):
        """Given the location and dimensions of the list box, we add it"""
        self.root.update()
        self.list = Listbox(self.root)
        self.list.place(x = x,y = y, width = width, height = height)

    def add_scroll_bar(self, height, x, y):
        """ Add a scrollbar so that it is right aligned with the listbox
            Given the location and dimensions of the scrollbar, we add it"""
        self.root.update()
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.list.config(yscrollcommand=scrollbar.set)
        self.list.bind('<Double-Button>', lambda event: self.get_selected())
        scrollbar.config(command=self.list.yview)
        scrollbar.place(x = x,y = y,height = height)

    def add_buttons(self, x, y, buttonsSpacing):
        """Add buttons so that they are bottom aligned and left aligned with the list box
           TODO: how do we most elegantly call controller functions from within the "view"
           and reversibly?"""
        ButtonTxts = ['insert', 'delete', 'update', 'get', 'get Selected',
                      'show Selected', 'clear all']
        ButtonCommands = [self.insert, self.delete, self.update, self.get,
                          self.get_selected, self.showSelected, self.clearAll]

        for txt, cmd in zip(ButtonTxts, ButtonCommands):
            btn = Button(self.root, text=txt, font=('italic', 10),
                         bg='white', command = cmd)
            btn.place(x = x + buttonsSpacing ,y = y)
            self.root.update()
            x += (buttonsSpacing + btn.winfo_width())

        return x

    def add_hits_label(self, x, y):
        """ Add a label to show the number of results retrieved """
        nofHitsLabel = Label(self.root, text='# of results:', font = ('bold', 10))
        nofHitsLabel.place(x = x,y = y)
        self.root.update()
        self.nofHitsText = StringVar()
        nofHits = Label(self.root, font = ('bold', 10), textvariable=self.nofHitsText)
        nofHits.place(x = x + nofHitsLabel.winfo_width() + 5,y = y)

    def add_retrieve_checkbox(self, x, y, buttonsSpacing):
        """ Add a checkbox at the end of the buttons that indicate if we want to retrieve
            everything or condition our retrieval on the checkboxes """
        self.root.update()
        self.ret_all = IntVar(value=1)
        chkRetrieveAll = Checkbutton(self.root, text="retrieve all", variable=self.ret_all,
                                     onvalue=1, offvalue=0)
        chkRetrieveAll.place(x = x + buttonsSpacing,y = y)

    def add_class_checkboxes(self, x, y, height):
        """Add check boxes for our PDF paper classifications"""
        self.flags = 0
        classes = ['machine learning','deep learning','reinforcement learning',
                   'Google','Computer Vision','printed','speculative','mathematics']
        self.vars = [IntVar() for x in [None] * len(classes)]
        self.chkBoxes = []
        for txt, i, variable in zip(classes, range(len(classes)), self.vars):
            self.root.update()
            chkBox = Checkbutton(self.root, text=txt, variable=variable,
                                 onvalue=1, offvalue=0)
            chkBox.place(x = x, y = y + height * i, height = height)
            self.chkBoxes.append(chkBox)

    def add_entry_fields(self, x, y):
        """Add the 3 fields for filename, filepath and id"""
        filepath = Label(self.root, text='Path', font = ('bold', 10))
        filepath.place(x=x,y=y)

        self.root.update()
        filename = Label(self.root, text='Filename', font = ('bold', 10))
        filename.place(x=x,y=filepath.winfo_height() + filepath.winfo_y())

        self.root.update()
        file_id = Label(self.root, text='ID', font = ('bold', 10))
        file_id.place(x=x,y=filename.winfo_height() + filename.winfo_y())

        self.root.update()
        number = Label(self.root, text='number', font = ('bold', 10))
        number.place(x=x,y=file_id.winfo_height() + file_id.winfo_y())

        self.root.update()
        leftOffset = 5
        entriesX = 90
        self.e_filepath = Entry()
        self.e_filepath.place(x=entriesX, y=filepath.winfo_y(),
                              width=self.root.winfo_width() - entriesX - leftOffset)

        self.e_filename = Entry()
        self.e_filename.place(x=entriesX, y=filename.winfo_y(),
                              width=self.root.winfo_width() - entriesX - leftOffset)

        self.e_id = Entry()
        self.e_id.place(x=entriesX, y=file_id.winfo_y(), width=60)

        self.numberText = StringVar()
        self.number_val = Label(self.root, font = ('bold',10), textvariable=self.numberText)
        self.number_val.place(x=entriesX, y=number.winfo_y(), width=60)

        return number.winfo_height(), number.winfo_y()

    def __init__(self, model):
        """init the main window"""
        self.flags = None
        self.sel = None

        self.model = model
        self.root = Tk()
        self.root.geometry("700x400")
        self.root.title("PDF administrator")

        self.model.update_numbers()

        controlsX = 10
        controlsY = 10
        [num_height, num_y] = self.add_entry_fields(controlsX, controlsY)

        self.root.update()
        self.add_list_box(self.root.winfo_width() - 160 - 25,
                          self.root.winfo_height() - self.e_filename.winfo_y()
                          - self.e_filename.winfo_height() - 28 - 10,
                          160,
                          self.e_id.winfo_y())

        self.root.update()
        self.add_scroll_bar(self.list.winfo_height(),
                            self.list.winfo_x() + self.list.winfo_width(),
                            self.list.winfo_y())

        self.root.update()
        buttonsY = self.root.winfo_height() - 28 - 5
        buttonsSpacing = 5
        btnX = self.add_buttons(self.list.winfo_x(), buttonsY, buttonsSpacing)

        self.add_hits_label(controlsX, buttonsY)

        self.root.update()
        self.add_retrieve_checkbox(btnX + buttonsSpacing, buttonsY, buttonsSpacing)
        self.add_class_checkboxes(controlsX, num_height + num_y, 20)
        self.root.mainloop()

    def fillCheckBoxes(self,var):
        """Given the numeric value var, we fill the checkboxes with
           its binary representation"""
        def get_bit(num, i) -> int:
            return (num & (1 << i)) != 0

        for i in range(len(self.vars)):
            self.vars[i].set(get_bit(var, i))
            if i == 5:
                self.chkBoxes[i].configure(state = 'disabled' if get_bit(var, i) == 1 else 'normal')

    def getFlags(bitfield) -> int:
        """This is an unbound Python function which works like a static C++ class function
           Given vars bit field list we turn it into a numeric value"""
        flags = 0
        for i, j in zip(range(len(bitfield)), bitfield):
            flags += (j.get() << i)
        return flags

    def insert(self):
        """insert a new entry into the database
           TODO: we still have to implement the insert operation"""
        filename = self.e_filename.get()
        filepath = self.e_filepath.get()

    def delete(self):
        """delete entry from database"""
        try:
            file_id = self.e_id.get()
            self.model.delete(file_id)
            self.e_filename.delete(0,'end')
            self.e_filepath.delete(0,'end')
            self.e_id.delete(0,'end')
            self.list.delete(self.sel,self.sel)
            self.nofHitsText.set("")
            self.numberText.set("")
        except ValueError as e:
            print(e)
            MessageBox.showinfo("DELETE STATUS","we got an exception")

    def update(self):
        """update entry in database"""
        try:
            self.flags = view_controller.getFlags(self.vars)
            self.model.update(self.e_id.get(), self.flags)
        except ValueError as e:
            print(e)
            MessageBox.showinfo("UPDATE STATUS","we got an exception")

    def displayRow(self,row):
        """Given a database row we display it in the frontend"""
        self.e_filename.delete(0, 'end')
        self.e_filepath.delete(0, 'end')
        self.e_id.delete(0, 'end')
        self.e_id.insert(0, row[0])
        self.e_filename.insert(0, row[1])
        self.e_filepath.insert(0, row[2])
        self.numberText.set(str(row[5]))
        self.flags = row[4]
        self.fillCheckBoxes(self.flags)

    def displayRows(self,rows):
        """Given a list of rows, display them in the list box"""
        rows.sort(key=lambda s: s[1].lower())
        self.list.delete(0,'end')
        for index in range(len(rows)):
            self.list.insert(index + 1, rows[index][1])

    def get(self):
        """Depending on which query fields are filed out we do the relavant database query"""
        try:
            # In case we don't supply any seach information, but have the retrieve all checkbox
            # unchecked we use the flags as a query
            self.flags = view_controller.getFlags(self.vars)
            if (self.e_id.get() == "" and self.e_filename.get() == ""
                and self.e_filepath.get() == "" and self.ret_all.get() == 0):
                rows = self.model.get_from_flags(self.flags)
                self.nofHitsText.set(str(len(rows)))

                if len(rows) == 1:
                    self.displayRow(rows[0])
                    self.list.delete(0,'end')
                    self.list.insert(1, rows[0][1])
                elif len(rows) == 0:
                    MessageBox.showinfo("GET FROM FLAGS STATUS","no records found with given flags")
                # In case of multiple matches fill the listbox so that the user can select
                elif rows:
                    self.displayRows(rows)

            # In case we have an ID entered we want to retrieve the corresponding database entry
            # and display the result
            elif (self.e_id.get() != "" and self.e_filename.get() == ""
                    and self.e_filepath.get() == ""):
                rows = self.model.get_from_id(self.e_id.get())
                self.displayRow(rows[0])
                self.list.delete(0, 'end')
                self.list.insert(1, rows[0][1])

            # in case we don't supply an ID but have an approximate file name, we want to find
            # the closest match in the database and update all fields (including the file name)
            elif (self.e_filename.get() != "" and self.e_id.get() == ""
                  and self.e_filepath.get() == ""):
                # First we extract the keywords
                filename = self.e_filename.get()
                keywords = filename.split()
                rows = self.model.get_from_keywords(keywords, self.flags, self.ret_all)
                self.nofHitsText.set(str(len(rows)))

                # If there is only one result we fill the fields with it
                if len(rows) == 1:
                    self.displayRow(rows[0])
                elif not rows:
                    MessageBox.showinfo("GET STATUS","no records found with given keywords")
                # In case of multiple matches fill the listbox so that the user can select
                if rows:
                    self.displayRows(rows)

            elif (self.e_filename.get() == "" and self.e_id.get() == ""
                  and self.e_filepath.get() != ""):
                # First we extract the windows sub path
                filepath = self.e_filepath.get()
                filepath = filepath. replace("\\", "/")
                rows = self.model.get_from_filepath(filepath, self.flags, self.ret_all)
                self.nofHitsText.set(str(len(rows)))

                # If there is only one result we fill the fields with it
                if len(rows) == 1:
                    self.displayRow(rows[0])

                # In case of multiple matches fill the listbox so that the user can select
                elif not rows:
                    MessageBox.showinfo("GET STATUS","no records found with given filepath")

                self.displayRows(rows)

        except ValueError as _e:
            print(_e)
            MessageBox.showinfo("GET STATUS","no records found with ID")

    def get_selected(self):
        """When the user double clicks on an item in the listbox, we display the
           result in the entry fields"""
        try:
            # If we where able to select something
            self.sel = self.list.curselection()
            if self.sel:
                itm = self.list.get(self.sel)
                rows = self.model.get_selected(itm)

                # it is possible that the same file name occurs in multiple
                # records in the database, so just select the first one
                self.displayRow(rows[0])

        except ValueError as e:
            print(e)
            MessageBox.showinfo("GET STATUS","no records found with ID")

    def showSelected(self):
        """When the user has selected an item in the listbox and clicks the show item
           button we display the PDF in the browser"""
        try:
            # If we where able to select something
            sel = self.list.curselection()
            if sel:
                itm = self.list.get(sel)
                rows = self.model.get_selected(itm)
                fullpath = rows[0][2] + '/' + rows[0][1]
                webbrowser.open(fullpath,new=2)

        except ValueError as e:
            print(e)
            MessageBox.showinfo("SHOW SELECTED STATUS","no records found with ID")


    def clearAll(self):
        """Clear all entry fields"""
        self.e_filename.delete(0, 'end')
        self.e_filepath.delete(0, 'end')
        self.e_id.delete(0, 'end')
        self.list.delete(0, self.list.size())
        self.nofHitsText.set("")
        self.numberText.set("")
        for v in self.vars:
            v.set(0)
