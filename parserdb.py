from configparser import ConfigParser

def config(filename='databasesetting.ini',section='postgres'):
    parser=ConfigParser()
    parser.read(filename)
    db={}
    if parser.has_section(section):
        db={k:v for k,v in parser.items(section)}
        # print(db)
    else:
        raise Exception('{0} has no section header {1}'.format(filename,section))
    return db