import csv # import csv library
import pandas
import time_util

def append_to_csv( name, fields ):
    with open(r'output/' + name + '', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

def dict_to_csv( name, csv_columns, dict_data ):
    """ Creates csv file named name in current directory

    1. Create file with name from the name parameter in current directory
    2. Load file as python object in memory as csvfile
    3. Write headers from csv_columns parameter
    4. Write data from dict_data parameter

    # Test Columns
    csv_columns = ['No','Name','Country']

    # Test Dictionary
    dict_data = [
    {'No': 1, 'Name': arg_path, 'Country': 'India'},
    {'No': 2, 'Name': arg_path, 'Country': 'USA'},
    {'No': 3, 'Name': arg_path, 'Country': 'India'},
    {'No': 4, 'Name': arg_path, 'Country': 'USA'},
    {'No': 5, 'Name': 'Yuva Raj', 'Country': 'India'},
    ]
    """

    csv_file = name + ".csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def list_to_csv( name, csv_columns, list_data ):
    """ Creates csv file named name in current directory

    1. Create file with name from the name parameter in current directory
    2. Load file as python object in memory as csvfile
    3. Write headers from csv_columns parameter
    4. Write data from list_data parameter

    # Test Columns
    csv_columns = ['No','Name','Country']

    # Test Dictionary
    list_data = [[1.2,'abc',3],[1.2,'werew',4],[1.4,'qew',2]]
    """
    csv_file = name + ".csv"
    try:
        with open('output/'+ csv_file,'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_columns)
            # NOTE for single dimension list use
            #for item in list_data:
            #    writer.writerow([item])
            # NOTE for multiple dimension list use
            for data in list_data:
                writer.writerows([data])
    except IOError:
        print("I/O error")

    # Using Pandas **WORKS**
    #df = pandas.DataFrame(data={"location": list_data})
    #df.to_csv("./" + csv_file, sep=',',index=False)

if __name__ == '__main__':
    name = "test.csv"
    fields=['first','second','third']
    # This is the start of the program   
    append_to_csv( name, fields ) # execute main
