# Phân tích code đã giải mã (Decoded Analysis)

## Tổng quan

File `tooldamemahoa_2877.txt` chứa một công cụ JavaScript đã bị **obfuscate (mã hóa)** bằng kỹ thuật **VM-based bytecode** (tương tự JScrambler). Code gốc được biên dịch thành bytecode tùy chỉnh và chạy trên một máy ảo (Virtual Machine) JavaScript tự xây dựng.

## Kỹ thuật mã hóa được sử dụng

| Kỹ thuật | Mô tả |
|----------|--------|
| **VM Interpreter** | `vmN_cf2ba9` - Trình thông dịch bytecode tùy chỉnh |
| **Global State Proxy** | `vmI_750bb6` - Proxy toàn bộ global objects (document, window, etc.) |
| **Bytecode Encoding** | Chuỗi Base64 chứa bảng string + opcodes |
| **Variable Mangling** | Tên biến dạng `_0x...` (hex) |
| **Control Flow Flattening** | Async generator pattern phức tạp |

## Tool gì?

Đây là **Facebook Auto Report Tool** - công cụ tự động báo cáo (report) profile Facebook.

### Thông tin tác giả
- **Tên**: Lê Hoàng Anh Kiệt
- **Telegram**: @AKIOS999
- **Giá bán**: 100K VND (bản quyền VIP)

## Chức năng chính

### 1. Giao diện UI (Floating Menu)
- Menu nổi góc phải màn hình (style hacker: xanh lá trên nền đen)
- Bộ đếm thời gian (rainbow animation)
- Các cài đặt:
  - **Tốc độ nhấp** (ms delay giữa các click)
  - **Số vòng chạy** (lặp lại bao nhiêu lần)
  - **Nghỉ giữa các vòng** (phút)
  - **Chuông báo động** khi account bị die

### 2. Tự động hóa quy trình Report
Tool tự động điều hướng qua các bước report của Facebook:

```
Bước 1: Click "Report profile"
Bước 2: Chọn lý do report (từ danh sách)
Bước 3: Click "Next"
Bước 4: Dò tìm "Meta" (cho account VIP/verified)
Bước 5: Điền URL (nếu cần)
Bước 6: Click "Submit"
Bước 7: Click "Done"
```

### 3. Lý do report được hỗ trợ
- Something about this profile
- Fake profile
- They're not a real person
- A celebrity or public figure
- Credible threat to safety
- Violent, hateful or disturbing content
- Scam, fraud or false information
- Fraud or scam
- Spam
- Physical abuse
- Problem involving someone under 18
- Something else

### 4. Tính năng đặc biệt
- **Meta/VIP Detection**: Radar tìm kiếm option "Meta" trong listbox (dành cho account verified)
- **Fuzzy Matching**: Khi text không khớp chính xác, dùng fuzzy search trong DOM
- **Click Simulation**: Mô phỏng mouse events đầy đủ (mousedown → mousemove → mouseup → click)
- **Keyboard Simulation**: Mô phỏng keydown/keypress/keyup cho input fields
- **Audio Alert**: Phát âm thanh cảnh báo khi account bị chặn (Web Audio API - square wave)
- **XPath Navigation**: Dùng XPath để tìm chính xác các element trên Facebook
- **Error Handling**: Phát hiện "Sorry, something went wrong" và dừng tự động

### 5. Global Objects được proxy
Tool chặn và proxy các global objects sau qua `vmI_750bb6`:
- `document`, `window`, `Promise`, `setTimeout`, `setInterval`
- `XPathResult`, `console`, `MouseEvent`, `KeyboardEvent`
- `Math`, `Date`, `Object`, `Event`
- `clearInterval`, `parseInt`, `parseFloat`, `isNaN`, `alert`

## File đã giải mã

Xem file `decoded_auto_report_tool.js` để đọc phiên bản đã được tái cấu trúc (reconstructed) từ bytecode.

> **Lưu ý**: Đây là bản tái cấu trúc logic từ các chuỗi và cấu trúc bytecode đã giải mã. Không phải 100% chính xác từng dòng code gốc (vì bytecode VM rất khó reverse hoàn toàn), nhưng logic và chức năng là chính xác.
