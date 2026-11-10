# NHẬT KÝ SỬ DỤNG AI (AI-USE LOG)
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** Nhóm 07  

---

| Công cụ / Model | Mục đích sử dụng | Phạm vi (File / Module) | Phương pháp kiểm chứng | Quyết định của nhóm | Người chịu trách nhiệm (Reviewer) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemini / ChatGPT** (Gemini 1.5 Pro) | Hỗ trợ cấu trúc hóa tài liệu phân tích, gợi ý định dạng Markdown cho các file báo cáo và tư vấn logic test cases. | `artifacts/` (REQUIREMENTS.md, TEST_PLAN.md) | Kiểm tra chéo thủ công với tài liệu đặc tả chính thức `docs/decision-table.md` và issue #15. | Giữ lại cấu trúc, tinh chỉnh lại câu chữ cho sát với đặc tả thực tế của giảng viên. | Vũ Ngọc Quang |
| **GitHub Copilot** | Gợi ý cú pháp viết unit test tự động bằng `pytest`. | `tests/test_classifier.py` | Chạy lệnh `pytest -q` kiểm tra tính đúng đắn và đối chiếu kết quả kỳ vọng. | Chấp thuận một phần, tự viết bổ sung các ca ranh giới (boundary cases). | Trần Minh Quân |