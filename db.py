from deta import Deta
a = "c02ff9ee_aRR2Gi3m4xe76"
deta = Deta(a+"F8txNbk77WqghL4nKKs")

# user table
# user = deta.Base("Notecaster_User")
# user = next(user.fetch({"username": "devangk22"}))

drive = deta.Drive("Notecaster_Subject")

that = drive.list()['names'][0].size()

f = open("demofile2.jpeg", "w")
f.write(that)
f.close()

print(drive.list())


