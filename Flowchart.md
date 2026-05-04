# 校園論壇與設施評價系統 - 流程圖 (Flowchart)

本文件描述使用者在「校園論壇與設施評價系統」中的主要操作流程與邏輯判斷。系統區分「訪客模式」與「會員模式」，以確保資料的正確追蹤。

## 系統核心操作流程

```mermaid
flowchart TD
    %% 節點定義
    Start((開始))
    VisitHome[進入系統首頁]
    CheckLogin{是否已登入?}
    
    %% 訪客路徑
    ViewOnly[訪客模式: 僅能瀏覽]
    ExploreFacilities[瀏覽設施列表與評價]
    ExploreForum[瀏覽論壇看板與文章]
    LoginAction[進行登入 / 註冊]
    
    %% 會員路徑
    LoggedIn[會員模式: 具備完整互動權限]
    SelectAction{選擇功能板塊}
    
    %% 設施評價流程
    FacilityFlow[進入設施評價區]
    SelectFacility[選擇特定校園設施]
    ViewReviews[查看該設施的歷史評價]
    InteractReview{對評價操作}
    LikeDislike[按讚 / 倒讚]
    LeaveReview[填寫星等 (1-5) 與評論文字]
    SubmitReview[送出評價並寫入資料庫]
    UpdateFacilityUI[系統重新渲染設施頁面]
    
    %% 校園論壇流程
    ForumFlow[進入校園論壇區]
    SelectBoard[選擇特定討論看板]
    ViewPosts[瀏覽看板內文章列表]
    PostAction{選擇後續動作}
    
    %% 發文流程
    CreatePost[撰寫新文章 (標題/內文/標籤)]
    SubmitPost[送出文章並寫入資料庫]
    UpdateBoardUI[系統重新渲染看板列表]
    
    %% 回覆流程
    ReadPost[閱讀單篇文章]
    LeaveComment[填寫留言或引用回覆]
    SubmitComment[送出留言並寫入資料庫]
    UpdatePostUI[系統重新渲染文章與留言區]

    %% 流程線條
    Start --> VisitHome
    VisitHome --> CheckLogin
    
    CheckLogin -- 否 --> ViewOnly
    ViewOnly --> ExploreFacilities
    ViewOnly --> ExploreForum
    ExploreFacilities -. 欲互動 .-> LoginAction
    ExploreForum -. 欲互動 .-> LoginAction
    LoginAction --> CheckLogin
    
    CheckLogin -- 是 --> LoggedIn
    LoggedIn --> SelectAction
    
    %% 設施評價線路
    SelectAction -- 點擊設施評價 --> FacilityFlow
    FacilityFlow --> SelectFacility
    SelectFacility --> ViewReviews
    ViewReviews --> InteractReview
    InteractReview -- 評價設施 --> LeaveReview
    InteractReview -- 與他人互動 --> LikeDislike
    LeaveReview --> SubmitReview
    SubmitReview --> UpdateFacilityUI
    LikeDislike --> UpdateFacilityUI
    
    %% 校園論壇線路
    SelectAction -- 點擊校園論壇 --> ForumFlow
    ForumFlow --> SelectBoard
    SelectBoard --> ViewPosts
    ViewPosts --> PostAction
    
    PostAction -- 發文 --> CreatePost
    CreatePost --> SubmitPost
    SubmitPost --> UpdateBoardUI
    
    PostAction -- 閱讀 --> ReadPost
    ReadPost --> LeaveComment
    LeaveComment --> SubmitComment
    SubmitComment --> UpdatePostUI
```

## 說明
1. **權限控制**：系統在使用者嘗試進行「評價」、「發文」、「留言」、「按讚」時，都會觸發登入驗證（對應圖中的 `CheckLogin`）。
2. **資料更新**：所有寫入資料庫的操作（送出評價、發布文章）完成後，頁面將會重新渲染（Update UI），即時讓使用者看到最新的資訊。
