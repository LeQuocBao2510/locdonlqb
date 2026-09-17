import io
import datetime
import importlib
import streamlit as st
import pandas as pd

import data_processor
import word_generator
import sample_data

importlib.reload(data_processor)
importlib.reload(word_generator)
importlib.reload(sample_data)

from data_processor import read_order_file, process_orders
from word_generator import generate_packing_word_doc
from sample_data import generate_sample_tiktok_orders

# -------------------------------------------------------------
# CẤU HÌNH TRANG STREAMLIT
# -------------------------------------------------------------
st.set_page_config(
    page_title="Lọc Đơn - Xử Lý Đơn Hàng TikTok & Shopee",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# TÙY CHỈNH CSS GIAO DIỆN HIỆN ĐẠI
# -------------------------------------------------------------
st.markdown("""
<style>
    /* Font và bố cục */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 6px 0 0 0;
        color: #94A3B8;
        font-size: 15px;
    }
    
    /* Nút tải xuống lớn màu xanh dương chuẩn Image 1 */
    div.stDownloadButton > button {
        background-color: #1D64F2 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 24px !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(29, 100, 242, 0.3) !important;
        transition: background-color 0.2s, transform 0.1s !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #1550c7 !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }
    
    /* Thẻ thống kê (Metric Card) */
    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 30px;
        font-weight: 800;
        margin-top: 4px;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 6px;
    }

    /* Khung tải file */
    .upload-box {
        background: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* Highlight badge */
    .badge-tiktok {
        background-color: #000000;
        color: #FE2C55;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# QUẢN LÝ SESSION STATE
# -------------------------------------------------------------
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = False
if 'sample_prev' not in st.session_state:
    st.session_state.sample_prev = None
if 'sample_curr' not in st.session_state:
    st.session_state.sample_curr = None

# -------------------------------------------------------------
# SIDEBAR - CẤU HÌNH SHOP & CA LÀM VIỆC
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏬 **LỌC ĐƠN**")
    st.caption("Công cụ quản lý & xử lý đơn hàng TMĐT")
    st.divider()

    st.markdown("#### ⚙️ Cấu hình gian hàng")
    platform = st.selectbox("Sàn thương mại:", ["TikTok Shop", "Shopee", "Đa sàn"], index=0)
    shop_name = st.selectbox("Tên Cửa Hàng / Shop:", ["GIMME TEE", "TITIKID"], index=0)

    st.markdown("#### 🕒 Thông tin ca làm việc")
    shift_name = st.selectbox("Chọn ca làm việc:", ["SÁNG", "CHIỀU"], index=0)

    # Tự động cập nhật ngày & giờ theo Múi giờ Việt Nam (GMT+7)
    vn_tz = datetime.timezone(datetime.timedelta(hours=7))
    vn_now = datetime.datetime.now(vn_tz)
    work_date = vn_now.strftime("%d/%m/%Y")
    vn_time_display = vn_now.strftime("%H:%M:%S")

    st.markdown("#### 🕒 Ngày & Giờ (Giờ Việt Nam GMT+7)")
    st.text_input("Ngày làm việc:", value=work_date, disabled=True, help="Tự động cập nhật theo giờ Việt Nam GMT+7")
    st.caption(f"🕒 Giờ hiện tại: **{vn_time_display}** *(Tự động đồng bộ)*")

    st.divider()
    st.markdown("#### 🛡️ Tùy chọn lọc đơn")
    filter_by_order_id = st.checkbox("Lọc trùng theo Mã đơn hàng (Khuyên dùng)", value=True, disabled=True)
    filter_by_phone = st.checkbox("Lọc thêm theo Số điện thoại trùng", value=False)
    
    st.divider()
    st.info("💡 **Gợi ý:** Để lọc đơn trùng chuẩn xác nhất, hãy tải cả **File ca hiện tại** và **File ca trước**.")

# -------------------------------------------------------------
# HEADER TRANG CHÍNH
# -------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1>📦 Lọc Đơn — Xử Lý Đơn Hàng {platform}</h1>
            <p>Tự động tổng hợp đơn hàng • Lọc trùng thông minh theo ca • Xuất phiếu Word & Excel soạn hàng chuẩn in</p>
        </div>
        <div>
            <span class="badge-tiktok">TIKTOK SHOP / SHOPEE READY</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# KHU VỰC TẢI FILE
# -------------------------------------------------------------
st.markdown("### 1. Tải lên tệp dữ liệu đơn hàng")

col_demo1, col_demo2 = st.columns([3, 1])
with col_demo2:
    if st.button("🧪 Thử nghiệm dữ liệu mẫu (Demo)", use_container_width=True, type="secondary"):
        st.session_state.use_sample = True
        buf_p, buf_c, df_p, df_c = generate_sample_tiktok_orders()
        st.session_state.sample_prev = df_p
        st.session_state.sample_curr = df_c
        st.toast("Đã nạp 15 đơn hàng mẫu (gồm 3 đơn trùng ca trước) để thử nghiệm!", icon="✅")

with col_demo1:
    if st.session_state.use_sample:
        st.info("⚡ Đang ở chế độ **Dữ liệu mẫu (Demo)**. Bạn có thể tải file thật bên dưới bất kỳ lúc nào để chuyển về dữ liệu thực tế.")

col_upload1, col_upload2 = st.columns(2)

with col_upload1:
    st.markdown("#### 📁 File ca hiện tại *(Bắt buộc)*")
    uploaded_curr = st.file_uploader(
        "Chọn file Excel (.xlsx) hoặc .csv xuất từ TikTok Shop / Shopee",
        type=["xlsx", "xls", "csv"],
        key="uploader_curr",
        help="Chứa toàn bộ danh sách đơn hàng cần xử lý trong ca này"
    )

with col_upload2:
    st.markdown("#### 📁 File ca trước *(Tùy chọn - Dùng lọc trùng)*")
    uploaded_prev = st.file_uploader(
        "Chọn file của ca trước để đối chiếu loại bỏ đơn trùng",
        type=["xlsx", "xls", "csv"],
        key="uploader_prev",
        help="Hệ thống sẽ loại bỏ các mã đơn trong ca hiện tại mà đã xuất hiện ở file này"
    )

# -------------------------------------------------------------
# XỬ LÝ DỮ LIỆU
# -------------------------------------------------------------
df_curr_raw = None
df_prev_raw = None

if uploaded_curr is not None:
    st.session_state.use_sample = False
    try:
        df_curr_raw = read_order_file(uploaded_curr)
    except Exception as e:
        st.error(f"Lỗi đọc file ca hiện tại: {e}")
        st.stop()
elif st.session_state.use_sample:
    df_curr_raw = st.session_state.sample_curr

if uploaded_prev is not None:
    try:
        df_prev_raw = read_order_file(uploaded_prev)
    except Exception as e:
        st.warning(f"Lỗi đọc file ca trước: {e}")
elif st.session_state.use_sample:
    df_prev_raw = st.session_state.sample_prev

# -------------------------------------------------------------
# KHI ĐÃ CÓ DỮ LIỆU ĐỂ XỬ LÝ
# -------------------------------------------------------------
if df_curr_raw is not None:
    try:
        with st.spinner("Đang phân tích dữ liệu, nhận diện cột và lọc đơn trùng..."):
            result = process_orders(df_curr_raw, df_prev_raw, filter_by_phone=filter_by_phone)
    except Exception as e:
        st.error(f"❌ Xảy ra lỗi khi xử lý dữ liệu: {str(e)}")
        st.stop()

    metrics = result['metrics']
    pick_list = result['pick_list']
    display_valid = result['display_valid']
    display_dup = result['display_dup']
    df_valid = result['df_valid']

    st.divider()

    # DASHBOARD THỐNG KÊ & KẾT QUẢ
    st.markdown("### 2. Kết quả phân tích & Lọc trùng")

    # Banner thông báo lọc trùng (nếu phát hiện đơn trùng)
    if metrics['dup_orders_count'] > 0:
        prev_cnt = metrics.get('prev_orders_count', 0)
        st.markdown(f"""
        <div style="background: #FFFBEB; border: 1.5px solid #FDE68A; border-radius: 12px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <div style="font-weight: 700; color: #92400E; font-size: 14px; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 16px;">⇄</span> Đã lọc trùng với file ca trước
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #EFF6FF; border: 1px solid #DBEAFE; color: #1E40AF; padding: 3px 10px; border-radius: 16px; font-size: 12px; font-weight: 600;">Ca này: {metrics['total_raw_orders']} đơn</span>
                    <span style="background: #EFF6FF; border: 1px solid #DBEAFE; color: #1E40AF; padding: 3px 10px; border-radius: 16px; font-size: 12px; font-weight: 600;">Ca trước: {prev_cnt} đơn</span>
                    <span style="background: #FEF3C7; border: 1px solid #FDE68A; color: #D97706; padding: 3px 10px; border-radius: 16px; font-size: 12px; font-weight: 700;">Loại: {metrics['dup_orders_count']} trùng</span>
                    <span style="background: #ECFDF5; border: 1px solid #A7F3D0; color: #059669; padding: 3px 10px; border-radius: 16px; font-size: 12px; font-weight: 700;">Giữ: {metrics['valid_orders_count']} mới</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 32px; font-weight: 800; color: #D97706; line-height: 1;">-{metrics['dup_orders_count']}</div>
                <div style="font-size: 12px; color: #B45309; margin-top: 2px;">đơn trùng</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 3 Thẻ thống kê chuẩn giao diện Ảnh 1
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📦 TỔNG ĐƠN HÀNG</div>
            <div class="metric-value" style="color:#0F172A;">{metrics['valid_orders_count']}</div>
            <div class="metric-sub">sau khi lọc {metrics['dup_orders_count']} trùng</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👕 TỔNG SẢN PHẨM</div>
            <div class="metric-value" style="color:#E11D48;">{metrics['total_valid_items']}</div>
            <div class="metric-sub">tổng số lượng áo</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏷️ LOẠI SKU</div>
            <div class="metric-value" style="color:#059669;">{metrics['unique_skus_count']}</div>
            <div class="metric-sub">mã sản phẩm khác nhau</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Chuẩn hóa tên file theo mẫu: GIMME_SHOPEE_SÁNG_17.09_418 ĐƠN_489 ÁO.docx
    shop_tag = "GIMME" if "GIMME" in str(shop_name).upper() else str(shop_name).upper()
    plat_tag = "SHOPEE" if "SHOPEE" in str(platform).upper() else "TIKTOK"
    shift_tag = str(shift_name).upper()
    date_parts = str(work_date).split("/")
    date_tag = f"{date_parts[0]}.{date_parts[1]}" if len(date_parts) >= 2 else str(work_date)
    orders_cnt = metrics.get('valid_orders_count', 0)
    items_cnt = metrics.get('total_valid_items', 0)
    skus_cnt = metrics.get('unique_skus_count', len(pick_list))

    filename_base = f"{shop_tag}_{plat_tag}_{shift_tag}_{date_tag}_{orders_cnt} ĐƠN_{items_cnt} ÁO"
    file_word_name = f"{filename_base}.docx"

    # Dòng tên .docx + nút Copy tên giống 100% Ảnh 1
    import streamlit.components.v1 as components
    components.html(f"""
    <div style="display: flex; align-items: center; gap: 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin-bottom: 2px;">
      <div style="display: flex; align-items: center; justify-content: space-between; background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 8px; padding: 7px 14px; flex: 1; font-size: 13.5px; font-weight: 600; color: #1E293B;">
        <span>{filename_base}</span>
        <span style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #2563EB; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 10px;">.DOCX</span>
      </div>
      <button id="btnCopy" onclick="doCopy()" style="display: inline-flex; align-items: center; gap: 6px; background: white; border: 1.5px solid #2563EB; color: #2563EB; padding: 7px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; white-space: nowrap;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        <span id="btnCopyText">Copy tên</span>
      </button>
      <span style="font-size: 12.5px; color: #64748B; white-space: nowrap; margin-left: 4px;">{orders_cnt} đơn · {items_cnt} sp · {skus_cnt} SKU</span>
    </div>
    <script>
    function doCopy() {{
      const t = '{filename_base}';
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(t).then(() => showCopied());
      }} else {{
        const ta = document.createElement('textarea');
        ta.value = t;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showCopied();
      }}
    }}
    function showCopied() {{
      const btn = document.getElementById('btnCopy');
      const txt = document.getElementById('btnCopyText');
      txt.innerText = '✓ Đã copy!';
      btn.style.background = '#EFF6FF';
      setTimeout(() => {{
        txt.innerText = 'Copy tên';
        btn.style.background = 'white';
      }}, 2000);
    }}
    </script>
    """, height=52)

    # Nút tải xuống phiếu soạn hàng Word DUY NHẤT (full width, màu xanh dương chuẩn Image 1)
    word_buffer = generate_packing_word_doc(
        shop_name=shop_name,
        platform=platform,
        shift_name=shift_name,
        work_date=work_date,
        metrics=metrics,
        pick_list_df=pick_list,
        df_valid=df_valid
    )
    st.download_button(
        label=f"📥 Tải xuống phiếu soạn hàng — {orders_cnt} đơn · {items_cnt} áo",
        data=word_buffer,
        file_name=file_word_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )

    st.write("")

    # -------------------------------------------------------------
    # TABS HIỂN THỊ CHI TIẾT
    # -------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📋 Bảng Gom Hàng Nhặt Kho ({len(pick_list)} dòng)",
        f"📦 Chi Tiết Đơn Hợp Lệ ({metrics['valid_orders_count']} đơn)",
        f"🚫 Danh Sách Đơn Trùng ({metrics['dup_orders_count']} đơn)",
        "⚙️ Dữ Liệu Gốc"
    ])

    with tab1:
        st.markdown("##### 🛒 Bảng tổng hợp số lượng sản phẩm cần nhặt (Pick List)")
        st.caption("Bảng cấu trúc chuẩn 4 cột: SKU sản phẩm | Màu | Size | Áo")
        
        search_sku = st.text_input("🔍 Tìm kiếm nhanh theo Mã SKU hoặc Màu:", "")
        df_show_pick = pick_list.copy()
        if search_sku:
            mask = (
                df_show_pick['SKU sản phẩm'].astype(str).str.contains(search_sku, case=False, na=False) |
                df_show_pick['Màu'].astype(str).str.contains(search_sku, case=False, na=False)
            )
            df_show_pick = df_show_pick[mask]
        
        st.dataframe(
            df_show_pick,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SKU sản phẩm": st.column_config.TextColumn("SKU sản phẩm", width="medium"),
                "Màu": st.column_config.TextColumn("Màu", width="medium"),
                "Size": st.column_config.TextColumn("Size", width="small"),
                "Áo": st.column_config.NumberColumn("Áo (SL) 🔥", width="small"),
                "Số đơn hàng": st.column_config.NumberColumn("Số Đơn", width="small"),
            }
        )

    with tab2:
        st.markdown("##### 📦 Danh sách đơn hàng hợp lệ đã làm sạch")
        st.caption("Toàn bộ các đơn hàng đã được loại bỏ đơn trùng, sẵn sàng để đóng gói gửi đi.")
        st.dataframe(
            display_valid,
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.markdown("##### 🚫 Danh sách các đơn bị loại bỏ do trùng lặp")
        if not display_dup.empty:
            st.warning(f"Phát hiện **{metrics['dup_orders_count']}** đơn trùng lặp với ca trước hoặc lặp lại trong file.")
            st.dataframe(
                display_dup,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("🎉 Tuyệt vời! Không phát hiện đơn trùng nào trong ca này.")

    with tab4:
        st.markdown("##### ⚙️ Dữ liệu gốc tải lên")
        st.dataframe(df_curr_raw, use_container_width=True)

else:
    # HƯỚNG DẪN KHI CHƯA CÓ FILE
    st.info("""
    👋 **Chào mừng bạn đến với Order Studio!**
    
    Để bắt đầu xử lý đơn hàng:
    1. Tải **File ca hiện tại** (file Excel/CSV xuất từ TikTok Shop Seller Center hoặc Shopee) vào ô bên trái.
    2. *(Tùy chọn)* Tải thêm **File ca trước** vào ô bên phải để hệ thống tự động lọc bỏ các đơn hàng bị trùng lặp.
    3. Nhấn **Tải Phiếu Soạn Hàng (Word .docx)** để in phiếu nhặt hàng và đóng gói!
    
    👉 Hoặc bạn có thể bấm nút **'🧪 Thử nghiệm dữ liệu mẫu (Demo)'** ở góc trên bên phải để trải nghiệm ngay lập tức.
    """)
