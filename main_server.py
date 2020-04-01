import socket
import sqlite3






def Main():

    port = 4000
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print(socket.gethostbyaddr(socket.gethostname()))
    s.bind((socket.gethostbyaddr(),port))

    print("Server started")
    while True:
        reg_db = sqlite3.connect("reg_db.db")
        reg_db_cur = reg_db.cursor()

        unp_db = sqlite3.connect("unp_db.db")
        unp_db_cur = unp_db.cursor()

        '''first quadrant table : f_q_table
           second quadrant table : s_q_table
           third quadrant table : t_q_table
           fourth quadrant table : fourth_q_table'''

        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        data = eval(data)

        if data[0] == "acc":
            data.remove(data[0])
            username = data[0].lower()
            email = data[1].lower()

            email = email.replace("@","_")


            password = data[2].lower()

            success = None

            unp_db_cur.execute("SELECT email FROM accounts where email = "+"'"+email+"'")
            res = unp_db_cur.fetchall()
            if len(res) == 0:
                try:

                    unp_db_cur.execute("INSERT INTO accounts values("+"'"+email+"',"+" '"+username+"', "+"'"+password+"')")
                    unp_db.commit()
                    unp_db_cur.execute("SELECT * FROM accounts")
                    print(unp_db_cur.fetchall())
                    s.sendto("ACCOUNT CREATED".encode("utf-8"),addr)

                except:
                    print("DATABASE REGISTRATION ERROR")
            elif len(res) ==1:
                print("email associated with account already exist")



        elif data[1] == "ch_acc_cred":
            email_ch = data[0][0].replace("@","_")
            name_ch = data[0][1]
            pw_ch = data[0][2]

            unp_db_cur.execute("SELECT * FROM accounts WHERE email ="+"'"+email_ch+"'")
            ch_res = unp_db_cur.fetchall()

            if ch_res == [] :
                print("no accounts associated with the email")
                s.sendto("error_lia".encode("utf-8"), addr)
            elif  ch_res[0][2]== pw_ch:
                print("Login success")
                s.sendto(str(["verified",ch_res[0][1]]).encode("utf-8"),addr)


        elif data[0] == "tr_reg":
            lat = data[1][0]
            lon = data[1][1]

            if lon >= 0 and lat >= 0:
                print("INSERT INTO f_q_table values('"+str(lon)+"', '"+str(lat)+")")
                reg_db_cur.execute("INSERT INTO f_q_table values('"+str(lon)+"', '"+str(lat)+"')")
        else:

            print("message from : ", addr)
            print("message : ",data)

            temp = data

        # the data from the client is of the form [[lo,lo*],[la,la*]]
            lo = temp[0][0]
            lo_p = temp[0][1]
            la = temp[1][0]
            la_p = temp[1][1]

            text = ""
            if lo >= 0 and la >=0:
                text = "FIRST QUADRANT"
                print(text)
                reg_db_cur.execute("SELECT DISTINCT * FROM f_q_table WHERE lon > %s AND lon < %s AND lat > %s AND lat < %s"%(lo,lo_p,la,la_p))
                coordinates = reg_db_cur.fetchall()

                coordinates = str(coordinates)
                print("sending : ", coordinates)
                s.sendto(coordinates.encode('utf-8'), addr)

            elif lo_p < 0 and la >= 0:
                text = "SECOND QUADRANT"
                print(text)
            elif lo_p < 0 and la_p < 0:
                text = "THIRD QUADRANT"
                print(text)
            elif lo >= 0 and la_p < 0:
                text = "FOURTH QUADRANT"
                print(text)
            else:
                text = "unidentified... but will find tomorrow"







if __name__ == "__main__":
    Main().run()

