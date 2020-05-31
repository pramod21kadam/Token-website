import sqlite3
from datetime import datetime, timedelta

class dbhandler:
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute('CREATE TABLE IF NOT EXISTS admintable (username TEXT PRIMARY KEY, password TEXT, starttime TEXT, endtime TEXT, numberof_tokens NUMBER)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS user (username TEXT, contact NUMBER,date TEXT, time_from TEXT, time_to TEXT, token_no INT, status TEXT)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS token (time_from TEXT UNIQUE, time_to TEXT UNIQUE, numberoftokens INT, remainingtokens INT, status TEXT)')
        self.conn.execute(f'CREATE TRIGGER IF NOT EXISTS change_status AFTER UPDATE ON token FOR EACH ROW BEGIN UPDATE token SET status = "booked" WHERE remainingtokens = 0; END;')
        self.conn.commit()
        # print("Trigger created..")

    def login(self, username, password):
        if 1 == self.conn.execute(f'Select count(*) from admintable where username = "{username}" and password = "{password}"').fetchone()[0]:
            return True
        else:
            return False

    def signup(self, username, password):
        try:
            self.conn.execute(f'Insert into admintable(username, password) values("{username}","{password}")')
            self.conn.commit()
            self.insert()
            return True
        except sqlite3.IntegrityError:
            self.insert()
            return True
        return False

    def searchtoken(self, username, number):
        result = self.cursor.execute(f'select time_from,time_to,token_no from user where username ="{username}"').fetchone()
        if result != None:
            return True,result
        return False,None

    def tokentable(self,username, number, time_from, time_to, number_of_tokens, status="open"):
        try:
            token = self.searchtoken(username,number)
            if token[1] == None:
                self.conn.execute(f'INSERT INTO token VALUES("{time_from}", "{time_to}", {number_of_tokens}, {number_of_tokens}, "{status}" )')
                self.conn.commit()
                return True
            else:
                return token[1]
        except:
            return False

    def showTable(self, table, condition=''):
        print(f'{table} :')
        result = self.cursor.execute(f'SELECT * FROM {table} {condition}').fetchall()
        # for i in result:
        #     print(i)
        print(result)
    def executeDB(self, cmd, type = "exe",commit = False):
        if type == "exe":
            try:
                    result = self.conn.execute(cmd)
                    if commit:
                        self.conn.commit()
                        print(result)
                    print("Executed")
                    return
            except:
                print("Already executed")
                return
        else:
            result = self.cursor.execute(cmd).fetchall()
            for i in result:
                print(i)
            return
    
    def gettoken(self, username, number, time_from, time_to):
        now = datetime.strptime(datetime.now().strftime("%I:%M %p"), "%I:%M %p")
        date = datetime.now().strftime("%d-%m-%Y")
        if now < datetime.strptime(time_to, "%I:%M %p"):
            result = self.conn.execute(f'SELECT numberoftokens,remainingtokens FROM token WHERE time_from = "{time_from}"').fetchone()
            self.conn.execute(f'INSERT INTO user values("{username}", "{number}","{date}","{time_from}", "{time_to}", {result[0]-result[1] + 1}, "active")')
            self.conn.execute(f'UPDATE token SET remainingtokens = remainingtokens-1 WHERE time_from = "{time_from}";')
            self.conn.commit()
            token_number = result[0]-result[1] + 1
            return True, token_number
        else:
            print("Invalid time")
            return False, None

    def checkusername(self, username):
        if self.cursor.execute(f"SELECT COUNT(*) FROM admintable WHERE username ='{username}'").fetchone()[0] == 0:
            return False
        else:
            return True

    def gettimeslots(self):
        return self.cursor.execute(f'SELECT time_from, time_to FROM token WHERE status = "open"').fetchall()

    def insert(self):
        now = "06:00 AM"
        then = datetime.strftime( datetime.strptime(now, "%I:%M %p") + timedelta(seconds=3600), "%I:%M %p" )
        for i in range(24):
            try:
                self.conn.execute(f'INSERT INTO token values( "{now}","{then}",25,25,"open" )')
                self.conn.commit()
            except:
                continue
            now = then 
            then = datetime.strftime( datetime.strptime(now, "%I:%M %p") + timedelta(seconds=3600), "%I:%M %p" )
        print("done")

    def getalltimeslots(self):
        return self.cursor.execute(f'SELECT * FROM TOKEN').fetchall()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def users(self):
        result = self.conn.execute(f" SELECT date as date,count(username) as users from user group by date").fetchall()
        data = [["Date", "customers"]]
        for i in result:
            data.append(list(i))
        return data

if __name__ == "__main__":
    d = dbhandler()
    d.showTable("token")
    d.users()
    # print(d.checkusername("a"))
    # print(d.gettimeslots())
    # now = "09:00 AM"
    # then = datetime.strftime( datetime.strptime(now, "%I:%M %p") + timedelta(seconds=3600), "%I:%M %p" )
    # for i in range(10):
    #     d.executeDB(f'INSERT INTO If NOT EXISTS token values( "{now}","{then}",25,25,"open" )',commit=True)
    #     now = then 
    #     then = datetime.strftime( datetime.strptime(now, "%I:%M %p") + timedelta(seconds=3600), "%I:%M %p" )

