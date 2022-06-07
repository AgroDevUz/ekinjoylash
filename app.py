import os
import time
from alive_progress import alive_bar

total = 0
ignore = ""

with open("map.md", "r") as f:
    ignore = f.read()
    total = len(ignore)
    

with open("leaflet.md", "w") as f:
    f.write("")


with alive_bar(total) as bar:
    for i in range(total):
        with open("leaflet.md", "a") as f:
            f.write(ignore[i])
        os.system("git add .")  
        os.system("git commit -m 'Commited'")
        if i % 100 == 0:
            os.system("git push")
        bar()

os.system("git push")  
