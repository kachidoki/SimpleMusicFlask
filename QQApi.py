import json, sys, random
from Network import Network
from QQParser import QQParser

class QQApi(object):
    def __init__(self):
        self.top_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?'
        self.search_url = 'https://c.y.qq.com/soso/fcgi-bin/search_cp?'
        self.musicexpress_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_musicexpress.fcg?'
        self.download_url = 'http://dl.stream.qqmusic.qq.com/'
        self.album_url = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000'

        self.network = Network()
        self.parser = QQParser()

        self.size_map = {
            'size128':'M500',
            'size320':'M800'
            }

    def Search(self, keyword, page, limit = 10):
        param = {
            'p':page,
            'n':limit,
            'w':keyword,
            'aggr':1,
            'lossless':1,
            'cr':1}

        uri = self.search_url + self.network.urlencode(param)
        #print(uri)
        data = self.network.urlrequest(uri)
        if not data:
            return None

        return self.parser.SearchParse(data)


    def GetTop(self, topid):
        param = {
            'topid':topid
        }
        uri = self.top_url + self.network.urlencode(param)
        js_data = self.network.urlrequest(uri)
        (date, song_nums, res_song_list) = self.parser.TopParse(js_data)
        #print(res_song_list)
        return (date, song_nums, res_song_list)

    def WrapRecommend(self, rd_list, limit=20):
        if not rd_list:
            return []
        res_rd_list = []
        for song in rd_list:
            wraped_song = self.parser.WrapRDSong(song)
            res_rd_list.append(wraped_song)
        return res_rd_list


    def GetMediaUrl(self, songid, size = 'size320'):
        guid = int(random.random() * 1000000000)
        param = {
            'json':3,
            'guid':guid
            }
        uri = self.musicexpress_url + self.network.urlencode(param)
        js_data = self.network.urlrequest(uri)
        if not js_data:
            return None
        length = len(js_data)
        data = json.loads(js_data[13:length - 2])
        url = self.download_url + self.size_map[size] + songid + '.mp3?'
        param = {
            'vkey':data['key'],
            'guid':guid,
            'fromtag':30
            }
        return url + self.network.urlencode(param)

if __name__ == '__main__':
    '''
    Api = QQApi()
    songlist = Api.Search('我是一只鱼', 1)
    if not songlist:
        sys.exit()

    for x in songlist:
        print(x)
        url = Api.GetMediaUrl(x['songid'])
        print(url)
    '''

    Api = QQApi()
    Api.GetTop(4)

    #url = Api.GetMediaUrl('003TfyNp47dm7E')
    #print(url)
