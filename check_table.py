from table_loader import TableLoader
import os

if __name__ == "__main__":
    a = os.listdir("./table")

    for file in a:
        t = TableLoader(file)
        print(len(t))

    print(".")

    t = TableLoader()