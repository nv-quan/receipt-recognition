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
* [x] Chuyển góc nhìn (perspective transform) về dạng thẳng góc, cắt và phóng to phần chứa ký tự
* [ ] Nhị phân hoá
* [ ] Khử nhiễu
* [ ] * Phân tích bố cục
### Thử nghiệm

#### Chuyển góc nhìn

Để chuyển được góc nhìn thì trước tiên cần phải xác định được viền bao của tờ hoá đơn. Quá trình này có thể được thực hiện bằng các cách sau:

##### Cách 1
1. Chuyển ảnh thành ảnh đơn sắc (gray). 
2. Áp dụng Gaussian filter để làm mờ ảnh sau đó 
3. Ap dụng Closing Transformation (Dilation và Erosion) (1 hoặc nhiều lần) để giữ lại các viền lớn. 
4. Sử dụng thuật toán otsu để nhị phân hoá hình ảnh. 
5. Từ ảnh đã được nhị phân hoá có thể xác định được contour và xấp xỉ lại thành một hình tứ giác.\

Đánh giá: Thuật toán này không hoạt động tốt với những hình có độ tương phản giữa nền và vật không được cao. Sau đây là ví dụ cho trường hợp thuật toán bị thất bại trong việc nhận diện. 

|Input|Output|Nhận xét|
|---|---|---|
|![Pic of receipt](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/data/001.jpg)|![After processed](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/sample/001-failed.png)|thuật toán đã thất bại trong việc làm nổi bật viền hình chữ nhật, do đó không xác định được chính xác contour.|

##### Cách 2
1. Vẫn chuyển ảnh thành đơn sắc như cách 1. 
2. Áp dụng Gaussian filter để giữ lại các viền chính
3. Sử dụng thuật toán Canny edge detection để xác định viền của vật. 
4. Từ ảnh viền tìm contour. 
5. Xấp xỉ lại thành tứ giác.
6. Từ contour tìm được áp dụng một ma trận biến hình để chuyển góc nhìn vật.\
Đánh giá: Đây là cách cho độ chính xác khá tốt trong nhiều trường hợp. Tuy nhiên thuật toán vẫn thất bại khi background có các chi tiết gây nhầm lẫn (Độ tương phản so với object quá thấp, có các vân thẳng nằm gần với viền của vật,...) hoặc tờ giấy không đủ phẳng. Một điều nữa là phương pháp này không thể áp dụng với những ảnh mà tờ giấy không được chụp đủ bốn góc. Dưới đây là 2 ví dụ cho thấy phương pháp bị thất bại trong việc nhận diện contour.

|Input|Output|Nhận xét|
|---|---|---|
|![Pic of receipt](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/data/011.jpg)|![After processed](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/sample/011-failed.png)|Nền bức ảnh có các vân thẳng khiến Canny edge detection bị nhầm lẫn.|
|![Pic of receipt](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/data/007.jpg)|![After processed](https://raw.githubusercontent.com/nv-quan/receipt-recognition/master/sample/007-failed.png)|Mặc dù thuật toán đã nhận diện khá tốt các đường bao nhưng lại không thể xấp xỉ được thành hình tứ giác do các viền xác định được không liền mạch|

##### Cách 3
1. Chuyển ảnh thành đơn sắc
2. Áp dụng Guassian filter để giữ lại các viền chính
3. Sử dụng thuật toán Canny edge detection để xác định viền của vật.
4. Từ viền ảnh tìm contours.
5. Giữ lại contours dài nhất và ghi lại contour đó vào một ảnh mới dưới dạng binary
6. Từ bức ảnh mới áp dụng thuật toán Hough Transformation để tìm tất cả các đường thẳng
7. Giữ lại 4 đường thẳng có số vote trong hough space lớn nhất với điều kiện không đường thẳng nào quá gần nhau 
8. Xác định 4 góc sau đó áp dụng ma trận chuyển góc nhìn để đưa ra output

Các bước được mô tả bởi ví dụ sau:

|1|2|3|4|
|---|---|---|---|
|![1](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/gray.png)|![2](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/blur.png)|![3](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/edges.png)|![4](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/contours.png)|
|5|6|7|8|
|![5](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/maxcontour.png)|![6](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/alllines.png)|![7](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/fourlines.png)|![8](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/output.png)|

Đối với các trường hợp bức hình hoá đơn bị thiếu một cạnh, cạnh bị thiếu sẽ được tạo ra bằng cách lấy song song với cạnh đã có. Sau đây là một ví dụ:

|Input|Viền xác định được|Tạo thêm cạnh|Output|
|---|---|---|---|
|![Input](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/edgemissing/original.png)|![Edges](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/edgemissing/largest.png)|![Hough](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/edgemissing/closing.png)|![Output](https://raw.githubusercontent.com/nv-quan/receipt-recognition/report/report/edgemissing/output.png)|

