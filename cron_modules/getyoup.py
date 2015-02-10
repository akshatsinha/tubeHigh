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

    response = urllib2.urlopen('http://www.youporn.com/videodump/output/?keywords=&categories=63,1,2,3,4,6,7,5,51,9,52,10,11,12,13,37,15,16,44,8,48,17,42,18,62,19,20,58,50,21,65,46,22,23,66,25,41,40,49,26,29,64,55,28,36,56,57,30,53,43,61,54,31,27,60,39,47,59,32,38,33,34,35,45&limit=200&thumbnailsize=240x180&rating=All&delimiter=%7C&fields=url,categories,title,duration,main_thumbnail,flipbook&period=alltime&orderby=rating&exportformat=CSV&utm_source=paid&utm_medium=hubtraffic&utm_campaign=hubtraffic_tribalmolecule')
    newline_delimited_info = response.read().split('\n')

    db = MySQLdb.connect("localhost", "root", "123456", "tubehigh")
    cursor = db.cursor()

    for pipe_delimited_info in enumerate(newline_delimited_info):
        index = pipe_delimited_info[0]
        info = pipe_delimited_info[1].split('|')
        if len(info) != 6:
            continue
        video_url = info[0]
        cat_list = info[1].split(';')
        title = info[2]
        duration = info[3]
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
            video_dict[index]['site'] = 'youporn.com'

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
