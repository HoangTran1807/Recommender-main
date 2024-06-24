python -version 3.11.8 cài anaconda để setup môi trường ko cần cũng được
chạy lệnh này để cài thư viện hoặc cài bằng cơm đi
pip install autoimport
autoimport your_project

python app.py -> để chạy app

[GET] http://127.0.0.1:5000/  test
[GET] http://127.0.0.1:5000/createTrainingData khởi tạo train data mất tầm (2p - 4p)
[GET] http://127.0.0.1:5000/createModel khởi tạo model (8s - 10s)
[GET] http://127.0.0.1:5000/recommendProduct/4?take={take} lấy về recommend product_id = 4 (0.2s - 0.4s)
[GET] http://127.0.0.1:5000/recommendProducts?ids={ids}&take={take} truyền vào ids: product_id | ex: ?ids=1,2,3,4&take=10
[GET] http://127.0.0.1:5000/collab/train train và save collaborative model
[GET] http://127.0.0.1:5000/collab/product?userId={userId}&take={take} lấy danh sách gợi ý
