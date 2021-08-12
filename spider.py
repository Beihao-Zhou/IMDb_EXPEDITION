# -*-coding = utf-8 -*-
#@Time: 2021/07/18
#@Author: Beihao Zhou
import codecs


# import modules
from bs4 import BeautifulSoup         #Parse web and get info
import re           #Regular expression and match words
import urllib.request, urllib.error         #request web information and catch errors
import xlwt         #export to excel
import sqlite3      #export data to SQLite


# Rules for looking for information of each movie
findLink = re.compile(r'<a href="(.*?)">')
findImgSrc = re.compile(r'<img.*?loadlate="(.*?)"',re.S)      #re.S includes the changing line part
findTitle = re.compile(r'<a href="/title/tt.*?ref_=adv_li_tt">(.*?)</a>')
findYear = re.compile(r'<span class="lister-item-year text-muted unbold">(.*?)</span>')
findCertificate = re.compile(r'<span class="certificate">(.*?)</span>')
findRuntime = re.compile(r'<span class="runtime">(\d*?) min</span>')
findGenre = re.compile(r'<span class="genre">(.*?)</span>',re.S)
findRating = re.compile(r'<div class="inline-block ratings-imdb-rating" data-value="(.*?)" name="ir">')
findMetascore = re.compile(r'<span class="metascore.*?">(.*?)</span>')
findDescription = re.compile(r'<p class="text-muted">(.*?)</p>',re.S)
findVotes = re.compile(r'<span class="text-muted">Votes:</span>\s+?<span data-value="(.*?)"')
findGross = re.compile(r'<span class="text-muted">Gross:</span>\s+?<span data-value="(.*?)"')
findDirector = re.compile(r'<a href="/name/nm.*?ref_=adv_li_dr_\d*">(.*?)</a>')
findStar = re.compile(r'<a href="/name/nm.*?ref_=adv_li_st_\d*">(.*?)</a>')



def main():
    baseurl = 'https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start='
    #crawl the web
    datalist = getData(baseurl)
    savepath = '.\\IMDb Top 250 movies.xls'         # IMDb Top 250 movies.xls --> store in the same folder
    dbpath = 'movie.db'
    #3. save data
    saveData(datalist,savepath)
    saveDataToDB(datalist,dbpath)




#crawl the web and parse it to get info
def getData(baseurl):
    datalist = []

    for i in range(0,5):            #call askURL function 5 times to get html of all 250 movies on each webpage
        url = baseurl+str(50*i+1)
        html = askURL(url)          #get the html of each webpage
        # parse the data
        soup = BeautifulSoup(html,"html.parser")

        for item in soup.find_all('div',class_="lister-item mode-advanced"):          # search for all the div, return a list
            data = []       # store all info for one movie
            item = str(item)

            link = "https://www.imdb.com"+re.findall(findLink,item)[0]
            data.append(link)

            img = re.findall(findImgSrc,item)[0]
            data.append(img)

            title = re.findall(findTitle,item)[0]
            data.append(title)

            year = re.findall('[0-9]+',re.findall(findYear,item)[0])[0]
            data.append(year)

            certificate = re.findall(findCertificate, item)
            if len(certificate)!=0:
                certificate = certificate[0]
                data.append(certificate)
            else:
                data.append(" ")

            runtime = re.findall(findRuntime,item)[0]
            data.append(runtime)

            genre = re.findall(findGenre,item)[0]
            genre = re.sub('\n','',genre)
            data.append(genre.strip())

            rating = re.findall(findRating,item)[0]
            data.append(rating)

            metascore = re.findall(findMetascore,item)
            if len(metascore)!=0:
                data.append(metascore[0].strip())          #delete the spaces
            else:
                data.append(" ")

            description = re.findall(findDescription,item)[1]
            description = re.sub('\n','',description)
            description = re.sub('"','',description)
            data.append(description)

            vote = re.findall(findVotes,item)[0]
            data.append(vote)

            gross = re.findall(findGross, item)
            if len(gross)!=0:
                gross = re.sub(',','',gross[0])
                data.append(gross)
            else:
                data.append(' ')

            director = re.findall(findDirector,item)
            data.append(", ".join(director))

            star = re.findall(findStar,item)
            data.append(", ".join(star))

            datalist.append(data)

    return datalist



#get the web content(html) of the assigned url
def askURL(url):
    head = {  #mimic the browser's headers info and send request to IMDb server
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
    } #user agent tells the IMDb server what kind of browser I am (In essense to tell the server what kind of content we can accept
    request = urllib.request.Request(url=url,headers=head)
    html=""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html



#save data
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet = book.add_sheet('IMDb Top 250 movies',cell_overwrite_ok=True)
    col = ('Movie Link','Image Link','Movie Title','Release Year','Certificate','Runtime','Genre','Rating','Meta Score','Description of Movie content','Votes','Gross($)','Director(s)','Star(s)')
    for i in range(14):
        sheet.write(0,i,col[i])
    for i in range(250):
        print("Movie %d"%(i+1))
        data = datalist[i]
        for j in range(14):
            sheet.write(i+1,j,data[j])
    book.save(savepath)



def saveDataToDB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for data in datalist:
        for i in range(len(data)):
            if i in [3,5,7,8,10,11] and data[i]!=" ":
                continue
            data[i] = '"'+data[i]+'"'
        sql = '''
            insert into movie250 (
            info_link,pic_link,title,year,certificate,runtime,genre,rating,meta_score,description,votes,gross,director,star)
            values (%s)'''%",".join(data)
        cur.execute(sql)
        conn.commit()

    cur.close()
    conn.close()



def init_db(dbpath):
    sql = '''
        CREATE TABLE movie250 (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        title varchar,
        year integer,
        certificate varchar,
        runtime numeric,
        genre varchar,
        rating numeric,
        meta_score integer,
        description text,
        votes integer,
        gross numeric,
        director text,
        star text
        );
    '''     # create a data table
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":          #The program is executed
    #call a function
    main()
    print("Finished!")