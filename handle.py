for i in range(2):
    file_name = "./new_project/result/txt/20.5_" + f"{i+1}"+ ".txt"
    with open(file_name, "r", encoding="utf-8") as f:
        with open("./new_project/result/txt/20.5.txt","a+", encoding="utf-8")as w:
            for line in f:
                if line == f"{386177}\n":
                    w.write(f"{386177+853}\n")
                elif not line == f"{853}\n":
                    w.write(line)