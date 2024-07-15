from bs4 import BeautifulSoup
import json

with open('init.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'lxml')

divs = soup.find_all('div',attrs={'class':'chart-container'})
nums = []
for div in divs:
    num = div.get('id').strip()
    nums.append(num)

with open('chart_config.json', 'r') as f:
    data = json.load(f)

for i in range(len(nums)):
    data[i]['cid'] = nums[i]

with open('chart_config.json', 'w') as f:
    json.dump(data, f,indent=4)
# legend: left:50%
# z: 2 top: 30% left: 35%