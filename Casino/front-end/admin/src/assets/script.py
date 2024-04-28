#!/usr/bin/python

### Script to generate the index.js file ###

import os

images = []
directories = []
content = ""

class Directory:

    def __init__(self, name):
        self.name = name
        self.files = []

    def add_file(self, file):
        self.files.append(file)

for file in os.listdir():
    if file == "index.js" or file == "script.py":
        continue
    if os.path.isfile(file):
        images.append(file)
    if os.path.isdir(file):
        directories.append(Directory(file))

for directory in directories:
    os.chdir(directory.name)
    for file in os.listdir():
        if os.path.isfile(file):
            directory.add_file(file)
        if os.path.isdir(file):
            raise Exception("Error: failed to generate index.js file. Multiple directories not supported.")
    os.chdir("../")

for image in images:
    name = image.replace("-", "")
    name = name.split(".")[0]
    content += ("import " + name + " from " + "\"./" + image + "\";\n")

for directory in directories:
    for file in directory.files:
        name = file.replace("-", "")
        name = name.split(".")[0]
        content += ("import " + name + " from " + "\"./" + directory.name + "/" + file + "\";\n")

content += "export {\n"

for image in images:
    name = image.replace("-", "")
    name = name.split(".")[0]
    content += (name + ",\n")

for directory in directories:
    for file in directory.files:
        name = file.replace("-", "")
        name = name.split(".")[0]
        content += (name + ",\n")

content += "};"

with open('index.js', 'w') as f:
    f.write(content)

print("[---Index.js generated successfully---]")