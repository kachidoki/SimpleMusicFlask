from QQApi import QQApi
from Network import Network

class MusicApi(object):
    def __init__(self, api_type = 'qq'):
        self.api_type = api_type
        if 'qq' == api_type:
            self.Api = QQApi()
        else:
            self.Api = QQApi()

    def Search(self, search_key, page = 1, limit = 8):
        return self.Api.Search(search_key, page, limit)

    def GetTop(self, topid):
        return self.Api.GetTop(topid)

    def GetMediaUrl(self, _id, size = 'size320'):
        return self.Api.GetMediaUrl(_id, size)

    def WrapRecommend(self, rd_list , limit = 20):
        return self.Api.WrapRecommend(rd_list ,limit)

    def Singer(self, simple_song_dict):
        singer = simple_song_dict['singername']
        if not singer:
            return None
        if len(singer) == 1:
            return singer[0]

        display = singer[0]
        for x in singer[1:]:
            display += ','
            display += x
        return display

    def Image(self, _id):
        return ''

    def RewriteUrl(self, url):
            return '/qqmusic' + url.split('dl.stream.qqmusic.qq.com')[1]

if __name__ == '__main__':
    Api = MusicApi()
    #songlist = Api.Search('胡桃夹子', 2, 10)
    #print(songlist)
    # if not songlist:
    #     sys.exit()

    # for x in songlist:
    #     print(Api.Singer(x))
        # print(x)
        # url = Api.GetMediaUrl(x['songid'])
        # print(url)
