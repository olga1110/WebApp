#!/usr/bin/env python
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import html
import sqlite3
import argparse
import json
from functools import reduce

import config
from init_db import create_bd
from log_config import create_log

host = config.HOST
port = config.PORT
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--host', help='server address', nargs='?', default=host)
parser.add_argument('-p', '--port', help='port contains 4 numbers', nargs='?', default=port, type=int)
# args = parser.parse_args('--host --port'.split())
args = parser.parse_args()
host = args.host
port = args.port
server_address = f'http://{host}:{port}'

logger = create_log('comments_log.log')

# Проверка на наличие файла БД в корне директории приложения
# При отсутствии БД файл создается и заполняется заново

bd_path = "comments.db"
if not os.path.exists(bd_path):
    logger.debug('creating data base...')
    create_bd()

conn = sqlite3.connect("comments.db")
cursor = conn.cursor()
limit = config.LIMIT_VIEW_COMMENTS


class RequestHandler(BaseHTTPRequestHandler):

    @staticmethod
    def response_encode(ex_data):
        return (json.dumps(ex_data)).encode('utf-8')

    @staticmethod
    def response_decode(in_data):
        return json.loads(in_data.decode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)

        # Static
        if self.path.endswith('.css'):
            self.send_header('Content-type', 'text/css; charset=utf-8')
            self.send_header('Cache-Control', config.CACHE_MODE)
            self.end_headers()
            path = os.path.join(os.getcwd(), 'static', 'css', self.path[1:])
            with open(path, 'rb') as f:
                self.wfile.write(f.read())

        if self.path.endswith('.js'):
            self.send_header('Content-type', 'application/javascript; charset=utf-8')
            self.send_header('Cache-Control', config.CACHE_MODE)
            self.end_headers()
            path = os.path.join(os.getcwd(), 'static', 'js', self.path[1:])
            with open(path, 'rb') as f:
                self.wfile.write(f.read())

        if self.path.endswith('.jpg'):
            self.send_header('Content-type', 'image/jpg; charset=utf-8')
            self.send_header('Cache-Control', config.CACHE_MODE)
            self.end_headers()
            path = os.path.join(os.getcwd(), 'static', 'img', self.path[1:])
            with open(path, 'rb') as f:
                self.wfile.write(f.read())

        # Rendering web-pages
        try:
            # Главная страница
            if self.path.endswith('/'):
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', config.CACHE_MODE)
                self.end_headers()
                path = os.path.join(os.getcwd(), 'templates', 'index.html')
                with open(path, 'r') as f:
                    main_page = f.read()
                    main_page = main_page.replace('server_address', server_address)
                    self.wfile.write(bytes(main_page, 'utf-8'))

            # Страница с формой обратной связи
            if self.path.endswith('comment'):
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', config.CACHE_MODE)
                self.end_headers()
                path = os.path.join(os.getcwd(), 'templates', 'comment.html')
                with open(path, 'r') as f:
                    comments_page = f.read()
                # Выводим список регионов из БД
                try:
                    cursor.execute('select guid, name from region')
                    regions = [f'<option value="{i[0]}">{i[1]}</option>' for i in cursor.fetchall()]
                    logger.debug('Получение списка регионов из БД')
                    logger.debug('Рендеринг страницы comment.html')
                except sqlite3.Error as e:
                    logger.error('Database error: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                except Exception as e:
                    logger.error('Exception in _query: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                else:
                    repls = ('server_address', server_address), ('region_options', ' '.join(regions))

                    # comments_page = comments_page.replace('server_address', server_address). \
                    #     replace('region_options', ' '.join(regions))
                    self.wfile.write(bytes(reduce(lambda a, kv: a.replace(*kv), repls, comments_page), 'utf-8'))

            # Список представлений
            if self.path.endswith('view'):
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                path = os.path.join(os.getcwd(), 'templates', 'view.html')
                with open(path, 'r') as f:
                    view_page = f.read()
                try:
                    cursor.execute("""
                    select com.guid, com.surname, com.name, com.patronymic, r.name, c.name, com.phone,
                      com.email, com.comment from comments com
                     left join region r on com.region_id=r.guid
                      left join city c on com.city_id = c.guid limit :limit
                    """, {'limit': config.LIMIT_VIEW_COMMENTS})
                    comments = [i for i in cursor.fetchall()]
                    view_comments = []
                    for row in comments:
                        view_comments.append('<tr id="{}">'.format(row[0]))
                        for num, cell in enumerate(row):
                            if num:
                                if cell is None:
                                    cell = ""
                                view_comments.append('<td>{}</td>'.format(cell))
                        view_comments.append('<td><input type="checkbox"></td>')
                        view_comments.append('</tr>')

                    logger.debug('Рендеринг страницы view.html')
                except sqlite3.Error as e:
                    logger.error('Database error: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                # except Exception as e:
                #     logger.error('Exception in _query: %s' % e)
                #     self.wfile.write(bytes('<h1 style="font-size=30px">'
                #                            'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))

                else:
                    repls = ('server_address', server_address), ('comment_table', ' '.join(view_comments))
                    self.wfile.write(bytes(reduce(lambda a, kv: a.replace(*kv), repls, view_page), 'utf-8'))

            # Статистика
            if self.path.endswith('stat'):
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                path = os.path.join(os.getcwd(), 'templates', 'stat.html')
                with open(path, 'r') as f:
                    view_page = f.read()
                try:
                    cursor.execute("""
                    select r.guid, r.name, count_comment
                    from
                    (select region_id, count(comment) count_comment from comments c
                     left join region r on c.region_id=r.guid group by region_id having count(comment)>?) com
                     left join region r on r.guid=com.region_id
                    """, (config.NUMBER_COMMENTS,))
                    stat = [i for i in cursor.fetchall()]
                    view_stat = []
                    for row in stat:
                        view_stat.append('<tr id="{}" onclick="ShowCitiesStats(this)">'.format(row[0]))
                        for num, cell in enumerate(row):
                            if num:
                                if cell is None:
                                    cell = ""
                                view_stat.append('<td>{}</td>'.format(cell))
                        view_stat.append('</tr>')
                    logger.debug('Рендеринг страницы stat.html')
                except sqlite3.Error as e:
                    logger.error('Database error: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                except Exception as e:
                    logger.error('Exception in _query: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))

                else:
                    repls = ('server_address', server_address), ('number_comments', str(config.NUMBER_COMMENTS)), \
                            ('stat_data', ' '.join(view_stat))
                    self.wfile.write(bytes(reduce(lambda a, kv: a.replace(*kv), repls, view_page), 'utf-8'))

        except IOError:
            self.send_error(404, 'Page not found: %s' % self.path)

        # AJAX-запросы
        # Передаем список городов в зависимости от региона
        if self.path.find('get_cities') != -1:
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            region_id = int(self.path[self.path.rfind('/') + 1:])

            if region_id:

                try:
                    cursor.execute('select guid, name from city where region_id = ?', (region_id,))
                    # cities = [f'<option value="{i[0]}">{i[1]}</option>' for i in cursor.fetchall()]
                    cities = [list(i) for i in cursor.fetchall()]
                    logger.debug('Ajax-запрос. Список городов по региону {}'.format(region_id))
                except sqlite3.Error as e:
                    logger.error('Database error: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                except Exception as e:
                    logger.error('Exception in _query: %s' % e)
                    self.wfile.write(bytes('<h1 style="font-size=30px">'
                                           'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
                else:
                    # self.wfile.write(bytes(' '.join(cities), 'utf-8'))
                    self.wfile.write(self.response_encode(cities))
                    logger.debug('Запрос выполнен успешно')
        # Обработка изменения limit

        # Передача указанного числа комментариев. Установка limit
        if self.path.find('set_limit') != -1:
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            global limit
            limit = int(self.path[self.path.rfind('/') + 1:])
            try:
                cursor.execute("""
                                               select com.guid, com.surname, com.name, com.patronymic, r.name, c.name,
                                                com.phone, com.email, com.comment from comments com
                                                left join region r on com.region_id=r.guid
                                                 left join city c on com.city_id = c.guid limit :limit offset :offset 
                                               """, {'limit': limit, 'offset': 0})
                part_comments = [list(i) for i in cursor.fetchall()]
                # logger.debug('Ajax-запрос. Список городов по региону {}'.format(region_id))
            except sqlite3.Error as e:
                logger.error('Database error: %s' % e)
                self.wfile.write(bytes('<h1 style="font-size=30px">'
                                       'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
            except Exception as e:
                logger.error('Exception in _query: %s' % e)
                self.wfile.write(bytes('<h1 style="font-size=30px">'
                                       'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
            else:
                # self.wfile.write(bytes(' '.join(cities), 'utf-8'))
                self.wfile.write(self.response_encode(part_comments))
                logger.debug('Запрос выполнен успешно')

        # Просмотр комментариев. Пагинация
        if self.path.find('get_comments') != -1:
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            offset = int(self.path[self.path.rfind('/') + 1:])
            try:
                cursor.execute("""
                                   select com.guid, com.surname, com.name, com.patronymic, r.name, c.name, com.phone,
                                     com.email, com.comment from comments com
                                    left join region r on com.region_id=r.guid
                                     left join city c on com.city_id = c.guid limit :limit offset :offset 
                                   """, {'limit': limit, 'offset': offset})
                part_comments = [list(i) for i in cursor.fetchall()]
                # logger.debug('Ajax-запрос. Список городов по региону {}'.format(region_id))
            except sqlite3.Error as e:
                logger.error('Database error: %s' % e)
                self.wfile.write(bytes('<h1 style="font-size=30px">'
                                       'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
            # except Exception as e:
            #     logger.error('Exception in _query: %s' % e)
            #     self.wfile.write(bytes('<h1 style="font-size=30px">'
            #                            'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
            else:
                # self.wfile.write(bytes(' '.join(cities), 'utf-8'))
                self.wfile.write(self.response_encode(part_comments))
                logger.debug('Запрос выполнен успешно')

        # Удаляем комментарии по запросу
        # if self.path.find('delete') != -1:
        # # if self.path.endswith('delete'):
        #     self.send_header('Content-type', 'text/html; charset=utf-8')
        #     self.end_headers()
        #     comment_id = int(self.path[self.path.rfind('/') + 1:])
        #     try:
        #         cursor.execute('delete from comments where guid=?', (comment_id,))
        #         conn.commit()
        #         logger.debug('Ajax-запрос. Удаление комментария {}'.format(comment_id))
        #     except sqlite3.Error as e:
        #         logger.error('Database error: %s' % e)
        #         self.wfile.write(bytes('error', 'utf-8'))
        #     except Exception as e:
        #         logger.error('Exception in _query: %s' % e)
        #         self.wfile.write(bytes('error', 'utf-8'))
        #     else:
        #         self.wfile.write(bytes('OK', 'utf-8'))
        #         logger.debug('Запрос выполнен успешно')

        # Передача статистики в разрезе городов в зависимости от выбранного региона
        if self.path.find('city_stats') != -1:
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            region_id = int(self.path[self.path.rfind('/') + 1:])
            try:
                cursor.execute("""
                                        select c.guid, c.name, count_comments
                                        from
                                        (select city_id, count(comment) count_comments from comments
                                        where region_id = ? group by city_id) com
                                        left join city c on c.guid = com.city_id""", (region_id,))
                stat = [list(i) for i in cursor.fetchall()]
                # stat = [i for i in cursor.fetchall()]
                # view_stat = []
                # for row in stat:
                #     view_stat.append('<tr id="{}">'.format(row[0]))
                #     for num, cell in enumerate(row):
                #         if num:
                #             if cell is None:
                #                 cell = ""
                #             view_stat.append('<td>{}</td>'.format(cell))
                #     view_stat.append('</tr>')
                logger.debug('Ajax-запрос. Получение статистики в разрезе городов по региону {}'.format(region_id))
            except sqlite3.Error as e:
                logger.error('Database error: %s' % e)
                self.wfile.write(bytes('<h1 style="font-size=30px">'
                                       'Ошибка сервера. Обратитесь к администратору</h1>', 'utf-8'))
            else:
                # self.wfile.write(bytes(' '.join(view_stat), 'utf-8'))
                self.wfile.write(self.response_encode(stat))
                logger.debug('Запрос выполнен успешно')

    def do_POST(self):
        # self.do_HEAD()
        # Обработка формы обратной связи
        if self.path.endswith('send'):
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         })

            region_id = None if form.getfirst("region") == '0' else int(form.getfirst("region"))
            city_id = None if form.getfirst("city") == '0' else int(form.getfirst("city"))
            try:
                cursor.execute("""
                    insert into comments (surname, name, patronymic,  region_id, city_id, phone, email, comment)
                    values(?, ?, ?, ?, ?, ?, ?, ?)""",
                               (form.getfirst("surname"), form.getfirst("name"), form.getfirst("patronymic"),
                                region_id, city_id, form.getfirst("phone"),
                                form.getfirst("email"), html.escape(form.getfirst("comment")),)
                               )
            except sqlite3.Error as e:
                logger.error('Database error: %s' % e)
                self.wfile.write(bytes('Ошибка сервера. Комментарий не сохранен, обратитесь к администратору', 'utf-8'))
            except Exception as e:
                logger.error('Exception in _query: %s' % e)
                self.wfile.write(bytes('Ошибка сервера. Комментарий не сохранен, обратитесь к администратору', 'utf-8'))
            else:
                conn.commit()
            self.send_response(301)
            url = f'http://{host}:{port}/view'
            self.send_header('Location', url)
            self.end_headers()

        # Удаление записей из БД
        if self.path.endswith('delete'):
            rows_to_delete = self.rfile.read(int(self.headers['Content-Length']))
            self.send_response(200)
            self.end_headers()
            rows_to_delete = self.response_decode(rows_to_delete)

            try:
                cursor.execute('delete from comments where guid in %s' % repr(rows_to_delete).
                               replace('[', '(').replace(']', ')'))
                conn.commit()
                logger.debug('Ajax-запрос. Удаление комментария(-ев) {}'.format(rows_to_delete))
            except sqlite3.Error as e:
                logger.error('Database error: %s' % e)
                self.wfile.write(bytes('error', 'utf-8'))
            # except Exception as e:
            #     logger.error('Exception in _query: %s' % e)
            #     self.wfile.write(bytes('error', 'utf-8'))
            else:
                self.wfile.write(bytes('OK', 'utf-8'))
                logger.debug('Запрос выполнен успешно')


def run():
    logger.debug('starting server...')
    # Server settings
    server = (host, port)
    httpd = HTTPServer(server, RequestHandler)
    logger.debug(f'running server on http://{host}:{port}/')

    httpd.serve_forever()


if __name__ == '__main__':
    run()
