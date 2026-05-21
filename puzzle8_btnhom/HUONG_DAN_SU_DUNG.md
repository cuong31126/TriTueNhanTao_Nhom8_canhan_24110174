# Hướng dẫn sử dụng 8-Puzzle Search Visualizer

## Cách chạy

1. Cài `pygame` nếu máy chưa có:

   ```bash
   pip install pygame
   ```

2. Chạy chương trình:

   ```bash
   python main.py
   ```

## Chỉnh bảng Start và Goal

- Bấm chuột vào một ô trong bảng `START` hoặc `GOAL`.
- Nhấn phím số `0` đến `8` để đổi giá trị ô đang chọn.
- Nếu số vừa nhập đã tồn tại trong bảng, chương trình sẽ tự đổi chỗ hai ô để bảng luôn có đủ đúng một lần các số `0..8`.
- Số `0` là ô trống.
- Khi chỉnh bảng, lượt chạy thuật toán hiện tại sẽ được reset để dùng trạng thái mới.

## Các nút chính

- Thanh tab phía trên gồm `BFS`, `DFS`, `DFS L`; mỗi tab chuyển sang nhóm thuật toán riêng.
- Trong tab `BFS`, dùng `BFS M1` để kiểm tra Goal ngay khi sinh child, hoặc `BFS M2` để chỉ kiểm tra Goal khi lấy trạng thái ra khỏi queue.
- Tab `DFS` dùng stack để duyệt DFS, ưu tiên các trạng thái gần Goal hơn để chạy nhanh và tránh đi quá sâu không cần thiết.
- Tab `DFS L` chạy DFS với giới hạn chiều sâu, chỉ đẩy node con khi độ dài đường đi nhỏ hơn giới hạn.
- `Next Step`: chạy đúng một bước của thuật toán đang chọn.
- `Prev Step`: quay lại trạng thái trước đó của lượt chạy.
- `Auto Run`: tự động chạy từng bước.
- `Pause`: dừng Auto Run.
- `Reset`: đưa lượt chạy hiện tại về trạng thái ban đầu.
- `Solve Full`: chạy thuật toán đến khi tìm được lời giải hoặc hết giới hạn.
- `Easy Test`: nạp bộ test dễ.
- `Main Test`: nạp bộ test chính.

## Các vùng hiển thị

- `CURRENT BOARD`: trạng thái vừa được lấy ra xử lý.
- `CHILDREN GENERATED`: các trạng thái con vừa sinh từ bước hiện tại.
- `SEARCH TREE`: mô phỏng cây tìm kiếm cục bộ từ node đang xét, các nhánh dùng ký hiệu `U`, `D`, `L`, `R`; node/nhánh đang xét được tô màu nổi.
- `FRONTIER / QUEUE` hoặc `FRONTIER / STACK`: các trạng thái đang chờ xử lý, hiển thị tối đa 30 phần tử đầu tiên.
- `ALGORITHM INFORMATION`: thống kê bước chạy, kích thước queue/stack, reached, số node đã mở rộng và sinh ra.
- `COMPARISON`: so sánh kết quả giữa Mode 1 và Mode 2 sau khi đã chạy từng mode.
- Với `DFS` và `DFS L`, nếu vượt giới hạn số node mở rộng thì chương trình dừng và báo không tìm thấy lời giải trong giới hạn đó. Đường đi kết quả được hiển thị đầy đủ bằng chuỗi `Len -> Trai -> Xuong -> Phai`.

## Phím tắt

- `Space`: chạy `Next Step`.
- `Home`: cuộn lên đầu.
- `End`: cuộn xuống cuối.
- `Page Up` / `Page Down`: cuộn nhanh.

## So sánh Mode 1 và Mode 2

- **Mode 1 (Kiểm tra khi sinh con - Early Goal Test):** Thuật toán sẽ kiểm tra xem trạng thái con vừa được tạo ra có phải là đích (Goal) hay không. Nếu đúng, chương trình dừng và trả về kết quả ngay lập tức. Cách làm này giúp phát hiện Goal sớm nhất có thể, qua đó giảm lượng trạng thái phải đưa vào hàng đợi, tiết kiệm bộ nhớ và rút ngắn thời gian chạy so với Mode 2.
- **Mode 2 (Kiểm tra khi lấy khỏi queue - Late Goal Test):** Các trạng thái con sinh ra đều được đưa vào hàng đợi chờ xử lý. Thuật toán chỉ tiến hành kiểm tra xem trạng thái đó có phải là Goal hay không khi nó được lấy ra khỏi queue (dequeue) để xét. Cách này bám sát vào định nghĩa cơ bản và nguyên thủy nhất của BFS, nhưng đánh đổi lại sẽ tốn nhiều không gian bộ nhớ (kích thước hàng đợi lớn hơn) và số lượng node sinh ra cũng nhiều hơn.

### Các thông số so sánh

- **Length (Chiều dài đường đi):** Số bước di chuyển cần thiết để đi từ trạng thái Start đến Goal. Do tính chất của thuật toán BFS luôn tìm được đường đi ngắn nhất, thông số này sẽ luôn bằng nhau ở cả hai Mode (đối với cùng một bài toán đầu vào).
- **Expanded (Số node đã mở rộng):** Số lượng trạng thái đã được lấy ra khỏi hàng đợi (dequeue) để xét và dùng làm node cha sinh ra các trạng thái con. Nhờ việc dừng sớm, Mode 1 thường có số node Expanded ít hơn so với Mode 2.
- **Generated (Số node đã sinh):** Tổng số các trạng thái con được tạo ra trong suốt quá trình chạy thuật toán (sau khi áp dụng các luật di chuyển lên/xuống/trái/phải hợp lệ).
- **Queue left (Số node còn trong hàng đợi):** Kích thước hàng đợi (số node đang chờ được duyệt) ngay tại thời điểm tìm thấy Goal hoặc thuật toán kết thúc. Thông số này phản ánh lượng tài nguyên bộ nhớ mà thuật toán tiêu tốn.
- **Reached (Số node đã xét):** Tổng số các trạng thái duy nhất (không trùng lặp) đã từng được sinh ra và ghi nhận. Việc đánh dấu này giúp chương trình không rơi vào trạng thái lặp vô hạn (chu trình).
