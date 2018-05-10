import json, sys, random
from datetime import datetime

'''
        musicbean

        "songname": "染",
        "seconds": 230,
        "albummid": "003TP3Eo2jbUhT",
        "songid": 213792281,
        "songmid":
        "singerid": 199515,
        "albumpic_big": "http://i.gtimg.cn/music/photo/mid_album_300/h/T/003TP3Eo2jbUhT.jpg",
        "albumpic_small": "http://i.gtimg.cn/music/photo/mid_album_90/h/T/003TP3Eo2jbUhT.jpg",
        "downUrl": "http://dl.stream.qqmusic.qq.com/213792281.mp3?vkey=5E370DE8490A24739A5F48745D9193DAF08D16B9E7D947389904DA2A87E43B410ECC384794660775A0954A63CB98F0A55B74C496134480F7&guid=2718671044",
        "url": "http://ws.stream.qqmusic.qq.com/213792281.m4a?fromtag=46",
        "singername": "张碧晨",
        "albumid": 4025347
'''
class QQParser(object):
    def __init__(self):
        self.album_url = 'https://y.gtimg.cn/music/photo_new/T002R300x300M000'


    def TopParse(self, top_js_data):
        size = len(top_js_data)
        raw_dict = json.loads(top_js_data)


        date = datetime.now().strftime('%Y-%m-%d')
        song_nums = raw_dict['cur_song_num']

        song_list = raw_dict['songlist']
        res_song_list = []
        for song in song_list:
            song_date = song['data']
            singer_date = song_date['singer']
            simple_song_dict = {}
            simple_song_dict['songname'] = song_date['songname']
            simple_song_dict['seconds'] = 200 #读秒咋做？？
            simple_song_dict['albummid'] = song_date['albummid']
            simple_song_dict['songid'] = song_date['songid']
            simple_song_dict['songmid'] = song_date['songmid']
            simple_song_dict['singerid'] = singer_date[0]['id']
            simple_song_dict['singername'] = singer_date[0]['name']
            simple_song_dict['albumpic_big'] = self.album_url + song_date['albummid'] + '.jpg'
            simple_song_dict['albumpic_small'] = self.album_url + song_date['albummid'] + '.jpg'
            simple_song_dict['downUrl'] = ''
            simple_song_dict['url'] = ''
            simple_song_dict['albumid'] = song_date['albumid']

            res_song_list.append(simple_song_dict)
        return (date, song_nums, res_song_list)
