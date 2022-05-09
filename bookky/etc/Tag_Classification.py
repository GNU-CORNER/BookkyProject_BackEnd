from cgi import test
import os
import json
import urllib.request as req
from xml.dom.minidom import Element



def convert():
    f = open(os.getcwd()+'\\input.txt', 'r', encoding='utf-8')
    f2 = open(os.getcwd()+'\\output.json', 'w', encoding='utf-8')
    #print("[\n")
    f2.write("[\n")
    cnt = 0
    for i in f:
        number = i.rsplit("	")
        
        # print("	{\n")
        # print('		"Tag" : "'+number[0]+'",\n		"Elements" : " [')
        f2.write("	{\n")
        f2.write('		"Tag" : "'+number[0]+'",\n		"Elements" : [')
        for j in range(1,len(number)):
            if(j == len(number)-1):
                #print('"' + number[j] + '" ]\n  },\n')
                f2.write('"' + number[j].strip("\n") + '"]\n	},\n')
            else:
                # print('"' + number[j] + '", ')
                f2.write('"' + number[j] + '", ')



    #print("]\n")
    f2.write("]\n")
    f.close()
    f2.close()


def matching_Tag():
    
    # dirpath = os.getcwd()+"/thumbnail/"

    # if not os.path.isdir(dirpath):
    #     os.makedirs(dirpath)

    #f2.write("[\n")
    # for i in f:
    #     number = i.split()[0].strip()
    #     f2.write("    {\n") 
    #     Tag = i.replace(number,"").strip()
    #     f2.write('        "number" : '+number+',\n')
    #     f2.write('        "tag" : '+Tag+'\n    },\n')

    # f2.write("]") 

    f = open(os.getcwd()+'\\Gang.json', 'r', encoding='utf-8')
    f2 = open(os.getcwd()+'\\output.json', 'r', encoding='utf-8')
    f3 = open(os.getcwd()+'\\Get_Tag.json', 'w', encoding='utf-8')
    book_data = json.load(f)
    tag_data = json.load(f2)


    cnt = 0 

    for i in book_data:
        cnt = cnt + 1
        TITLE = str(i.get("TITLE"))
        SUBTITLE = str(i.get("SUBTITLE"))
        BOOK_INDEX = str(i.get("BOOK_INDEX"))
        BOOK_INTRODUCTION = str(i.get("BOOK_INTRODUCTION"))
        Allah_BID = str(i.get("Allah_BID"))

        # 대소문자 구분
        #print(TITLE +"  " + Allah_BID)

        Tag_list = []

        Cnt = 0
        for k in tag_data:

            TITLE_cnt = 0
            SUBTITLE_cnt = 0
            BOOK_INDEX_cnt = 0
            BOOK_INTRODUCTION_cnt = 0
            
            temp = []

            for j in range(len(k["Elements"])):
                TAG = k["Elements"][j]

                if TAG in TITLE:
                    location = TITLE.find(TAG)
                    if (location != 0 and TITLE[location-1].isalpha() == False) or location == 0:
                            if location+len(TAG) <= len(TITLE):
                                if location+len(TAG) == len(TITLE) or TITLE[location + len(TAG)].isalpha() == False:
                                    TITLE_cnt = TITLE_cnt + TITLE.count(TAG)
                                    
                if TAG in SUBTITLE:
                    location = SUBTITLE.find(TAG)
                    if (location != 0 and SUBTITLE[location-1].isalpha() == False) or location == 0:
                            if location+len(TAG) <= len(SUBTITLE):
                                if location+len(TAG) == len(SUBTITLE) or SUBTITLE[location + len(TAG)].isalpha() == False:
                                    SUBTITLE_cnt = SUBTITLE_cnt + SUBTITLE.count(TAG)
                                    

                if TAG in BOOK_INDEX:
                    location = BOOK_INDEX.find(TAG)
                    if (location != 0 and BOOK_INDEX[location-1].isalpha() == False) or location == 0:
                            if location+len(TAG) <= len(BOOK_INDEX):
                                if location+len(TAG) == len(BOOK_INDEX) or BOOK_INDEX[location + len(TAG)].isalpha() == False:
                                    BOOK_INDEX_cnt = BOOK_INDEX_cnt + BOOK_INDEX.count(TAG)

                if TAG in BOOK_INTRODUCTION:
                    location = BOOK_INTRODUCTION.find(TAG)
                    if (location != 0 and BOOK_INTRODUCTION[location-1].isalpha() == False) or location == 0:
                            if location+len(TAG) <= len(BOOK_INTRODUCTION):
                                if location+len(TAG) == len(BOOK_INTRODUCTION) or BOOK_INTRODUCTION[location + len(TAG)].isalpha() == False:
                                    BOOK_INTRODUCTION_cnt = BOOK_INTRODUCTION_cnt + BOOK_INTRODUCTION.count(TAG)

            if TITLE_cnt != 0 or SUBTITLE_cnt != 0 or BOOK_INDEX_cnt != 0 or BOOK_INTRODUCTION_cnt != 0:
                temp.append(Cnt)
                temp.append(TAG)
                temp.append(TITLE_cnt)
                temp.append(SUBTITLE_cnt)
                temp.append(BOOK_INDEX_cnt+BOOK_INTRODUCTION_cnt)
                Tag_list.append(temp)

            Cnt= Cnt + 1

    
        Last_Tag = []
        
        Tag_list.sort(key=lambda x:(-x[2],-x[3]))
        
        for i in range(len(Tag_list)):
            if Tag_list[i][2] != 0:
                Last_Tag.append(Tag_list[i][0])
            if Tag_list[i][3] != 0:
                Last_Tag.append(Tag_list[i][0])

        Tag_list.sort(key=lambda x:(-x[4]))

        for i in range(len(Tag_list)):
            if Tag_list[i][2] == 0 and Tag_list[i][3] == 0:
                Last_Tag.append(Tag_list[i][0])

        f3.write('{ "Allah_BID" : ' + Allah_BID)
        f3.write(', "Tag" : ')
        f3.write(str(Last_Tag))
        f3.write(" },\n")



if __name__ == "__main__":
    #convert()
    matching_Tag()




