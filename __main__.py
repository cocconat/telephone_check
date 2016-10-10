#!/usr/bin/python
import logging
import csv
import os
from collections import defaultdict
#import sys
import easygui
#import argparse

def all_csv_files(db_folder):
    '''
    yield all csv file from db folder
    '''
    for file_ in os.listdir(db_folder):
        if file_[-3:]=='csv':
            yield db_folder+"/"+file_

def column(file_):
    '''
    find the column with phone numbers reading the headers"
    '''
    with open(file_,'r') as csvfile:
        z=csv.reader(csvfile).next()
        for count,tel in enumerate(z):
            if any(word in tel for word in ["Tel","TEL","tel","tEL","Tel","CEL","cel"]):
                return count

def import_names(file_,listone):
    '''
    import name from the file and save to a dict, you a have to pass the dict \
    it detects telephon column and enrich the dictionary
    '''

    try: col=column(file_)
    except ValueError:
        print "no column header"
    with open(file_,'r') as csvfile:
        z=csv.reader(csvfile)
        header=z.next()
        logging.warning(file_+ "the number column is the {}:".format(col,z.next()[0]))
        for name in z:
            listone[name[col]]=name
        logging.warning("new db header: {}".format(header))
        return header


def db_to_dict(db):
    '''
    enrich dict with db files
    '''
    dict_=defaultdict()
    if os.path.isfile(db):
        header=import_names(db,dict_)
    else:
        for file_ in all_csv_files(db):
            header=import_names(file_,dict_)
    return header,dict_

def check_list_to_dict(listToCheck):
    '''
    enrich check dictionary with check file
    '''
    check_dict={}
    header= import_names(listToCheck,check_dict)
    return header,check_dict

def check_list(check_fileheader,db,savepath,option=False):
    '''
    complex function: match the list!
    the option is required for a particular scope, if you want to \
    -clean- a db file in respct with the checklist.
    check_fileheader is a tuple with check_file dictionary and itself headers.
    '''
    logging.warning("matching in progress")
    sort=sorted(db[1].keys())
    check_file=check_fileheader[1]
    header=check_fileheader[0]
    if not option:
        for count, name in enumerate(check_file.keys()):
            if name in sort or "373" in name[:3]:
                print count, ', '.join(map(str, check_file[name]))
                check_file.pop(name)
        write_file(check_file,savepath,header)
        return check_file
    if option:
        logging.warning("db purify mode")
        for name in db[1].keys():
            if check_file.has_key(name) :
                db[1].pop(name)
        write_file(db[1],savepath,header=db[0])

def write_file(dict_,path,header=None):
    with open(path,'w+') as csvfile:
        z=csv.writer(csvfile, delimiter=',')
        if header: z.writerow(header)
        for name in dict_.keys():
            z.writerow(dict_[name])

if __name__=="__main__":
    print "executing program!"
    easygui.msgbox(msg="questo programma aggiungerà elementi al tuo database,la procedura standard è selezionare il db sidoti e il file nuovo. il programma verificherà che il db Gcall venga pulito dai nomi presenti nel resto")
    default="/home/cocco/Documents/redford/"
    proced= easygui.choicebox("cosa vuoi fare?\n 1)aggiungere elemento\n 2)pulire database\n 3)cercare nome",choices=["1","2","3"])
    if proced=="1":
        db=easygui.diropenbox(msg="seleziona la cartella con il db",default=default)
        listToCheck=easygui.fileopenbox("seleziona la lista da verificare",filetypes="*.csv")
        goodpath=easygui.enterbox(msg="numero del file nella cartella db, ex: 46")
        goodpath=db+"/sidoti."+goodpath+".csv"
        if not easygui.boolbox(msg="cartella db: {}\
                               file da controllare: {}\
                           procedere?".format(db,goodpath)):
            exit(0)
        check_dictionary=check_list(check_list_to_dict(listToCheck),db_to_dict(db),savepath=goodpath,option=False)
    if proced=="2":
        db_inverso=easygui.fileopenbox("seleziona il file database da pulire")
        listToCheck=easygui.fileopenbox("seleziona la lista di nomi",filetypes="*.csv")
        check_list(check_list_to_dict(listToCheck),db_to_dict(db_inverso),savepath=db_inverso[:-4]+"I.csv",option=True)
    if proced=="3":
        again=True
        db=easygui.diropenbox(msg="seleziona la cartella con il db",default=default)
        db=db_to_dict(db)[1]
        while again:
            search=easygui.enterbox().lower().split()
            a=[]
            for name in db.values():
                if all(element in "".join(name).lower() for element in search):
                    #logging.warn("".join(name)+search)
                    a.append(" ".join(name))
            easygui.msgbox(msg="\n".join(a))
            again=easygui.boolbox("cercare ancora?")
