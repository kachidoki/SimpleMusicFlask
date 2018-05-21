import sqlite3, logging ,time
from datetime import datetime, timedelta
from Recommendation import recommend
from MockData import Mock

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SQLiteDB(object):
    def __init__(self, db_path = './data.sqlite'):
        try:
            self.connect = sqlite3.connect(db_path,check_same_thread = False)
        except sqlite3.Error as e:
            logging.error('init database error')

        self.connect.row_factory = dict_factory
        self.cursor = self.connect.cursor()

    def init_schema(self):
        sql_create_song = """
            CREATE TABLE IF NOT EXISTS songs(
            songid TEXT PRIMARY KEY NOT NULL,
            songname TEXT NOT NULL,
            seconds INTETGER ,
            albummid TEXT NOT NULL,
            songmid TEXT NOT NULL,
            singerid TEXT NOT NULL,
            albumpic_big TEXT ,
            albumpic_small TEXT ,
            downUrl TEXT ,
            url TEXT ,
            singername TEXT NOT NULL,
            albumid TEXT NOT NULL,
            topid INTETGER NOT NULL
            )
        """

        sql_create_savetime = """
            CREATE TABLE IF NOT EXISTS toptime(
            topid INTETGER PRIMARY KEY NOT NULL,
            savetime TEXT NOT NULL
            )
        """

        sql_create_history = """
            CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            songid TEXT NOT NULL,
            songname TEXT NOT NULL,
            albummid TEXT,
            songmid TEXT NOT NULL,
            singerid TEXT,
            singername TEXT,
            albumid TEXT,
            tmstamp INTEGER NOT NULL
            )
        """

        try:
            self.cursor.execute(sql_create_song)
            self.cursor.execute(sql_create_savetime)
            self.cursor.execute(sql_create_history)
            self.connect.commit()
        except sqlite3.Error as e:
            logging.error(e)


    # ------- recommend -------

    def history_get_all(self):
        sql = 'SELECT uid, songmid FROM history'
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            return data
        except sqlite3.Error as e:
            logging.info(e)
            return []

    def user_played_list_fetch(self, client_id):
        sql = 'SELECT songmid,songname FROM history WHERE uid = ? ORDER BY tmstamp ASC'
        try:
            self.cursor.execute(sql, [client_id])
            data = self.cursor.fetchall()
            return data
        except sqlite3.Error as e:
            logging.info(e)
            return None

    # 没有曲库，只能从history提取信息
    def song_fetch_by_ids(self, ids):
        if None == ids or 0 == len(ids):
            return None
        res_list = []
        for id in ids:
            sql = 'SELECT songid, songname, albummid, songmid, singerid, singername, albumid FROM history WHERE songmid = ?'
            try:
                self.cursor.execute(sql,(id,))
                data = self.cursor.fetchone()
                if not data:
                    continue
                res_list.append(data)
            except sqlite3.Error as e:
                logging.info(e)
        return res_list


    def save_history(self,one_history):
        sql = 'INSERT INTO history(uid,songid,songname,albummid,songmid,singerid,singername,albumid,tmstamp)VALUES(?,?,?,?,?,?,?,?,?)'
        data = (one_history['uid'],one_history['songid'],one_history['songname'],one_history['albummid'],one_history['songmid'],one_history['singerid'],one_history['singername'],one_history['albumid'],one_history['tmstamp'])
        try:
            self.cursor.execute(sql, data)
            self.connect.commit()
            return True
        except sqlite3.Error as e:
            logging.info(e)
            return False

    def save_history_tmp(self,uid,one_history):
        sql = 'INSERT INTO history(uid,songid,songname,albummid,songmid,singerid,singername,albumid,tmstamp)VALUES(?,?,?,?,?,?,?,?,?)'
        data = (uid,one_history['songid'],one_history['songname'],one_history['albummid'],one_history['songmid'],one_history['singerid'],one_history['singername'],one_history['albumid'],time.time())
        try:
            self.cursor.execute(sql, data)
            self.connect.commit()
        except sqlite3.Error as e:
            print(e)
            logging.info(e)

    # ------- topdate -------
    def save_date(self, topid, date):
        sql = 'INSERT INTO toptime VALUES(?,?)'
        data = (topid,date)
        try:
            self.cursor.execute(sql, data)
            self.connect.commit()
        except sqlite3.Error as e:
            logging.info(e)

    def update_date(self, topid, date):
        sql = 'UPDATE toptime SET savetime = ? WHERE topid = ?'
        data = (date,topid)
        try:
            self.cursor.execute(sql, data)
            self.connect.commit()
        except sqlite3.Error as e:
            logging.info(e)

    def get_top_date(self, topid):
        sql = 'SELECT topid,savetime FROM toptime WHERE topid = ?'
        try:
            self.cursor.execute(sql, (topid, ))
        except sqlite3.Error as e:
            logging.error(e)
        raw = self.cursor.fetchone()
        if not raw:
            return None
        return raw['savetime']

    def is_need_fetch_top_from_net(self, topid):
        db_str_date = self.get_top_date(topid)
        if not db_str_date:
            return True
        date = datetime.strptime(db_str_date,'%Y-%m-%d')
        nowdate = datetime.now()
        print(nowdate,date)
        return nowdate - date >= timedelta(hours=24)

    # ------- topsongs -------
    def get_top_songs(self, topid):
        sql = 'SELECT * FROM songs WHERE topid = ?'
        try:
            self.cursor.execute(sql, (topid, ))
        except sqlite3.Error as e:
            logging.error(e)
        return self.cursor.fetchall()

    def delete_top_songs(self, topid):
        sql = 'DELETE FROM songs WHERE topid = ?'
        try:
            self.cursor.execute(sql, (topid, ))
            self.connect.commit()
        except sqlite3.Error as e:
            logging.error(e)

    def put_top_songs(self,topsongs, topid):
        sql = 'INSERT INTO songs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'
        for song in topsongs:
            data = (song['songid'],
                    song['songname'],
                    song['seconds'],
                    song['albummid'],
                    song['songmid'],
                    song['singerid'],
                    song['albumpic_big'],
                    song['albumpic_small'],
                    song['downUrl'],
                    song['url'],
                    song['singername'],
                    song['albumid'],
                    topid)
            try:
                self.cursor.execute(sql, data)
            except sqlite3.Error as e:
                logging.info(e)
        try:
            self.connect.commit()
        except sqlite3.Error as e:
            logging.info(e)

    # fetch 合集操作
    def GetTop(self, topid):
        res_list = self.get_top_songs(topid)
        if not res_list:
            return (None,0,None)
        res_date = self.get_top_date(topid) # list不为空一定有date
        res_count = len(res_list)
        return (res_date,res_count,res_list)

    # update 合集操作
    def UpdateTop(self, topid, topList, date):
        self.delete_top_songs(topid)
        self.put_top_songs(topList, topid)
        last_date = self.get_top_date(topid)
        if not last_date:
            self.save_date(topid,date)
        else:
            self.update_date(topid,date)


    def close(self):
        self.connect.close()

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    s = SQLiteDB('/tmp/sqlite3.test')
    s.init_schema()

    '''
    test_list = ([{'songname': 'Bloom', 'seconds': 200, 'albummid': '002Ws4Vf2mZ61h', 'songid': 213849494, 'songmid': '000G3py61tKvTl', 'singerid': 25115, 'singername': 'Troye Sivan', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002Ws4Vf2mZ61h.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002Ws4Vf2mZ61h.jpg', 'downUrl': '', 'url': '', 'albumid': 4033633}, {'songname': '不安', 'seconds': 200, 'albummid': '000kFqNl2ja3e3', 'songid': 213837949, 'songmid': '003F8SsV28SG6r', 'singerid': 89698, 'singername': '庄心妍', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000000kFqNl2ja3e3.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000000kFqNl2ja3e3.jpg', 'downUrl': '', 'url': '', 'albumid': 4031973}, {'songname': '圆梦一代', 'seconds': 200, 'albummid': '002wxisP3y0bUl', 'songid': 213869570, 'songmid': '000VYFDZ1CWLWa', 'singerid': 91580, 'singername': '王俊凯', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002wxisP3y0bUl.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002wxisP3y0bUl.jpg', 'downUrl': '', 'url': '', 'albumid': 4036249}])

    test_list_2 = ([{'songname': '1111', 'seconds': 200, 'albummid': '002Ws4Vf2mZ61h', 'songid': 213849494, 'songmid': '000G3py61tKvTl', 'singerid': 25115, 'singername': 'Troye Sivan', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002Ws4Vf2mZ61h.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002Ws4Vf2mZ61h.jpg', 'downUrl': '', 'url': '', 'albumid': 4033633}, {'songname': '222', 'seconds': 200, 'albummid': '000kFqNl2ja3e3', 'songid': 213837949, 'songmid': '003F8SsV28SG6r', 'singerid': 89698, 'singername': '庄心妍', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000000kFqNl2ja3e3.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000000kFqNl2ja3e3.jpg', 'downUrl': '', 'url': '', 'albumid': 4031973}, {'songname': '333', 'seconds': 200, 'albummid': '002wxisP3y0bUl', 'songid': 213869570, 'songmid': '000VYFDZ1CWLWa', 'singerid': 91580, 'singername': '王俊凯', 'albumpic_big': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002wxisP3y0bUl.jpg', 'albumpic_small': 'https://y.gtimg.cn/music/photo_new/T002R300x300M000002wxisP3y0bUl.jpg', 'downUrl': '', 'url': '', 'albumid': 4036249}])

    s.put_top_songs(test_list,4)
    print(s.get_top_songs(4))
    print(s.GetTop(4))
    s.UpdateTop(4,test_list_2,'2018-5-10')
    print(s.GetTop(4))
    s.delete_top_songs(4)
    print(s.get_top_songs(4))

    print("----- debug date -----")

    s.save_date(4,'2018-05-08')
    s.update_date(4,'2018-05-09')
    s.update_date(5,'2018-05-09')
    print(s.get_top_date(4))
    print(s.get_top_date(5))
    print(s.is_need_fetch_top_from_net(5))
    '''

    history1 = {
        'uid':'1111',
        'songid':'213849494',
        'songname':'Bloom',
        'albummid':'002Ws4Vf2mZ61h',
        'songmid':'000G3py61tKvTl',
        'singerid':25115,
        'singername':'Troye Sivan',
        'albumid':4033633,
        'tmstamp':time.time()
    }

    #mk = Mock(s)
    #mk.mock_insert_history()

    #rd = recommend(s)
    #rd.train_set()
    #rd.item_similarity()
    #print(rd.do_recommend('8888',10))

    #s.save_history(history1)


    #print(s.history_get_all())
    #print(s.user_played_list_fetch('5555'))
    #print(s.song_fetch_by_ids(['000G3py61tKvTl']))
    s.close()
