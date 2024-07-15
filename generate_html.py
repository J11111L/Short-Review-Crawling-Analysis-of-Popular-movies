from pyecharts.charts import Bar,Page,Pie,Map,Line,Timeline
from pyecharts import options as  opts
from pyecharts.globals import ThemeType
import mysql.connector
import jieba.analyse
import re
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType
from snownlp import SnowNLP
import os
import Spider_pplr_mv
def var(nums):
    val = 0
    length = len(nums)
    mean = sum(nums)/length
    for n in nums:
        val += (n-mean)**2
    return round(val/length,2)
def avg(nums):
    return round(sum(nums)/len(nums),2)

def hd(watched_provinces,watched_stars,
       watching_provinces,watching_stars,
       wishing_provinces
       ):
    P_len = len(watched_stars)
    N_len = len(watching_stars)
    F_len = len(wishing_provinces)
    result_pair = []
    result_pair.append(('看过',P_len))
    result_pair.append(('在看',N_len))
    result_pair.append(('想看',F_len))

    provinces_times = {}
    for p in watched_provinces:
        if not p in provinces_times:
            provinces_times[p] = 1
        else:
            provinces_times[p] += 1
    for p in watching_provinces:
        if not p in provinces_times:
            provinces_times[p] = 1
        else:
            provinces_times[p] += 1
            
    for p in wishing_provinces:
        if not p in provinces_times:
            provinces_times[p] = 1
        else:
            provinces_times[p] += 1
        
    avgs = [avg(watched_stars),avg(watching_stars)]
    varss = [var(watched_stars),var(watching_stars)]
    return result_pair,provinces_times,avgs,varss

def show_map(provinces_times,max_num):
    map = Map(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    map.add("评论人数", [list(z) for z in zip(list(provinces_times.keys()),list(provinces_times.values()))], "china")
    map.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    map.set_global_opts(title_opts=opts.TitleOpts(title="分布图"),
                        visualmap_opts=opts.VisualMapOpts(max_= max_num,pos_left = '10%',pos_bottom='10%'),
                        )
    return map
def show_rating(result_pair,centerx,centery,r,R):
    pie = Pie(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    pie.add(series_name='电影',
            center=[centerx,centery],
            data_pair = result_pair,
            radius=[r,R]
        )
    pie.set_global_opts(title_opts=opts.TitleOpts(title="比例"),
                        legend_opts=opts.LegendOpts(),)
    pie.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger='item',formatter='{a} <br/>{b}:{c} ({d}%)'),)
    return pie
def show_star(avgs,varss):
    bar = Bar(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    bar.add_xaxis(['看过','在看'])
    bar.add_yaxis('星级', avgs)
    bar.add_yaxis('评分方差',varss)
    bar.set_global_opts(
            title_opts=opts.TitleOpts(title='打分情况'),
            legend_opts=opts.LegendOpts(),
            yaxis_opts=opts.AxisOpts(name="星级"),
            xaxis_opts=opts.AxisOpts(name="类型")
        )
    return bar

def show_time_tend():
    times = []
    P_stars = []
    N_stars = []
    stars = {'P':P_stars,'N':N_stars}
    try:
        conn = mysql.connector.connect(**Spider_pplr_mv.db_config)

        if conn.is_connected():
            print('---------successfully connected---------')
            cursor = conn.cursor()

            query = 'SELECT type,star,time FROM reviews ORDER by time ASC'
            cursor.execute(query)

            rows = cursor.fetchall()
            standard_time = None
            P_stars_sum = 0
            N_stars_sum = 0
            stars_sum = {'P':P_stars_sum,'N':N_stars_sum}
            P_time = 0
            N_time = 0
            stars_time = {'P':P_time,'N':N_time}
            for row in rows:
                if row[0] == 'F':
                    continue
                if standard_time == None:
                    standard_time = row[2]
                    stars_sum[row[0]] = 0
                    stars_time[row[0]] = 0
                if row[2][:14] == standard_time[:14]:
                    star = int(row[1])
                    stars_sum[row[0]] += star
                    stars_time[row[0]] += 1
                else:
                    times.append(standard_time[:13])
                    standard_time = None
                    for type in ['P','N']:
                        if stars_time[type] != 0:
                            stars[type].append(round(stars_sum[type] / stars_time[type],2))
                        else:
                            stars[type].append(None)


    except mysql.connector.Error as err:
        print(f"---------Error: {err}---------")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print('---------MySQL connection closed---------')
    line = Line()
    line.add_xaxis(xaxis_data=times)
    line.add_yaxis(
        series_name="看过",
        y_axis=P_stars,
    )
    line.add_yaxis(
        series_name="在看",
        y_axis=N_stars,
    )
    line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line.set_global_opts(
        datazoom_opts=opts.DataZoomOpts(),
        title_opts=opts.TitleOpts(title="星级趋势"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(type_="value",min_=3,min_interval=1,),
    )
    return line

def get_keyword(text):
    keywords = jieba.analyse.textrank(
        sentence=text,
        topK=15,
        # allowPOS=['n','nz','ns', 'nr'],
        withWeight=False,  # 权重
        withFlag=False,    # 词性
    )
    return keywords

def hd_comment(comment):
    pattern = re.compile(r"[\u4e00-\u9fa5]+")
    words = re.findall(pattern, comment)
    text = ''
    for word in words:
        text += word
    stop_words = ['没有','感觉','看到','不能','希望','男人','时候', '防风', '知道','觉得','有点','清水','还有']
    words = jieba.lcut(text)
    text = ''
    for word in words:
        if not word in stop_words:
            text += word
    return text,words

def show_keywords_cloud(words):
    cloud = WordCloud(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    cloud.add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
    cloud.set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    return cloud

def emotion(comments):
    scores = []
    for comment in comments:
        s = SnowNLP(comment)
        scores.append(s.sentiments)
    return scores

def show_emotion(P_scores,N_scores,F_scores):
    types_scores =[P_scores,N_scores,F_scores]
    P_attitude = [0,0,0]
    N_attitude = [0,0,0]
    F_attitude = [0,0,0]
    types_attitude = [P_attitude,N_attitude,F_attitude]
    for i in range(3):
        for score in types_scores[i]:
            if score > 0.85:
                types_attitude[i][0] += 1
            elif score > 0.55:
                types_attitude[i][1] += 1
            else:
                types_attitude[i][2] += 1
    sum_attitude = [P_attitude[i] + N_attitude[i] + F_attitude[i] for i in range(3)]
    list1 = [{'value': P_attitude[i],'percent':round(P_attitude[i]/sum_attitude[i],2)} for i in range(3)]
    list2 = [{'value': N_attitude[i],'percent':round(N_attitude[i]/sum_attitude[i],2)} for i in range(3)]
    list3 = [{'value': F_attitude[i],'percent':round(F_attitude[i]/sum_attitude[i],2)} for i in range(3)]
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add_xaxis(['积极','中肯','消极'])
        .add_yaxis("看过", list1, stack="stack1", category_gap="50%")
        .add_yaxis("在看", list2, stack="stack1", category_gap="50%")
        .add_yaxis("想看", list3, stack="stack1", category_gap="50%")
        .set_series_opts(
            label_opts=opts.LabelOpts(
                position="right",
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title='情感分析'),
            legend_opts=opts.LegendOpts(),
            yaxis_opts=opts.AxisOpts(name="占比"),
            xaxis_opts=opts.AxisOpts(name="态度")
        )
    )
    return c

def time_tend():
    times = []
    P_stars = []
    N_stars = []
    stars = {'P':P_stars,'N':N_stars}
    try:
        conn = mysql.connector.connect(**Spider_pplr_mv.db_config)

        if conn.is_connected():
            print('---------successfully connected---------')
            cursor = conn.cursor()

            query = 'SELECT type,star,time FROM reviews ORDER by time ASC'
            cursor.execute(query)

            rows = cursor.fetchall()
            standard_time = None
            P_stars_sum = 0
            N_stars_sum = 0
            stars_sum = {'P':P_stars_sum,'N':N_stars_sum}
            P_time = 0
            N_time = 0
            stars_time = {'P':P_time,'N':N_time}
            count = 0
            for row in rows:
                if row[0] == 'F':
                    continue
                if standard_time == None:
                    standard_time = row[2]
                    stars_sum[row[0]] = 0
                    stars_time[row[0]] = 0
                if row[2][:14] == standard_time[:14]:
                    star = int(row[1])
                    stars_sum[row[0]] += star
                    stars_time[row[0]] += 1
                elif count == 0:
                    count = 0
                    times.append(standard_time[:13])
                    standard_time = None
                    for type in ['P','N']:
                        if stars_time[type] != 0:
                            stars[type].append(round(stars_sum[type] / stars_time[type],2))
                        else:
                            stars[type].append(None)
                else:
                    count += 1


    except mysql.connector.Error as err:
        print(f"---------Error: {err}---------")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print('---------MySQL connection closed---------')
    return times,P_stars,N_stars

def show_time_tend(times,P_stars,N_stars,days,good,mid,bad):
    tl = Timeline(init_opts=opts.InitOpts(theme = ThemeType.DARK))
    x_label = ['%s点'%(int(d)) for d in days]
    init_day = ''
    ps = [0 for i in range(24)]
    ns = [0 for i in range(24)]
    for i in range(len(times)):
        day = times[i][5:7] + times[i][8:10]
        time = int(times[i][11:13])
        if init_day == '':
            init_day = day
        elif init_day == day:
            ps[time] = P_stars[i]
            ns[time] = N_stars[i]
        else:
            init_day = ''
            line = Line()
            line.add_xaxis(x_label)
            line.add_yaxis(
                series_name="看过",
                y_axis=ps,
                yaxis_index=1,
            )
            line.add_yaxis(
                series_name="在看",
                y_axis=ns,
                yaxis_index=1,
            )
            line.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            bar = Bar(init_opts=opts.InitOpts(theme = ThemeType.DARK))
            bar.add_xaxis(x_label)
            bar.add_yaxis('好评',good)
            bar.add_yaxis('中评',mid)
            bar.add_yaxis('差评',bad)
            bar.set_global_opts(
                    title_opts=opts.TitleOpts(title='时段打分情况',subtitle='%s月%s日'%(times[i][5:7],times[i][8:10])),
                    legend_opts=opts.LegendOpts(),
                )
            bar.extend_axis(
                yaxis=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value} 星"), interval=1,max_=5
                )
            )
            bar.set_series_opts(itemstyle_opts=opts.ItemStyleOpts(opacity=0.4),
                                label_opts=opts.LabelOpts(is_show=False),
                                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} 次"),interval=2,max_=10)
                                )
            bar.overlap(line)
            tl.add(bar, day)
            ps = [0 for i in range(24)]
            ns = [0 for i in range(24)]
    return tl

if __name__ == '__main__':
    char = input('need to spider? y/n').strip()
    while True:
        if char == 'y' or char == 'Y':
            os.environ['Spider'] = 'True'
            break
        elif char == 'n' or char == 'N':
            os.environ['Spider'] = 'False'
            break
        else:
            char = input('wrong type!\nneed to spider? y/n').strip()
    from Spider_pplr_mv import download
    os.environ['Spider'] = 'False'
    P_s,P_p,P_t,P_r = download('P')
    N_s,N_p,N_t,N_r = download('N')
    F_s,F_p,F_t,F_r = download('F')
    comments = ''
    for i in range(len(P_r)):
        comments += P_r[i]
    for i in range(len(N_r)):
        comments += N_r[i]
    for i in range(len(F_r)):
        comments += F_r[i]
    text,words = hd_comment(comments)
    keywords = get_keyword(text)
    keyword_time = {}
    for keyword in keywords:
        keyword_time[keyword] = 0
    for word in words:
        if word in keywords:
            keyword_time[word] += 1
    ktk = list(keyword_time.keys())
    ktt = list(keyword_time.values())
    words = [(i,j) for i,j in zip(ktk,ktt)]
    result_pair,provinces_times,avgs,varss = hd(P_p,P_s,N_p,N_s,F_p)
    P_scores = emotion(P_r)
    N_scores = emotion(N_r)
    F_scores = emotion(F_r)
    times,P_stars,N_stars = time_tend()
    days = ['0%s'%str(i) for i in range(10)]
    for i in range(10,24):
        days.append('%s'%str(i))
    good = [0 for i in range(24)]
    mid = [0 for i in range(24)]
    bad = [0 for i in range(24)]
    for i in range(len(times)):
        pos = int(times[i][11:13])
        if P_stars[i] >= 4:
            good[pos] += 1
        elif P_stars[i] >= 2:
            mid[pos] += 1
        else:
            bad[pos] += 1
        if N_stars[i] >= 4:
            good[pos] += 1
        elif P_stars[i] >= 2:
            mid[pos] += 1
        else:
            bad[pos] += 1


    emotion_bar = show_emotion(P_scores,N_scores,F_scores)
    cloud = show_keywords_cloud(words)
    map_cn = show_map(provinces_times,200)
    pie = show_rating(result_pair,centerx='50%',centery='50%',r='20%',R='60%')
    bar = show_star(avgs,varss)
    tl = show_time_tend(times,P_stars,N_stars,days,good,mid,bad)


    page = Page(layout=Page.DraggablePageLayout) 
    page.add(emotion_bar,tl,cloud,pie,map_cn,bar) 
    page.render('init.html')