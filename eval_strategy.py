import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_all_strategies(base_folder='output'):
    """
    Quét toàn bộ các thư mục chiến lược, đọc file CSV và tổng hợp các chỉ số hiệu suất.
    """
    # Tìm tất cả các file có tên chứa 'summary' và kết thúc bằng '.csv'
    search_pattern = os.path.join(base_folder, '*', 'summary*.csv')
    csv_files = glob.glob(search_pattern)
    
    if not csv_files:
        print(f"⚠️ Không tìm thấy file CSV nào trong thư mục {base_folder}/<strategy_name>/")
        return
    
    all_data = []
    
    # Đọc và gộp dữ liệu
    for file in csv_files:
        # Lấy tên thư mục cha (ví dụ: 'strategy1') làm tên chiến lược
        strategy_name = os.path.basename(os.path.dirname(file))
        
        try:
            df = pd.read_csv(file)
            df['Strategy'] = strategy_name
            # Tính thêm cột: Chiến lược có thắng được Buy & Hold trên mã này không?
            df['Beat_B&H'] = (df['Total Return %'] > df['Buy & Hold %']).astype(int)
            all_data.append(df)
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file}: {e}")
            
    # Gộp thành 1 DataFrame duy nhất
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # ==========================================
    # CHẤM ĐIỂM & TỔNG HỢP THEO TỪNG CHIẾN LƯỢC
    # ==========================================
    leaderboard = combined_df.groupby('Strategy').agg(
        Avg_Total_Return=('Total Return %', 'mean'),
        Avg_Win_Rate=('Win Rate %', 'mean'),
        Worst_Max_Drawdown=('Max Drawdown %', 'min'), # Lấy mức sụt giảm tệ nhất
        Total_Trades=('Number of Trades', 'sum'),
        Beat_BH_Count=('Beat_B&H', 'sum'),
        Total_Stocks=('Stock', 'count')
    ).reset_index()
    
    # Tính tỉ lệ % số mã mà chiến lược chiến thắng Buy & Hold
    leaderboard['Beat_BH_Rate (%)'] = (leaderboard['Beat_BH_Count'] / leaderboard['Total_Stocks']) * 100
    
    # Sắp xếp xếp hạng theo Lợi nhuận trung bình giảm dần
    leaderboard = leaderboard.sort_values(by='Avg_Total_Return', ascending=False).round(2)
    
    print("\n🏆 BẢNG XẾP HẠNG CHIẾN LƯỢC TỔNG THỂ 🏆")
    print("-" * 80)
    print(leaderboard.to_string(index=False))
    print("-" * 80)
    
    # ==========================================
    # VẼ BIỂU ĐỒ SO SÁNH TRỰC QUAN
    # ==========================================
    plot_strategy_comparison(leaderboard)
    
    return leaderboard, combined_df

def plot_strategy_comparison(leaderboard_df):
    """Vẽ biểu đồ so sánh Lợi nhuận và Drawdown giữa các chiến lược"""
    # Đặt style cho biểu đồ
    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Trục chính: Cột Lợi nhuận trung bình (Màu xanh)
    sns.barplot(
        data=leaderboard_df, 
        x='Strategy', 
        y='Avg_Total_Return', 
        color='mediumseagreen', 
        ax=ax1, 
        label='Lợi nhuận TB (%)'
    )
    ax1.set_ylabel('Average Total Return (%)', color='mediumseagreen', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='mediumseagreen')

    # Trục phụ: Đường Max Drawdown tệ nhất (Màu đỏ)
    ax2 = ax1.twinx()
    sns.lineplot(
        data=leaderboard_df, 
        x='Strategy', 
        y='Worst_Max_Drawdown', 
        color='crimson', 
        marker='o', 
        linewidth=2.5, 
        markersize=8,
        ax=ax2, 
        label='Max Drawdown Tệ nhất (%)'
    )
    ax2.set_ylabel('Worst Max Drawdown (%)', color='crimson', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='crimson')

    # Căn chỉnh tiêu đề và legend
    plt.title('So sánh Lợi nhuận và Rủi ro giữa các Chiến lược', fontsize=14, fontweight='bold', pad=15)
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
    plt.tight_layout()
    plt.show()

# Thực thi hàm
if __name__ == "__main__":
    # Thay 'output' bằng đường dẫn thực tế nếu cần
    leaderboard, full_data = evaluate_all_strategies('output')