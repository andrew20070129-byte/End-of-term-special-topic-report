# 校園論壇與設施評價系統 - 路由與 API 設計 (Route & API Design)

本文件詳細列出系統中 Flask 後端所處理的所有路由（Routes）及其對應的方法、功能描述與權限要求。

由於本系統採用 **伺服器端渲染 (Server-Side Rendering, SSR)** 搭配 Jinja2 模板，多數路由會回傳 HTML 頁面，少數互動功能（如按讚）可能會設計為回傳 JSON 以搭配前端 AJAX 達到不刷新頁面的效果。

---

## 1. 基礎頁面 (Core Pages)
| Method | Route | Description (功能說明) | Auth Required (權限) |
| :---: | :--- | :--- | :---: |
| `GET` | `/` | 系統首頁 (顯示最新論壇文章與熱門評價設施) | 公開 |

---

## 2. 使用者驗證模組 (Authentication Module)
負責處理帳號的註冊、登入、登出機制。

| Method | Route | Description (功能說明) | Auth Required (權限) |
| :---: | :--- | :--- | :---: |
| `GET` | `/login` | 渲染並顯示登入表單頁面 | 公開 |
| `POST` | `/login` | 接收表單資料，驗證帳號密碼，建立 Session | 公開 |
| `GET` | `/register` | 渲染並顯示註冊表單頁面 | 公開 |
| `POST` | `/register` | 接收表單資料，寫入資料庫建立新帳號 | 公開 |
| `GET` | `/logout` | 清除 Session 狀態，登出系統 | **需登入** |

---

## 3. 設施評價模組 (Facility Rating Module)
負責設施瀏覽與評價的增刪改查 (CRUD) 操作。

| Method | Route | Description (功能說明) | Auth Required (權限) |
| :---: | :--- | :--- | :---: |
| `GET` | `/facilities` | 顯示所有設施列表，支援依分類篩選 | 公開 |
| `GET` | `/facility/<int:id>` | 顯示「單一設施」詳細資料及歷史評價列表 | 公開 |
| `POST` | `/facility/<int:id>/review` | 新增針對該設施的評價 (星等與文字) | **需登入** |
| `POST` | `/review/<int:id>/edit` | 修改自己過去發布的評價 (僅限原作者) | **需登入** |
| `POST` | `/review/<int:id>/delete`| 刪除自己過去發布的評價 (僅限原作者) | **需登入** |
| `POST` | `/review/<int:id>/vote` | (AJAX) 對他人的評價進行按讚或倒讚 | **需登入** |

---

## 4. 校園論壇模組 (Campus Forum Module)
負責論壇看板、文章管理與留言蓋樓功能。

| Method | Route | Description (功能說明) | Auth Required (權限) |
| :---: | :--- | :--- | :---: |
| `GET` | `/forum` | 顯示論壇首頁與所有看板列表 | 公開 |
| `GET` | `/board/<int:id>` | 顯示單一「看板」的文章列表 | 公開 |
| `GET` | `/post/<int:id>` | 進入單篇文章頁面，閱讀完整內文與底下留言 | 公開 |
| `GET` | `/post/new` | 渲染並顯示發布新文章的編輯器頁面 | **需登入** |
| `POST` | `/post/new` | 接收編輯器資料，將新文章寫入資料庫 | **需登入** |
| `POST` | `/post/<int:id>/comment` | 接收留言表單資料，在文章底下新增留言 | **需登入** |

---

## 5. 搜尋功能 (Search Module)
| Method | Route | Description (功能說明) | Auth Required (權限) |
| :---: | :--- | :--- | :---: |
| `GET` | `/search` | 透過查詢參數 `?q=關鍵字` 搜尋文章標題與內文 | 公開 |

---

## 📌 實作注意事項
1. **權限管控**：所有標記為「需登入」的路由，需在 Flask 中套用 `@login_required` 裝飾器進行保護。如果未登入的使用者嘗試存取，應重新導向至 `/login` 頁面。
2. **防範 CSRF**：所有的 POST 請求（尤其是刪除、修改、發文等操作），未來在撰寫 HTML 表單時需注意安全防護。
3. **動態載入**：`/review/<int:id>/vote` 建議設計為回傳 JSON (如 `{"status": "success", "likes": 12}`)，方便前端利用 JavaScript 即時更新按讚數字。
