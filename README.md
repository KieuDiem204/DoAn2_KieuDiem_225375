CÁC CHỨC NĂNG CHÍNH ĐÃ XÂY DỰNG ĐƯỢC NHƯ SAU : link chạy :https://doan2kieudiem225375-4tevahcmswzqgsv5haks2p.streamlit.app/

1. Tư vấn điểm đến cụ thể

Tổng quan địa điểm
Thời điểm lý tưởng để đi
Chi phí ước tính (khách sạn, ăn uống, đi lại)
Các địa điểm tham quan nổi bật
Đặc sản ẩm thực
Lưu ý thực tế khi đến

2. Lập lịch trình chi tiết
   Khi hỏi "Lên kế hoạch 3 ngày ở Sa Pa", bot tạo lịch trình từng ngày: sáng đi đâu, chiều làm gì, tối ở đâu ăn gì.

3. Phân tích chi phí
   Khi hỏi "Đi Phú Quốc hết bao nhiêu tiền?", bot đưa ra chi phí cụ thể từ dữ liệu thực tế:
   Chi phí lưu trú trung bình
   Chi phí di chuyển
   Tổng chi phí ước tính cho chuyến đi

4. So sánh điểm đến
   Khi hỏi "Nên đi Đà Nẵng hay Nha Trang?", bot tạo bảng so sánh theo các tiêu chí: chi phí, bãi biển, hoạt động, phù hợp với ai.

5. Gợi ý theo ngân sách
   Khi hỏi "Điểm đến budget dưới $500" hay "Đi đâu 5 ngày mà rẻ?", bot xếp hạng và gợi ý các điểm đến phù hợp với túi tiền.

6. Tư vấn khách sạn & lưu trú
   Khi hỏi "Ở đâu khi đến Hà Nội?", bot gợi ý khu vực nên ở, loại hình lưu trú (resort, homestay, khách sạn), tên khách sạn cụ thể và mức giá.

7. Nhận diện địa điểm từ ảnh
   Khi upload ảnh một địa điểm, bot nhận diện đó là nơi nào (ví dụ: Vịnh Hạ Long, Hội An, Bali...) rồi tự động tư vấn chi tiết về điểm đến đó.

8. Nhớ ngữ cảnh cuộc trò chuyện

=============================================================================

\*ẢNH CHATBOT SAU KHI CHẠY :

# KHI NHẬN DIỆN TỪ ẢNH :

<p align="center">
  <img src="/Screen/1.png" width="800">
</p>

# TƯ VẤN CỤ THỂ : 

<p align="center">
  <img src="/Screen/2.png" width="800">
</p>

# CHẲNG HẠN NHƯ TƯ VẤN KHI HỎI GỢI Ý KHÁCH SẠN :

<p align="center">
  <img src="/Screen/3.png" width="800">
</p>

# LÊN KẾ HOẠCH CHO CHUYẾN ĐI  : 

<p align="center">
  <img src="/Screen/4.png" width="800">
</p>

## \*LUỒNG HOẠT ĐỘNG CỤ THỂ :

Người dùng gửi câu hỏi (+ ảnh tùy chọn)
↓
[Nếu có ảnh] → CLIP phân loại địa điểm
↓
Hybrid Retrieval → Tìm top-5 Q&A liên quan từ database
↓
Groq LLM nhận context → Sinh câu trả lời
↓
Hiển thị kết quả trong giao diện chat

=============================================================================

# KIẾN TRÚC TỔNG QUAN :

Kiến trúc tổng thểHệ thống gồm 8 file Python hoạt động phối hợp với nhau:

- config.py — Trung tâm cấu hình, định nghĩa tất cả đường dẫn file, API keys, tên model, ngưỡng embedding. Mọi module khác import từ đây, đảm bảo thay đổi cấu hình chỉ cần sửa một chỗ.
- data_engine.py — Tầng đọc và xử lý dữ liệu thô từ CSV/XLSX. Đây là nơi dữ liệu thực tế được trích xuất và cấu trúc hóa trước khi đưa vào LLM.
- data_processing.py — Xây dựng knowledge base và các artifact phục vụ tìm kiếm (TF-IDF matrix, embeddings, label encoder).
- recommendation.py — Engine tìm kiếm ngữ nghĩa kết hợp TF-IDF + sentence embeddings.
- groq_client.py — Giao tiếp với Groq LLM API, quản lý conversation history, xây dựng prompt.
- image_classifier.py — Nhận diện địa điểm từ ảnh bằng CLIP model.
- translation.py — Phát hiện ngôn ngữ và hỗ trợ đa ngôn ngữ Vi/En.
- main.py — Giao diện Streamlit, điều phối toàn bộ luồng xử lý.

=============================================================================

- Nguồn các tập dữ liệu :
- https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data
- https://www.kaggle.com/datasets/pavelstefanovi/travel-dataset
- https://www.kaggle.com/datasets/leomauro/argodatathon2019
- https://www.kaggle.com/datasets/aravindanr22052001/travelcsv
- https://www.kaggle.com/datasets/umeradnaan/tourism-dataset
- https://www.kaggle.com/datasets/jacopoferretti/expedia-travel-dataset
- https://www.kaggle.com/datasets/saketk511/travel-dataset-guide-to-indias-must-see-places

---

```

```
