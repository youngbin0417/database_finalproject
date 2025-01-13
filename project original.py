import pandas as pd
import numpy as np
from db_conn import *

import sys

def read_excel_into_mysql():
    excel_file = "movie_list.xls"

    conn, cur = open_db()

    try:
        for table_name in ["filming", "movie_genre", "movie_country", "movie", "director"]:
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")

        cur.execute("""
            CREATE TABLE movie (
                m_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                m_korname VARCHAR(255) NOT NULL,
                m_engname VARCHAR(255),
                m_year INTEGER,
                m_type VARCHAR(50),
                m_status VARCHAR(50),
                m_company VARCHAR(200)
            );
        """)

        cur.execute("""
            CREATE TABLE movie_genre (
                mg_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                m_id INTEGER,
                genre_name VARCHAR(50),
                FOREIGN KEY (m_id) REFERENCES movie(m_id)
            );
        """)

        cur.execute("""
            CREATE TABLE movie_country (
                mc_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                m_id INTEGER,
                country_name VARCHAR(50),
                FOREIGN KEY (m_id) REFERENCES movie(m_id)
            );
        """)

        cur.execute("""
            CREATE TABLE director (
                d_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                d_name VARCHAR(100) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE filming (
                f_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                m_id INTEGER,
                d_id INTEGER,
                FOREIGN KEY (m_id) REFERENCES movie(m_id),
                FOREIGN KEY (d_id) REFERENCES director(d_id)
            );
        """)

        # Read the first sheet starting from the 6th row (skiprows=5)
        df_main = pd.read_excel(excel_file, sheet_name="영화정보 리스트", skiprows=4, engine='xlrd', dtype=str)
        df_main.fillna('', inplace=True)
        
        # Filter out rows where all elements are empty in the first sheet
        df_main = df_main.dropna(how='all')
        
        print("Processing first sheet")
        
        for i, row in df_main.iterrows():
            try:
                if row.iloc[0] == '':
                    print(f"Skipping row {i} due to missing '영화명'")
                    continue

                # 데이터 타입과 비어 있는 값을 처리
                m_korname = row.iloc[0] or None
                m_engname = row.iloc[1] or None
                m_year = int(row.iloc[2]) if row.iloc[2] != '' else None
                m_type = row.iloc[4] or None
                m_status = row.iloc[6] or None
                m_company = row.iloc[8] or None

                # 영화 정보 삽입 (movie 테이블)
                cur.execute("""
                    INSERT INTO movie (m_korname, m_engname, m_year, m_type, m_status, m_company) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (m_korname, m_engname, m_year, m_type, m_status, m_company))
                movie_id = cur.lastrowid  # 삽입된 영화의 m_id 값 가져오기
                print(f"Inserted into movie table for row {i}")

                # 장르 정보 삽입 (movie_genre 테이블)
                genres = row.iloc[5].split(',')
                for genre in genres:
                    genre = genre.strip()
                    cur.execute("INSERT IGNORE INTO movie_genre (m_id, genre_name) VALUES (%s, %s)", (movie_id, genre))
                print(f"Inserted into movie_genre table for row {i}")

                # 국가 정보 삽입 (movie_country 테이블)
                countries = row.iloc[3].split(',')
                for country in countries:
                    country = country.strip()
                    cur.execute("INSERT IGNORE INTO movie_country (m_id, country_name) VALUES (%s, %s)", (movie_id, country))
                print(f"Inserted into movie_country table for row {i}")

                # 감독 정보 삽입 (director, filming 테이블)
                directors = row.iloc[7].split(',')
                for director in directors:
                    director = director.strip()
                    cur.execute("SELECT d_id FROM director WHERE d_name = %s", (director,))
                    result = cur.fetchone()
                    if result:
                        d_id = result['d_id']
                    else:
                        cur.execute("INSERT INTO director (d_name) VALUES (%s)", (director,))
                        d_id = cur.lastrowid
                    cur.execute("INSERT IGNORE INTO filming (m_id, d_id) VALUES (%s, %s)", (movie_id, d_id))
                print(f"Inserted into director and filming tables for row {i}")
                
                conn.commit()

            except Exception as e:
                print(f"Error inserting movie row {i}: {e}")
                conn.rollback()
                continue  # 오류 발생 시 다음 행으로 넘어감

        # Read the second sheet starting from the 1st row (skiprows=0)
        df_second = pd.read_excel(excel_file, sheet_name="영화정보 리스트_2", engine='xlrd', dtype=str)
        df_second.fillna('', inplace=True)
        
        # Filter out rows where all elements are empty in the second sheet
        df_second = df_second.dropna(how='all')

        print("Processing second sheet")

        for i, row in df_second.iterrows():
            try:
                if row.iloc[0] == '':
                    print(f"Skipping row {i} due to missing '영화명'")
                    continue

                # 데이터 타입과 비어 있는 값을 처리
                m_korname = row.iloc[0] or None
                m_engname = row.iloc[1] or None
                m_year = int(row.iloc[2]) if row.iloc[2] != '' else None
                m_type = row.iloc[4] or None
                m_status = row.iloc[6] or None
                m_company = row.iloc[8] or None

                # 영화 정보 삽입 (movie 테이블)
                cur.execute("""
                    INSERT INTO movie (m_korname, m_engname, m_year, m_type, m_status, m_company) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (m_korname, m_engname, m_year, m_type, m_status, m_company))
                movie_id = cur.lastrowid  # 삽입된 영화의 m_id 값 가져오기
                print(f"Inserted into movie table for row {i}")

                # 장르 정보 삽입 (movie_genre 테이블)
                genres = row.iloc[5].split(',')
                for genre in genres:
                    genre = genre.strip()
                    cur.execute("INSERT IGNORE INTO movie_genre (m_id, genre_name) VALUES (%s, %s)", (movie_id, genre))
                print(f"Inserted into movie_genre table for row {i}")

                # 국가 정보 삽입 (movie_country 테이블)
                countries = row.iloc[3].split(',')
                for country in countries:
                    country = country.strip()
                    cur.execute("INSERT IGNORE INTO movie_country (m_id, country_name) VALUES (%s, %s)", (movie_id, country))
                print(f"Inserted into movie_country table for row {i}")

                # 감독 정보 삽입 (director, filming 테이블)
                directors = row.iloc[7].split(',')
                for director in directors:
                    director = director.strip()
                    cur.execute("SELECT d_id FROM director WHERE d_name = %s", (director,))
                    result = cur.fetchone()
                    if result:
                        d_id = result['d_id']
                    else:
                        cur.execute("INSERT INTO director (d_name) VALUES (%s)", (director,))
                        d_id = cur.lastrowid
                    cur.execute("INSERT IGNORE INTO filming (m_id, d_id) VALUES (%s, %s)", (movie_id, d_id))
                print(f"Inserted into director and filming tables for row {i}")
                
                conn.commit()

            except Exception as e:
                print(f"Error inserting movie row {i}: {e}")
                conn.rollback()
                time.sleep(5)
                continue  # 오류 발생 시 다음 행으로 넘어감

        conn.commit()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        close_db(conn, cur)

if __name__ == '__main__':
    read_excel_into_mysql()
