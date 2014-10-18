from lib import is_windows
from config import server, player_id
from os import system

if is_windows:
    system(".\client.exe SubmitAnswer %s 1 %s solved.txt" % (server, player_id))
else:
    system("mono SubmitAnswer %s 1 %s solved.txt" % (server, player_id))