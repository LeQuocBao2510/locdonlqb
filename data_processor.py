import pandas as pd
import numpy as np
import io

COL_ALIASES = {
    'order_id': [
        'mã đơn hàng', 'order id', 'order_id', 'mã đơn', 'id đơn hàng', 
        'mã đơn hàng / order id', 'order id / id đơn hàng', 'mã đặt hàng'
    ],
    'order_status': [
        'trạng thái đơn hàng', 'order status', 'trạng thái đơn', 'status', 'trạng thái'
    ],
    'product_name': [
        'tên sản phẩm', 'product name', 'tên mặt hàng', 'tên hàng', 'sản phẩm'
    ],
    'variation': [
        'tên phân loại', 'variation', 'tên biến thể', 'phân loại hàng', 
        'tên phân loại hàng', 'biến thể', 'thuộc tính', 'màu sắc/kích thước'
    ],
    'color': [
        'màu', 'màu sắc', 'color'
    ],
    'size': [
        'size', 'kích thước', 'kích cỡ'
    ],
    'sku': [
        'mã sku người bán', 'seller sku', 'mã sku', 'sku', 'mã sản phẩm', 
        'sku người bán', 'seller_sku', 'sku sản phẩm'
    ],
    'quantity': [
        'số lượng', 'quantity', 'sl', 'số lượng mua', 'qty', 'áo'
    ],
    'recipient': [
        'người nhận', 'recipient', 'tên người nhận', 'tên người mua', 
        'người mua', 'khách hàng', 'tên khách hàng', 'buyer username'
    ],
    'phone': [
        'số điện thoại', 'phone #', 'phone number', 'sđt', 'số đt', 'số đt người nhận', 'phone'
    ],
    'address': [
        'địa chỉ chi tiết', 'detail address', 'địa chỉ', 'địa chỉ nhận hàng', 
        'địa chỉ giao hàng', 'địa chỉ người nhận'
    ],
    'tracking_id': [
        'mã vận đơn', 'tracking id', 'mã bưu gửi', 'tracking number', 'tracking code'
    ],
    'carrier': [
        'đơn vị vận chuyển', 'shipping provider name', 'đvvc', 'nhà vận chuyển', 'kênh vận chuyển'
    ],
    'created_time': [
        'thời gian tạo', 'created time', 'ngày đặt hàng', 'thời gian tạo đơn', 'ngày tạo'
    ]
}

def clean_col_name(c):
    return str(c).strip().lower()

def identify_columns(df):
    """
    Tự động nhận diện và map các cột trong DataFrame theo từ điển chuẩn
    """
    col_map = {}
    cleaned_cols = {col: clean_col_name(col) for col in df.columns}
    
    for standard_key, aliases in COL_ALIASES.items():
        found = None
        for orig_col, c_clean in cleaned_cols.items():
            if c_clean in aliases:
                found = orig_col
                break
        if not found:
            for orig_col, c_clean in cleaned_cols.items():
                if any(alias in c_clean for alias in aliases):
                    found = orig_col
                    break
        if found:
            col_map[standard_key] = found

    return col_map

def extract_color_and_size(v):
    """
    Tách 'Màu' và 'Size' từ chuỗi phân loại hàng (Variation) của TikTok Shop / Shopee.
    Ví dụ:
    - 'Kem - Cổ Nâu, L' -> Màu: 'Kem - Cổ Nâu', Size: 'L'
    - 'Đen, L' -> Màu: 'Đen', Size: 'L'
    - 'Hồng Pastel Chữ Đỏ, L' -> Màu: 'Hồng Pastel Chữ Đỏ', Size: 'L'
    - 'Donut-Đen Chữ Trắng, S' -> Màu: 'Donut-Đen Chữ Trắng', Size: 'S'
    - 'Đen, L (Premium)' -> Màu: 'Đen', Size: 'L (Premium)'
    - 'Kem Cổ Navy - Size L' -> Màu: 'Kem Cổ Navy', Size: 'L'
    """
    if not v or pd.isna(v):
        return "", ""
    v = str(v).strip()
    
    # 1. Dấu phẩy phân tách
    if ',' in v:
        parts = [p.strip() for p in v.split(',')]
        if len(parts) == 2:
            c, s = parts[0], parts[1]
            if s.lower().startswith('size '):
                s = s[5:].strip()
            return c, s
        return ", ".join(parts[:-1]), parts[-1]
        
    # 2. Dấu gạch chéo
    if ' / ' in v:
        parts = [p.strip() for p in v.split(' / ')]
        return parts[0], parts[1]
        
    # 3. Phân tách "- Size "
    if ' - size ' in v.lower():
        idx = v.lower().find(' - size ')
        return v[:idx].strip(), v[idx + 8:].strip()
        
    # 4. Phân tách dấu gạch ngang mà phần đuôi là size
    size_keywords = {'s', 'm', 'l', 'xl', '2xl', '3xl', '4xl', 'xxl', 'xxxl', 'freesize', 'free size'}
    if ' - ' in v:
        parts = [p.strip() for p in v.split(' - ')]
        last_part = parts[-1]
        clean_last = last_part.lower().split(' ')[0]
        if clean_last in size_keywords or last_part.lower() in size_keywords or 'premium' in last_part.lower():
            return " - ".join(parts[:-1]), last_part
            
    return v, ""

def read_order_file(uploaded_file):
    """
    Đọc file Excel hoặc CSV một cách linh hoạt, xử lý mã hóa tiếng Việt
    """
    if uploaded_file is None:
        return None
    
    filename = getattr(uploaded_file, 'name', 'file.xlsx')
    
    try:
        if filename.endswith('.csv'):
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"Không thể đọc file {filename}: {str(e)}")

    df = df.dropna(how='all').reset_index(drop=True)
    return df

def process_orders(df_current, df_previous=None, filter_by_phone=False):
    """
    Xử lý logic cốt lõi:
    1. Nhận diện cột
    2. Tách Màu & Size
    3. Lọc trùng với ca trước
    4. Lọc trùng lặp dòng trong cùng ca
    5. Tổng hợp bảng kê soạn hàng (Pick List)
    """
    if df_current is None or len(df_current) == 0:
        return None

    # Nhận diện cột file ca hiện tại
    col_map_curr = identify_columns(df_current)
    order_id_col = col_map_curr.get('order_id')
    
    if not order_id_col:
        raise ValueError("Không tìm thấy cột 'Mã đơn hàng' (Order ID) trong file ca hiện tại. Vui lòng kiểm tra lại file!")

    df_curr_work = df_current.copy()
    df_curr_work['_norm_order_id'] = df_curr_work[order_id_col].astype(str).str.strip()
    
    # Chuẩn hóa cột số lượng
    qty_col = col_map_curr.get('quantity')
    if qty_col and qty_col in df_curr_work.columns:
        df_curr_work['_norm_quantity'] = pd.to_numeric(df_curr_work[qty_col], errors='coerce').fillna(1).astype(int)
    else:
        df_curr_work['_norm_quantity'] = 1

    # Chuẩn hóa các cột thông tin sản phẩm
    prod_col = col_map_curr.get('product_name')
    var_col = col_map_curr.get('variation')
    sku_col = col_map_curr.get('sku')
    color_col = col_map_curr.get('color')
    size_col = col_map_curr.get('size')
    phone_col = col_map_curr.get('phone')
    recip_col = col_map_curr.get('recipient')
    carrier_col = col_map_curr.get('carrier')
    tracking_col = col_map_curr.get('tracking_id')

    df_curr_work['_norm_product'] = df_curr_work[prod_col].astype(str).str.strip() if prod_col else "Chưa có tên SP"
    df_curr_work['_norm_variation'] = df_curr_work[var_col].astype(str).str.strip() if var_col else ""
    df_curr_work['_norm_sku'] = df_curr_work[sku_col].astype(str).str.strip() if sku_col else "N/A"
    df_curr_work['_norm_recipient'] = df_curr_work[recip_col].astype(str).str.strip() if recip_col else "Khách hàng"
    df_curr_work['_norm_phone'] = df_curr_work[phone_col].astype(str).str.strip() if phone_col else ""
    df_curr_work['_norm_carrier'] = df_curr_work[carrier_col].astype(str).str.strip() if carrier_col else "Tiêu chuẩn"
    df_curr_work['_norm_tracking'] = df_curr_work[tracking_col].astype(str).str.strip() if tracking_col else ""

    # Tách Màu và Size
    if color_col and size_col and color_col in df_curr_work.columns and size_col in df_curr_work.columns:
        df_curr_work['_norm_color'] = df_curr_work[color_col].astype(str).str.strip()
        df_curr_work['_norm_size'] = df_curr_work[size_col].astype(str).str.strip()
    else:
        parsed = df_curr_work['_norm_variation'].apply(extract_color_and_size)
        df_curr_work['_norm_color'] = [p[0] for p in parsed]
        df_curr_work['_norm_size'] = [p[1] for p in parsed]

    # Tập hợp các Mã đơn và SĐT từ ca trước (nếu có)
    prev_order_ids = set()
    prev_phones = set()
    if df_previous is not None and len(df_previous) > 0:
        col_map_prev = identify_columns(df_previous)
        prev_order_col = col_map_prev.get('order_id')
        if prev_order_col:
            prev_order_ids = set(df_previous[prev_order_col].astype(str).str.strip().unique())
        if filter_by_phone:
            prev_phone_col = col_map_prev.get('phone')
            if prev_phone_col:
                prev_phones = set(df_previous[prev_phone_col].astype(str).str.strip().unique())

    # Đánh dấu đơn trùng
    duplicate_rows = []
    valid_rows = []
    seen_order_ids = set()
    seen_row_signatures = set()

    for idx, row in df_curr_work.iterrows():
        oid = row['_norm_order_id']
        phone = row['_norm_phone']
        sku = row['_norm_sku']
        color = row['_norm_color']
        size = row['_norm_size']
        
        row_sig = (oid, sku, color, size)

        # 1. Kiểm tra trùng với ca trước
        if oid in prev_order_ids:
            row_dup = row.copy()
            row_dup['Lý do trùng'] = 'Đã có trong file ca trước'
            duplicate_rows.append(row_dup)
            continue
        
        # Kiểm tra trùng SĐT nếu bật tùy chọn
        if filter_by_phone and phone and phone in prev_phones:
            row_dup = row.copy()
            row_dup['Lý do trùng'] = f'Trùng số điện thoại ca trước ({phone})'
            duplicate_rows.append(row_dup)
            continue

        # 2. Kiểm tra trùng dòng trong chính ca hiện tại
        if row_sig in seen_row_signatures:
            row_dup = row.copy()
            row_dup['Lý do trùng'] = 'Dòng sản phẩm bị lặp lại trong cùng ca'
            duplicate_rows.append(row_dup)
            continue

        seen_row_signatures.add(row_sig)
        seen_order_ids.add(oid)
        valid_rows.append(row)

    df_valid = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=df_curr_work.columns)
    df_dup = pd.DataFrame(duplicate_rows) if duplicate_rows else pd.DataFrame(columns=list(df_curr_work.columns) + ['Lý do trùng'])

    # Tổng hợp thống kê
    total_raw_rows = len(df_curr_work)
    total_raw_orders = df_curr_work['_norm_order_id'].nunique()
    
    dup_orders_count = df_dup['_norm_order_id'].nunique() if not df_dup.empty else 0
    valid_orders_count = df_valid['_norm_order_id'].nunique() if not df_valid.empty else 0
    total_valid_items = df_valid['_norm_quantity'].sum() if not df_valid.empty else 0

    # 3. Tạo Bảng Gom Hàng (Pick List chuẩn 4 cột: SKU sản phẩm, Màu, Size, Áo)
    if not df_valid.empty:
        pick_list = df_valid.groupby(
            ['_norm_sku', '_norm_color', '_norm_size'], as_index=False
        ).agg(
            Số_Lượng=('_norm_quantity', 'sum'),
            Số_Đơn_Hàng=('_norm_order_id', 'nunique')
        ).sort_values(by=['_norm_sku', '_norm_color', '_norm_size'], ascending=True).reset_index(drop=True)
        
        pick_list.rename(columns={
            '_norm_sku': 'SKU sản phẩm',
            '_norm_color': 'Màu',
            '_norm_size': 'Size',
            'Số_Lượng': 'Áo',
            'Số_Đơn_Hàng': 'Số đơn hàng'
        }, inplace=True)
    else:
        pick_list = pd.DataFrame(columns=['SKU sản phẩm', 'Màu', 'Size', 'Áo', 'Số đơn hàng'])

    # Chuẩn bị bảng chi tiết đơn hợp lệ hiển thị người dùng
    display_valid = pd.DataFrame()
    if not df_valid.empty:
        display_valid = df_valid[[
            '_norm_order_id', '_norm_sku', '_norm_color', '_norm_size', 
            '_norm_quantity', '_norm_recipient', '_norm_phone', 
            '_norm_carrier', '_norm_tracking'
        ]].copy()
        display_valid.columns = [
            'Mã đơn hàng', 'SKU sản phẩm', 'Màu', 'Size', 
            'Áo', 'Người nhận', 'Số điện thoại', 
            'Đơn vị VC', 'Mã vận đơn'
        ]

    # Chuẩn bị bảng đơn trùng hiển thị
    display_dup = pd.DataFrame()
    if not df_dup.empty:
        dup_cols = ['_norm_order_id', '_norm_sku', '_norm_color', '_norm_size', '_norm_quantity', 'Lý do trùng']
        display_dup = df_dup[dup_cols].copy()
        display_dup.columns = ['Mã đơn hàng', 'SKU', 'Màu', 'Size', 'Áo', 'Lý do loại bỏ']

    metrics = {
        'total_raw_rows': total_raw_rows,
        'total_raw_orders': total_raw_orders,
        'prev_orders_count': len(prev_order_ids),
        'dup_orders_count': dup_orders_count,
        'valid_orders_count': valid_orders_count,
        'total_valid_items': int(total_valid_items),
        'unique_skus_count': pick_list['SKU sản phẩm'].nunique() if not pick_list.empty else 0
    }

    return {
        'metrics': metrics,
        'df_valid': df_valid,
        'display_valid': display_valid,
        'df_dup': df_dup,
        'display_dup': display_dup,
        'pick_list': pick_list,
        'col_map': col_map_curr
    }
