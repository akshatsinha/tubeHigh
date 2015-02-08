import json
import MySQLdb

from django.shortcuts import render_to_response
from django.http import HttpResponse


def categories(request):
    category_response = {}
    db = MySQLdb.connect("localhost", "root", "", "tubehigh")
    cursor = db.cursor()

    # Get all the categories from Category table
    try:
        category_read_sql = '''
select cat.id, cat.name, vid.thumbnail_url
from video vid
inner join category cat
on vid.category_id = cat.id
group by vid.category_id, vid.site
'''
        cursor.execute(category_read_sql)
        rows = cursor.fetchall()
        for row in rows:
            category_response[row[0]] = {}
            category_response[row[0]]['category_name'] = row[1]
            category_response[row[0]]['category_thumbnail'] = row[2]
            category_response[row[0]]['category_url'] = '/#/category/%s/' % (row[1].replace(' ', '').lower())
    except Exception, e:
        print e

    db.close()
    return HttpResponse(json.dumps(category_response), content_type="application/json")


def videobycategory(request, category):
    db = MySQLdb.connect("localhost", "root", "", "tubehigh")
    cursor = db.cursor()
    category_dict = {}
    video_response = {}

    # Get all categories from the database
    try:
        category_read_sql = '''SELECT id, name from category'''
        cursor.execute(category_read_sql)
        rows = cursor.fetchall()
        for row in rows:
            category_name_normalized = row[1].replace(' ', '').lower()
            category_dict[category_name_normalized] = int(row[0])
    except Exception, e:
        print e

    # Find the id of the category that came from the URL
    if category in category_dict:
        category_id = category_dict[category]
    else:
        category_id = 1

    # Get all videos for the category
    try:
        video_read_sql = '''
select id, title, thumbnail_url, video_url, duration
from video
where category_id = %s
''' % (category_id)
        cursor.execute(video_read_sql)
        rows = cursor.fetchall()
        for row in rows:
            video_response[row[0]] = {}
            video_response[row[0]]['title'] = row[1]
            video_response[row[0]]['thumbnail_url'] = row[2]
            video_response[row[0]]['video_url'] = row[3]
            video_response[row[0]]['duration'] = row[4]
    except Exception, e:
        print e

    db.close()
    return HttpResponse(json.dumps(video_response), content_type="application/json")
