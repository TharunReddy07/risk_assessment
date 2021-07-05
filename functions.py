import re
import pandas as pd

def extract(normal) :
    arr2 = re.split('-| ', normal)
    if arr2[1] == '' :
        arr2.remove(arr2[1])
        arr2.remove(arr2[1])
    a, b, c = float(arr2[0]), float(arr2[1]), arr2[2]
    if (c.lower() == 'hours') or (c.lower() == 'hour') :
        a = a/24
        b = b/24
        c = 'days'
    elif (c.lower() == 'weeks') or (c.lower() == 'week') :
        a = a*7
        b = b*7
        c = 'days'
    
    if (c.lower() == 'days') or (c.lower() == 'day') :
        a = a/360
        b = b/360
    elif (c.lower() == 'months') or (c.lower() == 'month') :
        a = a/12
        b = b/12
    else :
        pass
    return a, b

def check(patient_verdict, normal_report, z, normal, patient, j):
    var=re.compile(r'''
                   (([a-zA-Z]+\s?)+)?
                   ([0-9]+\.?([0-9]+)?)?
                   (>|<|-)?
                   ([0-9]+\.?([0-9]+)?)?
                   ''', re.VERBOSE)
    arr = list(var.match(normal).groups())
    print(arr, normal)
    if arr[0] != None :
        arr[0] = arr[0].strip().lower()
    else :
        pass
    if arr[1] != None :
        arr[1] = arr[1].lower()
    
    # positive/negative
    if (arr[1] == 'positive' or arr[1] == 'negative') :
        if patient.lower() == 'negative' or patient.lower() == 'positive' :
            flag = 1
            patient_verdict.at[z,'Verdict']= ''
        else :
            flag = 0
            j = j+1
        return flag, j
    # string type (like colors)
    elif arr[5] == None :
        if patient.lower() == normal.lower():
            flag = 1
            patient_verdict.at[z,'Verdict']= normal_report.at[j, 'Risk']
        else :
            flag = 0
            j = j+1
        return flag, j

    # string + greater than
    elif arr[4] == ">" :
        '''if arr[0] in patient_details :
            if (float(patient) > float(arr[3])) :
                flag = 1
                patient_verdict.at[z,'Verdict']= normal_report.at[j, 'Risk']
            else :
                flag = 0
                j = j+1'''
        if arr[0] == None :
            if (float(patient) > float(arr[5])) :
                flag = 1
                patient_verdict.at[z,'Verdict']= normal_report.at[j, 'Risk']
            else :
                flag = 0
                j = j+1
        else :
            flag = 0
            j = j+1    
        return flag, j
    # string + less than
    elif arr[4] == "<" :
        '''if arr[0] in patient_details :
            if (float(patient) < float(arr[3])) :
                flag = 1
                patient_verdict.at[z,'Verdict']= normal_report.at[j, 'Risk']
            else :
                flag = 0
                j = j+1'''
        if arr[0] == None :
            if (float(patient) < float(arr[5])) :
                flag = 1
                patient_verdict.at[z,'Verdict']= normal_report.at[j, 'Risk']
            else :
                flag = 0
                j = j+1
        else :
            flag = 0
            j = j+1    
        return flag, j
    # range
    elif arr[4] == '-' :
        a = float(arr[2])
        b = float(arr[5])
        if (a <= float(patient) and float(patient) <= b) :
            flag = 1
            patient_verdict.at[z,'Verdict']=normal_report.at[j, 'Risk']
        else :
            flag = 0
            j = j+1
        return flag, j

def patient_age(age) :
    age = re.split(' ', age)
    age_num = age[0]
    age_str = age[1]
    if (age_str.lower() == 'hours') or (age_str.lower() == 'hour') :
        age_num = age_num/24
        age_str = 'days'
    elif (age_str.lower() == 'weeks') or (age_str.lower() == 'week') :
        age_num = age_num*7
        age_str = 'days'
        
    if (age_str.lower() == 'days') or (age_str.lower() == 'day') :
        age = age_num/360
    elif (age_str.lower() == 'months') or (age_str.lower() == 'month') :
        age = age_num/12
    else :
        age = age_num
    return(age)


#----------------------pulls data from the database-------------------------------#
def from_database(cur1, cur2, table) :    
    
    if type(table) == int :
        cur1.execute("SELECT * FROM `%d`;" %table)
        sql_data = pd.DataFrame(cur1.fetchall())
        sql_data.columns = cur1.column_names
    else :
        cur2.execute("SHOW TABLES LIKE '%s';" %table)
        result = cur2.fetchone()
        if result :
            cur2.execute("SELECT * FROM `%s`;" %table)
            sql_data = pd.DataFrame(cur2.fetchall())
            sql_data.columns = cur2.column_names
        else :
            sql_data = 'no record'

    return(sql_data)  