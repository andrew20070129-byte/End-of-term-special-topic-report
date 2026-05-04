# 校園論壇與設施評價系統 - 系統架構設計 (System Architecture)

## 1. 系統概觀 (System Overview)
本系統採用經典的 **MVC (Model-View-Controller)** 架構模式，基於 Client-Server 網頁應用程式架構運行。前端負責介面展示與使用者互動，後端處理商業邏輯與資料庫交互，確保系統具備良好的可維護性與擴展性。

## 2. 技術選型 (Technology Stack)
考量開發效率與部署便利性，本專案選擇以下技術棧：
- **前端 (Frontend / View)**：HTML5, 原生 CSS3 (搭配具設計感的現代化樣式), 原生 JavaScript, Jinja2 (由後端渲染的模板引擎)。
- **後端 (Backend / Controller)**：Python 3, Flask 網頁框架。
- **資料庫 (Database / Model)**：SQLite (輕量級關聯式資料庫，適合初期專案與展示)。
- **開發環境與版本控制**：Git, GitHub。

## 3. 系統架構圖 (Architecture Diagram)

```mermaid
graph TD
    Client[Web Browser (Client)] -->|HTTP Requests (GET, POST)| FlaskApp[Flask Web Server (app.py)]
    
    subgraph Backend Server
        FlaskApp -->|Render| Views[Jinja2 Templates]
        FlaskApp -->|CRUD Operations| Models[SQLite Database (models.py)]
        Models -->|Return Data| FlaskApp
    end
    
    Views -->|HTML/CSS/JS Responses| Client
```

## 4. 模組劃分 (Module Breakdown)
為了讓程式碼結構清晰，系統邏輯將劃分為三大主要模組：

1. **User Module (使用者模組)**
   - 負責處理會員註冊、登入、登出。
   - 使用 Flask `session` 管理登入狀態。
   - 提供密碼雜湊 (Password Hashing) 安全機制。
2. **Facility Rating Module (設施評價模組)**
   - 處理設施清單的展示。
   - 處理新增、修改、刪除設施評論 (CRUD)。
   - 處理使用者對評論的按讚與倒讚互動機制。
3. **Forum Module (論壇模組)**
   - 管理論壇各個看板的分類與文章。
   - 支援文章的發布、蓋樓留言與引用回覆。
   - 提供關鍵字搜尋文章標題與內文的演算法。

## 5. 資料流設計 (Data Flow)
以「發布設施評價」的操作為例，系統的資料流如下：
1. **View (前端)**：使用者登入後，在網頁表單填寫星等與評價文字，按下送出產生 HTTP POST 請求。
2. **Controller (Flask 路由)**：攔截請求，驗證使用者是否已登入 (`@login_required`)，並檢查輸入資料 (如星等是否在 1~5 之間) 是否合法。
3. **Model (Database)**：驗證通過後，將評價資料透過 SQL 寫入 `facility_reviews` 資料表。
4. **View (前端)**：資料庫寫入成功後，後端重新渲染該設施的詳細頁面 (Jinja2)，並附帶成功提示訊息 (Flash message)，回傳給前端呈現。

## 6. 專案目錄結構 (Directory Structure)
未來專案將採用以下目錄結構進行開發：

```text
/End-of-term-special-topic-report
├── app.py              # Flask 主程式入口、路由與 Controller 邏輯
├── models.py           # 資料庫設計、SQL 指令與 Model 邏輯
├── requirements.txt    # Python 依賴套件清單
├── README.md           # 專案說明文件
├── PRD.md              # 產品需求文件
├── Architecture.md     # 系統架構設計文件 (本文件)
│
├── static/             # 靜態資源目錄
│   ├── css/
│   │   └── style.css   # 全域與組件樣式表
│   ├── js/
│   │   └── main.js     # 前端互動邏輯腳本
│   └── images/         # 網站圖片與 Logo
│
└── templates/          # Jinja2 網頁模板目錄
    ├── base.html       # 共用基礎模板 (包含 Header, Navigation, Footer)
    ├── index.html      # 網站首頁
    ├── auth/           # 註冊登入相關頁面 (login.html, register.html)
    ├── forum/          # 論壇相關頁面 (board.html, post.html)
    └── facilities/     # 設施評價相關頁面 (facility_list.html, facility_detail.html)
```
