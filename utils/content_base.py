import time as Time
import pyodbc
import json 
import re
from underthesea import word_tokenize
import unidecode
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import random
import os
import dotenv

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def renderContent():
    return "Hello World"

def get_stopwords():
    with open("./data/vietnamese-stopwords.txt", encoding='utf-8') as f:
        return f.readlines()

def preprocessing_text(text, stopwords):
    # Loại bỏ html bằng regex
    text = re.sub('<[^>]*>', ' ', text)
    text = text.lower()

    # Loại bỏ các ký tự Unicode không mong muốn
    text = unidecode.unidecode(text)
    # Tách từ bằng thư viện underthesea
    text = word_tokenize(text, format="text")

    # Loại bỏ dấu chấm câu và khoảng trắng thừa
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)


    # Loại bỏ các ký tự còn sót lại
    text = re.sub(r"[^\w ]", "", text)

    # Loại bỏ stopword
    filtered_words = [word for word in text.split() if word not in stopwords]
    # Ghép lại thành chuỗi
    result = ' '.join(filtered_words)
    return result

def check_rating(rating):
    if rating == None:
        return 3
    return rating

def convert_categories(categories):
    return categories.split(',')

def get_trainData():
    try:
        start_time = Time.time()
        stopwords = get_stopwords()
        # Kết nối đến cơ sở dữ liệu SQL Server
        conn = pyodbc.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Truy vấn để lấy dữ liệu từ bảng product
        cursor.execute('''
        SELECT
            p.[Id], 
            p.[Name], 
            p.[AuthorId], 
            p.[SupplierId], 
            p.[Desc], 
            AVG(c.[Rating]) as AverageRating,
            STRING_AGG(pc.[CategoryId], ',') WITHIN GROUP (ORDER BY pc.[CategoryId]) as Categories
        FROM 
            product p
        LEFT JOIN 
            comment c ON p.[Id] = c.[ProductId]
        LEFT JOIN 
            ProductCategory pc ON p.[Id] = pc.[ProductId]
        GROUP BY 
            p.[Id], 
            p.[Name], 
            p.[AuthorId], 
            p.[SupplierId], 
            p.[Desc]
    ''')
        rows = cursor.fetchall()

        # Chuyển dữ liệu đã lấy được thành dạng JSON
        data = []
        # shinkRows = rows[:100]
        for row in rows:
            processed_desc = preprocessing_text(row[4], stopwords)
            rating = check_rating(row[5])
            categories = convert_categories(row[6])
            data.append({
                'Id': row[0],
                'Name': row[1],
                'AuthorId': row[2],
                'SupplierId': row[3],
                'Desc': processed_desc,
                'AverageRating': rating,
                'CategoryId': categories
            })
    except Exception as e:
        print(f"Loi : {e}")

        
    # Ghi dữ liệu JSON vào file
    with open('./data/product_data2.json', 'w') as f:
        current_data = data
        json.dump(data, f)

    # Đóng kết nối với cơ sở dữ liệu
    conn.close()

    end_time = Time.time()
    return {
        'success': True,
        'message': 'Get data successfully',
        'time': end_time - start_time
    }

def createModel():
    start_time = Time.time()
    products = pd.read_json('./data/product_data2.json')
    if products is None:
        return {
            'success': False,
            'message': 'Data not found'
        }
    products['AuthorId'] = products['AuthorId'].fillna('').astype(str)
    products['Desc'] = products['Desc'].fillna('').astype(str)
    products['CategoryId'] = products['CategoryId'].fillna('').astype(str)
    products['content'] = products['AuthorId'] + ' ' + products['Desc'] + ' ' + products['CategoryId']

    # tạo đối tượng TfidfVectorizer và fit dữ liệu vào đối tượng đó
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0.01)
    tfidf_matrix = tf.fit_transform(products['content'])
    # tfidf matrix shape = (số lượng sản phẩm, số lượng từ trong tập dữ liệu)

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    # cosine_sim shape = (số lượng sản phẩm, số lượng sản phẩm)
    # save the model to disk 
    pd.to_pickle(cosine_sim, './data/cosine_sim.pkl')
    end_time = Time.time()
    time = end_time - start_time
    return {
        'success': True,
        'message': 'Create model successfully',
        'time': time
    }

def recommendProduct(product_id, take):
    start_time = Time.time()
    try:
        cosine_sim = pd.read_pickle('./data/cosine_sim.pkl')
    except:
        return {
            'success': False,
            'message': 'Model not found'
        }

    try:
        products = pd.read_json('./data/product_data2.json')
    except:
        return {
            'success': False,
            'message': 'Data not found'
        }

    # Lấy index của sản phẩm dựa vào product_id
    idx = products[products['Id'] == int(product_id)].index[0]
    # Lấy ra các giá trị tương tự của sản phẩm đó
    sim_scores = list(enumerate(cosine_sim[idx]))
    # Sắp xếp các giá trị tương tự theo thứ tự giảm dần
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = list(filter(lambda x: x[1] > 0.3, sim_scores))
    
    if(take != -1):
        sim_scores = sim_scores[1:take]

    # Lấy ra index của các sản phẩm đó
    product_indices = [i[0] for i in sim_scores]
    # Lấy ra id của các sản phẩm đó
    product_indices = products['Id'].iloc[product_indices].tolist()
    end_time = Time.time()
    time = end_time - start_time
    return {"success": True, "data": product_indices, "time": time}

def recommendProducts(list_product_id, take):
    start_time = Time.time()
    try:
        cosine_sim = pd.read_pickle('./data/cosine_sim.pkl')
    except:
        return {
            'success': False,
            'message': 'Model not found'
        }

    try:
        products = pd.read_json('./data/product_data2.json')
    except:
        return {
            'success': False,
            'message': 'Data not found'
        }

    # với mỗi product_id trong list_product_id, thực hiện gợi ý sản phẩm
    result = []
    for product_id in list_product_id:
        # Lấy index của sản phẩm dựa vào product_id
        idx = products[products['Id'] == int(product_id)].index[0]
        # Lấy ra các giá trị tương tự của sản phẩm đó
        sim_scores = list(enumerate(cosine_sim[idx]))
        # Sắp xếp các giá trị tương tự theo thứ tự giảm dần
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = list(filter(lambda x: x[1] > 0.3, sim_scores))

        if take != -1:
            sim_scores = sim_scores[1:take]
        # Lấy ra index của các sản phẩm đó
        product_indices = [i[0] for i in sim_scores]
        # Lấy ra id của các sản phẩm đó
        product_indices = products['Id'].iloc[product_indices].tolist()
        # chỉ thêm các sản phẩm chưa có trong result
        result.extend([product for product in product_indices if product not in result])
    # lấy ngẫu nhiên 20 sản phẩm từ result bằng cách shuffle result và lấy 20 phần tử đầu tiên
    random.shuffle(result)
    result = result[:take]
    end_time = Time.time()
    time = end_time - start_time
    return {
        'success': True,
        'list': result,
        'time': time
    }
