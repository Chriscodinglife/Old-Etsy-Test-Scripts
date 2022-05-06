import os
import csv
import re


file = input("Please enter csv template file path for project: ")
stripped_file = file.replace('"', "")

rendered_folder = input("Enter the folder with the final rendered items: ")
stripped_rendered_folder = rendered_folder.replace('"', "")
files_in_rendered_folder = os.listdir(stripped_rendered_folder)

for file in files_in_rendered_folder:
    actual_file_name = os.path.splitext(file)[0]
    actual_file_path = os.path.join(stripped_rendered_folder, file)
    print(actual_file_path)


csv_data = []
with open(stripped_file, newline='') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        csv_data.append(row)

i = 0
for row in csv_data:
    this_csv_row = csv_data[i]

    file_element = this_csv_row[0]
    file_width = this_csv_row[1]
    file_height = this_csv_row[2]
    file_type = this_csv_row[3]
    if file_type == "None":
        expected_file_name = file_element + "_" + file_width + "_" + file_height
        #print(expected_file_name)
    else:
        file_type = file_type.replace("[", "")
        file_type = file_type.replace("]", "")
        these_types = file_type.split("|")
        for this_type in these_types:
            expected_file_name = this_type + "_" + file_element + "_" + file_width + "_" + file_height
            #print(expected_file_name)

    i += 1