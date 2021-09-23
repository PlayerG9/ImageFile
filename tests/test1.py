import tkinter as tk


root = tk.Tk()

label = tk.Button(root, text="Hello World", fg='systemTextColor', bg='systemWindowBackgroundColor')
label.pack()

root.mainloop()
