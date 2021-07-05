import re
import numpy as np
import pandas as pd
import mysql.connector
from cryptography.fernet import Fernet
import http.server
import socketserver
import urllib
import io
import logging
import traceback
import ntpath
from tabulate import tabulate
from bs4 import BeautifulSoup
from functions import *
#-----------------------------------Connector-----------------------------------#
PORT_NUMBER=8000

COLUMNS=["Ser","EngHrs","Vibration","CoolantTemp","OilPressure"] #Ser,EngHrs,Vibration,CoolantTemp,OilPressure
RECORDS_ALL=[[0.0], [0.0], [0.0], [0.0],[0.0]]

x = str()
y = 'Dentist'
q = {'id' : ['1'], 'submit' : ['']}

#----------------------------------------------------------------#

cipher_suite = Fernet(b'VFJNZCQxNQn-nBxMyowGa8XyVGcrN7eTQPU3SQz8urk=')   
with open(r'C:\Users\tharu\Desktop\PS-1\pwds\mssqltip_bytes.bin', 'rb') as file_object:
    for line in file_object :
        encryptedpwd = line
unciphered_text = (cipher_suite.decrypt(encryptedpwd))

db1 = mysql.connector.connect(
        host = 'LAPTOP-7L7HJAIG',
        user = 'root',
        password = bytes(unciphered_text).decode('utf-8'),
        database = 'patient_records' )
cur1 = db1.cursor() 

db2 = mysql.connector.connect(
        host = 'LAPTOP-7L7HJAIG',
        user = 'root',
        password = bytes(unciphered_text).decode('utf-8'),
        database = 'standard_values' )
cur2 = db2.cursor()

#------------------------------------------------------------------#

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        global model
        global q
        global x

        print(self.path)
        self.connection.settimeout(1)
        if self.path.endswith('.png') or self.path.endswith('.ico'):
            self.send_response(200)
            self.send_header('Content-type','image/png')
            self.end_headers()
            file = ntpath.basename(self.path)
            with open(file, 'rb') as myfile:
                html=myfile.read()
            self.wfile.write(bytes(html))

        elif self.path.endswith('.js') or self.path.endswith('.map'):
            self.send_response(200)
            self.send_header('Content-type','text/javascript')
            self.end_headers()
            file = ntpath.basename(self.path)
            with open(file, 'r') as myfile:
                html=myfile.read()
            self.wfile.write(bytes(html, "utf8"))

        elif self.path.endswith('.css'):
            self.send_response(200)
            self.send_header('Content-type','text/css')
            self.end_headers()
            file = ntpath.basename(self.path)
            with open(file, 'r') as myfile:
                html=myfile.read()
            self.wfile.write(bytes(html, "utf8"))

        elif self.path.endswith('/') or self.path.endswith('?'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            with open('./index.html', 'r') as myfile:
                html=myfile.read()
            self.wfile.write(bytes(html, "utf8"))

        elif self.path.endswith('.mp4'):
            self.send_response(200)
            self.send_header('Content-type','application/mp4')
            self.end_headers()
            with open('./yashodha_hospitals.mp4', 'rb') as myfile:
                html=myfile.read()
            self.wfile.write(html)

        elif 'submit' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            o = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(o.query)
            print(o)
            print(q)
            
            flag = 0
            
            # add cur1 and cur2
                
            #--------------------------------------------------------------------------------#
            
            #patient_id = 123456
            print(q)
            patient_id = q.get('id')
            patient_id = int(patient_id[0])
            #patient_id = int(q.get('id', ['1'])[0])  # will be given by frontend
            print(patient_id)
            
            #--------------------------------------------------------------------------------- #
            
            cur1.execute("SELECT * FROM patient_details WHERE id='%s';" %patient_id)
            patient_details = pd.DataFrame(cur1.fetchall())
            
            if patient_details.empty :
                self.send_response(200)
                #self.send_header('Content-type','text/css')
                #self.end_headers()

                with open('./intermediate.html', 'r') as myfile:
                    html=myfile.read()
                    #html=html.replace('$RESULT', x)
                self.wfile.write(bytes(html, "utf8"))
                
                #print('Patient id not found')
                '''cur1.close()
                db1.close()
                cur1.close()
                db1.close()'''
            else :
                patient_details.columns = cur1.column_names
                
                gender = patient_details.at[0, 'Gender']
                age = patient_age(patient_details.at[0, 'Age'])
                package = patient_details.at[0, 'Package']
                cur1.execute("SELECT `Consultants` FROM `consultation` WHERE `Package` = '%s';" %package)
                y = cur1.fetchall()
                cur1.execute("SELECT `Name` FROM patient_details WHERE id = '%s';" %patient_id)
                name = cur1.fetchall()
                
                patient_report = from_database(cur1, cur2, patient_id)
                # patient_reports is the name of the database where all the information about patient is stored
                # patient id will be the name of the table where results of his/her tests will be stored
            
                column_check = 'Verdict' in patient_report
                if column_check :
                    assign=tabulate(patient_report, headers='keys', tablefmt='html')
                    soup=BeautifulSoup(assign, 'html.parser')
                    x = soup.prettify()
                    print(type(x))
            
                else :
                    patient_report = patient_report.replace(np.nan, '', regex = True)
                    test = patient_report['Test']
                    
                    patient_verdict=patient_report
                    patient_verdict['Verdict']=patient_verdict['Analytes']
                    test = patient_report['Test']
                    
                    k = 0
                    test_num = 0
                    test_len = len(test)
                    patient_tests = []
                    
                    while k in range(test_num, test_len) :
                        if (test[k] == '' or test[k] == test[test_num]):
                            k = k+1
                        else :
                            patient_tests.append([test_num, test[test_num], k])
                            test_num = k
                            k = k+1
                    patient_tests.append([test_num, test[test_num], k])
                    i = 0
                    z = 0
                          
                    for i in range(len(patient_tests)):
                        test_taken = patient_tests[i][1]
                        test_taken = test_taken.lower().split(' ')
                        test_taken = '_'.join(test_taken)
                        normal_report = from_database(cur1, cur2, test_taken)
                        if type(normal_report) == str :
                            patient_verdict.at[z,'Verdict']=''
                            z = z+1
                            continue
                        else :
                            pass
                        normal_report = normal_report.replace(np.nan, '', regex = True)
                        
                        start = patient_tests[i][0]
                        end = patient_tests[i][2]
                        analytes = patient_report.iloc[start:end, 1]
                            
                        for z in range(start, end):
                            j = 0
                            flag = 0
                            patient = patient_report.at[z, 'Results']
                            
                            while j < (len(normal_report)):
                        
                                if (analytes[z] == normal_report.at[j, 'Analytes']):
                                    normal = normal_report.at[j, 'Reference Intervals']
                                    if normal_report.at[j, 'Age'] == '' :
                                        if normal_report.at[j, 'Gender'] == '' :
                                            flag, j = check(patient_verdict, normal_report, z, normal, patient, j)
                                        else :
                                            if gender.lower() == normal_report.at[j, 'Gender'].lower() :
                                                flag, j = check(patient_verdict, normal_report, z, normal, patient, j) 
                                            else :
                                                j = j+1
                                    else :
                                        a, b = extract(normal_report.at[j, 'Age'])
                                        if a <= float(age) and float(age) <= b :
                                            if normal_report.at[j, 'Gender'] == '' :
                                                flag, j = check(patient_verdict, normal_report, z, normal, patient, j)
                                            else :
                                                if gender.lower() == normal_report.at[j, 'Gender'].lower() :  
                                                    flag, j = check(patient_verdict, normal_report, z, normal, patient, j)                            
                                                else :
                                                    j = j+1
                                        else :
                                            j = j+1
                                else:
                                    j = j+1
                                
                                if flag == 1:
                                    break
                                else:
                                    pass
                
                                if (j == len(normal_report)) and flag == 0:
                                    if patient == '' :
                                        patient_verdict.at[z,'Verdict']=''
                                    elif  normal == 'NIL' :
                                        patient_verdict.at[z,'Verdict']=''
                                    else :
                                        patient_verdict.at[z,'Verdict']='Abnormal'
                                else :
                                    pass
                        z = z+1
                    
            #------------------------adds patient verdict table to database------------------------#
                    
                    '''cur1.execute("DELETE FROM `%d`;" %patient_id)
                    cur1.execute("ALTER TABLE `%d` ADD Verdict text;" %patient_id)
                    for (row, rs) in patient_verdict.iterrows() :
                        Test = str(rs[0])
                        Analytes = str(rs[1])
                        Results = str(rs[2])
                        Verdict = str(rs[4])
                        Comments = str(rs[3])
                        query = "INSERT INTO `{5}` VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(Test, Analytes, Results, Comments, Verdict, patient_id)
                        cur1.execute(query)'''
                    '''db1.commit()
                    cur1.close()
                    db1.close()
                    cur1.close()
                    db1.close()'''
                    
            #--------------------------------------------------------------------------------------#   
                
                    assign=tabulate(patient_verdict, headers='keys', tablefmt='html', numalign='left', stralign='left')
                    soup=BeautifulSoup(assign, 'html.parser')
                    x = soup.prettify()
                    print(type(x))
                    
                

                with open('./result.html', 'r') as myfile:
                    html=myfile.read()
                    html=html.replace('$RESULT', x)
                    html=html.replace('$DEP', y[0][0].upper())
                    #html=html.replace('$DEP', 'Physician')
                    html=html.replace('$NAME', 'Name : ' + name[0][0])
    
                self.wfile.write(bytes(html, "utf8"))

        elif 'Exit' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            o = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(o.query)
            
            

            with open('./index.html', 'r') as myfile:
                html=myfile.read()

            self.wfile.write(bytes(html, "utf8"))
        else:
            print("Unknown request " + self.path)
        return
 
#---------------------------------------------------------------------------#
        
'''try:
    print('Server listening on port 8000...')
    httpd = socketserver.TCPServer(('', PORT_NUMBER), Handler)
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.socket.close()'''
    
#-----------------------------------Model-----------------------------------#


#-----------------------------------View-----------------------------------#
try:
    print('Server listening on port 8000...')
    httpd = socketserver.TCPServer(('', PORT_NUMBER), Handler)
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.socket.close()

db1.commit()
cur1.close()
db1.close()
cur1.close()
db1.close()


