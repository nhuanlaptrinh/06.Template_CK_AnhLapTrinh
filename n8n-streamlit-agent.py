import streamlit as st
import requests
import uuid
from supabase import create_client, Client


# Hàm đọc nội dung từ file văn bản
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
            st.error(f"File {name_file} không tồn tại.")


# Constants
WEBHOOK_URL = rfile("WEBHOOK_URL.txt").strip()
SUPABASE_URL = rfile("SUPABASE_URL.txt").strip()
SUPABASE_KEY = rfile("SUPABASE_KEY.txt").strip()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Chào mừng bạn đến với Trợ lý AI"

def generate_session_id():
    return str(uuid.uuid4())

def login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Đăng nhập thất bại: {str(e)}")
        return None

def signup(email: str, password: str):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return res
    except Exception as e:
        st.error(f"Đăng ký thất bại: {str(e)}")
        return None

def send_message_to_llm(session_id, message, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print("Response status code:", response)  # In ra mã trạng thái HTTP
        print("Full response:", response_data)  # In ra toàn bộ dữ liệu trả về
        return response_data.get("output", "No output received") # Trả về "output"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the LLM - {str(e)}"


def init_session_state():
    if "auth" not in st.session_state:
        st.session_state.auth = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

def handle_logout():
    st.session_state.auth = None
    st.session_state.session_id = None
    st.session_state.messages = []
    st.success("Bạn đã đăng xuất.")
    st.rerun()

def auth_ui():
    st.title("Chào mừng đến với AI Chat")
    st.subheader("Vui lòng đăng nhập hoặc đăng ký để tiếp tục")

    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký"])

    with tab1:
        st.subheader("Đăng nhập")
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Mật khẩu", type="password", key="login_password")
            login_button = st.form_submit_button("Đăng nhập")

            if login_button:
                if not login_email or not login_password:
                    st.warning("Vui lòng nhập cả email và mật khẩu.")
                else:
                    auth_response = login(login_email, login_password)
                    if auth_response and hasattr(auth_response, 'user') and auth_response.user:
                        st.session_state.auth = auth_response
                        st.session_state.session_id = generate_session_id()
                        st.session_state.messages = []
                        st.success("Đăng nhập thành công!")
                        st.rerun()
                    elif auth_response is None:
                        pass
                    else:
                        st.error("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập hoặc thử lại.")
                        if hasattr(auth_response, 'error') and auth_response.error:
                             st.error(f"Chi tiết: {auth_response.error.message}")

    with tab2:
        st.subheader("Đăng ký")
        with st.form("signup_form"):
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Mật khẩu", type="password", key="signup_password")
            signup_confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="signup_confirm_password")
            signup_button = st.form_submit_button("Đăng ký")

            if signup_button:
                if not signup_email or not signup_password or not signup_confirm_password:
                    st.warning("Vui lòng điền đầy đủ các trường.")
                elif signup_password != signup_confirm_password:
                    st.error("Mật khẩu không khớp.")
                else:
                    signup_response = signup(signup_email, signup_password)
                    if signup_response and hasattr(signup_response, 'user') and signup_response.user:
                        st.success("Đăng ký thành công! Vui lòng kiểm tra email để xác minh (nếu được yêu cầu), sau đó đăng nhập.")
                    elif signup_response is None:
                        pass
                    else:
                        st.error("Đăng ký thất bại. Email có thể đã được sử dụng hoặc mật khẩu quá yếu.")
                        if hasattr(signup_response, 'error') and signup_response.error:
                             st.error(f"Chi tiết: {signup_response.error.message}")

def main():
    st.set_page_config(page_title="AI Chat", layout="wide")
    init_session_state()

    if st.session_state.auth is None or not hasattr(st.session_state.auth, 'user') or not st.session_state.auth.user:
        auth_ui()
    else:
        try:
            col1_main, col2_main, col3_main = st.columns([3, 1, 3])
            with col2_main:
                st.image("logo.png", width=100)
        except FileNotFoundError:
            pass
        except Exception:
            pass

        title_content = rfile("00.xinchao.txt")
        st.markdown(
            f"""<h1 style="text-align: center; font-size: 28px; margin-bottom: 20px;">{title_content}</h1>""",
            unsafe_allow_html=True
        )

        st.sidebar.subheader("Thông tin người dùng")
        if st.session_state.auth and st.session_state.auth.user:
             st.sidebar.success(f"Đăng nhập với tên: {st.session_state.auth.user.email}")
        st.sidebar.info(f"ID Phiên: {st.session_state.session_id}")
        if st.sidebar.button("Đăng xuất", key="logout_button"):
            handle_logout()

        st.markdown(
            """
            <style>
                .message-container {
                    display: flex;
                    flex-direction: column;
                    margin-bottom: 10px;
                }
                .assistant {
                    max-width: 70%;
                    color: #fff;
                    text-align: left;
                    align-self: flex-start;
                    margin-right: auto;
                    
                }
                .user {
                    padding: 10px 15px;
                    border-radius: 15px;
                    max-width: 70%;
                    color: white;
                    text-align: left;
                    align-self: flex-end;
                    margin-left: auto;
                    border-bottom-right-radius: 0px;
                }
                .stAlert {
                    display:none;}
                .assistant::before { content: "🤖 "; font-weight: bold; }
                .user::before { content: ""; }
            </style>
            """,
            unsafe_allow_html=True
        )

        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "assistant":
                    st.markdown(f'<div class="message-container"><div class="assistant">{message["content"]}</div></div>', unsafe_allow_html=True)
                elif message["role"] == "user":
                    st.markdown(f'<div class="message-container"><div class="user">{message["content"]}</div></div>', unsafe_allow_html=True)

        prompt = st.chat_input("Nhập nội dung cần trao đổi ở đây nhé?")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                 st.markdown(f'<div class="message-container"><div class="user">{prompt}</div></div>', unsafe_allow_html=True)

            access_token = ""
            if st.session_state.auth and hasattr(st.session_state.auth, 'session') and st.session_state.auth.session:
                access_token = st.session_state.auth.session.access_token
            else:
                st.error("Không tìm thấy mã thông báo xác thực. Vui lòng đăng nhập lại.")
                return

            with st.spinner("Đang chờ phản hồi từ AI..."):
                llm_response = send_message_to_llm(st.session_state.session_id, prompt, access_token)

            st.session_state.messages.append({"role": "assistant", "content": llm_response})
            with chat_container:
                st.markdown(f'<div class="message-container"><div class="assistant">{llm_response}</div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    if not SUPABASE_KEY:
         try:
            #SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
            SUPABASE_KEY = rfile("SUPABASE_KEY.txt").strip()
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
         except (FileNotFoundError, KeyError):
            st.error("Không tìm thấy khóa Supabase. Vui lòng cấu hình trong Streamlit secrets hoặc trực tiếp trong script để kiểm thử cục bộ (không khuyến nghị cho productie).")
            st.stop()

    if not SUPABASE_KEY:
        st.error("Ứng dụng không thể khởi động: Thiếu Khóa Supabase.")
        st.stop()

    main()