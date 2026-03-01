'''
1. Điều kiện để mua: đạt ít nhất 4/6 tín hiệu mua và không có tín hiệu bán nào.
- MA50 cắt lên 
- Đường MA50 dốc lên so với 5 ngày trước 
- Breakout: giá vượt đỉnh của 20 ngày trước 
- Volume breakout: volume > 1.2 * MA20 và giá tăng so với hôm trước
- RSI > 50 và < 70 (vừa có động lượng tăng nhưng chưa quá mua)
- ATR > ATR trung bình 20 ngày (thị trường có biến động đủ lớn)
2. Điều kiện để bán: có ít nhất 2/6 tín hiệu bán hoặc tất cả tín hiệu mua đều mất hiệu lực.
- MA50 cắt xuống 
- Giá đóng cửa thấp xuống dưới đáy 20 ngày trước 
- Đường 50 bẻ cong đi xuống 
- Volume breakout: volume > 1.2 * MA20 và giá giảm so với hôm trước
- RSI < 50 và > 30 (động lượng giảm nhưng chưa quá bán)

'''

import numpy as np

def generate_strategy(df):

    df = df.copy()

    # =========================
    # 1️⃣ MA50
    # =========================
    df["MA50"] = df["close"].rolling(50).mean()

    df["MA_Buy"] = (
        (df["close"] > df["MA50"]) &
        (df["close"].shift(1) <= df["MA50"].shift(1))
    ).astype(int)

    df["MA_Sell"] = (
        (df["close"] < df["MA50"]) &
        (df["close"].shift(1) >= df["MA50"].shift(1))
    ).astype(int)

    # MA50 slope (trend strength)
    df["MA50_slope"] = df["MA50"] - df["MA50"].shift(5)

    df["Trend_Buy"] = (df["MA50_slope"] > 0).astype(int)
    df["Trend_Sell"] = (df["MA50_slope"] < 0).astype(int)

    # =========================
    # 2️⃣ Breakout 20 phiên
    # =========================
    df["High_20"] = df["high"].rolling(20).max().shift(1)
    df["Low_20"] = df["low"].rolling(20).min().shift(1)

    df["Breakout_Buy"] = (df["close"] > df["High_20"]).astype(int)
    df["Breakout_Sell"] = (df["close"] < df["Low_20"]).astype(int)

    # =========================
    # 3️⃣ Volume breakout
    # =========================
    df["Vol_MA20"] = df["volume"].rolling(20).mean()

    df["Volume_Buy"] = (
        (df["volume"] > 1.2 * df["Vol_MA20"]) &
        (df["close"] > df["close"].shift(1))
    ).astype(int)

    df["Volume_Sell"] = (
        (df["volume"] > 1.2 * df["Vol_MA20"]) &
        (df["close"] < df["close"].shift(1))
    ).astype(int)

    # =========================
    # 4️⃣ RSI
    # =========================
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["RSI_Buy"] = ((df["RSI"] > 50) & (df["RSI"] < 70)).astype(int)
    df["RSI_Sell"] = ((df["RSI"] < 50) & (df["RSI"] > 30)).astype(int)

    # =========================
    # 5️⃣ ATR filter (loại thị trường quá yếu)
    # =========================
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    tr = np.maximum(high_low, np.maximum(high_close, low_close))
    df["ATR"] = tr.rolling(14).mean()

    df["ATR_filter"] = (df["ATR"] > df["ATR"].rolling(20).mean()).astype(int)

    # =========================
    # 6️⃣ Score
    # =========================
    df["Score"] = (
        df["MA_Buy"]
        + df["Breakout_Buy"]
        + df["Volume_Buy"]
        + df["RSI_Buy"]
        + df["Trend_Buy"]
        + df["ATR_filter"]
        - df["MA_Sell"]
        - df["Breakout_Sell"]
        - df["Volume_Sell"]
        - df["RSI_Sell"]
        - df["Trend_Sell"]
    )

    df["Signal"] = 0
    df.loc[df["Score"] >= 4, "Signal"] = 1
    df.loc[df["Score"] <= -2, "Signal"] = -1
    # =========================
    # 7️⃣ Enforce alternating Buy/Sell
    # =========================
    # =========================
# 7️⃣ Enforce Buy-first + alternating Buy/Sell
# =========================
    position = 0  # 0 = không nắm giữ, 1 = đang nắm giữ
    final_signals = []

    for sig in df["Signal"]:
        if sig == 1 and position == 0:
            # Chỉ mua khi chưa có vị thế
            final_signals.append(1)
            position = 1

        elif sig == -1 and position == 1:
            # Chỉ bán khi đang nắm giữ
            final_signals.append(-1)
            position = 0

        else:
            # Không làm gì nếu signal không phù hợp với trạng thái
            final_signals.append(0)

    # Đảm bảo lệnh đầu tiên là Buy
    if final_signals[0] == -1:
        final_signals[0] = 0

    df["Signal"] = final_signals

    return df.dropna().reset_index(drop=True)
