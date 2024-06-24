from django.db import connection
from django.core.paginator import Paginator
from django.shortcuts import render


def movie_list(request):
    title_query = request.GET.get('title', '')
    director_query = request.GET.get('director', '')
    year_from = request.GET.get('year_from', '')
    year_to = request.GET.get('year_to', '')
    index_query = request.GET.get('index', '')
    production_status = request.GET.get('production_status', '')
    movie_type = request.GET.get('type', '')
    genre = request.GET.get('genre', '')
    country = request.GET.get('country', '')
    sort = request.GET.get('sort', 'm_korname')  # Default sort by movie name
    page = request.GET.get('page', 1)

    production_status_list = ["개봉", "개봉준비", "촬영진행", "기타", "개봉예정", "후반작업", "촬영준비"]
    type_list = ["장편", "단편", "옴니버스", "온라인전용", "기타"]
    genre_list = ["드라마", "코미디", "액션", "멜로/로맨", "스릴러", "미스터리", "공포(호러)", "어드벤처", "범죄", "가족", "판타지", "SF", "서부극(웨스턴)",
                  "사극", "애니메이션", "다큐멘터리", "전쟁", "뮤지컬", "성인물(에로)", "공연", "기타"]
    country_lists = [
        ["한국", "대만", "말레이시아", "북한", "싱가포르", "아프가니스탄", "이란", "인도", "중국", "태국", "이스라엘", "필리핀", "아랍에미리트연합국정부", "몽고", "티베트",
         "카자흐스탄", "캄보디아", "이라크", "우즈베키스탄", "베트남", "인도네시아", "카타르", "일본", "홍콩"],
        ["미국", "멕시코", "캐나다", "자메이카", "엘살바도르", "트리니다드토바고", "케이맨 제도"],
        ["그리스", "네덜란드", "덴마크", "독일", "러시아", "벨기에", "스웨덴", "스위스", "스페인", "영국", "오스트리아", "이탈리아", "체코", "터키", "포르투갈",
         "폴란드", "프랑스", "핀란드", "헝가리", "불가리아", "보스니아", "크로아티아", "노르웨이", "에스토니아"],
        ["아일랜드", "잉글랜드", "아이슬란드", "루마니아", "팔레스타인", "세르비아", "룩셈부르크", "마케도니아", "서독", "알바니아", "유슬라비아", "몰타", "우크라이나",
         "슬로바키아", "총괄(연감)"],
        ["남아프리카공화국", "부탄", "이집트", "나이지리아", "보츠와나", "리비아", "모로코", "케냐", "호주", "뉴질랜드", "피지", "기타"]
    ]

    selected_statuses = production_status.split(',') if production_status else []
    selected_types = movie_type.split(',') if movie_type else []
    selected_genres = genre.split(',') if genre else []
    selected_countries = country.split(',') if country else []

    sql = '''
        SELECT movie.m_id, movie.m_korname, movie.m_engname, movie.m_year, 
               movie.m_type, movie.m_status, movie.m_company, 
               GROUP_CONCAT(DISTINCT director.d_name) AS directors,
               GROUP_CONCAT(DISTINCT genre.genre_name) AS genres,
               GROUP_CONCAT(DISTINCT country.country_name) AS countries
        FROM movie
        LEFT JOIN filming ON movie.m_id = filming.m_id
        LEFT JOIN director ON filming.d_id = director.d_id
        LEFT JOIN movie_genre AS genre ON movie.m_id = genre.m_id
        LEFT JOIN movie_country AS country ON movie.m_id = country.m_id
        WHERE movie.m_korname LIKE %s AND director.d_name LIKE %s
    '''

    params = ['%' + title_query + '%', '%' + director_query + '%']

    if year_from:
        sql += ' AND movie.m_year >= %s'
        params.append(year_from)

    if year_to:
        sql += ' AND movie.m_year <= %s'
        params.append(year_to)

    if index_query:
        if index_query.isalpha():  # English alphabet filtering
            sql += ' AND movie.m_korname LIKE %s'
            params.append(index_query + '%')
        else:  # Korean initial consonant filtering
            initial_consonants = {
                'ㄱ': '[가-깋]', 'ㄴ': '[나-닣]', 'ㄷ': '[다-딯]', 'ㄹ': '[라-맇]', 'ㅁ': '[마-밓]',
                'ㅂ': '[바-빟]', 'ㅅ': '[사-싷]', 'ㅇ': '[아-잏]', 'ㅈ': '[자-짛]', 'ㅊ': '[차-칳]',
                'ㅋ': '[카-킿]', 'ㅌ': '[타-팋]', 'ㅍ': '[파-핗]', 'ㅎ': '[하-힣]'
            }
            if index_query in initial_consonants:
                sql += ' AND movie.m_korname REGEXP %s'
                params.append(initial_consonants[index_query])

    if production_status:
        status_list = production_status.split(',')
        sql += ' AND movie.m_status IN (%s)' % ','.join(['%s'] * len(status_list))
        params.extend(status_list)

    if movie_type:
        type_list = movie_type.split(',')
        sql += ' AND movie.m_type IN (%s)' % ','.join(['%s'] * len(type_list))
        params.extend(type_list)

    if genre:
        genre_list = genre.split(',')
        sql += ' AND genre.genre_name IN (%s)' % ','.join(['%s'] * len(genre_list))
        params.extend(genre_list)

    if country:
        country_list = country.split(',')
        sql += ' AND country.country_name IN (%s)' % ','.join(['%s'] * len(country_list))
        params.extend(country_list)

    sql += '''
        GROUP BY movie.m_id, movie.m_korname, movie.m_engname, movie.m_year, 
                 movie.m_type, movie.m_status, movie.m_company
    '''

    # Adjust sorting
    if sort == 'm_year':
        sql += ' ORDER BY movie.m_year DESC'
    else:  # Default to sorting by movie name
        sql += ' ORDER BY movie.m_korname'

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        movies = cursor.fetchall()

    movie_data = [
        {
            'm_id': row[0],
            'm_korname': row[1],
            'm_engname': row[2],
            'm_year': row[3],
            'm_type': row[4],
            'm_status': row[5],
            'm_company': row[6],
            'directors': row[7].split(',') if row[7] else [],
            'genres': row[8].split(',') if row[8] else [],
            'countries': row[9].split(',') if row[9] else []
        }
        for row in movies
    ]

    paginator = Paginator(movie_data, 10)  # 10 movies per page
    page_obj = paginator.get_page(page)

    return render(request, 'movie_list.html', {
        'page_obj': page_obj,
        'title_query': title_query,
        'director_query': director_query,
        'year_from': year_from,
        'year_to': year_to,
        'index_query': index_query,
        'production_status': production_status,
        'production_status_list': production_status_list,
        'selected_statuses': selected_statuses,
        'type': movie_type,
        'type_list': type_list,
        'selected_types': selected_types,
        'genre': genre,
        'genre_list': genre_list,
        'selected_genres': selected_genres,
        'country': country,
        'country_lists': country_lists,
        'selected_countries': selected_countries,
        'sort': sort,
    })
