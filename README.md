# 📦 Order Studio — Web App Xử Lý Đơn Hàng TikTok Shop & Shopee

Ứng dụng web được xây dựng bằng **Python + Streamlit**, mô phỏng và nâng cấp 100% các tính năng của `xulydontiktok.streamlit.app` (Order Studio).

---

## 🌟 Các Tính Năng Nổi Bật

1. **Tổng hợp & Nhận diện dữ liệu thông minh**:
   - Tải file Excel (`.xlsx`, `.xls`) hoặc `.csv` xuất trực tiếp từ **TikTok Shop Seller Center** hoặc **Shopee**.
   - Tự động nhận diện các cột (Mã đơn hàng, Tên sản phẩm, Phân loại, SKU, Số lượng, Người nhận, SĐT, Vận đơn...).

2. **Lọc đơn trùng chuyên nghiệp giữa các ca**:
   - **File ca hiện tại (Bắt buộc)**: Chứa danh sách đơn cần xử lý trong phiên làm việc.
   - **File ca trước (Tùy chọn)**: Dùng để đối soát, tự động loại bỏ các đơn đã đóng gói ở ca trước để tránh gửi trùng hàng.
   - Loại bỏ các dòng sản phẩm bị trùng lặp trong cùng phiên.

3. **Bảng thống kê Dashboard Metrics**:
   - 📦 Tổng đơn hàng nạp vào
   - ⚠️ Số đơn bị trùng (loại bỏ tự động)
   - ✅ Số đơn hợp lệ cần soạn
   - 🏷️ Tổng số lượng hàng hóa (SKU) cần nhặt

4. **Bảng gom hàng nhặt kho (Pick List)**:
   - Tự động gom nhóm theo SKU, Phân loại (màu, size), Sản phẩm kèm tổng số lượng cần lấy từ kệ kho.
   - Tìm kiếm nhanh theo tên sản phẩm hoặc mã SKU.

5. **Xuất file Word (.docx) & Excel (.xlsx) chuẩn in**:
   - **Phiếu Soạn Hàng (Word .docx)**: Thiết kế đẹp mắt, sẵn sàng in A4 gồm Bảng kê nhặt hàng (có ô `[   ]` để tick kiểm tra) và Danh sách đơn chi tiết để đóng gói.
   - **File Excel (.xlsx)**: Đã phân chia sheet rõ ràng (Bảng gom hàng & Đơn chi tiết & Đơn trùng).

6. **Chế độ Thử nghiệm Nhanh (Demo Sample)**:
   - Tích hợp sẵn nút bấm nạp dữ liệu mẫu để bạn thử nghiệm ngay các tính năng mà chưa cần chuẩn bị file thật.

---

## 🚀 Hướng Dẫn Khởi Chạy Trên Máy Tính

### Cách 1: Click chạy ngay (Windows)
Double-click vào file **`run_app.bat`** trong thư mục này. Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ `http://localhost:8501`.

### Cách 2: Chạy bằng Terminal / PowerShell
```bash
cd c:\Users\Admin\Downloads\shopee-price-extension\tiktok_order_studio
python -m streamlit run app.py
```

---

## 🌐 Hướng Dẫn Đưa Lên Streamlit Cloud (Để Có Link Web Dùng Chung Miễn Phí)

Nếu bạn muốn có một đường link công khai như `https://xulydontiktok-cua-ban.streamlit.app` để nhân viên kho và quản lý dùng chung trên điện thoại hoặc máy tính khác:

1. **Đăng mã nguồn lên GitHub**:
   - Tạo 1 repository mới trên GitHub (ví dụ: `tiktok-order-studio`).
   - Đẩy toàn bộ các file trong thư mục này (`app.py`, `data_processor.py`, `word_generator.py`, `sample_data.py`, `requirements.txt`) lên repository đó.

2. **Triển khai trên Streamlit Cloud**:
   - Truy cập: [https://share.streamlit.io](https://share.streamlit.io) và đăng nhập bằng tài khoản GitHub.
   - Nhấn **New app**.
   - Chọn Repository của bạn, Branch: `main`, Main file path: `app.py`.
   - Đặt App URL (Subdomain tùy chọn): ví dụ `xuly-don-shopabc.streamlit.app`.
   - Nhấn **Deploy**! Chỉ sau 1-2 phút, ứng dụng của bạn sẽ hoạt động trực tuyến 24/7 hoàn toàn miễn phí.
