import os

total = 0
ignore = ""

with open("test.py", "r") as f:
    ignore = f.read()
    total = len(ignore)
    print(f.read())
    
with open("map.md", "w") as f:
    f.write("")



for i in range(total):
    with open("test.py", "a") as f:
        f.write(ignore[i])
    os.system("git add .")  
    os.system("git commit -m 'Commited'")
    if i % 100 == 0:
        os.system("git push")
    

os.system("git push")  
