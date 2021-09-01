# PDF-administrator
Manage your PDF files that may be scattered around on your PC. I implemented this app. so that no more would I have to use Microsoft's built in file browser to detect where my files PDF files are (I have 1300+). The app has a single window as GUI and is implemented in Python using the tkinter and mysql packages.
<p align="center">
  <img src="https://user-images.githubusercontent.com/6919287/130425554-d9ea6423-9ef6-40c4-85cb-b71c49ec06ba.png" alt="image" width="50%"/>
</p>

##### Short user manual 

The path, filename and the checkboxes with PDF classifications (machine learning, deep learning, ...) are the main entry entry points for the app. The ID is the MySQL primary key, while number is an automatically assigned serial number for all PDF's that have been printed. This enables you to label your PDF's and nicely organize them in binders for easy retrieval. 

Here follows some use cases

###### Find PDF doc's in a folder and all subfolders

Enter the folder path in the Path entry and leave ID and Filename empty. Then press the get button. The PDF filenames now appear in the list box. The number of found PDF's appear in the '# of results' field. 

###### Find PDF that have key words in their names

Enter the keywords in the Filename entry and leave ID and Path empty. Then press the get button. The PDF filenames now appear in the list box. The number of found PDF's appear in the '# of results' field. 

###### Find the PDF that has a certain MySQL primary key

Enter the key in ID and leave Path and Filename empty. The PDF now appears in the list box with Path and Filename filled out.

###### Show information for an entry in the list box

Double click the entry or press 'get Selected'

###### Display the PDF in your internet browser

Press 'show Selected'

###### Start a new search

Press 'clear all' and type in new search criteria.

###### Add classifications (machine learning, deep learning, ...) to a PDF

Check some of the classification checkboxes and press 'Update'





