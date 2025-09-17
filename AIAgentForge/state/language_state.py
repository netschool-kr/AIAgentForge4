# AIAgentForge/aiagentforge/state/language_state.py
import reflex as rx
from.base import BaseState
from gotrue.types import User

class LanguageState(BaseState):
    """다국어 처리를 위한 상태 정의"""
    locale: str = "ko"
    translations: dict = {
        "ko": {
            # Chapter 13 strings
            "boards_page_title": "게시판 목록",
            "board_card_no_desc": "설명이 없습니다.",
            "loading_generic": "로딩 중...",

            "column_title": "제목",
            "column_created_at": "생성일",
            "search_placeholder": "제목 또는 내용으로 검색...",
            "btn_search": "검색",
            "btn_write_post": "글쓰기",

            "post_page_title": "게시글",
            "title_untitled": "제목 없음",
            "author_label": "작성자:",
            "author_unknown": "알 수 없음",
            "created_at_label": "작성일:",
            "content_none": "내용 없음",
            "btn_back_to_list": "목록으로",
            "btn_edit": "수정",
            "btn_delete": "삭제",

            "new_post_heading": "새 글 작성",
            "current_board_label": "현재 게시판:",
            "input_title_placeholder": "제목을 입력하세요",
            "input_content_placeholder": "내용을 입력하세요",
            "btn_cancel": "취소",
            "btn_submit_post": "글 등록",

            "unknown_board": "알 수 없는 게시판",
            "board_not_found": "게시판을 찾을 수 없습니다.",
            "date_format_error": "날짜 형식 오류",
                    
            # Chapter 12 strings
            "research_agent_title": "Reflex를 이용한 AI 자동 리서치 에이전트",
            "research_agent_subtitle": "연구 질문을 입력하면 AI 에이전트가 여러 단계에 걸쳐 심층 보고서를 생성합니다.",

            "subq_placeholder_indexed": "하위 질문 #{index}",
            "btn_add_question": "질문 추가",
            "btn_start_research_with_edits": "수정된 질문으로 리서치 시작",
            "btn_generate_sub_questions": "하위 질문 생성",

            "card_generated_subqs_editable": "생성된 하위 질문 (편집 가능)",
            "card_subqs_used": "리서치에 사용된 하위 질문",
            "card_subq_summaries": "하위 질문별 리서치 요약",
            "card_final_report": "최종 보고서",

            "main_question_placeholder": "예: 양자 컴퓨팅의 현재 발전 수준과 미래 전망은?",

            "status_generating_initial": "초기 하위 질문 생성 중...",
            "status_review_and_edit": "생성된 하위 질문을 검토하고 수정하세요.",
            "status_no_subqs": "리서치를 진행할 하위 질문이 없습니다.",
            "status_research_in_progress": "{count}개의 하위 질문에 대해 리서치 진행 중...",
            "status_research_done_count": "리서치 완료 ({done}/{total})",
            "status_writing_final_report": "최종 보고서 작성 중...",
            "status_research_complete": "리서치 완료!",
            "status_error_prefix": "오류 발생: {error}",

            "default_new_subq": "새로운 질문을 입력하세요...",            
            
            # Chapter 11 strings
            "yt_page_title": "유튜브 영상 요약 및 번역",
            "yt_input_placeholder": "https://www.youtube.com/watch?v=...",
            "yt_btn_run": "요약 및 번역",

            "yt_result_original": "원문 스크립트",
            "yt_result_translated": "번역 결과",
            "yt_result_summary": "요약 결과",

            "yt_err_enter_url": "유튜브 URL을 입력해주세요.",
            "yt_err_invalid_url": "유효한 유튜브 영상 URL이 아닙니다.",
            "yt_err_prefix": "오류 발생: {error}",

            "yt_status_extracting": "자막 추출 중...",
            "yt_status_translating": "한국어로 번역 중...",
            "yt_status_summarizing": "내용 요약 중...",
            "yt_skip_translation": "원문이 한국어이므로 번역을 건너뜁니다.",
            
            # Chapter 10 strings
            "blog_generator_title": "AI 블로그 포스팅 생성기 🤖",
            "blog_generator_subtitle": "제품 키워드를 입력하면 AI가 제목, 목차, 본문까지 자동으로 생성해줍니다.",

            "step1_heading": "Step 1: 제품 키워드 입력",
            "step1_input_placeholder": "예: LG 트롬 오브제컬렉션 워시타워",
            "btn_generate_titles": "제목 생성하기",

            "step2_heading": "Step 2: 마음에 드는 제목 선택",

            "step3_heading": "Step 3: 생성된 목차 확인",
            "btn_generate_final_posting": "최종 포스팅 생성하기",

            "step4_heading": "Step 4: 완성된 포스팅",

            "btn_restart": "새로 시작하기",
            
            #chapter 9 strings
            "nav_dashboard": "대시보드",
            "nav_boards": "게시판",
            "nav_collections": "컬렉션",
            "nav_chat": "채팅",
            "nav_youtube": "유튜브",
            "nav_blog": "블로그",
            "nav_research": "리서치",
            "nav_admin_panel": "관리자 패널",
            "nav_menu": "메뉴",
            "logout_button": "로그아웃",

            "admin_dashboard_title": "관리자 대시보드",
            "tab_main": "메인",
            "tab_board_management": "게시판 관리",
            "tab_email": "이메일 전송",
            "admin_only_notice": "이 페이지는 관리자만 접근할 수 있습니다.",

            "new_board_heading": "새 게시판 생성",
            "input_board_name_placeholder": "게시판 이름",
            "input_board_desc_placeholder": "게시판 설명",
            "label_read_permission": "읽기 권한:",
            "label_write_permission": "쓰기 권한:",
            "btn_create": "생성하기",

            "boards_list_heading": "게시판 목록",
            "table_name_header": "이름",
            "table_desc_header": "설명",
            "table_read_perm_header": "읽기 권한",
            "table_write_perm_header": "쓰기 권한",
            "table_actions_header": "관리",
            "btn_delete": "삭제",
            
            # Chapter 8 strings
            "hybrid_search_title": "하이브리드 검색",
            "hybrid_search_engine": "하이브리드 검색 엔진",
            "input_placeholder": "질문을 입력하세요...",
            "btn_search": "검색",
            "answer_heading": "답변",
            "search_initial_hint": "질문을 입력하면 문서 기반의 답변을 생성합니다.",
            "sources_heading": "참고 문서",
            "label_id": "ID",
            "label_score": "점수",            
            # Chapter 7 strings
            "doc_collection_id_missing": "컬렉션 ID를 찾을 수 없습니다.",
            "name_untitled": "이름 없음",
            "unknown_collection": "알 수 없는 컬렉션",
            "doc_loading_failed": "문서 로딩 실패: {error}",
            "user_not_found": "사용자를 찾을 수 없습니다.",
            "doc_exists_same_name": "이미 같은 이름의 파일이 존재합니다.",
            "upload_waiting": "대기 중...",
            "upload_storage_uploading": "스토리지에 업로드 중...",
            "upload_text_extracting": "텍스트 추출 중",
            "upload_chunking": "청크 분할 중",
            "upload_embedding": "임베딩 생성 중",
            "upload_db_updating": "DB 업데이트 중",
            "status_done": "완료",
            "status_failed": "실패",
            "upload_error": "오류: {error}",
            "docs_upload_success_alert": "{ok} / {total}개의 파일이 성공적으로 업로드되었습니다.",
            "doc_not_found": "문서를 찾을 수 없습니다.",
            "delete_no_permission": "삭제 권한이 없습니다.",
            "storage_delete_failed": "스토리지 파일 삭제 실패: 파일을 찾을 수 없음 또는 경로 오류.",
            "doc_delete_success": "문서가 성공적으로 삭제되었습니다.",
            "doc_delete_failed": "문서 삭제 실패: {error}",
            # collection_detail.py strings
            "col_doc_name": "문서 이름",
            "col_created_at": "생성일",
            "col_actions": "작업",
            "btn_delete": "삭제",
            "collection_heading": "컬렉션:",
            "link_search": "검색",
            "btn_choose_files": "파일 선택",
            "upload_drag_drop_hint": "또는 여기에 파일을 드래그 앤 드롭하세요.",
            "heading_uploaded_docs": "업로드된 문서",
            
            # Chapter 6 strings
            "collections_title": "내 컬렉션 관리",
            "new_collection_name_placeholder": "새 컬렉션 이름...",
            "create_button": "생성",
            "delete_button": "삭제",
            "created_at": "생성일:",
            "empty_collections_message": "생성된 컬렉션이 없습니다. 첫 번째 컬렉션을 만들어보세요!",
            "collection_name_empty_error": "컬렉션 이름은 비워둘 수 없습니다.",
            "collection_create_success": "컬렉션이 성공적으로 생성되었습니다.", 
            "collection_create_fail": "컬렉션 생성 실패",
            "collection_delete_success": "컬렉션이 삭제되었습니다.",
            "collection_delete_fail": "컬렉션 삭제 실패",
            
            # Chapter 5 strings
            "collections_link": "컬렉션",
            "login_heading": "로그인",
            "signup_heading": "회원가입",
            "email_placeholder": "이메일",
            "password_placeholder": "비밀번호",
            "password_confirm_placeholder": "비밀번호 확인",
            "login_button": "로그인",
            "signup_button": "회원가입",
            "no_account_yet": "아직 회원이 아니신가요?",
            "signup_link": "회원가입",
            "already_have_account": "이미 계정이 있으신가요?",
            "login_link": "로그인",
            
            #Chapter 2 strings
            "dashboard_title": "사용자 대시보드",
            "name": "이름",
            "age": "나이",
            "role": "역할",
            "add_user": "사용자 추가",
            "total_users": "총 사용자"            
        },
        "en": {
            
            # --- Chapter 13 strings ---
            "boards_page_title": "Boards",
            "board_card_no_desc": "No description.",
            "loading_generic": "Loading...",

            "column_title": "Title",
            "column_created_at": "Created At",
            "search_placeholder": "Search by title or content...",
            "btn_search": "Search",
            "btn_write_post": "Write Post",

            "post_page_title": "Post",
            "title_untitled": "Untitled",
            "author_label": "Author:",
            "author_unknown": "Unknown",
            "created_at_label": "Created:",
            "content_none": "No content",
            "btn_back_to_list": "Back to List",
            "btn_edit": "Edit",
            "btn_delete": "Delete",

            "new_post_heading": "New Post",
            "current_board_label": "Current board:",
            "input_title_placeholder": "Enter a title",
            "input_content_placeholder": "Enter content",
            "btn_cancel": "Cancel",
            "btn_submit_post": "Submit",

            "unknown_board": "Unknown board",
            "board_not_found": "Board not found.",
            "date_format_error": "Invalid date format",
                        
            # Chapter 12 strings
            "research_agent_title": "AI Auto Research Agent with Reflex",
            "research_agent_subtitle": "Enter a research question and the AI agent will produce a multi-step, in-depth report.",

            "subq_placeholder_indexed": "Sub-question #{index}",
            "btn_add_question": "Add Question",
            "btn_start_research_with_edits": "Start Research with Edited Questions",
            "btn_generate_sub_questions": "Generate Sub-questions",

            "card_generated_subqs_editable": "Generated Sub-questions (Editable)",
            "card_subqs_used": "Sub-questions Used for Research",
            "card_subq_summaries": "Summaries by Sub-question",
            "card_final_report": "Final Report",

            "main_question_placeholder": "e.g., What is the current state and future outlook of quantum computing?",

            "status_generating_initial": "Generating initial sub-questions...",
            "status_review_and_edit": "Review and modify the generated sub-questions.",
            "status_no_subqs": "There are no sub-questions to research.",
            "status_research_in_progress": "Research in progress for {count} sub-questions...",
            "status_research_done_count": "Research complete ({done}/{total})",
            "status_writing_final_report": "Writing the final report...",
            "status_research_complete": "Research complete!",
            "status_error_prefix": "Error: {error}",

            "default_new_subq": "Enter a new question...",            
            
            # Chapter 11 strings
            "yt_page_title": "YouTube Video Summarizer & Translator",
            "yt_input_placeholder": "https://www.youtube.com/watch?v=...",
            "yt_btn_run": "Summarize & Translate",

            "yt_result_original": "Original Transcript",
            "yt_result_translated": "Translation",
            "yt_result_summary": "Summary",

            "yt_err_enter_url": "Please enter a YouTube URL.",
            "yt_err_invalid_url": "This is not a valid YouTube video URL.",
            "yt_err_prefix": "Error: {error}",

            "yt_status_extracting": "Extracting captions...",
            "yt_status_translating": "Translating into Korean...",
            "yt_status_summarizing": "Summarizing content...",
            "yt_skip_translation": "Original is Korean. Skipping translation.",
            
            # Chapter 10 strings
            "blog_generator_title": "AI Blog Posting Generator 🤖",
            "blog_generator_subtitle": "Enter a product keyword and AI will generate titles, outlines, and full content automatically.",

            "step1_heading": "Step 1: Enter Product Keyword",
            "step1_input_placeholder": "e.g., LG Tromm Objet Collection WashTower",
            "btn_generate_titles": "Generate Titles",

            "step2_heading": "Step 2: Select a Title You Like",

            "step3_heading": "Step 3: Review Generated Outline",
            "btn_generate_final_posting": "Generate Final Posting",

            "step4_heading": "Step 4: Completed Posting",

            "btn_restart": "Start Over",
            
            # Chapter 9 strings
            "nav_dashboard": "Dashboard",
            "nav_boards": "Boards",
            "nav_collections": "Collections",
            "nav_chat": "Chat",
            "nav_youtube": "YouTube",
            "nav_blog": "Blog",
            "nav_research": "Research",
            "nav_admin_panel": "Admin Panel",
            "nav_menu": "Menu",
            "logout_button": "Logout",

            "admin_dashboard_title": "Admin Dashboard",
            "tab_main": "Main",
            "tab_board_management": "Board Management",
            "tab_email": "Send Email",
            "admin_only_notice": "This page is restricted to administrators.",

            "new_board_heading": "Create New Board",
            "input_board_name_placeholder": "Board Name",
            "input_board_desc_placeholder": "Board Description",
            "label_read_permission": "Read Permission:",
            "label_write_permission": "Write Permission:",
            "btn_create": "Create",

            "boards_list_heading": "Board List",
            "table_name_header": "Name",
            "table_desc_header": "Description",
            "table_read_perm_header": "Read Permission",
            "table_write_perm_header": "Write Permission",
            "table_actions_header": "Actions",
            "btn_delete": "Delete",
            
            # Chapter 8 strings
            "hybrid_search_title": "Hybrid Search",
            "hybrid_search_engine": "Hybrid Search Engine",
            "input_placeholder": "Type your question...",
            "btn_search": "Search",
            "answer_heading": "Answer",
            "search_initial_hint": "Enter a question to generate a document-grounded answer.",
            "sources_heading": "Sources",
            "label_id": "ID",
            "label_score": "Score",            
            # Chapter 7 strings
            "doc_collection_id_missing": "Collection ID not found.",
            "name_untitled": "Untitled",
            "unknown_collection": "Unknown collection",
            "doc_loading_failed": "Failed to load documents: {error}",
            "user_not_found": "User not found.",
            "doc_exists_same_name": "A file with the same name already exists.",
            "upload_waiting": "Waiting...",
            "upload_storage_uploading": "Uploading to storage...",
            "upload_text_extracting": "Extracting text",
            "upload_chunking": "Chunking",
            "upload_embedding": "Embedding",
            "upload_db_updating": "Updating DB",
            "status_done": "Done",
            "status_failed": "Failed",
            "upload_error": "Error: {error}",
            "docs_upload_success_alert": "{ok} / {total} files uploaded successfully.",
            "doc_not_found": "Document not found.",
            "delete_no_permission": "No permission to delete.",
            "storage_delete_failed": "Failed to delete storage file: not found or path error.",
            "doc_delete_success": "Document deleted successfully.",
            "doc_delete_failed": "Document deletion failed: {error}",
            
            # collection_detail.py strings
            "col_doc_name": "Document Name",
            "col_created_at": "Created At",
            "col_actions": "Actions",
            "btn_delete": "Delete",
            "collection_heading": "Collection:",
            "link_search": "Search",
            "btn_choose_files": "Choose Files",
            "upload_drag_drop_hint": "Or drag and drop files here.",
            "heading_uploaded_docs": "Uploaded Documents",
                        
            # Chapter 6 strings
            "collections_title": "My Collections",
            "new_collection_name_placeholder": "New collection name...",
            "create_button": "Create",
            "delete_button": "Delete",
            "created_at": "Created at:",
            "empty_collections_message": "No collections created yet. Create your first collection!",
            "collection_name_empty_error": "Collection name cannot be empty.",
            "collection_create_success": "Collection created successfully.",
            "collection_create_fail": "Collection creation failed.",
            "collection_delete_success": "Collection deleted successfully.",
            "collection_delete_fail": "Collection deletion failed.",

            # Chapter 5 strings
            "collections_link": "Collections",
            "login_heading": "Login",
            "signup_heading": "Sign Up",
            "email_placeholder": "Email",
            "password_placeholder": "Password",
            "password_confirm_placeholder": "Confirm Password",
            "login_button": "Login",
            "signup_button": "Sign Up",
            "no_account_yet": "Don't have an account yet?",
            "signup_link": "Sign up",
            "already_have_account": "Already have an account?",
            "login_link": "Login",
            
            #Chapter 2 strings
            "dashboard_title": "User Dashboard",
            "name": "Name",
            "age": "Age",
            "role": "Role",
            "add_user": "Add User",
            "total_users": "Total Users"            
        },
        "ja": {
            # --- Chapter 13 strings ---
            "boards_page_title": "掲示板一覧",
            "board_card_no_desc": "説明はありません。",
            "loading_generic": "読み込み中...",

            "column_title": "タイトル",
            "column_created_at": "作成日",
            "search_placeholder": "タイトルまたは内容で検索...",
            "btn_search": "検索",
            "btn_write_post": "投稿する",

            "post_page_title": "投稿",
            "title_untitled": "無題",
            "author_label": "作成者：",
            "author_unknown": "不明",
            "created_at_label": "作成日：",
            "content_none": "内容がありません",
            "btn_back_to_list": "一覧へ戻る",
            "btn_edit": "編集",
            "btn_delete": "削除",

            "new_post_heading": "新規投稿",
            "current_board_label": "現在の掲示板：",
            "input_title_placeholder": "タイトルを入力してください",
            "input_content_placeholder": "内容を入力してください",
            "btn_cancel": "キャンセル",
            "btn_submit_post": "投稿",

            "unknown_board": "不明な掲示板",
            "board_not_found": "掲示板が見つかりません。",
            "date_format_error": "日付形式のエラー",
                        
            # Chapter 12 strings
            "research_agent_title": "ReflexによるAI自動リサーチエージェント",
            "research_agent_subtitle": "研究テーマを入力すると、AIエージェントが複数のステップで詳細なレポートを生成します。",

            "subq_placeholder_indexed": "サブ質問 #{index}",
            "btn_add_question": "質問を追加",
            "btn_start_research_with_edits": "修正した質問でリサーチ開始",
            "btn_generate_sub_questions": "サブ質問を生成",

            "card_generated_subqs_editable": "生成されたサブ質問（編集可）",
            "card_subqs_used": "リサーチに使用したサブ質問",
            "card_subq_summaries": "サブ質問ごとの要約",
            "card_final_report": "最終レポート",

            "main_question_placeholder": "例：量子コンピューティングの現状と将来展望は？",

            "status_generating_initial": "初期サブ質問を生成中...",
            "status_review_and_edit": "生成されたサブ質問を確認して編集してください。",
            "status_no_subqs": "リサーチするサブ質問がありません。",
            "status_research_in_progress": "{count}件のサブ質問でリサーチを進行中...",
            "status_research_done_count": "リサーチ完了（{done}/{total}）",
            "status_writing_final_report": "最終レポートを作成中...",
            "status_research_complete": "リサーチ完了！",
            "status_error_prefix": "エラー: {error}",

            "default_new_subq": "新しい質問を入力してください...",
            
            # Chapter 11 strings
            "yt_page_title": "YouTube動画 要約と翻訳",
            "yt_input_placeholder": "https://www.youtube.com/watch?v=...",
            "yt_btn_run": "要約と翻訳",

            "yt_result_original": "元のスクリプト",
            "yt_result_translated": "翻訳結果",
            "yt_result_summary": "要約結果",

            "yt_err_enter_url": "YouTubeのURLを入力してください。",
            "yt_err_invalid_url": "有効なYouTube動画URLではありません。",
            "yt_err_prefix": "エラー: {error}",

            "yt_status_extracting": "字幕を抽出中...",
            "yt_status_translating": "韓国語へ翻訳中...",
            "yt_status_summarizing": "内容を要約中...",
            "yt_skip_translation": "元が韓国語のため翻訳をスキップします。",
            
            # Chapter 10 strings
            "blog_generator_title": "AIブログ投稿ジェネレーター 🤖",
            "blog_generator_subtitle": "製品キーワードを入力すると、AIがタイトル、目次、本文まで自動生成します。",

            "step1_heading": "ステップ1: 製品キーワードを入力",
            "step1_input_placeholder": "例: LG トロム オブジェコレクション ウォッシュタワー",
            "btn_generate_titles": "タイトルを生成",

            "step2_heading": "ステップ2: 気に入ったタイトルを選択",

            "step3_heading": "ステップ3: 生成された目次を確認",
            "btn_generate_final_posting": "最終投稿を生成",

            "step4_heading": "ステップ4: 完成した投稿",

            "btn_restart": "新しく始める",
            
            # Chapter 9 strings
            "nav_dashboard": "ダッシュボード",
            "nav_boards": "掲示板",
            "nav_collections": "コレクション",
            "nav_chat": "チャット",
            "nav_youtube": "YouTube",
            "nav_blog": "ブログ",
            "nav_research": "リサーチ",
            "nav_admin_panel": "管理者パネル",
            "nav_menu": "メニュー",
            "logout_button": "ログアウト",

            "admin_dashboard_title": "管理者ダッシュボード",
            "tab_main": "メイン",
            "tab_board_management": "掲示板管理",
            "tab_email": "メール送信",
            "admin_only_notice": "このページは管理者のみがアクセスできます。",

            "new_board_heading": "新規掲示板の作成",
            "input_board_name_placeholder": "掲示板名",
            "input_board_desc_placeholder": "掲示板の説明",
            "label_read_permission": "閲覧権限：",
            "label_write_permission": "投稿権限：",
            "btn_create": "作成",

            "boards_list_heading": "掲示板一覧",
            "table_name_header": "名前",
            "table_desc_header": "説明",
            "table_read_perm_header": "閲覧権限",
            "table_write_perm_header": "投稿権限",
            "table_actions_header": "操作",
            "btn_delete": "削除",
            
            # Chapter 8 strings
            "hybrid_search_title": "ハイブリッド検索",
            "hybrid_search_engine": "ハイブリッド検索エンジン",
            "input_placeholder": "質問を入力してください...",
            "btn_search": "検索",
            "answer_heading": "回答",
            "search_initial_hint": "質問を入力すると、文書に基づく回答を生成します。",
            "sources_heading": "参考資料",
            "label_id": "ID",
            "label_score": "スコア",            
            # Chapter 7 strings
            "doc_collection_id_missing": "コレクションIDが見つかりません。",
            "name_untitled": "無題",
            "unknown_collection": "不明なコレクション",
            "doc_loading_failed": "ドキュメントの読み込みに失敗しました: {error}",
            "user_not_found": "ユーザーが見つかりません。",
            "doc_exists_same_name": "同じ名前のファイルが既に存在します。",
            "upload_waiting": "待機中...",
            "upload_storage_uploading": "ストレージにアップロード中...",
            "upload_text_extracting": "テキスト抽出中",
            "upload_chunking": "チャンク分割中",
            "upload_embedding": "埋め込み生成中",
            "upload_db_updating": "DB更新中",
            "status_done": "完了",
            "status_failed": "失敗",
            "upload_error": "エラー: {error}",
            "docs_upload_success_alert": "{ok} / {total} 個のファイルが正常にアップロードされました。",
            "doc_not_found": "ドキュメントが見つかりません。",
            "delete_no_permission": "削除権限がありません。",
            "storage_delete_failed": "ストレージファイルの削除に失敗: 見つからないかパスエラーです。",
            "doc_delete_success": "ドキュメントは正常に削除されました。",
            "doc_delete_failed": "ドキュメントの削除に失敗しました: {error}",

            # collection_detail.py strings
            "col_doc_name": "ドキュメント名",
            "col_created_at": "作成日",
            "col_actions": "操作",
            "btn_delete": "削除",
            "collection_heading": "コレクション:",
            "link_search": "検索",
            "btn_choose_files": "ファイルを選択",
            "upload_drag_drop_hint": "またはここにファイルをドラッグ＆ドロップしてください。",
            "heading_uploaded_docs": "アップロード済みドキュメント",
                        
            # Chapter 6 strings
            "collections_title": "コレクション管理",
            "new_collection_name_placeholder": "新しいコレクション名...",
            "create_button": "作成",
            "delete_button": "削除",
            "created_at": "作成日:",
            "empty_collections_message": "作成されたコレクションがありません。最初のコレクションを作成してください！",
            "collection_name_empty_error": "コレクション名は空にできません。",
            "collection_create_success": "コレクションが正常に作成されました。",
            "collection_create_fail": "コレクション作成に失敗しました。",
            "collection_delete_success": "コレクションが削除されました。",
            "collection_delete_fail": "コレクションの削除に失敗しました。",

            # Chapter 5 strings
            "collections_link": "コレクション",
            "login_heading": "ログイン",
            "signup_heading": "サインアップ",
            "email_placeholder": "メール",
            "password_placeholder": "パスワード",
            "password_confirm_placeholder": "パスワードを確認",
            "login_button": "ログイン",
            "signup_button": "サインアップ",
            "no_account_yet": "まだアカウントをお持ちではありませんか？",
            "signup_link": "サインアップ",
            "already_have_account": "既にアカウントをお持ちですか？",
            "login_link": "ログイン",
            
            #Chapter 2 strings
            "dashboard_title": "ユーザーダッシュボード",
            "name": "名前",
            "age": "年齢",
            "role": "役割",
            "add_user": "ユーザー追加",
            "total_users": "合計ユーザー"
            
        }
    }

    def set_locale(self, lang: str):
        """언어 변경"""
        self.locale = lang

    @rx.var
    def t(self) -> dict:
        """현재 언어에 맞는 번역 딕셔너리 반환"""
        return self.translations.get(self.locale, self.translations["ko"])
    
    @staticmethod
    def tr(key: str, **kwargs) -> str:
        return (LanguageState.t[key] if key in LanguageState.t else key).format(**kwargs)    
    
    def tr_str(self, key: str, **kwargs) -> str:
        translations = self.translations.get(self.locale, self.translations["ko"])
        return translations.get(key, key).format(**kwargs)    