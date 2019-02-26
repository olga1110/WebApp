#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3


def create_bd():
    conn = sqlite3.connect("comments.db")
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute('drop table if exists comments')
    cursor.execute('drop table if exists city')
    cursor.execute('drop table if exists region')

    cursor.execute("""
    
        create table
    
        region
    
            (
                guid integer primary key autoincrement,
                kod text unique,
                name text unique             
            )
    
        """)

    cursor.execute("""
    
        create table
    
            city
    
            (
                guid integer primary key autoincrement,
                region_id integer references region (guid),            
                name text,
                CONSTRAINT region_city UNIQUE (region_id, name)
            )
    
        """)

    cursor.execute("""
    
        create table
    
            comments
    
            (
                guid integer primary key autoincrement,
                surname text not null,
                name text not null,         
                patronymic text,
                region_id integer references region (guid),
                city_id integer references city (guid),
                phone text,
                email text,
                comment text not null      
                         
            )
    
        """)

    conn.commit()

    # Заполняем справочники

    regions = [
        (23, 'Краснодарский край',),
        (61, 'Ростовская область',),
        (26, 'Ставропольский край',),
        (59, 'Пермский край',),
        (66, 'Свердловская область',),
    ]

    cursor.executemany("insert into region (kod, name) values (?, ?);", regions)

    conn.commit()

    cities = [
        (1, 'Краснодар',),
        (1, 'Абинск',),
        (1, 'Армавир',),
        (1, 'Анапа',),
        (1, 'Кропоткин',),
        (1, 'Славянск',),
        (2, 'Ростов',),
        (2, 'Шахты',),
        (2, 'Батайск',),
        (3, 'Ставрополь',),
        (3, 'Пятигорск',),
        (3, 'Кисловодск',),
        (4, 'Пермь',),
        (4, 'Александровск',),
        (4, 'Березники',),
        (4, 'Верещагино',),
        (4, 'Горнозаводск',),
        (4, 'Гремячинск',),
        (5, 'Екатеринбург',),
        (5, 'Алапаевск',),
        (5, 'Первоуральск',),
        (5, 'Ирбит',),
        (5, 'Каменск-Уральский',),

    ]

    cursor.executemany("insert into city (region_id, name) values (?, ?);", cities)

    conn.commit()

# cursor.execute("""
#
#     create table
#
#         phones
#
#         (
#             guid integer primary key autoincrement,
#             user_id integer references users (guid),
#             phone text
#         )
#
#     """)
#
# cursor.execute("""
#
#     create table
#
#         emails
#
#         (
#             guid integer primary key autoincrement,
#             user_id integer references users (guid),
#             email text
#         )
#
#     """)


# if __name__ == '__main__':
#     pass
