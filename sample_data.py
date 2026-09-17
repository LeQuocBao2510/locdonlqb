import io
import pandas as pd
import datetime

def generate_sample_tiktok_orders():
    """
    Sinh dữ liệu mẫu đơn hàng chuẩn với các SKU và phân loại thực tế
    như GMB104, GMB106, GMB113, GMB135... (chuẩn mẫu xulydontiktok / Order Studio)
    """
    # Đơn hàng ca trước (để đối soát lọc trùng)
    prev_orders = [
        {"Mã đơn hàng": "5789123450001", "Trạng thái đơn hàng": "Đã hoàn thành", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Kem - Cổ Nâu, L", "Mã SKU người bán": "GMB104", "Số lượng": 1, "Người nhận": "Nguyễn Văn An", "Số điện thoại": "0987111222", "Địa chỉ chi tiết": "123 Cầu Giấy, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-16 08:30:00"},
        {"Mã đơn hàng": "5789123450002", "Trạng thái đơn hàng": "Đang vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Hồng Pastel Chữ Đỏ, L", "Mã SKU người bán": "GMB106", "Số lượng": 2, "Người nhận": "Trần Thị Bình", "Số điện thoại": "0912333444", "Địa chỉ chi tiết": "45 Lê Lợi, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-16 09:15:00"},
        {"Mã đơn hàng": "5789123450003", "Trạng thái đơn hàng": "Đang vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Donut-Đen Chữ Trắng, S", "Mã SKU người bán": "GMB113", "Số lượng": 1, "Người nhận": "Lê Văn Cường", "Số điện thoại": "0905555666", "Địa chỉ chi tiết": "78 Trần Phú, Đà Nẵng", "Đơn vị vận chuyển": "J&T Express", "Thời gian tạo": "2026-09-16 10:00:00"},
        # 3 đơn sẽ bị trùng ở ca hiện tại:
        {"Mã đơn hàng": "5789123450008", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Đen, L", "Mã SKU người bán": "GMB104", "Số lượng": 1, "Người nhận": "Bùi Thị Lan", "Số điện thoại": "0923456789", "Địa chỉ chi tiết": "67 Bà Triệu, Nha Trang", "Đơn vị vận chuyển": "Giao Hàng Nhanh", "Thời gian tạo": "2026-09-16 16:30:00"},
        {"Mã đơn hàng": "5789123450009", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Kem Cổ Navy, M (Premium)", "Mã SKU người bán": "GMB135", "Số lượng": 1, "Người nhận": "Đỗ Văn Khoa", "Số điện thoại": "0988776655", "Địa chỉ chi tiết": "15 Trần Hưng Đạo, Vũng Tàu", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-16 17:15:00"},
        {"Mã đơn hàng": "5789123450010", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Kem - Tóc Vàng, M (Premium)", "Mã SKU người bán": "GMB142", "Số lượng": 1, "Người nhận": "Ngô Thị Mai", "Số điện thoại": "0911223344", "Địa chỉ chi tiết": "92 Điện Biên Phủ, Đà Nẵng", "Đơn vị vận chuyển": "J&T Express", "Thời gian tạo": "2026-09-16 18:00:00"},
    ]
    
    # Đơn hàng ca hiện tại (chứa đầy đủ các mặt hàng đúng form mẫu)
    current_orders = [
        # 3 Đơn trùng ca trước
        {"Mã đơn hàng": "5789123450008", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Đen, L", "Mã SKU người bán": "GMB104", "Số lượng": 1, "Người nhận": "Bùi Thị Lan", "Số điện thoại": "0923456789", "Địa chỉ chi tiết": "67 Bà Triệu, Nha Trang", "Đơn vị vận chuyển": "Giao Hàng Nhanh", "Thời gian tạo": "2026-09-16 16:30:00"},
        {"Mã đơn hàng": "5789123450009", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Kem Cổ Navy, M (Premium)", "Mã SKU người bán": "GMB135", "Số lượng": 1, "Người nhận": "Đỗ Văn Khoa", "Số điện thoại": "0988776655", "Địa chỉ chi tiết": "15 Trần Hưng Đạo, Vũng Tàu", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-16 17:15:00"},
        {"Mã đơn hàng": "5789123450010", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun Unisex Cotton GIMME", "Tên phân loại": "Kem - Tóc Vàng, M (Premium)", "Mã SKU người bán": "GMB142", "Số lượng": 1, "Người nhận": "Ngô Thị Mai", "Số điện thoại": "0911223344", "Địa chỉ chi tiết": "92 Điện Biên Phủ, Đà Nẵng", "Đơn vị vận chuyển": "J&T Express", "Thời gian tạo": "2026-09-16 18:00:00"},
        
        # Các đơn hợp lệ chuẩn theo form ảnh:
        # GMB104
        {"Mã đơn hàng": "5789123450011", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB104", "Tên phân loại": "Kem - Cổ Nâu, L", "Mã SKU người bán": "GMB104", "Số lượng": 1, "Người nhận": "Trịnh Văn Nam", "Số điện thoại": "0933445566", "Địa chỉ chi tiết": "100 Kim Mã, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 07:10:00"},
        {"Mã đơn hàng": "5789123450012", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB104", "Tên phân loại": "Đen, L", "Mã SKU người bán": "GMB104", "Số lượng": 2, "Người nhận": "Dương Quỳnh Nga", "Số điện thoại": "0966778899", "Địa chỉ chi tiết": "44 Nguyễn Oanh, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 07:25:00"},
        
        # GMB106
        {"Mã đơn hàng": "5789123450013", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB106", "Tên phân loại": "Hồng Pastel Chữ Đỏ, L", "Mã SKU người bán": "GMB106", "Số lượng": 2, "Người nhận": "Lý Văn Phát", "Số điện thoại": "0977889900", "Địa chỉ chi tiết": "28 Bạch Đằng, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 07:40:00"},
        {"Mã đơn hàng": "5789123450014", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB106", "Tên phân loại": "Hồng Pastel Chữ Đỏ, S", "Mã SKU người bán": "GMB106", "Số lượng": 1, "Người nhận": "Mai Thu Quỳnh", "Số điện thoại": "0909123456", "Địa chỉ chi tiết": "15 Đinh Tiên Hoàng, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 08:05:00"},
        
        # GMB113
        {"Mã đơn hàng": "5789123450015", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB113", "Tên phân loại": "Donut-Đen Chữ Trắng, S", "Mã SKU người bán": "GMB113", "Số lượng": 1, "Người nhận": "Trương Minh Sang", "Số điện thoại": "0918273645", "Địa chỉ chi tiết": "72 Lê Duẩn, Đà Nẵng", "Đơn vị vận chuyển": "Giao Hàng Nhanh", "Thời gian tạo": "2026-09-17 08:15:00"},
        {"Mã đơn hàng": "5789123450016", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB113", "Tên phân loại": "Teddy-Đen Chữ Trắng, S", "Mã SKU người bán": "GMB113", "Số lượng": 1, "Người nhận": "Võ Thị Thảo", "Số điện thoại": "0944556677", "Địa chỉ chi tiết": "50 Nguyễn Văn Cừ, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 08:30:00"},
        
        # GMB128, GMB129, GMB130
        {"Mã đơn hàng": "5789123450017", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB128", "Tên phân loại": "Đen, L (Premium)", "Mã SKU người bán": "GMB128", "Số lượng": 1, "Người nhận": "Nguyễn Hoàng Uyên", "Số điện thoại": "0938495061", "Địa chỉ chi tiết": "18 CMT8, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 08:45:00"},
        {"Mã đơn hàng": "5789123450018", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB129", "Tên phân loại": "Kem Chữ Hồng, S (Premium)", "Mã SKU người bán": "GMB129", "Số lượng": 1, "Người nhận": "Lâm Quốc Việt", "Số điện thoại": "0981928374", "Địa chỉ chi tiết": "88 Cầu Đất, Hải Phòng", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:00:00"},
        {"Mã đơn hàng": "5789123450019", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB130", "Tên phân loại": "Đen Cổ Trắng, M (Premium)", "Mã SKU người bán": "GMB130", "Số lượng": 1, "Người nhận": "Phan Thị Xuân", "Số điện thoại": "0929384756", "Địa chỉ chi tiết": "33 Trần Phú, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:12:00"},
        
        # GMB135 (Có 3 size: L, M, S với số lượng 2, 5, 2)
        {"Mã đơn hàng": "5789123450020", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB135", "Tên phân loại": "Kem Cổ Navy, L (Premium)", "Mã SKU người bán": "GMB135", "Số lượng": 2, "Người nhận": "Tạ Văn Yên", "Số điện thoại": "0971239874", "Địa chỉ chi tiết": "99 Lạc Long Quân, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:20:00"},
        {"Mã đơn hàng": "5789123450021", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB135", "Tên phân loại": "Kem Cổ Navy, M (Premium)", "Mã SKU người bán": "GMB135", "Số lượng": 5, "Người nhận": "Chu Văn An", "Số điện thoại": "0912983746", "Địa chỉ chi tiết": "12 Bà Hom, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:30:00"},
        {"Mã đơn hàng": "5789123450022", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB135", "Tên phân loại": "Kem Cổ Navy, S (Premium)", "Mã SKU người bán": "GMB135", "Số lượng": 2, "Người nhận": "Lê Bảo", "Số điện thoại": "0944112233", "Địa chỉ chi tiết": "45 Trường Sa, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:35:00"},
        
        # GMB142
        {"Mã đơn hàng": "5789123450023", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB142", "Tên phân loại": "Kem - Tóc Vàng, M (Premium)", "Mã SKU người bán": "GMB142", "Số lượng": 1, "Người nhận": "Đặng Thị Thúy", "Số điện thoại": "0977665544", "Địa chỉ chi tiết": "19 Lý Tự Trọng, Đà Nẵng", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:40:00"},
        {"Mã đơn hàng": "5789123450024", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB142", "Tên phân loại": "Kem - Tóc Đen, S (Premium)", "Mã SKU người bán": "GMB142", "Số lượng": 1, "Người nhận": "Trần Đình Khang", "Số điện thoại": "0933221100", "Địa chỉ chi tiết": "22 Nguyễn Huệ, TP. HCM", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:45:00"},
        {"Mã đơn hàng": "5789123450025", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB142", "Tên phân loại": "Đen - Tóc Vàng, S (Premium)", "Mã SKU người bán": "GMB142", "Số lượng": 1, "Người nhận": "Phạm Quốc Dũng", "Số điện thoại": "0988001122", "Địa chỉ chi tiết": "66 Hàng Bài, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:50:00"},

        # GMB143
        {"Mã đơn hàng": "5789123450026", "Trạng thái đơn hàng": "Chờ vận chuyển", "Tên sản phẩm": "Áo Thun GIMME GMB143", "Tên phân loại": "Chữ Hồng, M", "Mã SKU người bán": "GMB143", "Số lượng": 1, "Người nhận": "Hoàng Minh Tâm", "Số điện thoại": "0911778899", "Địa chỉ chi tiết": "15 Lê Duẩn, Hà Nội", "Đơn vị vận chuyển": "SPX Express", "Thời gian tạo": "2026-09-17 09:55:00"},
    ]
    
    df_prev = pd.DataFrame(prev_orders)
    df_curr = pd.DataFrame(current_orders)
    
    buf_prev = io.BytesIO()
    with pd.ExcelWriter(buf_prev, engine='openpyxl') as writer:
        df_prev.to_excel(writer, index=False, sheet_name="Order_List")
    buf_prev.seek(0)
    
    buf_curr = io.BytesIO()
    with pd.ExcelWriter(buf_curr, engine='openpyxl') as writer:
        df_curr.to_excel(writer, index=False, sheet_name="Order_List")
    buf_curr.seek(0)
    
    return buf_prev, buf_curr, df_prev, df_curr
