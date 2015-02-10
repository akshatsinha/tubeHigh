import urllib2
import json
import MySQLdb

if __name__ == '__main__':
    category_set = set()
    category_list = []
    category_dict = {}
    video_tuple = ()
    video_list = []
    video_dict = {}

    response = urllib2.urlopen('http://www.redtube.com/_status/export.php?search=&categories=1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.31.32.33.34.35&limit=10000&thumb_size=p&min_rating=0&delimiter=%7C&embed=&include_url=1&include_categories=1&include_duration=1&include_title=1&added_before_x_days=0&thumbs=1&order_by=time&export=csv&do=export&utm_source=paid&utm_medium=hubtraffic&utm_campaign=hubtraffic_tribalmolecule')
    newline_delimited_info = response.read().split('\n')
    newline_delimited_info = newline_delimited_info[1:]

    db = MySQLdb.connect("localhost", "root", "123456", "tubehigh")
    cursor = db.cursor()

    for pipe_delimited_info in enumerate(newline_delimited_info):
        index = pipe_delimited_info[0]
        info = pipe_delimited_info[1].split('|')
        if len(info) != 6:
            continue
        jpeg_url = info[0]
        video_url = info[1]
        title = info[2]
        cat_list = info[3].split(';')
        duration = info[4]

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
            video_dict[index]['duration'] = duration
            video_dict[index]['category'] = cat
            video_dict[index]['site'] = 'redtube.com'

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
