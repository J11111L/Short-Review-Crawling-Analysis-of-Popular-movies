import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pyecharts.charts import Pie
from pyecharts.charts import Bar
from pyecharts.charts import Grid
from pyecharts import options as  opts
from pyecharts.globals import ThemeType

def popular_reviews():#最受欢迎评论
    movies = []
    stars = []
    for i in range(0,100,20):
        headers={
            'User-Agent':UserAgent().random
        }
        url = "https://movie.douban.com/review/best/?start=%s"%str(i)
        resp = requests.get(url,headers=headers)
        soup = BeautifulSoup(resp.text,'lxml')
        tar_movies = soup.find_all('a',attrs={"class":"subject-img"})
        tar_stars = soup.find_all('header',attrs={'class':'main-hd'})
        for tar in tar_movies:
            movies.append(tar.img.get('title'))
        for tar in tar_stars:
            class_ = tar.find('span').get('class')
            stars.append(class_[0][7])
    return movies,stars

def get_hd_pplr_rvws():
    movies,stars = popular_reviews()

    M_S = {}
    M_T = {}
    for i in range(len(movies)):
        if(stars[i] == 't'):
            continue
        movie = movies[i]
        if not movie in M_S:
            M_T[movie] = 1
            M_S[movie] = round(float(stars[i]),1)
        else:
            M_S[movie] = round(((M_S[movie] * M_T[movie] + int(stars[i]))/(M_T[movie] + 1)),1)
            M_T[movie] += 1
    M_S_T = []
    for movie in list(M_S.keys()):
        M_S_T.append([movie,M_S[movie],M_T[movie]])
    M_S_T = sorted(M_S_T,key = lambda x:x[2],reverse=True)

    movies=[]
    stars=[]
    times=[]
    for i in range(len(M_S_T)):
        movies.append(M_S_T[i][0])
        stars.append(M_S_T[i][1])
        times.append(M_S_T[i][2])
    
    return movies,stars,times

def show_wlcmed_rvws_percent(movies,times):
    result_list = [(i,j) for i,j in zip(movies,times)]
    pie = Pie(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    pie.add(series_name='电影',
        center=['50%','35%'],
        data_pair = result_list,
        rosetype='radius',
        radius='40%',
        )
    pie.set_global_opts(title_opts=opts.TitleOpts(title="电影比例"),
                        legend_opts=opts.LegendOpts(pos_top='5%')
                        )
    pie.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger='item',formatter='{a} <br/>{b}:{c} ({d}%)'))
    return pie
def show_wlcmed_rvws_percent_star(movies,stars):
    bar = Bar(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    bar.add_xaxis(movies)
    bar.add_yaxis('星级', stars)
    bar.set_global_opts(
            title_opts=opts.TitleOpts(title="平均评分",pos_top = '60%'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-40)),
            legend_opts=opts.LegendOpts(orient='vertical',pos_top = '60%'),
            datazoom_opts=opts.DataZoomOpts(pos_top = '92%'),
        )
    bar.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger='item',formatter='{a} <br/>{b}:{c}星'))
    return bar

if __name__ == '__main__':
    m,s,t = get_hd_pplr_rvws()
    pie = show_wlcmed_rvws_percent(m,t)
    bar = show_wlcmed_rvws_percent_star(m,s)
    grid = Grid(init_opts = opts.InitOpts(width = "1700px",height = "950px",theme = ThemeType.DARK))
    grid.add(bar,grid_opts=opts.GridOpts(pos_top='65%',pos_bottom = '20%'))
    grid.add(pie,grid_opts=opts.GridOpts())
    grid.render('热评电影.html')