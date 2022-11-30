import tkinter
import customtkinter
import queue


queue_commands = queue.Queue()


def add_text():
    command = entry.get()
    if command == "close":
        root.destroy()
    queue_commands.put(command)


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("Inverted Index Client")
root.geometry("620x470")

lable_frame = customtkinter.CTkFrame(root, corner_radius=10)
lable_frame.pack(pady=20)

entry = customtkinter.CTkEntry(lable_frame, width=400, height=40, border_width=1, placeholder_text="Enter the command",
                               text_color="silver")
entry.grid(row=0, column=0, padx=10, pady=10)

button = customtkinter.CTkButton(lable_frame, text="Proceed", command=add_text)
button.grid(row=0, column=1, padx=10)

text_frame = customtkinter.CTkFrame(root, corner_radius=10)
text_frame.pack(pady=10)

text = tkinter.Text(text_frame, height=20, width=69, bd=0, bg="#292929", fg="silver")
text.pack(pady=10, padx=10)
