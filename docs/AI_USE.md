# AI_USE — Khai báo sử dụng AI

> Nhóm: `[mã nhóm / alias]` · Theo Mục 5.3 của đề (chính sách `ai-allowed`).
> Không ghi secret hay thông tin cá nhân vào file này. Dùng MSSV, không ghi họ tên.

| # | Công cụ / model | Mục đích | Phạm vi (file/module) | Kiểm chứng | Quyết định của nhóm | Người chịu trách nhiệm |
|---|---|---|---|---|---|---|
| 1 | Claude (claude.ai) | Giải thích đề, bảng quyết định và quy trình nộp bài | Không tạo file trong repo | Đối chiếu trực tiếp với đề thi và `decision-table.md` | Giữ phần giải thích đúng với đề | `[MSSV]` |
| 2 | Claude (claude.ai) | Soạn **bản nháp** `REQUIREMENTS.md` | `REQUIREMENTS.md` | `[điền: nhóm tự tính tay các ca biên AC-09…AC-18, đối chiếu từng FR với decision-table.md]` | `[điền: phần giữ, phần sửa, phần loại]` | `[MSSV]` |
| 3 | Claude (claude.ai) | Soạn **bản nháp** `TEST_PLAN.md` | `TEST_PLAN.md` | `[điền: nhóm rà lại từng AC có test tương ứng]` | `[điền]` | `[MSSV]` |
| 4 | Claude (claude.ai) | Soạn **bản nháp** `DECISIONS.md` (ADR-001, ADR-002) | `DECISIONS.md` | `[điền: nhóm đọc lại và đồng ý hoặc sửa lý do]` | `[điền]` | `[MSSV]` |

## Ghi chú
- Mọi nội dung do AI soạn đều là bản nháp; nhóm đã đọc, hiểu và chịu trách nhiệm trước khi nộp.
- Các giả định về điểm đặc tả chưa rõ (Q-01…Q-06) đã được gửi hỏi TA; kết quả sẽ cập nhật vào `DECISIONS.md`.
- File này sẽ được cập nhật khi nhóm dùng AI cho phần code, test và tài liệu về sau.
