import urllib2
import json
import MySQLdb
import time

if __name__ == '__main__':
    category_set = set()
    category_list = []
    category_dict = {}
    video_tuple = ()
    video_list = []
    video_dict = {}

    response = urllib2.urlopen('http://www.pornhub.com/webmasters/dump_output?keywords=&categories=3,35,1,6,5,40,66,4,7,8,76,44,9,13,10,11,14,74,12,79,57,15,16,47,72,55,48,17,18,19,73,32,80,63,62,20,21,36,70,101,25,39,26,50,27,29,78,22,28,51,2,24,41,53,30,84,31,42,67,75,83,59,92,69,82,33,37,65,23,49,81,43,61&count=10000&size=medium&rating=All&delimeter=%7C&fields=url,categories,title,duration,thumbnail&period=all_time&order=mr&format=csv&utm_source=paid&utm_medium=hubtraffic&utm_campaign=hubtraffic_tribalmolecule')
    newline_delimited_info = response.read().split('\r\n')

    db = MySQLdb.connect("localhost", "root", "123456", "tubehigh")
    cursor = db.cursor()

    for pipe_delimited_info in enumerate(newline_delimited_info):
        index = pipe_delimited_info[0]
        info = pipe_delimited_info[1].split('|')
        if len(info) != 5:
            continue
        video_url = info[0]
        cat_list = info[1].split(';')
        duration = info[3]
        title = info[2]
        jpeg_url = info[4]

        # Make categories unique
        for cat in cat_list:
            if len(cat.strip()) == 0:
                continue
            category_set.add(cat)
            # Video deatils into dict. Key is the index. 1 video = n categories
            video_dict[index] = {}
            video_dict[index]['title'] = title
            video_dict[index]['jpeg_url'] = jpeg_url
            video_dict[index]['video_url'] = video_url
            video_dict[index]['duration'] = time.strftime("%M:%S", time.gmtime(int(duration)))
            video_dict[index]['category'] = cat
            video_dict[index]['site'] = 'pornhub.com'

    # Convert the unique categories into tuples for executemany
    for cat in category_set:
        cat = (cat,)
        category_list.append(cat)

    # Write the categories into the Category table
    try:
        category_insert_sql = '''INSERT IGNORE INTO `category` (name) values (%s)'''
        cursor.executemany(category_insert_sql, category_list)
        db.commit()
    except Exception, e:
        print e

    # Read the newly written categories with their id
    try:
        category_read_sql = '''SELECT id, name from category'''
        cursor.execute(category_read_sql)
        rows = cursor.fetchall()
        for row in rows:
            category_dict[row[1]] = int(row[0])
    except Exception, e:
        print e

    # Replace the category name from video_dict to category id (FK)
    for k, v in video_dict.iteritems():
        v.update({'category': category_dict[v['category']]})
        # Reformat video_dict into executemany format
        video_tuple = (v['category'], v['title'], v['jpeg_url'], v['video_url'], v['duration'], v['site'])
        video_list.append(video_tuple)

    # Write the video_list into database
    try:
        video_insert_sql = '''INSERT IGNORE INTO video (category_id, title, thumbnail_url, video_url, duration, site) values (%s, %s, %s, %s, %s, %s)'''
        cursor.executemany(video_insert_sql, video_list)
        db.commit()
    except Exception, e:
        print e

    db.close()
