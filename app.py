import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
from contextlib import closing
import socket

app = Flask(__name__, static_folder='./static')

db_connect = sqlite3.connect("texpo.db", check_same_thread=False)
cursor = db_connect.cursor()

#ここで選択できるスポーツを追加
sports_name = ["サッカー", "テニス", "ゴルフ", "バレー"]

user_host = socket.gethostname()
user_ip = socket.gethostbyname(user_host)

@app.route("/")
def search():
    cursor.execute("select user_ip from user where user_ip like ?",(user_ip,))
    user_certification = cursor.fetchall()
    if  not user_certification:
        cursor.execute("INSERT INTO user (user_ip) VALUES (?)", (user_ip,))

    db_connect.commit()
    return render_template("search.html")


@app.route("/search_pattern", methods=["GET","POST"])

def search_pattern():
    search_name = request.form["Sport"]

    sort_result = request.form.get("sort")

    if search_name == "":
        return render_template("search.html")

    else:
        if sort_result == "id":
            cursor.execute("select title, sport, content, id, like from post where sport like ? order by id desc;",(search_name,))
            search_result = cursor.fetchall()
        elif sort_result == "like":
            cursor.execute("select title, sport, content, id, like from post where sport like ? order by like desc;",(search_name,))
            search_result = cursor.fetchall()
        else:
            cursor.execute("select title, sport, content, id, like from post where sport like ?",(search_name,))
            search_result = cursor.fetchall()

    if search_result ==[]:

        if sort_result == "id":
            cursor.execute("select title, sport, content, id, like from post where title like ? order by id desc;",("%"+ search_name +"%",))
            search_result = cursor.fetchall()
        elif sort_result == "like":
            cursor.execute("select title, sport, content, id, like from post where title like ? order by like desc;",("%"+ search_name +"%",))
            search_result = cursor.fetchall()
        else:
            cursor.execute("select title, sport, content, id, like from post where title like ?",("%"+ search_name +"%",))
            search_result = cursor.fetchall()

        if search_result ==[]:
            notfound = "検索結果が見つかりませんでした。"
            return render_template("search.html", notfound=notfound)
        else:
            return render_template("search.html",search_result=search_result)
    else:
        return render_template("search.html",search_result=search_result)
    cursor.close()

@app.route('/another', methods=["GET", "POST"])
def second():
    return render_template('another.html', sports_name=sports_name)

@app.route('/upload', methods=["GET", "POST"])
def upload():
    title = request.form.get("title")
    sport = request.form.get("sport")
    content = request.form.get("content")
    search_result = [(title, sport, content)]
    cursor.execute("INSERT INTO post (title, sport, content) VALUES (?, ?, ?)",
            [title, sport, content])
    # cursor.execute("select like from post where=" )
    return render_template("search.html",search_result=search_result)

@app.route('/like', methods=["GET", "POST"])
def like():
    
    #like数を一つ増やす
    #post_id
    post_id = request.form.get("like")
    cursor.execute("select user_id from like where post_id = ?", (post_id,))
    like_user = cursor.fetchall()

    cursor.execute("select like from post where id = ?", (post_id,))
    like_add = cursor.fetchall()

    if not like_user:
        cursor.execute("select user_id from user where user_ip = ?", (user_ip,))
        user_id = cursor.fetchall()
        for userID in user_id:
            for user_id in userID:
                cursor.execute("INSERT INTO like (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
                cursor.execute("select bool from like where post_id = ?", (post_id,))
                like_bool = cursor.fetchall()
                for likeBool in like_bool:
                    for like_bool in likeBool:
                        if like_bool == 1:
                            print("いいねできませんよ")
                        else:
                            cursor.execute("update like set bool = ? where post_id = ?", (1, post_id))
                            for Addlike in like_add:
                                for like_add in Addlike:
                                    like_add += 1
                                    cursor.execute("update post set like = ? where id = ?", (like_add, post_id))
                            print("追加した")
        db_connect.commit()
    else:
        cursor.execute("select bool from like where post_id = ?", (post_id,))
        like_bool = cursor.fetchall()
        for likeBool in like_bool:
            for like_bool in likeBool:
                if like_bool == 1:
                    print("いいねできません")
                else:
                    cursor.execute("update like set bool = ? where post_id = ?", (1, post_id))
                    for Addlike in like_add:
                        for like_add in Addlike:
                            like_add += 1
                            cursor.execute("update post set like = ? where id = ?", (like_add, post_id))

    
    
    # # ここで以前検索したページの情報を取りたいんですけど、このsearch_nameをどうやって取得するのかがわかりません
    cursor.execute("select title from post where id=?",(post_id,))
    search_result = cursor.fetchall()
    for SERCH_result in search_result:
        for search in SERCH_result:
            cursor.execute("select title, sport, content, id, like from post where title=?", (search,))
            search_result = cursor.fetchall()
    db_connect.commit()
    return render_template("search.html",search_result=search_result)
    # # likedはsearch.htmlでif文を使うために設定しました。とくに関係ありません。post_idはそのidの投稿に飛べるようにと思ったんですが、まだhtmlではなにもしていません。
    # return render_template("search.html",search_result=search_result, liked=True, post_id=request.form.get("like"))
    
    

db_connect.commit()

app.debug =  True
app.run()

#cssが更新されてもwebにキャッシュされる不具合を解消するコード
#また、このコードを追記するにあたってos,url_forをimportした
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
#ここまで