# Báo cáo bài toán trích xuất thông tin hoá đơn
Bài toán bao gồm 3 bước:
1. [Tiền xử lý](#tiền-xử-lý)
2. [Nhận diện ký tự quang học (OCR)](#)
3. [Xử lý và trích xuất thông tin](#)
## Tiền xử lý
### Một số tiêu chí của một bức ảnh tốt sau khi được xử lý
* Các ký tự có viền rõ nét
* Độ phân giải cao
* Các ký tự nằm thẳng hàng
* Ít nhiễu
### Các bước cần thực hiện
* [x] Tăng hoặc giảm kích thước ảnh để có kích cỡ chữ phù hợp. Với cỡ chữ 10pt thì DPI tối thiểu phải đạt 300dpi
* [ ] Chuyển góc nhìn (perspective transform) về dạng thẳng góc, cắt và phóng to phần chứa ký tự
* [ ] Nhị phân hoá
* [ ] Khử nhiễu
* [ ] * Phân tích bố cục
### Thử nghiệm
#### Chuyển góc nhìn
Để chuyển được góc nhìn thì trước tiên cần phải xác định được viền bao của tờ hoá đơn. Quá trình này có thể được thực hiện bằng các cách sau:
##### Cách 1
Áp dụng Gaussian filter để làm mờ ảnh sau đó áp dụng dilation và erosion (1 hoặc nhiều lần) để giữ lại các viền lớn. Tiếp đó sử dụng thuật toán otsu để nhị phân hoá hình ảnh. Từ ảnh đã được nhị phân hoá có thể xác định được contour và xấp xỉ lại thành một hình tứ giác. Thuật toán này không hoạt động tốt với những hình có độ tương phản giữa nền và vật không được cao. Ví dụ đối với bức hình sau, thuật toán đã thất bại trong việc làm nổi bật viền hình chữ nhật, do đó không xác định được contour.

|Input|Output|
|---|---|
|![Pic of receipt](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/data/001.jpg)|![After processed](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/sample/001-failed.png)|
