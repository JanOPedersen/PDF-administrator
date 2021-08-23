from tkinter import *
import tkinter.messagebox as MessageBox
import webbrowser
from backend import *

# This is just a wrapper class for the static stuff in the backend.py file
class ModelMySQL(object):

    def __init__(self):
        self._connection = connect_to_db()

    def __del__(self):
        disconnect_from_db(self._connection)
        
    @property
    def connection(self):
        return self._connection

    def insert(self, filename, filepath):
        mySQLinsert(self._connection, filename, filepath)

    def delete(self, id):
        mySQLdelete(self._connection, id)

    def update(self, id, flags):
        mySQLupdate(self._connection, id, flags)

    def getSelected(self, filename):
        return mySQLgetSelected(self._connection, filename)

    def getFromId(self, id):
        return getFromId(self._connection, id)

    def getFromKeywords(self, keywords, flags, retAll):
        return getFromKeywords(self._connection, keywords, flags, retAll)

    def getFromFilepath(self, filepath, flags, retAll):
        return getFromFilepath(self._connection, filepath, flags, retAll)

    def getFromFlags(self, flags):
        return getFromFlags(self._connection, flags)

    def updateNumbers(self):
        updateNumbers(self._connection)



# In a sense a GUI framework like Tk acts as both a viewer and controller
# so bundle it into one class, and leave it as a future exercise to
# distill it into two classes (View + Controller)
class ViewController(object):

    # init the main window
    def __init__(self, model):
        self.model = model
        self.root = Tk()
        self.root.geometry("700x400")
        self.root.title("PDF administrator")

        self.model.updateNumbers()

        controlsX = 10
        controlsY = 10
        filepath = Label(self.root, text='Path', font = ('bold',10))
        filepath.place(x=controlsX,y=controlsY)

        self.root.update()
        filename = Label(self.root, text='Filename', font = ('bold',10))
        filename.place(x=controlsX,y=filepath.winfo_height() + filepath.winfo_y())

        self.root.update()
        id = Label(self.root, text='ID', font = ('bold',10))
        id.place(x=controlsX,y=filename.winfo_height() + filename.winfo_y())

        self.root.update()
        number = Label(self.root, text='number', font = ('bold',10))
        number.place(x=controlsX,y=id.winfo_height() + id.winfo_y())

        self.root.update()
        leftOffset = 5
        entriesX = 90
        self.e_filepath = Entry()
        self.e_filepath.place(x=entriesX, y=filepath.winfo_y(), width=self.root.winfo_width() - entriesX - leftOffset)

        self.e_filename = Entry()
        self.e_filename.place(x=entriesX, y=filename.winfo_y(), width=self.root.winfo_width() - entriesX - leftOffset)

        self.e_id = Entry()
        self.e_id.place(x=entriesX, y=id.winfo_y(), width=60)

        self.numberText = StringVar()
        self.number_val = Label(self.root, font = ('bold',10),textvariable=self.numberText)
        self.number_val.place(x=entriesX, y=number.winfo_y(), width=60)

        # Add list box
        self.root.update()
        listBoxHeight   = self.root.winfo_height() - self.e_filename.winfo_y() - self.e_filename.winfo_height() - 28 - 10
        listBoxY        = self.e_id.winfo_y()
        listBoxX        = 160
        listBoxWidth    = width=self.root.winfo_width() - listBoxX - 25
        self.list = Listbox(self.root)
        self.list.place(x = listBoxX,y = listBoxY, width = listBoxWidth, height = listBoxHeight)

        # Add a scrollbar so that it is right aligned with the listbox
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.list.config(yscrollcommand=scrollbar.set)
        self.list.bind('<Double-Button>', lambda event: self.getSelected())
        scrollbar.config(command=self.list.yview)
        scrollbar.place(x = listBoxX + listBoxWidth,y = listBoxY,height = listBoxHeight)

        # Add buttons so that they are bottom aligned and left aligned with the list box
        # TODO: how do we most elegantly call controller functions from within the "view" and reversibly?
        self.root.update()
        buttonsY = self.root.winfo_height() - 28 - 5
        buttonsSpacing = 5

        ButtonTxts = ['insert', 'delete', 'update', 'get', 'get Selected', 'show Selected', 'clear all']
        ButtonCommands = [self.insert, self.delete, self.update, self.get, self.getSelected, self.showSelected, self.clearAll]

        btnX = listBoxX
        for i in range(len(ButtonTxts)):
            btn = Button(self.root, text=ButtonTxts[i],font=('italic',10),bg='white', command = ButtonCommands[i])
            btn.place(x = btnX + buttonsSpacing ,y = buttonsY)
            self.root.update()
            btnX += (buttonsSpacing + btn.winfo_width())

        # Add a label to show the number of results retrieved
        nofHitsLabel = Label(self.root, text='# of results:', font = ('bold',10))
        nofHitsLabel.place(x = controlsX,y = buttonsY)
        self.root.update()
        self.nofHitsText = StringVar()
        nofHits = Label(self.root, font = ('bold',10),textvariable=self.nofHitsText)
        nofHits.place(x = controlsX + nofHitsLabel.winfo_width() + 5,y = buttonsY)

        # Add a checkbox at the end of the buttons that indicate if we want to retrieve everything or 
        # condition our retrieval on the checkboxes
        self.root.update()
        self.retAll = IntVar(value=1)
        chkRetrieveAll = Checkbutton(self.root, text="retrieve all",variable=self.retAll, onvalue=1, offvalue=0)
        chkRetrieveAll.place(x = btnX + buttonsSpacing,y = buttonsY)

        # Add check boxes for our PDF paper classifications
        self.flags = 0
        classes = ['machine learning','deep learning','reinforcement learning','Google','Computer Vision','printed','speculative','mathematics']
        self.vars = [IntVar() for x in [None] * len(classes)]
        CheckBoxesStartY = number.winfo_height() + number.winfo_y()
        CheckBoxesHeight = 20
        self.chkBoxes = []
        for i in range(len(classes)):
            self.root.update()
            chkBox = Checkbutton(self.root, text=classes[i],variable=self.vars[i], onvalue=1, offvalue=0)
            chkBox.place(x = controlsX, y = CheckBoxesStartY + CheckBoxesHeight * i,height = CheckBoxesHeight)
            self.chkBoxes.append(chkBox)

        self.root.mainloop()

    def fillCheckBoxes(self,var):
        for i in range(len(self.vars)):
            self.vars[i].set(ViewController.get_bit(var, i))
            if i == 5:
                self.chkBoxes[i].configure(state = 'disabled' if ViewController.get_bit(var, i) == 1 else 'normal')
                   
    # This is an unbound Python function which works like a static C++ class function
    def getFlags(vars):
        flags = 0
        for i in range(len(vars)):
            flags += (vars[i].get() << i)
        return flags

    def get_bit(num, i):
        return (num & (1 << i)) != 0

    # TODO: we still have to implement the insert operation
    def insert(self):
        filename = self.e_filename.get()
        filepath = self.e_filepath.get()

    def delete(self):
        try:
            id = self.e_id.get()
            self.model.delete(id)
            self.e_filename.delete(0,'end')
            self.e_filepath.delete(0,'end')
            self.e_id.delete(0,'end')
            self.list.delete(self.sel,self.sel)
            self.nofHitsText.set("")
            self.numberText.set("")
        except Exception as e:
            print(e)
            MessageBox.showinfo("DELETE STATUS","we got an exception")

    def update(self):
        try:
            self.flags = ViewController.getFlags(self.vars)
            self.model.update(self.e_id.get(), self.flags)
        except Exception as e:
            print(e)
            MessageBox.showinfo("UPDATE STATUS","we got an exception")

    # Given a database row we display it in the frontend
    def displayRow(self,row):
        self.e_filename.delete(0,'end')
        self.e_filepath.delete(0,'end')
        self.e_id.delete(0,'end')
        self.e_id.insert(0,row[0])
        self.e_filename.insert(0,row[1])
        self.e_filepath.insert(0,row[2])
        self.numberText.set(str(row[5]))
        self.flags = row[4]
        self.fillCheckBoxes(self.flags)

    # Given a list of rows, display them in the list box
    def displayRows(self,rows):
        rows.sort(key=lambda s: s[1].lower())
        self.list.delete(0,'end')
        for index in range(len(rows)):
            self.list.insert(index + 1, rows[index][1])

    def get(self):
        try:
            # In case we don't supply any seach information, but have the retrieve all checkbox
            # unchecked we use the flags as a query
            self.flags = ViewController.getFlags(self.vars)
            if (self.e_id.get() == "" and self.e_filename.get() == "" and self.e_filepath.get() == "" and self.retAll.get() == 0):
                rows = self.model.getFromFlags(self.flags)
                self.nofHitsText.set(str(len(rows)))

                if (len(rows) == 1):
                    self.displayRow(rows[0])
                    self.list.delete(0,'end')
                    self.list.insert(1, rows[0][1])
                elif (len(rows) == 0):
                    MessageBox.showinfo("GET FROM FLAGS STATUS","no records found with given flags")
                # In case of multiple matches fill the listbox so that the user can select
                elif (len(rows) > 0):
                    self.displayRows(rows)

            # In case we have an ID entered we want to retrieve the corresponding database entry
            # and display the result
            elif (self.e_id.get() != "" and self.e_filename.get() == "" and self.e_filepath.get() == ""):
                rows = self.model.getFromId(self.e_id.get())
                self.displayRow(rows[0])
                self.list.delete(0,'end')
                self.list.insert(1, rows[0][1])

            # in case we don't supply an ID but have an approximate file name, we want to find
            # the closest match in the database and update all fields (including the file name)
            elif (self.e_filename.get() != "" and self.e_id.get() == "" and self.e_filepath.get() == ""):
                # First we extract the keywords
                filename = self.e_filename.get()
                keywords = filename.split()
                rows = self.model.getFromKeywords(keywords, self.flags, self.retAll)
                self.nofHitsText.set(str(len(rows)))
 
                # If there is only one result we fill the fields with it
                if (len(rows) == 1):
                    self.displayRow(rows[0])
                elif (len(rows) == 0):
                    MessageBox.showinfo("GET STATUS","no records found with given keywords")
                # In case of multiple matches fill the listbox so that the user can select
                if (len(rows) > 0):
                    self.displayRows(rows)

            elif (self.e_filename.get() == "" and self.e_id.get() == "" and self.e_filepath.get() != ""):
                # First we extract the windows sub path
                filepath = self.e_filepath.get()
                filepath = filepath. replace("\\", "/")
                rows = self.model.getFromFilepath(filepath, self.flags, self.retAll)
                self.nofHitsText.set(str(len(rows)))
 
                # If there is only one result we fill the fields with it
                if (len(rows) == 1):
                    self.displayRow(rows[0])

                # In case of multiple matches fill the listbox so that the user can select
                elif (len(rows) == 0):
                    MessageBox.showinfo("GET STATUS","no records found with given filepath")

                self.displayRows(rows)
                
        except Exception as e:
            print(e)
            MessageBox.showinfo("GET STATUS","no records found with ID")

    def getSelected(self):
        try:
            # If we where able to select something
            self.sel = self.list.curselection()
            if (len(self.sel)) > 0:
                itm = self.list.get(self.sel)
                rows = self.model.getSelected(itm)

                # it is possible that the same file name occurs in multiple
                # records in the database, so just select the first one
                self.displayRow(rows[0])

        except Exception as e:
                    print(e)
                    MessageBox.showinfo("GET STATUS","no records found with ID")

    def showSelected(self):
        try:
            # If we where able to select something
            sel = self.list.curselection()
            if (len(sel)) > 0:
                itm = self.list.get(sel)
                rows = self.model.getSelected(itm)
                fullpath = rows[0][2] + '/' + rows[0][1]
                webbrowser.open(fullpath,new=2)

        except Exception as e:
            print(e)
            MessageBox.showinfo("SHOW SELECTED STATUS","no records found with ID")
                

    def clearAll(self):
        self.e_filename.delete(0,'end')
        self.e_filepath.delete(0,'end')
        self.e_id.delete(0,'end')
        self.list.delete(0,self.list.size())
        self.nofHitsText.set("")
        self.numberText.set("")
        for v in self.vars:
            v.set(0)
