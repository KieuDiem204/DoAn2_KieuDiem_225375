"""
setup.py — Script thiết lập ban đầu cho TravelBot.
Kiểm tra cấu trúc, download dependencies, và chạy data_processing pipeline.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def check_env():
    """Kiểm tra .env file có GROQ_API_KEY."""
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        print("⚠️  File .env chưa tồn tại.")
        print("    Tạo file .env và thêm: GROQ_API_KEY=gsk_xxxxxxxxxxxx")
        print("    Lấy API key tại: https://console.groq.com\n")
        return False
    else:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        key = os.getenv("GROQ_API_KEY", "")
        if key and key != "your_groq_api_key_here":
            print("✅ GROQ_API_KEY đã được đặt.")
            return True
        else:
            print("⚠️  GROQ_API_KEY chưa hợp lệ trong .env")
            return False


def check_data():
    """Kiểm tra CSV files."""
    from config import DATA_FILES
    
    print("\n📁 Kiểm tra dữ liệu:")
    found_any = False
    found_files = []
    
    for name, path in DATA_FILES.items():
        if os.path.exists(path):
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"  ✅ {name}: {path} ({size_mb:.1f} MB)")
                found_any = True
                found_files.append(name)
            except Exception as e:
                print(f"  ⚠️  {name}: {path} — lỗi: {e}")
        else:
            print(f"  ⚠️  {name}: {path} — không tìm thấy")
    
    if not found_any:
        print("\n  ❌ Không tìm thấy file dữ liệu nào!")
        print("      Tải về từ các nguồn:")
        print("      - https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data")
        print("      - https://www.kaggle.com/datasets/pavelstefanovi/travel-dataset")
        print("      - https://www.kaggle.com/datasets/leomauro/argodatathon2019")
        print("      Đặt vào thư mục: data/")
        return False
    
    print(f"\n  ✅ Tìm thấy {len(found_files)} file dữ liệu: {', '.join(found_files)}")
    return True


def check_artifacts():
    """Kiểm tra artifacts đã build chưa."""
    artifacts_dir = os.path.join(BASE_DIR, "artifacts")
    files_needed = ["tfidf_matrix.pkl", "tfidf_vectorizer.pkl", "embeddings_cache.pkl"]

    print("\n📦 Kiểm tra artifacts:")
    all_ok = True
    for f in files_needed:
        fpath = os.path.join(artifacts_dir, f)
        if os.path.exists(fpath):
            try:
                size_kb = os.path.getsize(fpath) / 1024
                print(f"  ✅ {f} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"  ⚠️  {f} — lỗi: {e}")
                all_ok = False
        else:
            print(f"  ❌ {f} — chưa tạo")
            all_ok = False

    return all_ok


def build_artifacts():
    """Chạy data_processing để build all artifacts."""
    print("\n🔨 Đang build artifacts...")
    print("=" * 50)
    try:
        from data_processing import build_all
        build_all()
        print("=" * 50)
        print("\n✅ Build artifacts thành công!")
        return True
    except Exception as e:
        print("=" * 50)
        print(f"\n❌ Build thất bại: {e}")
        print("\nGợi ý khắc phục:")
        print("  1. Kiểm tra các file CSV trong thư mục data/ có hợp lệ không")
        print("  2. Kiểm tra encoding của file CSV (UTF-8, Latin1, etc.)")
        print("  3. Đảm bảo các file CSV có cột 'Question' và 'Answer'")
        print("  4. Chạy lại: python setup.py")
        return False


def print_usage():
    """In hướng dẫn sử dụng."""
    print("\n" + "=" * 60)
    print("🌏  TRAVELBOT — Trợ lý AI Du Lịch")
    print("=" * 60)
    print("\n📋 Cách chạy ứng dụng:")
    print("   streamlit run main.py")
    print("\n📋 Cấu trúc dự án:")
    print("   ├── main.py              # Streamlit frontend")
    print("   ├── config.py            # Cấu hình hệ thống")
    print("   ├── data_processing.py   # Xử lý CSV, build index")
    print("   ├── recommendation.py    # Hệ thống tra cứu")
    print("   ├── image_classifier.py  # Phân loại địa điểm từ ảnh (CLIP)")
    print("   ├── groq_client.py       # Tích hợp Groq LLM API")
    print("   ├── translation.py       # Đa ngôn ngữ Vi/En")
    print("   ├── setup.py             # Script thiết lập")
    print("   ├── requirements.txt     # Dependencies")
    print("   ├── .env                 # API Keys (GROQ_API_KEY)")
    print("   ├── data/")
    print("   │   ├── flights.csv")
    print("   │   ├── hotels.csv")
    print("   │   ├── tourism_dataset.csv")
    print("   │   └── ... (các CSV files khác)")
    print("   └── artifacts/           # Cached models & indexes")
    print("       ├── tfidf_matrix.pkl")
    print("       ├── tfidf_vectorizer.pkl")
    print("       └── embeddings_cache.pkl")
    print("\n📋 Bước thiết lập:")
    print("   1. pip install -r requirements.txt")
    print("   2. Tạo .env, đặt GROQ_API_KEY=gsk_xxxx")
    print("   3. Tải CSV files vào data/")
    print("   4. python setup.py          # Build artifacts")
    print("   5. streamlit run main.py    # Chạy app")
    print("\n📋 Tính năng:")
    print("   ✅ Nhận dạng địa điểm du lịch từ ảnh")
    print("   ✅ Tư vấn điểm đến, lịch trình, chi phí")
    print("   ✅ Tìm kiếm vé máy bay, khách sạn")
    print("   ✅ Hỗ trợ đa ngôn ngữ (Tiếng Việt/English)")
    print("   ✅ Tra cứu thông tin từ nhiều nguồn dữ liệu")
    print("\n" + "=" * 60)


def main():
    print("🌏  TRAVELBOT — Setup & Validation")
    print("-" * 40)

    # Check environment
    env_ok = check_env()
    
    # Check data files
    data_ok = check_data()
    
    # Check artifacts
    artifacts_ok = check_artifacts()

    if not artifacts_ok and data_ok:
        print("\n💡 Artifacts chưa đầy đủ. Bạn muốn build ngay bây giờ? (y/n)")
        choice = input("   > ").strip().lower()
        if choice in ("y", "yes", ""):
            build_ok = build_artifacts()
            if build_ok:
                artifacts_ok = True
        else:
            print("   Bỏ qua build. Chạy 'python setup.py' sau khi có dữ liệu.")
    elif not data_ok:
        print("\n❌ Không đủ file dữ liệu để build artifacts.")
        print("   Bạn cần có ít nhất 1 file CSV hợp lệ trong thư mục data/")
    elif artifacts_ok:
        print("\n✅ Tất cả artifacts đã sẵn sàng!")

    print_usage()


if __name__ == "__main__":
    main()