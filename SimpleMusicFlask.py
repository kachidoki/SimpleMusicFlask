import os, sys, logging
import argparse, io, urllib
from datetime import datetime

from flask import Flask
from flask import request
from flask import Response
from flask import send_file
from flask import jsonify
from flask_cors import CORS

from MusicApi import MusicApi
from SQLiteDB import SQLiteDB
from Recommendation import recommend
from MockData import Mock

app = Flask(__name__)
Api = MusicApi()
Db = SQLiteDB()
Rd = recommend(Db)

CORS(app)

def api_v1_error():
    error_message = 'Unexpected error'
    return Response(response = error_message, status = 404)

@app.route('/getMediaUrl', methods = ['GET'])
def api_v1_get_media_url():
    logging.debug(request.args)
    _id = request.args.get('songid')
    qqmusicurl = Api.GetMediaUrl(_id)

    if not qqmusicurl:
        return api_v1_error()

    res = {
        'res_code': 200,
        'res_err': '',
        'res_body': {
            'playurl' : qqmusicurl
        }
    }
    return jsonify(res)


@app.route('/getSearchList', methods = ['GET'])
def api_v1_get_search_list():
    logging.debug(request.args)
    word = request.args.get('keyword')
    limit = request.args.get('limit')
    page = request.args.get('page')

    if not word:
        return api_v1_error()

    search_list = Api.Search(word,page,limit)
    if not search_list:
        return api_v1_error()
    res = {
        'res_code': 200,
        'res_err': '',
        'res_body': {
            'songlist' : search_list,
            'cur_song_num' : len(search_list),
            'update_time' : datetime.now().strftime('%Y-%m-%d'),
        }
    }
    return jsonify(res)


@app.route('/getTopList', methods = ['GET'])
def api_v1_get_top_list():
    logging.debug(request.args)
    _id = request.args.get('topid')
    # 判断本地topList是否过期
    if Db.is_need_fetch_top_from_net(_id):
        (date,cur_song_num,topList) = Api.GetTop(_id)
        if not topList:
            return api_v1_error()
        Db.UpdateTop(_id,topList,date)
        print('fetch from net')
    else:
        (date,cur_song_num,topList) = Db.GetTop(_id)
        print('fetch from db')

    if not topList:
        return api_v1_error()

    res = {
        'res_code': 200,
        'res_err': '',
        'res_body': {
            'songlist' : topList,
            'cur_song_num' : cur_song_num,
            'update_time' : date,
        }
    }
    return jsonify(res)

@app.route('/getRecommendList', methods = ['GET'])
def api_v1_get_recommend_list():
    logging.debug(request.args)
    _id = request.args.get('uid')

    rd_list = Rd.do_recommend(_id,10)
    res_list = Api.WrapRecommend(rd_list)

    res = {
        'res_code': 200,
        'res_err': '',
        'res_body': {
            'songlist' : res_list,
            'cur_song_num' : len(res_list),
            'update_time' : datetime.now().strftime('%Y-%m-%d'),
        }
    }
    return jsonify(res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Web server port", type=int)
    parser.add_argument("-d", "--debug", help="debug mode: yes/no")
    args = parser.parse_args()

    if args.debug and args.debug == 'yes':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)
    # init
    Db.init_schema()
    #mk = Mock(Db)
    #mk.mock_insert_history()
    Rd.train_set()
    Rd.item_similarity()


    if args.port:
        try:
            app.run(host = '0.0.0.0', port = args.port)
        except PermissionError as e:
            logging.error('Permission denied')
    else:
        logging.info('Use default port')
        app.run(host = '0.0.0.0')
