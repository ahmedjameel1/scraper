import tkinter as tk
from tkinter import Tk, Label, Entry, Button, Checkbutton, scrolledtext, filedialog, BooleanVar
import os
from tkinter import PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from scrape_products import get_products
    
class WebScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("AlixExpress Scraper")
        self.master.minsize(600, 600)
        self.master.maxsize(600, 600)
        self.master.configure(bg='#000000')
        self.default_font = ('Arial', 12)       

        # Get the directory where the current script is located
        current_directory = os.path.dirname(os.path.realpath(__file__))
        
        # Assuming your icon file is named 'icon.ico'
        master_icon_file = os.path.join(current_directory, 'icon.ico')
        browse_icon_file = os.path.join(current_directory, 'browser_icon.png')
        add_file = os.path.join(current_directory, 'add.png')
        logo = os.path.join(current_directory, 'aliexpress_logo.png')
        
        # Change the icon (replace 'icon.ico' with your icon file)
        self.master.iconbitmap(master_icon_file)
        
        # Place logo in the top-right corner
        self.logo = tk.PhotoImage(file=logo).subsample(3, 3)
        self.logo_label = tk.Label(master, image=self.logo, background='#000000')
        self.logo_label.grid(row=3, column=1, sticky="ne", padx=0, pady=0)  # Adjust as needed

        self.url_label = Label(master, text="Enter URL:", background='#000000', foreground='#FFFFFF')
        self.url_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)
        self.url_entry = Entry(master, background='#2b2b2b', foreground='#FFFFFF')
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        self.add_list_label = Label(master, text="Add List:(only .txt or .csv files)", background='#000000', foreground='#FFFFFF')
        self.add_list_label.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
        self.add_list_entry = Entry(master, background='#2b2b2b', foreground='#FFFFFF')
        self.add_list_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Add button to browse for the file
        self.add_icon = tk.PhotoImage(file=add_file).subsample(10, 10)
        self.add_file_button = tk.Button(master, image=self.add_icon, command=self.browse_file,
                                        borderwidth=0, background='#000000', foreground='#FFFFFF')
        self.add_file_button.grid(row=1, column=2, padx=(0, 200), pady=5)

        self.save_label = Label(master, text="Save to:", background='#000000', foreground='#FFFFFF')
        self.save_label.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=5)
        self.save_entry = Entry(master, background='#2b2b2b', foreground='#FFFFFF')
        self.save_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Load the icon file using PhotoImage
        self.browse_icon = tk.PhotoImage(file=browse_icon_file).subsample(10, 10)
        self.browse_button = tk.Button(master, image=self.browse_icon,
                                    background='#000000', foreground='#000000',
                                    command=self.browse_directory, borderwidth=0)
        self.browse_button.grid(row=2, column=2, padx=(0, 200), pady=5)

        self.scrape_button = Button(master, text="Scrape", command=self.start_scraping,
                            background='#104E00', foreground='#FFFFFF')
        self.scrape_button.grid(row=4, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.stop_button = Button(master, text="Stop", command=self.stop_scraping,
                                background='#520000', foreground='#FFFFFF')
        self.stop_button.grid(row=4, column=1, padx=(5, 10), pady=10, sticky="ew")

        self.headless_var = BooleanVar()
        self.headless_checkbox = Checkbutton(master, text="Show browser window", 
                                            background='#000000', foreground='#FFFFFF', 
                                            variable=self.headless_var, 
                                            font=self.default_font, 
                                            selectcolor='#000000')  # Set the color when the checkbox is selected
        self.headless_checkbox.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self.message_label = Label(master, text="Messages:", background='#000000', foreground='#FFFFFF')
        self.message_label.grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.message_text = scrolledtext.ScrolledText(master, height=9, wrap='word',
                                                    background='#2b2b2b', foreground='#FFFFFF', font=("Helvetica", 11))
        self.message_text.grid(row=7, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        new_height = self.master.winfo_height() - 140  # Adjust the constant value according to your layout
        self.message_text.config(height=new_height)
        # Configure message text to always scroll to the bottom
        self.message_text.config(state='disabled')  # Initially set to disabled
        self.message_text.bind("<1>", lambda event: self.message_text.focus_set())  # Focus to enable scrolling
        
        # Use grid row and column weights to make widgets expand to fill available space
        master.grid_rowconfigure(7, weight=1)
        master.grid_columnconfigure(1, weight=1)

        
        self.task_list = []
        self.is_processing = False
        self.stop_flag = False
        
        window_width = 600
        window_height = 600
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set the geometry of the main window to center it on the screen
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.show_popup()

    def show_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Welcome!")
        # Calculate the center coordinates for the pop-up window
        popup_width = 400
        popup_height = 300
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        popup_x = (screen_width - popup_width) // 2
        popup_y = (screen_height - popup_height) // 2

        # Set the geometry of the pop-up window to center it on the main window
        popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        # Disable maximize button
        popup.resizable(False, False)
        current_directory = os.path.dirname(os.path.realpath(__file__))

        # Change icon
        icon_path = os.path.join(current_directory, 'info.ico')  # Specify the path to your icon file
        popup.iconbitmap(icon_path)

        # Load the GIF image
        gif_path = os.path.join(current_directory, 'help.gif')  # Specify the path to your GIF file
        gif_image = Image.open(gif_path)
        gif_frames = []
        try:
            while True:
                gif_frames.append(ImageTk.PhotoImage(gif_image))
                gif_image.seek(len(gif_frames))
        except EOFError:
            pass

        # Display the GIF image in a label
        gif_label = ttk.Label(popup)
        gif_label.pack(fill=None, expand=True)
        self.animate_gif(gif_label, gif_frames, 0)
        popup.lift()
        popup.mainloop() 


    def animate_gif(self, label, frames, idx):
        idx %= len(frames)
        label.configure(image=frames[idx])
        label.image = frames[idx]  # Keep a reference to the image object
        self.master.after(100, self.animate_gif, label, frames, idx + 1)

    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, directory)
            
    def browse_file(self):
        # Open a file dialog to choose a file
        file_path = filedialog.askopenfilename()
        
        # Set the selected file path to the entry field
        self.add_list_entry.delete(0, tk.END)  # Clear any existing text
        self.add_list_entry.insert(0, file_path)

    def start_scraping(self):
        url = self.url_entry.get()
        list_file_path = self.add_list_entry.get()
        self.save_directory = self.save_entry.get()
        self.headless = self.headless_var.get()

        if not any([url, list_file_path]):
            self.display_message("Add a url or a list of urls file boss!", error=True)
            return
    
        elif any([url, list_file_path]) and not self.save_directory:
            self.save_directory = os.path.dirname(os.path.realpath(__file__))
            self.display_message("Files will be saved in the current directory!", sys=True)
        
        if url:
            # URL validation for AliExpress
            if 'https://www.aliexpress.' not in url:
                self.display_message("Invalid AliExpress URL", error=True)
                return
            self.task_list.append(url)
            
        # Check if both URL and file are provided
        if list_file_path:
            # Check if the file exists
            if os.path.exists(list_file_path):
                # Check the file extension to determine the type
                _, file_extension = os.path.splitext(list_file_path)
                if file_extension.lower() == '.txt':
                    # Process the text file
                    with open(list_file_path, 'r') as file:
                        lines = file.readlines()
                        for line in lines:
                            if 'https://www.aliexpress.' in line:
                                self.task_list.append(line.strip())  # Strip to remove trailing newline characters
                            else:
                                self.display_message("Invalid AliExpress URL, trying next one...", error=True)
                                continue
                                                                      
                elif file_extension.lower() == '.csv':
                    # Process the CSV file
                    with open(list_file_path, 'r') as file:
                        # Assuming you use csv module to read CSV files
                        import csv
                        reader = csv.reader(file)
                        for row in reader:
                            if 'https://www.aliexpress.' in row:
                                self.task_list.append(row.strip())  # Strip to remove trailing newline characters
                            else:
                                self.display_message("Invalid AliExpress URL, trying next one...", error=True)
                                continue
                else:
                    self.display_message("Unsupported file format. Only .txt and .csv files are supported.", error=True)
            else:
                self.display_message("File does not exist.", error=True)
        
        self.is_processing = True 
        self.stop_flag = False
        self.scrape_button.configure(state='disabled')
        self.headless_checkbox.configure(state='disabled')
        self.save_entry.configure(state='disabled')
        self.browse_button.configure(state='disabled')
        self.add_file_button.configure(state='disabled')
        self.add_list_entry.configure(state='disabled')
        self.add_list_label.configure(state='disabled')
        self.save_label.configure(state='disabled')
        self.url_entry.configure(state='disabled')
        self.url_label.configure(state='disabled')
        threading.Thread(target=self.scrape_data).start()

    def stop_scraping(self):
            if self.is_processing:
                self.display_message('Waiting to finish current task...', info=True)
                self.stop_flag = True
                self.is_processing = False
                self.task_list = []
            elif not self.is_processing and len(self.task_list) == 0:
                self.display_message('There are no tasks running!', sys=True)
                
            self.stop_button.configure(state='disabled')
        
    def scrape_data(self):            
        plural = 'urls' if len(self.task_list) > 1 else 'url'
        self.stop_button.configure(state='normal')
        self.display_message(f'Starting to scrape {len(self.task_list)} {plural}...', sys=True)
        while self.task_list and not self.stop_flag:
            task = self.task_list.pop(0)  # Get the first task from the list
            self.display_message(f'Processing url: {task[:60]}...', sys=True)
            try:
                products, page_title = get_products(task, self.save_directory, False if self.headless else True)
                self.display_message(f'Successfully saved {len(products)} entries to {page_title} in {self.save_directory}!', success=True)
            except Exception as e:
                self.display_message(str(e), error=True)

        self.is_processing = False
        self.stop_flag = True

        self.scrape_button.configure(state='normal')
        self.headless_checkbox.configure(state='normal')
        self.save_entry.configure(state='normal')
        self.browse_button.configure(state='normal')
        self.add_file_button.configure(state='normal')
        self.add_list_entry.configure(state='normal')
        self.add_list_label.configure(state='normal')
        self.save_label.configure(state='normal')
        self.url_entry.configure(state='normal')
        self.url_label.configure(state='normal')
        self.display_message(f'Tasks are executed, start another queue or a new url!', info=True)


    def display_message(self, message, error=False, success=False, info=False, sys=False):
        # Enable the message box to insert text
        self.message_text.configure(state='normal')
        
        if error:
            self.message_text.insert(tk.END, f'[Error] {message}\n', "error")
            self.message_text.tag_config("error", foreground="#FF6347")
        elif success: 
            self.message_text.insert(tk.END, f'[Success] {message}\n', 'success')
            self.message_text.tag_config("success", foreground="#32CD32")
        elif info: 
            self.message_text.insert(tk.END, f'[Info] {message}\n', 'info')
            self.message_text.tag_config("info", foreground="#ADD8E6")
        elif sys:
            self.message_text.insert(tk.END, f'[SYS] {message}\n', 'sys')
            self.message_text.tag_config("sys", foreground="orange")
        else:
            self.message_text.insert(tk.END, message + '\n')
            
        # Disable the message box again after inserting the text
        self.message_text.configure(state='disabled')
        
        # Scroll to the end of the message box
        self.message_text.see(tk.END)

        
        
def main(): 
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.geometry("600x600")  # Fixed window size
    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    main()