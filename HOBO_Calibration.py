import os, sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import glob
import pandas as pd
from datetime import timedelta
import datetime as dt
import shutil
from datetime import datetime

def exit_program():
    print ("exiting program...")
    root.destroy()
    sys.exit("The allhobos csv file already exist in the directory, program terminated.")

def highlight_cells(value, limit_value):
    print()
    print(value, limit_value)
    if value > limit_value:
        return ['background-color: yellow']

def fetch_Directory(target):
    filename = filedialog.askdirectory(parent=root, title='Choose a folder')
    target.set(filename)

def ifexists(src):
    os.chdir(src)
    fileList = glob.glob("*.csv")

    for filename in fileList:
        if filename[-12:] == "allhobos.csv":
            exit_program()

def datetime_formatter(datetime):

    SPLIT_startdatetime = str(datetime).split(" ")
    SPLIT_date = SPLIT_startdatetime[0].split("-")
    SPLIT_time = SPLIT_startdatetime[1].split(":")

    hourraw = dt.datetime.strptime(str((int(SPLIT_time[0]))) + ":" + SPLIT_time[1] + ":" + SPLIT_time[2], "%H:%M:%S")
    date = SPLIT_date[1] + "/" + SPLIT_date[2] + "/" +str((int(SPLIT_date[0]) % 100))
    hour = hourraw.strftime("%I:%M:00 %p")

    return date + " " + hour

def CSV_formatter(src_csv_dir, out_dir, start, end):

    os.chdir(src_csv_dir)
    csvListPath = sorted(glob.glob("*.csv"))
    
    for csv_file in csvListPath:
        print(csv_file)
        with open(csv_file, 'rb') as f:
            df_csv = pd.read_csv(f, skiprows=1)
            df_csv = df_csv.set_index("#")
    
            COL_datetime = df_csv.dtypes.index[0]
            COL_temp = df_csv.dtypes.index[1]
            start_datetime = start
            end_datetime = end
            print(start_datetime)
            print(end_datetime)
            SPLIT_start_datetime = start_datetime.split(" ")
            SPLIT_date = SPLIT_start_datetime[0].split("/")

            for datetime in df_csv[COL_datetime]:

                if (datetime == start_datetime):
                    print("Passed if 1")

                    df_csv = df_csv[(df_csv[COL_datetime] >= start_datetime) & (df_csv[COL_datetime] <= end_datetime)]
                    df_formatted = df_csv.select_dtypes(['float64'])

                    mainHeaderString = df_formatted.dtypes.index[0]
                    substring = "S/N:"
                    print(mainHeaderString)
                    print(substring)


                    if substring in mainHeaderString:
                        print("Passed if 2")
                        s = mainHeaderString
                        substring1 = "SEN S/N: "
                        substring2 = ")"
                        serial_HOBO = s[s.index(substring1) + len(substring1):s.index(substring2)]

                        df_formatted.rename(columns={mainHeaderString: serial_HOBO}, inplace=True)
                        df_formatted.drop(df_formatted.columns[0], axis=1)
                        df_formatted.to_csv(out_dir + serial_HOBO + "_" + SPLIT_date[0] + "-" + SPLIT_date[1] + "-" + SPLIT_date[
                                2] + '.csv', index=False)
    os.chdir(out_dir)

def add_avg_std(src_csv_dir):
    os.chdir(src_csv_dir)
    csvListPath = sorted(glob.glob("*.csv"))
    for csv_file in csvListPath:
        print(csv_file)
        with open(csv_file, 'rb') as f:
            df_csv = pd.read_csv(f)

            COL_temp = df_csv[df_csv.dtypes.index[0]]
            tempmean = COL_temp.mean()
            tempstd = COL_temp.std()

            df_csv.loc[len(df_csv)] = [tempmean]
            df_csv.loc[len(df_csv) + 1] = [tempstd]
            #df_csv.style.apply(highlight_cells(df_csv.loc[len(df_csv[COL_temp])], 0.2))
            df_csv.to_csv(src_csv_dir+csv_file, index=False)

def concatenate(src, name):

    allcsvs = sorted(glob.glob(src+"/formatted_CSVs/*.csv"))
    frame = pd.DataFrame()
    list_ = []
    for file_ in allcsvs:
        df = pd.read_csv(file_, index_col=None, header=0)
        list_.append(df)

    print("pass 1")
    frame = pd.concat(list_, axis=1)
    print(frame)
    name = name.replace("-", "")
    name = name.replace(":", "")
    print("pass 2")
    frame.to_csv(src+"/CalCheck_allhobos.csv", index=False)
    print("pass 3")
    os.chdir(src)
    shutil.rmtree(src+"/formatted_CSVs/")
    print("pass 4")

def main():

    in_folder = entry_filepath_input.get()
    main_dir = in_folder + "\\"
    formatted_csv_dir = main_dir + "formatted_CSVs\\"

    #ifexists(in_folder)

    digit_startmonth = int(startmonthEntry.get())
    digit_startday = int(startdayEntry.get())
    digit_startyear = int(startyearEntry.get())
    digit_startyear_original = int(startyearEntry.get())
    digit_starthour = int(TIME_starthours.get())
    digit_startmin = str(TIME_startminutes.get()).zfill(2)+":00"
    digit_startmin_original = int(TIME_startminutes.get())
    digit_starthoursafter = int(TIME_hoursafter.get())

    dtstart_datetime = dt.datetime.combine(dt.date(digit_startyear_original, digit_startmonth, digit_startday), dt.time(digit_starthour, digit_startmin_original))
    dtend_datetime = dtstart_datetime + timedelta(hours=digit_starthoursafter)

    formatted_start_datetime = datetime_formatter(dtstart_datetime)
    formatted_end_datetime = datetime_formatter(dtend_datetime)

    print(formatted_start_datetime)
    print(formatted_end_datetime)
    print(dtend_datetime)

    os.chdir(main_dir)

    if not os.path.exists(formatted_csv_dir):
        os.makedirs(formatted_csv_dir)

    outputname = str(dtstart_datetime)+"_"+str(dtend_datetime)
    CSV_formatter(in_folder, formatted_csv_dir, formatted_start_datetime, formatted_end_datetime)
    add_avg_std(formatted_csv_dir)
    concatenate(in_folder, outputname)

    print("program successfully finished!!!")

if __name__ == '__main__':
    root_dir = os.getcwd()
    icon_path = root_dir+"\\images\\ICON_UVI_logo.ico"
    root = tk.Tk()
    root.title("HOBO: Auto Calibration")
    root.iconbitmap(default=icon_path)
    root.resizable(0,0)

    mainframe = ttk.Frame(root, width=500, height=150)
    mainframe.grid(sticky="nw")

    filepath_input= tk.StringVar(None)
    entry_filepath_input = ttk.Entry(mainframe, width=48, textvariable=filepath_input)
    entry_filepath_input.update()
    entry_filepath_input.focus_set()

    label_input = ttk.Label(mainframe, text="HOBO CSVs: ")
    label_output = ttk.Label(mainframe, text="Output Folder: ")

    button_browse_input = ttk.Button(mainframe, text="Browse...", command=lambda: fetch_Directory(filepath_input))

    label_start_datetime = ttk.Label(mainframe, text="Start Datetime:")

    startmonthEntry = ttk.Entry(mainframe, width=3)
    startdayEntry = ttk.Entry(mainframe, width=3)
    startyearEntry = ttk.Entry(mainframe, width=5)

    Label_slash = ttk.Label(mainframe, text="/")
    Label_slash2 = ttk.Label(mainframe, text="/")

    startoptionhours = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    TIME_starthours = tk.StringVar(None)
    TIME_starthours.set(3)
    entry_starthours = ttk.OptionMenu(mainframe, TIME_starthours, *startoptionhours)
    entry_starthours.update()
    entry_starthours.focus_set()

    Label_column = ttk.Label(mainframe, text=" :  ")

    startoptionminutes = [0, 00, 15, 30, 45]
    TIME_startminutes = tk.StringVar(None)
    TIME_startminutes.set(00)
    entry_startmins = ttk.OptionMenu(mainframe, TIME_startminutes, *startoptionminutes)
    entry_startmins.update()
    entry_startmins.focus_set()

    Label_hoursafter = ttk.Label(mainframe, text="get                hours after")

    startoptionhoursafter = [0, 1, 2, 3, 4, 5]
    TIME_hoursafter = tk.StringVar(None)
    TIME_hoursafter.set(2)
    entry_hoursafter = ttk.OptionMenu(mainframe, TIME_hoursafter, *startoptionhoursafter)
    entry_hoursafter.update()
    entry_hoursafter.focus_set()

    button_start = ttk.Button(mainframe, text="Start", command=main)
    button_quit = ttk.Button(mainframe, text="Quit", command=exit_program)

    label_input.place(relx=0.02, rely=0.1)
    entry_filepath_input.place(relx=0.2, rely=0.1)
    button_browse_input.place(relx=0.81, rely=0.09)

    label_start_datetime.place(relx=0.02, rely=0.30)
    startmonthEntry.place(relx=0.2, rely=0.30)
    Label_slash.place(relx=0.25, rely=0.30)
    startdayEntry.place(relx=0.27, rely=0.30)
    Label_slash2.place(relx=0.32, rely=0.30)
    startyearEntry.place(relx=0.34, rely=0.30)
    entry_starthours.place(relx=0.45, rely=0.30)
    Label_column.place(relx=0.50, rely=0.31)
    entry_startmins.place(relx=0.52, rely=0.30)
    Label_hoursafter.place(relx=0.63, rely=0.30)
    entry_hoursafter.place(relx=0.68, rely=0.29)

    button_start.place(relx=0.25, rely=0.80)
    button_quit.place(relx=0.6, rely=0.80)

    root.mainloop()