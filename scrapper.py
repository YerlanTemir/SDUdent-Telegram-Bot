from selenium import webdriver
import secret_data as sd
from time import sleep
from bs4 import BeautifulSoup
import datetime
import json
from json import JSONEncoder
from JsonUtils import DateTimeDecoder,DateTimeEncoder


class Subject:

    def __init__(self,title,teacher_name,room,timeAtt):
        
        self.title = title
        self.teacher_name = teacher_name
        self.room = room
        self.timeAtt = timeAtt.split(':')
        self.time = datetime.time(int(self.timeAtt[0]),int(self.timeAtt[1]),00)
        self.time = json.loads(json.dumps(self.time,cls = DateTimeEncoder),cls = DateTimeDecoder)
    
    def json_serial(self,obj):

        if isinstance(obj, (datetime.datetime, datetime.time)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    
    
    def __lt__ (self, other):
        return self.time < other.time
        
    def __repr__(self):
        return '{},{},{},{}'.format(self.title,self.teacher_name,self.room,self.time)

    def __eq__ (self, other):
        return self.time == other.time


class SubjectEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Subject):
            return o.__dict__
        return json.JSONEncoder.default(self, o)

class Schedule:

    
    def __init__(self,username,password):

        self.username = username
        self.password = password
        self.login()        
    
    def login(self):

        self.driver = webdriver.Firefox()
        self.driver.get('https://my.sdu.edu.kz/')
        self.driver.find_element_by_id("username").send_keys(self.username)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.driver.find_element_by_class_name("q-button").click()
    
    def get_grades_data(self):
        
        self.driver.find_element_by_css_selector(".leftLinks a[href^='?mod=grades'] ").click()
        sleep(2)

        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")        
        soup = BeautifulSoup(html,'lxml')

        lists = soup.find('div',id='divShowStudGrades').find_all('tr')[2:-1]

        grades = {}

        
        
        for index in range(len(lists)) :

            tds = lists[index].find_all('td')
            name = tds[4].text
            grade = tds[8].text.strip()
            grades[index] = {'name':name,'grade':grade}
        
        return grades


    def get_schedule_data(self):
        
        self.driver.find_element_by_css_selector(".leftLinks a[href^='?mod=schedule'] ").click()
        sleep(2)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html,'lxml')
        
        lists = soup.find('div',id='div_results').find_all('tr')
        weekdays = {1:[],
                    2:[],
                    3:[],
                    4:[],
                    5:[],
                    6:[]}

        
        
        for i in range(1,len(lists)):
            
            tds = lists[i].find_all('td')

            for j in range(1,len(tds)):
                
                span = tds[j].find('span')

                if(len(span) == 1):
                    continue

                
                title = span.find('a')["title"]
                
                imgs = span.find_all('img')
                teacher_name = imgs[0]["title"]
                
                room = imgs[1]["title"]
                
                time = tds[0].find('span').text
                subject = json.dumps(Subject(title,teacher_name,room,time),cls=SubjectEncoder)

                weekdays[j].append(subject) 

        return weekdays               
                
    


