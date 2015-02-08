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

    response = urllib2.urlopen('http://partners.xhamster.com/2export.php?ch=!.150.189.151.190.152.191.153.154.155.192.156.193.194.217.106.195.157.158.196.159.160.161.162.163.164.197.165.166.115.167.168.198.169.170.171.199.141.200.201.172.202.173.174.175.203.80.177.178.179.180.204.205.206.181.207.218.208.82.182.209.210.183.211.184.212.131.185.214.186.216.187.188&cnt=4&tcnt=1&tmb=3&url=on&dlm=%7C&ttl=on&chs=on&sz=on')
    newline_delimited_info = response.read().split('\r\n')
    # Skip the first title line ['#THUMB', '#URL', '#TITLE', '#CHANNEL', '#DURATION', '']
    newline_delimited_info = newline_delimited_info[1:]

    db = MySQLdb.connect("localhost", "root", "", "tubehigh")
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
            video_dict[index]['site'] = 'xhamster.com'

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
