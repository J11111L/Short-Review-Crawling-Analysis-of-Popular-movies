import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import mysql.connector
import os
my_cookie = "gr_user_id=365152de-2f6f-445a-ad82-8b03064b595a; douban-fav-remind=1; ll=\"118318\"; bid=2uXnUuhqjFE; __yadk_uid=nJZfvl1Vf2Ov1qrYovKCWwctK3HSdqnW; _vwo_uuid_v2=DDC4449A754A4B9088C27B3678A9D1F41|9ba91b0e05a97c0b6baa8e2cc655397a; _pk_id.100001.4cf6=0ab5feb6f793fe25.1720514583.; __utmz=30149280.1720528388.5.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ct=y; push_doumail_num=0; push_noty_num=0; __utmv=30149280.28182; __utmz=223695111.1720849003.8.3.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; dbcl2=\"281829339:36PhNryeN7A\"; ck=3szs; ap_v=0,6.0; __utmc=30149280; __utmc=223695111; frodotk_db=\"444bc41de2f2b227cce34c59a8d81675\"; __utma=30149280.517235761.1667117881.1720918321.1720922070.13; __utmb=30149280.0.10.1720922070; __utma=223695111.1166054037.1667117881.1720918321.1720922070.10; __utmb=223695111.0.10.1720922070; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1720922070%2C%22https%3A%2F%2Fwww.douban.com%2F%3Fp%3D5%22%5D; _pk_ses.100001.4cf6=1"
standard_provinces = {
    '河北':'河北省',
    '山西':'山西省',
    '辽宁':'辽宁省',
    '吉林':'吉林省',
    '黑龙江':'黑龙江省',
    '江苏':'江苏省',
    '浙江':'浙江省',
    '安徽':'安徽省',
    '福建':'福建省',
    '江西':'江西省',
    '山东':'山东省',
    '河南':'河南省',
    '湖北':'湖北省',
    '湖南':'湖南省',
    '广东':'广东省',
    '海南':'海南省',
    '四川':'四川省',
    '贵州':'贵州省',
    '云南':'云南省',
    '陕西':'陕西省',
    '甘肃':'甘肃省',
    '青海':'青海省',
    '台湾':'台湾省',
    '内蒙古':'内蒙古自治区',
    '广西':'广西壮族自治区',
    '西藏':'西藏自治区',
    '宁夏':'宁夏回族自治区',
    '新疆':'新疆维吾尔自治区',
    '北京':'北京市',
    '天津':'天津市',
    '上海':'上海市',
    '重庆':'重庆市',
    '香港':'香港特别行政区',
    '澳门':'澳门特别行政区'
}
db_config = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : 'movie_reviews'
}

def init_password():
    db_config['password'] = input('Password:').strip()

def short_reviews(type,sort):#P for watched,N for watching, F for wishing
    stars = []
    reviews = []
    provinces = []
    times = []
    print('----------type:%s----------'%type)
    print('----------sort:%s----------'%sort)
    if type == 'P':
        for i in range(0,600,20):
            if sort == 'time':
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=time"%(str(i),type)
            else:
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=new_score"%(str(i),type)
            headers = {
                'User-Agent':UserAgent().random,
                'Cookie': my_cookie
            }
            resp = requests.get(url,headers=headers)
            soup = BeautifulSoup(resp.text,'lxml')
            if soup.title.text == "没有访问权限":
                break
            divs = soup.find_all('div',attrs={'class':'comment'})
            if divs == None:
                break
            for div in divs:
                span1 = div.find('span',attrs={'class':'comment-info'})
                span2 = span1.find_all('span')
                star = span2[1].get('class')[0][7]
                if  star == '-':
                    continue #处理未打分用户
                province = span2[3].text.strip()
                if not province in standard_provinces:
                    continue
                stars.append(int(star))
                span3 = div.find('span',attrs={'class':'short'})
                reviews.append(span3.text.strip())
                provinces.append(standard_provinces[province])
                times.append(span1.find('span',attrs={'class':'comment-time'}).text.strip())
        return stars,provinces,times,reviews
    elif type == 'N':
        for i in range(0,600,20):
            if sort == 'time':
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=time"%(str(i),type)
            else:
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=new_score"%(str(i),type)
            headers = {
                'User-Agent':UserAgent().random,
                'Cookie': my_cookie
            }
            resp = requests.get(url,headers=headers)
            soup = BeautifulSoup(resp.text,'lxml')
            if soup.title.text == "没有访问权限":
                break
            divs = soup.find_all('div',attrs={'class':'comment'})
            if divs == None:
                break
            for div in divs:
                span1 = div.find('span',attrs={'class':'comment-info'})
                span2 = span1.find_all('span')
                star = span2[0].get('class')[0][7]
                if  star == '-':
                    continue #处理未打分用户
                province = span2[2].text.strip()
                if not province in standard_provinces:
                    continue
                stars.append(int(star))
                span3 = div.find('span',attrs={'class':'short'})
                reviews.append(span3.text.strip())
                provinces.append(standard_provinces[province])
                times.append(span1.find('span',attrs={'class':'comment-time'}).text.strip())
        return stars,provinces,times,reviews
    else:
        for i in range(0,600,20):
            if sort == 'time':
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=time"%(str(i),type)
            else:
                url = "https://movie.douban.com/subject/36553434/comments?start=%s&limit=20&status=%s&sort=new_score"%(str(i),type)
            headers = {
                'User-Agent':UserAgent().random,
                'Cookie': my_cookie
            }
            resp = requests.get(url,headers=headers)
            soup = BeautifulSoup(resp.text,'lxml')
            if soup.title.text == "没有访问权限":
                break
            divs = soup.find_all('div',attrs={'class':'comment'})
            if divs == None:
                break
            for div in divs:
                span1 = div.find('span',attrs={'class':'comment-location'})
                province = span1.text.strip()
                if not province in standard_provinces:
                    continue
                provinces.append(standard_provinces[province])
                span2 = div.find('span',attrs={'class':'short'})
                reviews.append(span2.text.strip())
                times.append(div.find('span',attrs={'class':'comment-time'}).text.strip())
                stars.append(0)
        return stars,provinces,times,reviews

def upload(type,stars,provinces,times,reviews):
    try:
        conn = mysql.connector.connect(**db_config)

        if conn.is_connected():
            print('---------successfully connected---------')
            for i in range(len(stars)):
                cursor = conn.cursor()
                insert_query = "INSERT INTO reviews VALUES (%s, %s, %s, %s, %s);"

                data_to_insert = (type, stars[i], provinces[i], times[i], reviews[i])

                cursor.execute(insert_query, data_to_insert)

            conn.commit()


    except mysql.connector.Error as err:
        print(f"---------Error: {err}---------")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print('---------MySQL connection closed---------')

def download(type):
    stars=[]
    provinces=[]
    times=[]
    reviews=[]    
    try:
        conn = mysql.connector.connect(**db_config)

        if conn.is_connected():
            print('---------successfully connected---------')
            cursor = conn.cursor()

            query = 'SELECT * FROM reviews WHERE reviews.type = %s'
            cursor.execute(query, [type])

            rows = cursor.fetchall()
            for row in rows:
                stars.append(row[1])
                provinces.append(row[2])
                times.append(row[3])
                reviews.append(row[4])


    except mysql.connector.Error as err:
        print(f"---------Error: {err}---------")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print('---------MySQL connection closed---------')
    return stars,provinces,times,reviews

def delete():
    try:
        conn = mysql.connector.connect(**db_config)

        if conn.is_connected():
            print('---------successfully connected---------')
            cursor = conn.cursor()

            cursor.execute('DELETE FROM reviews;')

            conn.commit()


    except mysql.connector.Error as err:
        print(f"---------Error: {err}---------")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print('---------MySQL connection closed---------')

def spider(type,sort):
    s,p,t,r = short_reviews(type,sort)
    upload(type,s,p,t,r)
def spider_multi_types(types,sorts):
    for type in types:
        for sort in sorts:
            spider(type,sort)

def clean(stars,provinces,times,reviews):
    length = len(stars)
    locs = []
    for i in range(length):
        for j in range(i+1,length):
            if stars[i] == stars[j] and provinces[i] == provinces[j] and times[i] == times[j] and reviews[i] == reviews[j]:
                if not i in locs:
                    locs.append(i)
    locs.reverse()
    if locs == None:
        return
    for loc in locs:
        del stars[loc]
        del provinces[loc]
        del times[loc]
        del reviews[loc]

def clean_db():
    P_s,P_p,P_t,P_r = download('P')
    N_s,N_p,N_t,N_r = download('N')
    F_s,F_p,F_t,F_r = download('F')
    clean(P_s,P_p,P_t,P_r)
    clean(N_s,N_p,N_t,N_r)
    clean(F_s,F_p,F_t,F_r)
    delete()
    upload('P',P_s,P_p,P_t,P_r)
    upload('N',N_s,N_p,N_t,N_r)
    upload('F',F_s,F_p,F_t,F_r)

init_password()
if os.getenv('Spider'):
    types = ['P','N','F']
    sorts = ['hot','time']
    spider_multi_types(types,sorts)
    clean_db()