import numpy as np
import pandas as pd

def generate_strategy(df, stoploss_pct=0.07):

    df = df.copy()

    # =========================
    # 1️⃣ MA50 cross up
    # =========================
    df["MA50"] = df["close"].rolling(50).mean()

    df["MA50_Cross_Up"] = (
        (df["close"] > df["MA50"]) &
        (df["close"].shift(1) <= df["MA50"].shift(1))
    ).astype(int)

    # =========================
    # 2️⃣ Break 60-day high
    # =========================
    df["High_60"] = df["high"].rolling(60).max().shift(1)
    df["Breakout"] = (df["close"] > df["High_60"]).astype(int)

    # =========================
    # 3️⃣ Volume condition
    # =========================
    df["Vol_MA20"] = df["volume"].rolling(20).mean()
    df["Volume_OK"] = (df["volume"] > 1.5 * df["Vol_MA20"]).astype(int)

    # =========================
    # 4️⃣ Exit indicator (MA50)
    # =========================
    df["MA50"] = df["close"].rolling(50).mean()
    df["MA50_Break"] = (df["close"] < df["MA50"]).astype(int)

    # =========================
    # 5️⃣ Score = tổng 3 điều kiện
    # =========================
    df["Score"] = (
        df["MA50_Cross_Up"] +
        df["Breakout"] +
        df["Volume_OK"]
    )

    df["Buy_Condition"] = (df["Score"] >= 2).astype(int)

    # =========================
    # 6️⃣ Generate Signals
    # =========================
    position = 0
    entry_price = 0
    signals = []

    for i in range(len(df)):

        if position == 0:
            if df.loc[i, "Buy_Condition"] == 1:
                position = 1
                entry_price = df.loc[i, "close"]
                signals.append(1)
            else:
                signals.append(0)

        elif position == 1:
            current_price = df.loc[i, "close"]

            stoploss_hit = current_price <= entry_price * (1 - stoploss_pct)
            ma50_break = df.loc[i, "MA50_Break"] == 1

            if  ma50_break:
                position = 0
                signals.append(-1)
            else:
                signals.append(0)

    df["Signal"] = signals

    return df.dropna().reset_index(drop=True)