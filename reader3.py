#!/usr/bin/python

import psycopg2,datetime

#connecting to the database
try:
    conn="host='152.1.58.206' port=5432 dbname='postgres' user='postgres' password='ssr'"
    con=psycopg2.connect(conn)
    cur=con.cursor()
    connection_status="Connected"
except:
    connection_status="Not Connected"
    var=datetime.datetime.now().isoformat()
    var=var.replace(":"," ");var=var.replace("-"," ");
    with open('xaa3.out', 'w') as f:
        f.write("connection_status = No Connection Made\n" )
        f.write("timestamp_current = " + str(var) + "\n" )
        f.write("data_points = 0.00\n")
        f.write("current_average = 0.00\n")
        f.write("acceleration_x_average = 0.00\n")
        f.write("acceleration_y_average = 0.00\n")
        f.write("acceleration_z_average = 0.00\n")
        f.write("comment = ERROR Is the server running on host 152.1.58.206 and accepting connections at port 5432")


#input extraction
if connection_status=="Connected":
    input=open('xaa3','r')
    #print('a')
    input_init=input.readlines()
    time_period=float(input_init[3][13:(len(input_init[3])-1)])
    if 'HAAS' in input_init[1]:
        machine_name='HAAS-VF2'
    if 'MAZAK' in input_init[1]:
        machine_name='MAZAK-M7303290458'
    #print('a')
    times=datetime.datetime.now()-datetime.timedelta(hours=time_period)

    timestamp_begin= str(input_init[0][17:(len(input_init[0])-1)])
    timestamp_begin=timestamp_begin.replace(" ","")
    timestamp_begin=timestamp_begin.replace("Y","-")
    timestamp_begin=timestamp_begin.replace("H",":")
    #print(timestamp_begin)
    #print('a')
    timestamp_end= str(input_init[2][15:(len(input_init[2])-1)])
    timestamp_end=timestamp_end.replace(" ","")
    timestamp_end=timestamp_end.replace("Y","-")
    timestamp_end=timestamp_end.replace("H",":")

    #query to identify the time range
    con.rollback()
    if len(timestamp_begin)>3 and len(timestamp_end)>3:
        cur.execute(""" SELECT * from login where machine_name='"""+str(machine_name)+"""' and timestamp>='"""+ str(timestamp_begin)+"""' and timestamp<='"""+ str(timestamp_end)+"""' order by timestamp desc""")
        b=cur.fetchall()
        #print(b)
        cur.execute(""" SELECT * from login where machine_name='"""+str(machine_name)+"""' and machine_status='OFF' and timestamp>='"""+ str(timestamp_begin)+"""' and timestamp<='"""+ str(timestamp_end)+"""' order by timestamp desc""")
        c=cur.fetchall()
        #print(c)
    else:
        cur.execute(""" SELECT * from login where machine_name='"""+str(machine_name)+"""' and timestamp>='"""+ str(times.isoformat())+"""' order by timestamp desc""")
        b=cur.fetchall()
        #print(b)
        cur.execute(""" SELECT * from login where machine_name='"""+str(machine_name)+"""' and machine_status='OFF' and timestamp>='"""+ str(times.isoformat())+"""' order by timestamp desc""")
        c=cur.fetchall()
        #print(c)

    temp=open('Sensorfile.txt','wb')
    const=1
    try:
        for x in range(0,len(c)):
            if b[0][3]=='OFF':
                if x!=0:
                    #print 'st'
                    cur.execute(""" SELECT timestamp,sensor_file from sensorfile where timestamp>='"""+ str(b[(b.index(c[x])-1)][1])+"""' and timestamp<='"""+ str(c[x-1][1])+"""' order by timestamp desc""")
                    a=cur.fetchall()
                    for y in range(len(a),0,-1):
                        temp.write(a[y-1][1])
                        #print('a1')
        
            if b[0][3]=='ON':
                if x==0:
                    #print 'sta'
                    if len(timestamp_begin)>3 and len(timestamp_end)>3:
                        cur.execute(""" SELECT timestamp,sensor_file from sensorfile where timestamp>='"""+ str(b[(b.index(c[x])-1)][1])+"""' and timestamp<='"""+ str(timestamp_end)+"""' order by timestamp desc""")
                        a=cur.fetchall()
                    else:
                        cur.execute(""" SELECT timestamp,sensor_file from sensorfile where timestamp>='"""+ str(b[(b.index(c[x])-1)][1])+"""' and timestamp<='"""+ str(datetime.datetime.now().isoformat())+"""' order by timestamp desc""")
                        a=cur.fetchall()  
                    for y in range(len(a),0,-1):
                        temp.write(a[y-1][1])
                        #print('a4')
                if x!=0:
                    cur.execute(""" SELECT timestamp,sensor_file from sensorfile where timestamp>='"""+ str(b[(b.index(c[x])-1)][1])+"""' and timestamp<='"""+ str(c[x-1][1])+"""' order by timestamp desc""")
                    a=cur.fetchall()
                    for y in range(len(a),0,-1):
                        temp.write(a[y-1][1])
                        #print('a3')

        if b[len(b)-1][3]=='ON':
            cur.execute(""" SELECT timestamp,sensor_file from sensorfile where timestamp>='"""+ str(b[len(b)-1][1])+"""' and timestamp<='"""+ str(c[len(c)-1][1])+"""' order by timestamp desc""")
            a=cur.fetchall()
            for y in range(len(a),0,-1):
                temp.write(a[y-1][1])
                #print('a5')
    except:
        "Nothing"

    temp.close()
    
    #calculating averages
    try:
        curr=float(0)
        accx=float(0)
        accy=float(0)
        accz=float(0)
        s=0
        openfile=open('Sensorfile.txt','r')
        readfile=openfile.readlines()
        for line in readfile:
            if len(line)>47:
                reading=line.split('\t')    
                curr=curr+float(reading[0])
                accx=accx+float(reading[1])
                accy=accy+float(reading[2])
                accz=accz+float(reading[3])

                s+=1

        curr=curr/s
        accx=accx/s
        accy=accy/s
        accz=accz/s
        
    except:
        'nothing'
    
    if len(b)>0:
        var=datetime.datetime.now().isoformat();var=var.replace(":"," ");var=var.replace("-"," ");
        with open('xaa3.out', 'w') as f:
            f.write("connection_status = Connected\n" )
            f.write("timestamp_current = " + str(var) + "\n" )
            f.write("data_points = " + str(s) + "\n")
            f.write("current_average = "+str(curr)+"\n")
            f.write("acceleration_x_average = "+str(accx)+"\n")
            f.write("acceleration_y_average = "+str(accy)+"\n")
            f.write("acceleration_z_average = "+str(accz)+"\n")
            f.write("comment = Successful Execution")
    else:
        var=datetime.datetime.now().isoformat();var=var.replace(":"," ");var=var.replace("-"," ");
        with open('xaa3.out', 'w') as f:
            f.write("connection_status = Connected\n" )
            f.write("timestamp_current = " + str(var) + "\n" )
            f.write("data_points = 0.00\n")
            f.write("current_average = 0.00\n")
            f.write("acceleration_x_average = 0.00\n")
            f.write("acceleration_y_average = 0.00\n")
            f.write("acceleration_z_average = 0.00\n")
            f.write("comment = No data found for the given set of inputs")
       







