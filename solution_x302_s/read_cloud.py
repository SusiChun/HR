import requests
# FOR TESTING #
r = requests.session()
datas = {'sdate': '2017-12-28','edate': '2017-12-28', 'uid': 3}
# datas = {}
response = r.post('http://172.16.5.11/form/Download',data=datas, stream=True)
block = response.text.split('\n')
print(block[0].split('\t')[4])
for elmt in range(len(block)):
    print(block[elmt])
