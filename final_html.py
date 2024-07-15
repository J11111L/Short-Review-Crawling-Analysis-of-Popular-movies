from pyecharts.charts import Page

Page.save_resize_html(
    source="init.html", 
    cfg_file="chart_config.json", 
    dest="final_dashboard.html")
