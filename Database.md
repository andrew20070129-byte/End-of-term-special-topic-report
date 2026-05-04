# 校園論壇與設施評價系統 - 資料庫設計 (Database Design)

本文件詳細說明系統所使用的 SQLite 資料庫結構（Schema）。為確保資料完整性與關聯性，系統設計了以下 7 張核心資料表。

## 實體關聯圖 (ERD Concept)
- **User** 是一切互動的核心。一則 `User` 可以發布多個 `Review` (評價)、`Post` (文章)、`Comment` (留言) 與 `Vote` (按讚)。
- **Facility** (設施) 與 **Review** 是一對多的關係。
- **Board** (看板) 與 **Post** 是一對多的關係。
- 針對「按讚/倒讚」防呆機制，我們加入了 **ReviewVote** 表格，利用 `UNIQUE(review_id, user_id)` 來確保同一個使用者對同一則評論只能投票一次。

## 資料表結構 (Table Schemas)

### 1. `users` (使用者表)
紀錄註冊會員的基本資料與身分驗證資訊。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 使用者唯一 ID |
| `username` | TEXT | NOT NULL, UNIQUE | 登入帳號 / 顯示名稱 |
| `password_hash` | TEXT | NOT NULL | 經過 bcrypt 加密處理的密碼 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 帳號建立時間 |

### 2. `facilities` (設施清單表)
紀錄校園中可供評價的各項設施。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 設施唯一 ID |
| `name` | TEXT | NOT NULL | 設施名稱 (例如: 圖書館自習區) |
| `category` | TEXT | NOT NULL | 分類 (廁所、讀書空間、垃圾桶等) |
| `description`| TEXT | | 設施詳細描述或位置說明 |

### 3. `facility_reviews` (設施評價表)
紀錄使用者對特定設施的星等評分與文字心得。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 評價唯一 ID |
| `facility_id`| INTEGER | FOREIGN KEY | 關聯的設施 ID |
| `user_id` | INTEGER | FOREIGN KEY | 發布此評價的使用者 ID |
| `rating` | INTEGER | CHECK (rating 1~5) | 星等評分 |
| `content` | TEXT | | 文字評論內容 |
| `likes` | INTEGER | DEFAULT 0 | 總按讚數快取 (提升讀取效能) |
| `dislikes` | INTEGER | DEFAULT 0 | 總倒讚數快取 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 評價發布時間 |

### 4. `review_votes` (評價投票紀錄表)
紀錄哪位使用者對哪則評價按了讚或倒讚，確保防重複投票。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 投票唯一 ID |
| `review_id` | INTEGER | FOREIGN KEY | 關聯的評價 ID |
| `user_id` | INTEGER | FOREIGN KEY | 投票的使用者 ID |
| `vote_type` | TEXT | CHECK ('like' / 'dislike') | 讚或倒讚 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 投票時間 |
*註：設定 `UNIQUE(review_id, user_id)` 防止重複灌水。*

### 5. `boards` (論壇看板表)
定義論壇的不同討論版塊。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 看板唯一 ID |
| `name` | TEXT | NOT NULL, UNIQUE | 看板名稱 (例如: 二手交易版) |

### 6. `posts` (論壇文章表)
紀錄使用者在各看板發布的文章。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 文章唯一 ID |
| `board_id` | INTEGER | FOREIGN KEY | 關聯的看板 ID |
| `user_id` | INTEGER | FOREIGN KEY | 發文的使用者 ID |
| `title` | TEXT | NOT NULL | 文章標題 |
| `content` | TEXT | NOT NULL | 文章詳細內文 |
| `tags` | TEXT | | 標籤 (以逗號分隔字串) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 發文時間 |

### 7. `post_comments` (文章留言/回覆表)
紀錄文章底下的蓋樓留言，支援引用回覆機制。
| 欄位名稱 | 型態 | 屬性 | 說明 |
| --- | --- | --- | --- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | 留言唯一 ID |
| `post_id` | INTEGER | FOREIGN KEY | 所屬的文章 ID |
| `user_id` | INTEGER | FOREIGN KEY | 留言的使用者 ID |
| `content` | TEXT | NOT NULL | 留言內容 |
| `parent_id` | INTEGER | FOREIGN KEY | 若為引用回覆，則紀錄被引用的留言 ID |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 留言發布時間 |
