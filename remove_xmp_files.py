import os

directory = input("Input directory to remove XMP files: ")
stripped_path = directory.replace('"', "")

files_in_directory = os.listdir(stripped_path)

filtered_files = [file for file in files_in_directory if file.endswith(".xmp")]

for file in filtered_files:
	path_to_file = os.path.join(stripped_path, file)
	os.remove(path_to_file)
