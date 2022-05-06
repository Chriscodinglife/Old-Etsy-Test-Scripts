import re
import os

directory = input("Input directory to clean up png files: ")
stripped_path = directory.replace('"', "")

files_in_directory = os.listdir(stripped_path)

filtered_files = [file for file in files_in_directory if file.endswith(".png")]

for file in filtered_files:
    path_to_file = os.path.join(stripped_path, file)
    # Do regex to grab the portion of the file name that we want
    x = re.split("\s", file, 1)
    file_extension = ".png"
    file_name = x[0]
    new_file_name = file_name + file_extension

    print(new_file_name)

    # Rename png files
    source = f"{stripped_path}/{file}"
    destination = f"{stripped_path}/{new_file_name}"
    os.rename(source, destination)