import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = 'database.db'

def seed():
    # 確保資料庫已經初始化
    if not os.path.exists(DB_PATH):
        import database
        database.init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Seeding database...")

    # 1. 建立測試使用者 (如果已經存在則獲取，否則插入)
    users = [
        ('andrew', generate_password_hash('password')),
        ('alice', generate_password_hash('password')),
        ('bob', generate_password_hash('password'))
    ]
    
    user_ids = {}
    for username, p_hash in users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, p_hash))
            user_ids[username] = cursor.lastrowid
        else:
            user_ids[username] = row[0]

    # 2. 獲取或建立看板
    boards = ['二手交易版', '選課討論版', '失物招領版', '心情版']
    board_ids = {}
    for b_name in boards:
        cursor.execute("SELECT id FROM boards WHERE name = ?", (b_name,))
        row = cursor.fetchone()
        if row:
            board_ids[b_name] = row[0]
        else:
            cursor.execute("INSERT INTO boards (name) VALUES (?)", (b_name,))
            board_ids[b_name] = cursor.lastrowid

    # 3. 建立測試文章 (如果無文章則插入)
    cursor.execute("SELECT COUNT(*) FROM posts")
    if cursor.fetchone()[0] == 0:
        posts = [
            (board_ids['選課討論版'], user_ids['alice'], 'FCU 網頁系統開發這門課推嗎？', '想問問看有沒有學長姐修過這門課？老師人好不好，會不會很重？有分組報告或期末專題嗎？', '選課,網頁開發,推不推'),
            (board_ids['選課討論版'], user_ids['andrew'], '微積分基礎觀念分享與考古題整理', '期末考快到了，幫大家整理了幾題常見的考題跟極限、微分公式的觀念解析，有問題可以在下面一起討論！祝大家歐趴！', '微積分,考古題,課業討論'),
            (board_ids['二手交易版'], user_ids['bob'], '畢業出清！二手教科書/螢幕/人體工學椅', '要搬出宿舍了，便宜售出二手教科書（經濟學原理、計算機概論）跟一些生活用品，還有一個 24 吋螢幕 and 人體工學椅，意者私訊！', '二手交易,出清,教科書'),
            (board_ids['失物招領版'], user_ids['alice'], '在人言大樓2樓女廁撿到鑰匙', '在人言大樓2樓女廁的洗手台撿到一串有熊大吊飾的鑰匙，已送到教官室，失主請趕快去認領喔！', '失物招領,鑰匙,人言大樓'),
            (board_ids['心情版'], user_ids['andrew'], '今天期末考考完終於解脫了...', '考了整整一週，今天最後一科考完走出教室看到夕陽差點哭出來。大家期末辛苦了！', '心情,期末考,放假')
        ]
        post_ids = []
        for b_id, u_id, title, content, tags in posts:
            cursor.execute("INSERT INTO posts (board_id, user_id, title, content, tags) VALUES (?, ?, ?, ?, ?)",
                           (b_id, u_id, title, content, tags))
            post_ids.append(cursor.lastrowid)

        # 4. 建立文章留言
        comments = [
            (post_ids[0], user_ids['andrew'], '大推！這門課老師上課很有料，而且專題做完真的學到很多實務經驗！'),
            (post_ids[0], user_ids['bob'], '推！但建議要有基本的前端或後端程式基礎，不然做期末專題時會有點吃力喔。'),
            (post_ids[3], user_ids['bob'], '天啊！好像是我的鑰匙！感謝好心人，等等立馬去教官室認領！'),
            (post_ids[4], user_ids['alice'], '恭喜解脫！我也還剩一科明天考，祝大家都歐趴！')
        ]
        for p_id, u_id, content in comments:
            cursor.execute("INSERT INTO post_comments (post_id, user_id, content) VALUES (?, ?, ?)",
                           (p_id, u_id, content))
            
    # 4.5. 程式化大量建立設施資料
    cursor.execute("SELECT COUNT(*) FROM facilities")
    if cursor.fetchone()[0] == 0:
        facilities_to_insert = []
        
        # 1. 人言大樓
        ren_yan_floors = ["B2", "B1", "1樓", "2樓", "3樓", "4樓", "5樓", "6樓", "7樓", "8樓", "9樓", "10樓"]
        for fl in ren_yan_floors:
            # Classrooms & special facilities
            if fl == "B2":
                facilities_to_insert.append(("人言大樓", fl, "B201教室", "教室", "B201普通階梯教室"))
                facilities_to_insert.append(("人言大樓", fl, "B202教室", "教室", "B202普通階梯教室"))
            elif fl == "B1":
                facilities_to_insert.append(("人言大樓", fl, "B101電腦教室", "讀書空間", "B101高性能電腦教室"))
                facilities_to_insert.append(("人言大樓", fl, "B102電腦教室", "讀書空間", "B102教學電腦教室"))
                facilities_to_insert.append(("人言大樓", fl, "啟垣廳", "其他", "大型演講廳，多辦理演講與大型活動"))
            elif fl == "1樓":
                facilities_to_insert.append(("人言大樓", fl, "101教室", "教室", "備有雙投影設備及充足插座的一般教室"))
                facilities_to_insert.append(("人言大樓", fl, "102教室", "教室", "中型多媒體教學教室"))
                facilities_to_insert.append(("人言大樓", fl, "積學堂", "讀書空間", "人言教育創新中心，提供舒適寬敞的沙發自修與小組討論區"))
                facilities_to_insert.append(("人言大樓", fl, "哺集乳室", "其他", "提供隱密安全的溫馨育嬰哺乳空間"))
            else:
                f_num = fl.replace("樓", "")
                for r in range(1, 7):
                    name = f"{f_num}0{r}教室" if int(f_num) < 10 else f"{f_num}{r:02d}教室"
                    facilities_to_insert.append(("人言大樓", fl, name, "教室", f"{name}多媒體教學教室"))
            
            # Public facilities
            facilities_to_insert.append(("人言大樓", fl, "飲水機", "飲水機", f"人言大樓 {fl} 公共飲水機，提供冰溫熱水，定期檢測保養"))
            facilities_to_insert.append(("人言大樓", fl, "垃圾桶", "垃圾桶", f"人言大樓 {fl} 一般垃圾與資源回收桶"))
            facilities_to_insert.append(("人言大樓", fl, "男廁", "廁所", f"人言大樓 {fl} 男生廁所，乾淨衛生"))
            facilities_to_insert.append(("人言大樓", fl, "女廁", "廁所", f"人言大樓 {fl} 女生廁所，採光明亮"))
            if fl in ["B1", "1樓", "5樓", "10樓"]:
                facilities_to_insert.append(("人言大樓", fl, "販賣機", "販賣機", f"人言大樓 {fl} 自動販賣機，提供冷飲與零食"))
                
        # 2. 忠勤樓
        zhong_qin_floors = ["B1", "1樓", "2樓", "3樓", "4樓"]
        for fl in zhong_qin_floors:
            if fl == "B1":
                facilities_to_insert.append(("忠勤樓", fl, "地下停車場", "其他", "師生專用地下室內汽機車收費停車場"))
            else:
                f_num = fl.replace("樓", "")
                for r in range(1, 9):
                    name = f"{f_num}0{r}教室"
                    facilities_to_insert.append(("忠勤樓", fl, name, "教室", f"忠勤樓 {name} 多媒體教學教室"))
                if fl == "2樓":
                    facilities_to_insert.append(("忠勤樓", fl, "讀書空間", "讀書空間", "安靜自習角，提供插座與自習隔板"))
            
            facilities_to_insert.append(("忠勤樓", fl, "飲水機", "飲水機", f"忠勤樓 {fl} 公共飲水機"))
            facilities_to_insert.append(("忠勤樓", fl, "垃圾桶", "垃圾桶", f"忠勤樓 {fl} 垃圾與回收桶"))
            facilities_to_insert.append(("忠勤樓", fl, "男廁", "廁所", f"忠勤樓 {fl} 男生廁所"))
            facilities_to_insert.append(("忠勤樓", fl, "女廁", "廁所", f"忠勤樓 {fl} 女生廁所"))
            if fl == "1樓":
                facilities_to_insert.append(("忠勤樓", fl, "販賣機", "販賣機", f"忠勤樓 {fl} 自動飲料販賣機"))

        # 3. 商學大樓
        shang_xue_floors = ["B1", "1樓", "2樓", "3樓", "4樓", "5樓", "6樓", "7樓", "8樓"]
        for fl in shang_xue_floors:
            if fl != "B1":
                f_num = fl.replace("樓", "")
                for r in range(1, 11):
                    name = f"{f_num}0{r}教室" if r < 10 else f"{f_num}{r}教室"
                    facilities_to_insert.append(("商學大樓", fl, name, "教室", f"商學大樓 {name} 商管課程教學教室"))
                if fl == "1樓":
                    facilities_to_insert.append(("商學大樓", fl, "哺集乳室", "其他", "便利溫馨的集乳室"))
                elif fl == "3樓":
                    facilities_to_insert.append(("商學大樓", fl, "研討室", "討論空間", "小組專案報告討論室，備有白板與投影機"))
                    
            facilities_to_insert.append(("商學大樓", fl, "飲水機", "飲水機", f"商學大樓 {fl} 飲水機"))
            facilities_to_insert.append(("商學大樓", fl, "垃圾桶", "垃圾桶", f"商學大樓 {fl} 垃圾桶"))
            facilities_to_insert.append(("商學大樓", fl, "男廁", "廁所", f"商學大樓 {fl} 男生廁所"))
            facilities_to_insert.append(("商學大樓", fl, "女廁", "廁所", f"商學大樓 {fl} 女生廁所"))
            if fl in ["B1", "1樓", "4樓", "8樓"]:
                facilities_to_insert.append(("商學大樓", fl, "販賣機", "販賣機", f"商學大樓 {fl} 自動飲料販賣機"))

        # 4. 資訊電機館
        zi_dian_floors = ["B1", "1樓", "2樓", "3樓", "4樓"]
        for fl in zi_dian_floors:
            if fl == "B1":
                facilities_to_insert.append(("資訊電機館", fl, "B01教室", "教室", "資電館地下階梯教室，考場首選"))
                facilities_to_insert.append(("資訊電機館", fl, "B02教室", "教室", "資電館地下階梯教室，設有雙槍投影"))
                facilities_to_insert.append(("資訊電機館", fl, "B15電腦教室", "讀書空間", "軟體工程專用實作電腦教室"))
            else:
                f_num = fl.replace("樓", "")
                for r in range(1, 9):
                    name = f"{f_num}0{r}教室"
                    facilities_to_insert.append(("資訊電機館", fl, name, "教室", f"資訊電機館 {name} 教學教室"))
                if fl == "1樓":
                    facilities_to_insert.append(("資訊電機館", fl, "1樓大廳", "其他", "寬敞公共大廳，常作為學生小組非正式討論區"))
                elif fl == "2樓":
                    facilities_to_insert.append(("資訊電機館", fl, "資電學院辦公室", "其他", "資電學院行政事務處理處"))
                    facilities_to_insert.append(("資訊電機館", fl, "性別友善廁所", "廁所", "新穎時尚且安全的性別友善空間，乾淨無味"))
                elif fl == "3樓":
                    facilities_to_insert.append(("資訊電機館", fl, "電機系辦公室", "其他", "電機工程學系行政業務辦公室"))
                elif fl == "4樓":
                    facilities_to_insert.append(("資訊電機館", fl, "自控系辦公室", "其他", "自動控制工程學系行政辦公室"))
                    
            facilities_to_insert.append(("資訊電機館", fl, "飲水機", "飲水機", f"資訊電機館 {fl} 飲水機"))
            facilities_to_insert.append(("資訊電機館", fl, "垃圾桶", "垃圾桶", f"資訊電機館 {fl} 垃圾回收桶"))
            facilities_to_insert.append(("資訊電機館", fl, "男廁", "廁所", f"資訊電機館 {fl} 男生廁所"))
            facilities_to_insert.append(("資訊電機館", fl, "女廁", "廁所", f"資訊電機館 {fl} 女生廁所"))
            if fl in ["1樓", "3樓"]:
                facilities_to_insert.append(("資訊電機館", fl, "販賣機", "販賣機", f"資訊電機館 {fl} 自動飲料販賣機"))

        # 5. 學思樓
        xue_si_floors = ["1樓", "2樓", "3樓", "4樓", "5樓", "6樓", "7樓", "8樓", "9樓"]
        for fl in xue_si_floors:
            f_num = fl.replace("樓", "")
            for r in range(1, 7):
                name = f"{f_num}0{r}教室"
                facilities_to_insert.append(("學思樓", fl, name, "教室", f"學思樓 {name} 通識與外語教室"))
            if fl == "1樓":
                facilities_to_insert.append(("學思樓", fl, "國際會議廳", "討論空間", "大型國際學術會議與演講場地，冷氣強"))
            elif fl == "3樓":
                facilities_to_insert.append(("學思樓", fl, "研討室", "討論空間", "多功能學術研討室，備有大長桌"))

            facilities_to_insert.append(("學思樓", fl, "飲水機", "飲水機", f"學思樓 {fl} 飲水機"))
            facilities_to_insert.append(("學思樓", fl, "垃圾桶", "垃圾桶", f"學思樓 {fl} 垃圾與回收桶"))
            facilities_to_insert.append(("學思樓", fl, "男廁", "廁所", f"學思樓 {fl} 男生廁所"))
            facilities_to_insert.append(("學思樓", fl, "女廁", "廁所", f"學思樓 {fl} 女生廁所"))
            if fl in ["1樓", "5樓"]:
                facilities_to_insert.append(("學思樓", fl, "販賣機", "販賣機", f"學思樓 {fl} 自動飲料販賣機"))

        # 6. 圖書館
        library_floors = ["B1", "1樓", "2樓", "3樓", "4樓", "5樓"]
        for fl in library_floors:
            if fl == "1樓":
                facilities_to_insert.append(("圖書館", fl, "借還書櫃台", "其他", "提供圖書借還、證件辦理與諮詢服務"))
                facilities_to_insert.append(("圖書館", fl, "資訊檢索區", "其他", "提供公用電腦以進行圖書查詢與網路資料檢索"))
            elif fl == "2樓":
                facilities_to_insert.append(("圖書館", fl, "中西文書庫", "讀書空間", "豐富藏書庫，旁設有多個安靜臨窗自修座位"))
            elif fl == "3樓":
                facilities_to_insert.append(("圖書館", fl, "多媒體學習區", "讀書空間", "可借閱DVD與影音教材，有專用視聽沙發座"))
                facilities_to_insert.append(("圖書館", fl, "小組討論室", "討論空間", "密閉隔音討論室，需先線上預約系統借用"))
            elif fl == "4樓":
                facilities_to_insert.append(("圖書館", fl, "經典圖書室", "讀書空間", "經典文獻與特藏圖書閱覽室，環境極為靜謐"))
            elif fl == "5樓":
                facilities_to_insert.append(("圖書館", fl, "校史館", "其他", "展示本校發展歷史、校友貢獻與紀念文獻"))

            facilities_to_insert.append(("圖書館", fl, "飲水機", "飲水機", f"圖書館 {fl} 飲水機"))
            facilities_to_insert.append(("圖書館", fl, "垃圾桶", "垃圾桶", f"圖書館 {fl} 垃圾與分類回收桶"))
            facilities_to_insert.append(("圖書館", fl, "男廁", "廁所", f"圖書館 {fl} 男生廁所"))
            facilities_to_insert.append(("圖書館", fl, "女廁", "廁所", f"圖書館 {fl} 女生廁所"))
            if fl == "B1":
                facilities_to_insert.append(("圖書館", fl, "販賣機", "販賣機", f"圖書館 {fl} 自動飲料販賣機"))

        # 7. 體育館
        gym_floors = ["1樓", "2樓", "3樓"]
        for fl in gym_floors:
            if fl == "1樓":
                facilities_to_insert.append(("體育館", fl, "羽球場", "其他", "數個標準室內羽球場，木地板防滑良好"))
                facilities_to_insert.append(("體育館", fl, "體育室辦公室", "其他", "辦理校內體育活動與器材借用處"))
            elif fl == "2樓":
                facilities_to_insert.append(("體育館", fl, "桌球室", "其他", "設有十幾張標準桌球桌"))
            elif fl == "3樓":
                facilities_to_insert.append(("體育館", fl, "籃球場", "其他", "室內挑高綜合籃球場，有看台座位"))
                facilities_to_insert.append(("體育館", fl, "健身房", "其他", "重訓與有氧器材完備，僅限校內師生憑證進入"))

            facilities_to_insert.append(("體育館", fl, "飲水機", "飲水機", f"體育館 {fl} 飲水機"))
            facilities_to_insert.append(("體育館", fl, "垃圾桶", "垃圾桶", f"體育館 {fl} 垃圾分類桶"))
            facilities_to_insert.append(("體育館", fl, "男廁", "廁所", f"體育館 {fl} 男生廁所"))
            facilities_to_insert.append(("體育館", fl, "女廁", "廁所", f"體育館 {fl} 女生廁所"))
            if fl in ["1樓", "3樓"]:
                facilities_to_insert.append(("體育館", fl, "販賣機", "販賣機", f"體育館 {fl} 自動飲料與零食販賣機"))

        cursor.executemany("INSERT INTO facilities (building, floor, name, category, description) VALUES (?, ?, ?, ?, ?)", facilities_to_insert)

    # 5. 建立設施評價
    cursor.execute("SELECT COUNT(*) FROM facility_reviews")
    if cursor.fetchone()[0] == 0:
        # 獲取設施 ID
        cursor.execute("SELECT id, building, floor, name FROM facilities")
        fac_rows = cursor.fetchall()
        fac_ids = {f"{r[1]}_{r[2]}_{r[3]}": r[0] for r in fac_rows}
        
        # 人言大樓 2樓 女廁
        target_key = "人言大樓_2樓_女廁"
        if target_key in fac_ids:
            reviews = [
                (fac_ids[target_key], user_ids['andrew'], 5, '每次來人都很多，但是清潔阿姨打掃得很乾淨，5星好評！'),
                (fac_ids[target_key], user_ids['alice'], 4, '水壓有點小，洗手要洗比較久，但整體真的很乾淨。')
            ]
            for f_id, u_id, rating, content in reviews:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))
        
        # 忠勤樓 2樓 讀書空間
        target_key_2 = "忠勤樓_2樓_讀書空間"
        if target_key_2 in fac_ids:
            reviews_2 = [
                (fac_ids[target_key_2], user_ids['bob'], 5, '冷氣超強超舒服，位置很大還有插座，期末考溫書首選！')
            ]
            for f_id, u_id, rating, content in reviews_2:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

        # 圖書館 2樓 中西文書庫
        target_key_3 = "圖書館_2樓_中西文書庫"
        if target_key_3 in fac_ids:
            reviews_3 = [
                (fac_ids[target_key_3], user_ids['alice'], 5, '臨窗自修座位非常舒服，視野很好，讀書氛圍很棒！'),
                (fac_ids[target_key_3], user_ids['andrew'], 4, '下午時段陽光可能會有點刺眼，但整體環境極佳。')
            ]
            for f_id, u_id, rating, content in reviews_3:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

        # 體育館 3樓 健身房
        target_key_4 = "體育館_3樓_健身房"
        if target_key_4 in fac_ids:
            reviews_4 = [
                (fac_ids[target_key_4], user_ids['bob'], 4, '器材很齊全，憑學生證就能免費進去，CP值爆表！')
            ]
            for f_id, u_id, rating, content in reviews_4:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

        # 額外新增公共設施（飲水機、垃圾桶、販賣機）的測試評價，使系統更生動
        # 人言大樓 1樓 飲水機
        target_key_5 = "人言大樓_1樓_飲水機"
        if target_key_5 in fac_ids:
            reviews_5 = [
                (fac_ids[target_key_5], user_ids['andrew'], 5, '這台飲水機的水壓特別足，而且水喝起來非常清甜，完全沒有任何怪味。大推！')
            ]
            for f_id, u_id, rating, content in reviews_5:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

        # 資訊電機館 1樓 販賣機
        target_key_6 = "資訊電機館_1樓_販賣機"
        if target_key_6 in fac_ids:
            reviews_6 = [
                (fac_ids[target_key_6], user_ids['alice'], 2, '投幣有時候會吃錢，而且常有某些熱門飲料缺貨的問題，希望學校維修處可以加強管理。')
            ]
            for f_id, u_id, rating, content in reviews_6:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

        # 學思樓 1樓 垃圾桶
        target_key_7 = "學思樓_1樓_垃圾桶"
        if target_key_7 in fac_ids:
            reviews_7 = [
                (fac_ids[target_key_7], user_ids['bob'], 3, '因為在走廊轉角，到了中午常常滿出來，偶爾會有果蠅，不過打掃人員下午清理完後就還好。')
            ]
            for f_id, u_id, rating, content in reviews_7:
                cursor.execute("INSERT INTO facility_reviews (facility_id, user_id, rating, content) VALUES (?, ?, ?, ?)",
                               (f_id, u_id, rating, content))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    seed()
