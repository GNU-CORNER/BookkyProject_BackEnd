import os
import json
import urllib.request as req



def get_thumbnail(url,path,img_name):

    thumbnail =  str(img_name) + ".png"

    print(url+"\n"+path+thumbnail)

    req.urlretrieve(url, path+thumbnail)

            
def get_jsondata():

    f = open(os.getcwd()+'\\BookData4.json', 'r', encoding='utf-8')
    json_data = json.load(f)

    dirpath = os.getcwd()+"/thumbnail/"

    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)


    cnt = 0 

    for i in json_data:
        url = i.get("thumbnail")
        Allah_BID = i.get("Allah_BID")
        get_thumbnail(url,dirpath,Allah_BID)
        



if __name__ == "__main__":
    get_jsondata()

 