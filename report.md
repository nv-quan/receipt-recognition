# Báo cáo bài toán trích xuất thông tin hoá đơn
Bài toán bao gồm 3 bước:
1. [Tiền xử lý](#tiền-xử-lý)
2. [Nhận diện ký tự quang học (OCR)](#)
3. [Xử lý và trích xuất thông tin](#)
## Tiền xử lý
### Một số tiêu chí của một bức ảnh tốt để đưa vào nhận diện
* Các ký tự có viền rõ nét
* Độ phân giải cao
* Các ký tự nằm thẳng hàng
* Ít nhiễu
### Các bước cần thực hiện
* [ ] Tăng hoặc giảm kích thước ảnh để có kích cỡ chữ phù hợp. Với cỡ chữ 10pt thì DPI tối thiểu phải đạt 300dpi
* [ ] Chuyển góc nhìn (perspective transform) về dạng thẳng góc, cắt và phóng to phần chứa ký tự
* [ ] Nhị phân hoá
* [ ] Khử nhiễu
* [ ] * Phân tích bố cục
### Thử nghiệm

