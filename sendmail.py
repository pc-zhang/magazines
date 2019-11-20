import sys, traceback
import settings
from email.headerregistry import Address
from email.message import EmailMessage
from os import path
import hashlib
import argparse
import sqlite3
import mysql.connector
from time import sleep
import smtplib, ssl
import urllib.request
import re
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
def isValidEmail(email):
    if re.search(regex, email):
        return True
    else:
        return False

def get_content_from_url(url = ''):
    content=urllib.request.urlopen(url).read().decode('utf-8')
    online_header = '<p>HAVING DIFFICULTY VIEWING THIS EMAIL? OPEN IT IN YOUR BROWSER <a href="%s" target="_blank">OPEN IT IN YOUR BROWSER</a>.</p>'%url
    content = online_header + content

    return content

def message(subject = '', content = ''):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = Address("USTCIF", "ustcif", "ustc.edu.cn")
    msg.set_content('')
    msg.add_alternative(content, subtype = 'html')

    return msg

def url2db(url):
    hashStr = hashlib.md5(url.encode()).hexdigest()
    return 'task_{}.db'.format(hashStr)
    

def newtask(url = ""):
    '''
    input:
        url: 要发送的网页地址
        
    output:
        Fail:
            create task table failed!
                task already exist
                ...
        Succeed:
    '''

    db = url2db(url)
    if path.exists(db):
        print('任务已存在，可删除该数据库文件后再新建任务')
        exit(0)
    sqlite3_conn = sqlite3.connect(db)
    sqlite3_c = sqlite3_conn.cursor()

    sqlite3_c.execute('''CREATE TABLE tasks (email text, mail_group text, sended integer, fail_count integer)''')
    

    mysql_cnx = mysql.connector.connect(user=settings.mysql_user, password=settings.mysql_password,
        host=settings.mysql_host,
        database=settings.mysql_database)

    mysql_cursor = mysql_cnx.cursor()

    query = ("select min(id) as id,email_addr from if_donor_email where priority>=0 and deleted=0 group by email_addr order by id")

    mysql_cursor.execute(query)

    for (id, email_addr) in mysql_cursor:
        email_addr = "{}".format(email_addr)
        if email_addr.find('@googlegroups.com')!=-1 :
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'google_group'))
        elif email_addr.find('@ustc.edu')!=-1 and email_addr.find('@mail.ustc.edu.cn')==-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'ustc'))            
        elif email_addr.find('@mail.ustc.edu.cn')!=-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'mail_ustc'))
        elif email_addr.find('@qq.com')!=-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'qq'))
        else:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'others'))
                

    sqlite3_conn.commit()
    sqlite3_conn.close()
    
    mysql_cursor.close()
    mysql_cnx.close()

def testtask(url = ''):
    db = url2db(url)
    if path.exists(db):
        print('任务已存在，可删除该数据库文件后再新建任务')
        exit(0)
    sqlite3_conn = sqlite3.connect(db)
    sqlite3_c = sqlite3_conn.cursor()

    sqlite3_c.execute('''CREATE TABLE tasks (email text, mail_group text, sended integer, fail_count integer)''')
    
    for email_addr in settings.test_mail_list:
        if email_addr.find('@googlegroups.com')!=-1 :
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'google_group'))
        elif email_addr.find('@ustc.edu')!=-1 and email_addr.find('@mail.ustc.edu.cn')==-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'ustc'))            
        elif email_addr.find('@mail.ustc.edu.cn')!=-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'mail_ustc'))
        elif email_addr.find('@qq.com')!=-1:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'qq'))
        else:
            sqlite3_c.execute("INSERT INTO tasks VALUES ('{}', '{}',0, 0)".format(email_addr,'others'))
                

    sqlite3_conn.commit()
    sqlite3_conn.close()


def check(url = "", max_fail_count = 3):
    '''
    input:
        url: 要发送的网页地址
        resent_max_count: 对同一个邮件地址，最多失败重发次数
    '''
    db = url2db(url)
    if not path.exists(db):
        print('任务不存在')
        exit(0)

    sqlite3_conn = sqlite3.connect(db)
    sqlite3_c = sqlite3_conn.cursor()

    statistics = {
                  "google_group":{'sended':0, 'fail_exceed_max_count':0, 'to_be_send':0},
                  "ustc":{'sended':0, 'fail_exceed_max_count':0, 'to_be_send':0},
                  "mail_ustc":{'sended':0, 'fail_exceed_max_count':0, 'to_be_send':0},
                  "qq":{'sended':0, 'fail_exceed_max_count':0, 'to_be_send':0},
                  "others":{'sended':0, 'fail_exceed_max_count':0, 'to_be_send':0}
                  }

    for row in sqlite3_c.execute('SELECT email, mail_group, sended, fail_count FROM tasks'):
        mail_group = '{}'.format(row[1])
        sended = row[2]
        fail_count = row[3]
        if sended != 0:
            statistics[mail_group]['sended'] += 1
        elif fail_count >= max_fail_count:
            statistics[mail_group]['fail_exceed_max_count'] += 1
        else:
            statistics[mail_group]['to_be_send'] += 1
            
    sqlite3_conn.close()

    print_statistics(statistics)

def print_statistics(statistics):
    print('group\tsended\tfails\tto_be_send')
    print('Ggroup\t{}\t{}\t{}'.format(statistics['google_group']['sended'], statistics['google_group']['fail_exceed_max_count'], statistics['google_group']['to_be_send']))
    print('ustc\t{}\t{}\t{}'.format(statistics['ustc']['sended'], statistics['ustc']['fail_exceed_max_count'], statistics['ustc']['to_be_send']))
    print('mailust\t{}\t{}\t{}'.format(statistics['mail_ustc']['sended'], statistics['mail_ustc']['fail_exceed_max_count'], statistics['mail_ustc']['to_be_send']))
    print('qq\t{}\t{}\t{}'.format(statistics['qq']['sended'], statistics['qq']['fail_exceed_max_count'], statistics['qq']['to_be_send']))
    print('others\t{}\t{}\t{}'.format(statistics['others']['sended'], statistics['others']['fail_exceed_max_count'], statistics['others']['to_be_send']))


def run(url = "", subject = '', groups = [], max_fail_count = 3):
    # connect mail server
    context = ssl.create_default_context()
    content = get_content_from_url(url)

    # connect task database
    db = url2db(url)
    conn = sqlite3.connect(db)
    c = conn.cursor()

    for group in groups:
        c.execute('select email from tasks where mail_group = "{}" and sended = 0 and fail_count < {} order by fail_count'.format(group, max_fail_count))
        email_list = c.fetchall()
        for row in email_list:
            email = row[0]
            if not isValidEmail(email):
                continue
            msg = message(subject, content)
            msg["To"] = email

            try:
                server = smtplib.SMTP_SSL("mail.ustc.edu.cn", 465, context=context)
                server.login("ustcif@ustc.edu.cn", settings.mail_server_password)
            except Exception as ex:
                print(ex)
                server.quit()
                sleep(5)
                continue 

            try:
                server.send_message(msg)
                c.execute('UPDATE tasks SET sended = 1 where email = "{}"'.format(email))
                print("{} --- sended".format(email))
            except Exception as ex:
                c.execute('UPDATE tasks SET fail_count = fail_count + 1 where email = "{}"'.format(email))
                print("{} --- failed".format(email))
                print("Exception in send_message:")
                print("-"*60)
                traceback.print_exc(file=sys.stdout)
                print("-"*60)

            conn.commit()
            server.quit()

            if group in ['ustc', 'mail_ustc', 'qq']:
                sleep(0.05)
            else:
                sleep(5)

    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='从uscif@ustc.edu.cn向邮件列表发送邮件')
    parser.add_argument('command', choices=['newtask', 'check', 'run', 'testtask'], help = '''
        newtask: 建立待发送邮件的任务表 表头 email, sended, fail_count \n
        testtask: 测试：建立待发送邮件的任务表 表头 email, sended, fail_count \n
        check: 统计各个邮件组已发送，待发送，发送超过最大失败次数的邮件数 \n
        run: 发送邮件 \n
    ''')
    parser.add_argument('url', help = '待发送页面url地址')
    parser.add_argument('subject', help = '邮件主题')
    
    parser.add_argument('--max_fail_count', type=int, default = 3, help= '最大失败次数')
    
    parser.add_argument('--all', action='store_true', help='发送全部邮件组')
    parser.add_argument('--google_group', action='store_true', help='发送google group，5秒发送一封邮件')
    parser.add_argument('--ustc', action='store_true', help='发送%%@ustc.edu.cn，0.05秒发送一封邮件')
    parser.add_argument('--mail_ustc', action='store_true', help='发送%%@mail.ustc.edu.cn，0.05秒发送一封邮件')
    parser.add_argument('--qq', action='store_true', help='发送%%@qq.com，0.05秒发送一封邮件')
    parser.add_argument('--others', action='store_true', help='发送其他邮件组，5秒发送一封邮件')
    
    args = parser.parse_args()    

    groups = []
    if args.all:
        groups = ['google_group', 'ustc', 'mail_ustc', 'qq', 'others']
    else:
        if args.google_group:
            groups.append('google_group')
        if args.ustc:
            groups.append('ustc')
        if args.mail_ustc:
            groups.append('mail_ustc')
        if args.qq:
            groups.append('qq')
        if args.others:
            groups.append('others')

    if args.command == 'newtask':
        print("url: {} \n task database: {} \n".format(args.url, url2db(args.url)))
        newtask(args.url)
        check(args.url, args.max_fail_count)
    elif args.command == 'testtask':
        print("url: {} \n task database: {} \n".format(args.url, url2db(args.url)))
        testtask(args.url)
        check(args.url, args.max_fail_count)
    elif args.command == 'check':
        print("url: {} \n task database: {} \n max fail count: {} \n".format(args.url, url2db(args.url), args.max_fail_count))
        check(args.url, args.max_fail_count)
    elif args.command == 'run':
        print("url: {} \n subject: {} \n task database: {} \n max fail count: {} \n".format(args.url, args.subject, url2db(args.url), args.max_fail_count))
        check(args.url, args.max_fail_count)

        run(args.url, args.subject, groups, args.max_fail_count)
