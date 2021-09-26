#!/usr/bin/python3

#
#
#pip3 install jira
#pip3 install gTTS
#pip3 install playsound
#
#

import getpass
from jira import JIRA
from gtts import gTTS
from jira.exceptions import JIRAError
from time import sleep
from sys import platform
from random import randint
from datetime import datetime
from tkinter import * 
from tkinter import messagebox
from itertools import compress
from tkinter.scrolledtext import ScrolledText
from queue import Empty,Full
from multiprocessing import Queue
import threading
import playsound
import os
import pathlib


if platform.startswith('win'):
    import winsound
    beep = winsound.Beep
elif platform.startswith('lin') or platform.startswith('dar'):
    import os
    def beep(freq,ms_duration):
        os.system(f'play -nq -t alsa synth {ms_duration} sine {freq/1000}')
else:
    raise OSError("Unknown Operating System! Not Unix or Windows?")#


class speaker():
    def __init__(self,TextPref="",Lang='en',PathPref="sounddb/CRT/"):
        self._TextPref = TextPref
        self._Lang = Lang
        self._PathPref = PathPref
        self._CrtSoundDict = self.default_map()
        self._make_path()

    def create_sound_db(self, Texts = 'NoneNull', Keys = 'NoneNull'):
        del self._CrtSoundDict
        self._CrtSoundDict = {}
        if Texts == 'NoneNull':
            Texts = speaker._Text
        if Keys == 'NoneNull':
            Keys = speaker._CRT
        if len(Texts) != len(Keys):
            raise KeyError("Text data and Key data differ in length!")
        for idx,Text in enumerate(Texts):
            File = self.speak(idx,Text,self._TextPref,self._Lang)
            self._CrtSoundDict[Keys[idx]] = File
            self.play_sound(self.get_db_text2sound_file(Keys[idx]))

    def speak(self,Idx,Text,Pref="",Lang='en'):
        Text2Speech = gTTS(text=f'{Pref} {Text}', lang=Lang)
        File = f'{self._PathPref}{Idx}-voice.mp3'
        Text2Speech.save(File)
        return File

    def play_sound(self,File):
        playsound.playsound(File)

    def get_db_text2sound_file(self,Text):
        if Text in self._CrtSoundDict.keys():
            return self._CrtSoundDict[Text]
        else:
            raise KeyError("Text is not known to sound database!")

    def db(self):
        return self._CrtSoundDict

    def language(self):
        return self._Lang
    def path(self):
        return self._PathPref
    def text_prefix(self):
        return self._Pref
    def set_language(self, Lang):
        self._Lang = Lang
    def set_path(self, Path):
        self._PathPref = Path

    def default_keys(self):
        return speaker._CRT

    def default_text(self):
        return speaker._Text

    def default_map(self):
        return speaker._FileMap

    def _make_path(self):
        pathlib.Path('sounddb/CRT/').mkdir(parents=True, exist_ok=True)

    def has_default_db(self):
        HasDB = True
        for Key in speaker._FileMap:
            if not pathlib.Path(speaker._FileMap[Key]).is_file():
                HasDB = False
        return HasDB

### PLEASE SPECIFY TO YOUR NEEDS! ###
    _CRT = [
        "Request_Type_1",
        "Request_Type_1"
    ]
    _Text = [
        "Incidient RT 1",
        "Important RT 2"
    ]
    _FileMap = {
        'Incidient RT 1': 'sounddb/CRT/1-voice.mp3',
        'Important RT 2': 'sounddb/CRT/2-voice.mp3',
    }

class Options:
### Customer Request Types of JSD ###
    CRT = [
        "\"Incidient RT 1 (<PROJEKTKEY>)\"",
        "\"Incidient RT 2 (<PROJEKTKEY>)\"",
    ]

    IgnoreUsers = ['userid1', 'userid2']
    def __init__(self,Selection=[True]*len(CRT)):
        self.select_jsd_crt(Selection)

    def jql(self):
        return self._JQL

    def set_jql(self,JQL):
        self._JQL = JQL;

    def select_jsd_crt(self,Selection=[True]*len(CRT)):
        self._JQL = Options.jql_function(Selection)

    def jql_function(Selection):
        if len(Selection) != len(Options.CRT):
            raise ValueError("There are more entries then Customer Request Types!")
        if sum(Selection) == 0:
            return 'project = <PROJECTKEY> AND assignee IS EMPTY ORDER BY created DESC'
        return f'project = PROJECTKEY> AND assignee IS EMPTY AND "Customer Request Type" in ({",".join(compress(Options.CRT,Selection))})  ORDER BY created DESC'


class jira_connector():
    def __init__(self,Server="https://my.jira-server.com/jira",Silent=False,Speak = speaker(),SoundOn = True):
        self._Server = Server
        self._Options = Options()
        self._Speaker = Speak
        self._Speak = SoundOn
        self._User = ""
        self._DisplayName = ""
        self._IssueHistory = set()
        self._HistoryCmd = []
        self._Output = print
        self._Errput = print
        self._connected = False
        self._Stop = False
        self._beep = beep if not Silent else jira_connector.void


        # User = Username; Pass = Password or Path to Cert(?)
    def connect(self, User, Pass):
        self._User = User
        self._connected = False
        if not self._Speaker.has_default_db():
            self._Errput("SoundDB setup","Speaker DB is setup; this will take some time.")
            self._Speaker.create_sound_db()
        try:
            self._Connection = JIRA(server=self._Server,auth=(self._User, Pass))
            self._Output(f'Connected to "{self._Connection.client_info()}".')
            self._DisplayName = self._Connection.myself()["displayName"]
            self._Output(f'Logged in for User \"{self._DisplayName}\".')
            self._connected = True
        except RecursionError:
            self._Errput("Recursion-Error","There is probably an error with wrong credentials!")
        except JIRAError as Exc:
            if Exc.status_code == 401:
                self._Errput("Credential-Error","Login to JIRA failed. Check your username and password")
            else:
                self._Errput("Error during connection",Exc)
        except Exception as Exc:
            self._Errput("General Error",Exc)

    def is_connected(self):
        return self._connected

    def close(self):
        if hasattr(self,'_Connection'):
            self._Connection.close()
        self._connected = False

    def jql_search(self,JQL):
        self._HistoryCmd.append(f"'{JQL}' at {datetime.now()}")
        return self._Connection.search_issues(JQL)

    def print_history(self):
        self._Output("\n".join(self._HistoryCmd))


    def history(self):
        return self._HistoryCmd
    def crt(self):
        return jira_connector.CRT
    def server(self):
        return self._Server
    def user(self):
        return self._User
    def display_name(self):
        return self._DisplayName


    def options(self):
        return self._Options
    def jql(self):
        return self._Options.jql()
    def void():
        pass
    def stop(self):
        self._Stop = True
    

    def set_server(self,Serv):
        self._Server = Serv
    def set_output_stream(self,OStream):
        self._Output = OStream
    def set_error_stream(self,EStream):
        self._Errput = EStream
    def set_jql(self,JQL):
        self._Options.set_jql(JQL)


    def _notify_issues(self,Issues):
        self._beep(880,1000) #440Hz 1000ms
        self._Output(f"\n\nIssues detected on {datetime.now()}!")
        for idx,Issue in enumerate(Issues):
            self._Output(f"{idx+1}. {Issue.key}: '{Issue.fields.summary}'")

    def _issue_notify(self,Issue,Buffer="\t"):
        if self._Speak:
            RT = Issue.fields.customfield_10202.requestType.name
            self._Speaker.play_sound(self._Speaker.get_db_text2sound_file(RT))
        else:
            self._beep(440,500) #440Hz 500ms
        self._Output(f'\n{Issue.key}\n'+\
            f'{Buffer}Summary      = "{Issue.fields.summary}"\n'+\
            f'{Buffer}Request Type = "{Issue.fields.customfield_10202.requestType.name}"\n'+\
            f'{Buffer}Assignee     = "{Issue.fields.assignee}"\n'+\
            f'{Buffer}Reporter     = "{Issue.fields.reporter}"\n'+\
            f'{Buffer}Status       = "{Issue.fields.status.name}"\n'+\
            f'{Buffer}Created      = "{Issue.fields.created}"\n')

    def _issue_information(Issue,Buffer="\t"):
        return f'{Issue.key}\n'+\
            f'{Buffer}Summary      = "{Issue.fields.summary}"\n'+\
            f'{Buffer}Request Type = "{Issue.fields.customfield_10202.requestType.name}"\n'+\
            f'{Buffer}Assignee     = "{Issue.fields.assignee}"\n'+\
            f'{Buffer}Reporter     = "{Issue.fields.reporter}"\n'+\
            f'{Buffer}Status       = "{Issue.fields.status.name}"\n'+\
            f'{Buffer}Created      = "{Issue.fields.created}"\n'


    def background_daemon(self,Rounds=3600,Assign = False,Verbose = True):
        self._Stop = False
        self._HistoryCmd.append(f"'{self._Options.jql()}' at {datetime.now()} for {Rounds} times")
        self._Output(f"\nStarting on: {datetime.now()}")
        for Round in range(Rounds):
            if self._Stop:
                break
            RawIssues = self._Connection.search_issues(self._Options.jql())
            Issues = [Issue for Issue in RawIssues if Issue.key not in self._IssueHistory]
            self._IssueHistory.update([Issue.key for Issue in Issues])

            if len(Issues) == 0:
                if Verbose:
                    self._Output(f"\rRound {Round}: Nothing found or todo.",end="")
                sleep(0.8612) #1-~JqlAnfrageZeit(~140ms)
            else:
                self._notify_issues(Issues)
                for Issue in Issues:
                    Assignee = None if Issue.fields.assignee is None else Issue.fields.assignee.key
                    Reporter = None if Issue.fields.reporter is None else Issue.fields.reporter.key
                    if Assignee is None and Reporter not in Options.IgnoreUsers:
                        self._issue_notify(Issue)
                    else:
                        self._Output(f"'{Issue.key}' is not important.\n")
        self._Output(f"\rStopping on: {datetime.now()}")

class LoginGui():
    def __init__(self, Connector,Master):
        self._Connector = Connector
        self._Master = Master
        self._MainWindow = Toplevel(Master.as_master())
        self._set_info()
        self._Server = self._set_field("Server:")
        self._Server[1].insert(END,self._Connector.server())
        self._User = self._set_field("Username:",Width=20)
        self._User[1].insert(END,self._Connector.user())
        self._Pass = self._set_field("Password:","\u2022",Width=20)
        self._MainWindow.bind('<Escape>',self._exit)
        self._MainWindow.bind('<Return>',(lambda event: self._login()))
        self._Logon = Button(self._MainWindow, text="Login",command=(lambda: self._login()))
        self._Quit = Button(self._MainWindow, text="Quit",command=(lambda : self._exit(0)))
        self._Logon.pack(side=LEFT,padx=25,pady=15)
        self._Quit.pack(side=RIGHT,padx=25,pady=15)
        self._MainWindow.protocol('WM_DELETE_WINDOW',self._exit)
        self._MainWindow.resizable(0, 0)

    def run(self):
        self._MainWindow.mainloop()

    def hide(self):
        self._MainWindow.withdraw()
    def shrink(self):
        self._MainWindow.iconify()
    def reveal(self):
        self._MainWindow.deiconify()

    def _exit(self,event):
        self._Master.cancel()

    def _error(self,Data,Title="Error"):
        messagebox.showerror(Data,Title)
    def _warning(self,Data,Title="Warning"):
        messagebox.showwarning(Data,Title)

    def _set_info(self):
        InfoFrame = Frame(self._MainWindow)
        InfoText = "Welcome to the graphical Jira Issue Notifier - JIN.\n\n"+\
                    "With this tool you can connect to a Jira instance over the REST-API.\n"+\
                    "For the login a cookie based session of the REST-API is created.\n\n"+\
                    "Afterwards you can execute any JQL expressions, even repetitively.\n"+\
                    "If there is any issue to be found, you will be acoustically notified."
        InfoFrame.pack(side=TOP,fill=X,anchor="w")
        Label(InfoFrame, text=InfoText,justify=LEFT,padx = 10,pady=10,bg="white").pack(side=LEFT)

    def _set_field(self,FieldName,Show="",Width=40):
        FieldRow = Frame(self._MainWindow)
        FieldLab = Label(FieldRow,width=15,text=FieldName,anchor="w")
        FieldEnt = Entry(FieldRow,show=Show,width=Width)
        FieldRow.pack(side=TOP,fill=X,padx=10,pady=5)
        FieldLab.pack(side=LEFT)
        FieldEnt.pack(side=LEFT)
        return (FieldName,FieldEnt)

    def _login(self):
        if len(self._Server[1].get()) == 0:
            self._warning("Server-Warning","Please provide a server URL!")
            return
        if not self._Server[1].get().endswith("/jira"):
            self._Server[1].config(state='readonly')
            IsCorrect = messagebox.askyesno("Jira Suffix missing",f"The submitted URL \"{self._Server[1].get()}\" does not end with \"https://.../jira\", is it still correct?")
            self._Server[1].config(state='normal')
            if not IsCorrect:
                return  
        if len(self._User[1].get()) == 0 or len(self._Pass[1].get()) ==0:
            self._warning("Credential-Warning","Please provide regular credentials!")
            return
        self._freeze()
        self._Connector.set_server(self._Server[1].get())
        self._Connector.connect(self._User[1].get(),self._Pass[1].get())
        if not self._Connector.is_connected():
            self._melt()
            self._error("Connection-Error","Connection not established, please try again!")
        else:
           self.shrink()
           self._Master._melt()
           self._Master.reveal()
        self.shrink()
        self._Master._melt()
        self._Master.reveal()

    def _freeze(self):
        self._Server[1].config(state='readonly')
        self._User[1].config(state='readonly')
        self._Pass[1].config(state='disabled')
        self._Logon.config(state='disabled')

    def _melt(self):
        self._Server[1].config(state='normal')
        self._User[1].config(state='normal')
        self._Pass[1].config(state='normal')
        self._Logon.config(state='normal')


class ProtocolGui():
    def __init__(self,Connector,Master):
        self._Connector = Connector
        self._Master = Master
        self._MainWindow = Toplevel(self._Master.as_master())
        TextRow = Frame(self._MainWindow)
        TextRow.pack(side=TOP,fill=X,padx=10,pady=5)
        self._Textfield = ScrolledText(TextRow,width=120,height=50,state='disabled')
        self._Textfield.pack(side=TOP,fill=X)
        self._Textfield.tag_configure("last_insert", background="bisque")
        ButtonRow = Frame(self._MainWindow)
        ButtonRow.pack(side=TOP,fill=X,padx=10,pady=5)
        self._ClearB = Button(ButtonRow, text="Clear history",command=(lambda : self.clear()))
        self._QuitB = Button(ButtonRow, text="Stop execution",command=(lambda: self._close()))
        self._ClearB.pack(side=LEFT,padx=25,pady=15)
        self._QuitB.pack(side=RIGHT,padx=25,pady=15)
        self._MainWindow.protocol('WM_DELETE_WINDOW',self._close)
        self._IsFirstOverwrite = True
        #self._MainWindow.resizable(0, 0)


    def run(self):
        self._MainWindow.mainloop()

    def print(self,Data,end="\n"):
        self._Textfield.config(state='normal')
        TmpData = Data
        if TmpData.startswith("\r") and end == "":
            if not self._IsFirstOverwrite:
                last_insert = self._Textfield.tag_ranges("last_insert")
                self._Textfield.delete(last_insert[0], last_insert[1])
                TmpData = TmpData.replace('\r', '')+'\n'
            self._IsFirstOverwrite = False
        else:
            self._IsFirstOverwrite = True
        self._Textfield.tag_remove("last_insert", "1.0", "end")
        self._Textfield.insert("end",f'{TmpData}{end}', "last_insert")
        self._Textfield.see(END)
        self._Textfield.config(state='disabled')

    def clear(self):
        if messagebox.askyesno("Deleting history?","Do you really want to delete the history?"):
            self._Textfield.config(state='normal')
            self._Textfield.delete(1.0,END)
            self._Textfield.config(state='disabled')

    def hide(self):
        self._MainWindow.withdraw()
    def shrink(self):
        self._MainWindow.iconify()
    def reveal(self):
        self._ClearB.config(state='normal')
        self._QuitB.config(state='normal')
        self._MainWindow.deiconify()

    def _close(self):
        self._ClearB.config(state='disabled')
        self._QuitB.config(state='disabled')
        self._Connector.stop()
        self._Master._melt()
        self.hide()


class GuiUpdater():
    def __init__(self):
        self._Queue = Queue()
        self._Queue.cancel_join_thread()

    def print(self,Data,end="\n"):
        self._Queue.put(f"{Data}{end}")

    def background_task(self,Task,Args,CmdsFinal):
        self._Thread = threading.Thread(target=self._thread,args=[Task,Args,CmdsFinal,])
        self._Thread.start()

    def _thread(self,Task,Args,CmdsFinal):
        Task(Args)
        for Cmd in CmdsFinal:
            Cmd()

    def queue(self):
        return self._Queue


class MenuGui():
    def __init__(self, Connector=jira_connector(),Updater=GuiUpdater(), Speaker = speaker(),SoundOn = True, Version="1.0.0"):
        self._Init0 = False
        self._Updater = Updater
        self._Connector = Connector
        self._Connector._Speaker = Speaker
        self._IsCrt = False
        self._Sound = SoundOn
        self._Connector.set_error_stream(self._error)
        self._Connector.set_output_stream(self._Updater.print)
        self._MainWindow = Tk()
        self._MainWindow.title(f"JIN - Jira Issue Notifier {Version}")
        self._set_info()
        JqlButtonRow = Frame(self._MainWindow)
        self._JqlBC = Button(JqlButtonRow, text="Customised CRT JQL",command=(lambda : self._put_crt()))
        self._JqlBI = Button(JqlButtonRow, text="Individual JQL",command=(lambda : self._remove_crt()))
        self._JqlBC.pack(side=LEFT,padx=25,pady=15)
        self._JqlBI.pack(side=RIGHT,padx=25,pady=15)
        JqlButtonRow.pack(side=TOP,fill=X,padx=10,pady=5)
        self._JQL = self._jql_box("JQL:",Width=40)
        self._Rounds = self._set_field("Rounds:",Width=5)
        self._Rounds[1].insert(END,3600)
        self._put_crt()
        ButtonRow = Frame(self._MainWindow)
        self._RunB = Button(ButtonRow, text="Run job",command=(lambda : self._execute()))
        self._QuitB = Button(ButtonRow, text="Close connection", command=(lambda : self._return(0)))
        self._RunB.pack(side=LEFT,padx=25,pady=15)
        self._QuitB.pack(side=RIGHT,padx=25,pady=15)
        ButtonRow.pack(side=BOTTOM,fill=X,padx=10,pady=5)
        self._MainWindow.protocol('WM_DELETE_WINDOW',self.cancel)
        self._Login = LoginGui(self._Connector,self)
        self._Protocol = ProtocolGui(self._Connector,self)
        self._MainWindow.after(100, self._refresh)
        #self._MainWindow.resizable(0, 0)

    def run(self):
        self.hide()
        self._Protocol.hide()
        self._MainWindow.mainloop()

    def as_master(self):
        return self._MainWindow

    def hide(self):
        self._MainWindow.withdraw()
    def shrink(self):
        self._MainWindow.iconify()
    def reveal(self):
        self._update_info()
        self._MainWindow.deiconify()

    def cancel(self):
        self._Connector.stop()
        if hasattr(self._Updater,"_Thread"):
            self._Updater._Thread.join()
        self._Connector.close()
        self._Login._MainWindow.destroy()
        self._Protocol._MainWindow.destroy()
        self._Init0 = True
        self._MainWindow.destroy()

    def _jql_box(self,FieldName,Width=20,Height=5):
        FieldRow = Frame(self._MainWindow)
        FieldLab = Label(FieldRow,width=10,text=FieldName,anchor="w")
        FieldEnt = ScrolledText(FieldRow,width=Width,height=Height)
        FieldRow.pack(side=TOP,fill=X,padx=10,pady=5)
        FieldLab.pack(side=LEFT)
        FieldEnt.pack(side=LEFT)
        return (FieldName,FieldEnt)

    def _put_crt(self):
        if not self._IsCrt:
            self._CheckBoxes = [ self._set_checkbox(CRT) for CRT in Options.CRT]
            self._updated_checkboxes()
            self._JQL[1].config(state='disabled')
            self._JqlBC.config(relief=SUNKEN)
            self._JqlBI.config(relief=RAISED)
            self._IsCrt = True
    def _remove_crt(self):
        if self._IsCrt:
            for FieldName,FieldChB,FieldVar,FieldRow in self._CheckBoxes:
                FieldChB.destroy()
                FieldRow.destroy()
                del FieldName,FieldChB,FieldVar,FieldRow
            self._JQL[1].config(state='normal')
            self._JQL[1].delete(1.0,END)
            self._JqlBC.config(relief=RAISED)
            self._JqlBI.config(relief=SUNKEN)
            self._IsCrt = False

    def _set_info(self):
        InfoFrame = Frame(self._MainWindow)
        InfoFrame.pack(side=TOP,fill=X,anchor="w")
        self._InfoLabel = Label(InfoFrame,justify=LEFT,padx = 20,pady=10,bg="white")
        self._update_info()
        self._InfoLabel.pack(side=LEFT)

    def _update_info(self):
        InfoText = f"Connection was created successfully to '{self._Connector.server()}'.\n"+\
                    f"You have been logged in as {self._Connector.display_name()}.\n\n"+\
                    "Now you have to set some options concerning your JQL.\n"+\
                    "A JQL expression can either be executed once or more.\n\n"+\
                    "For several executions you can enter the round number (round ~ sec).\n"+\
                    "You can either enter your own JQL or use a customised one,\n"+\
                    "where you can select the customer request types to search for."
        self._InfoLabel['text'] = InfoText

    def _return(self,event):
        self._Connector.close()
        self.hide()
        self._Protocol.hide()
        self._Login.reveal()
        self._Login._melt()

    def _error(self,Data,Title="Error"):
        messagebox.showerror(Data,Title)
    def _warning(self,Data,Title="Warning"):
        messagebox.showwarning(Data,Title)

    def _set_field(self,FieldName,Show="",Width=40):
        FieldRow = Frame(self._MainWindow)
        FieldLab = Label(FieldRow,width=10,text=FieldName,anchor="w")
        FieldEnt = Entry(FieldRow,show=Show,width=Width)
        FieldRow.pack(side=TOP,fill=X,padx=10,pady=5)
        FieldLab.pack(side=LEFT)
        FieldEnt.pack(side=LEFT)
        return (FieldName,FieldEnt)

    def _set_checkbox(self,FieldName,Show=""):
        FieldVar = IntVar(value=1)
        FieldRow = Frame(self._MainWindow)
        FieldChB = Checkbutton(FieldRow,text=FieldName,variable=FieldVar,command = self._updated_checkboxes)
        FieldRow.pack(side=TOP,fill=X,padx=10)
        FieldChB.pack(side=TOP,anchor="w",expand=YES)
        return (FieldName,FieldChB,FieldVar,FieldRow)


    def _updated_checkboxes(self):
        IsChecked = [Entry[2].get() for Entry in self._CheckBoxes]
        self._Connector.options().select_jsd_crt(IsChecked)
        self._JQL[1].delete(1.0,END)
        self._JQL[1].insert(END,f'{self._Connector.jql()}')


    def _execute(self):
        if not self._IsCrt:
            self._Connector.set_jql(self._JQL[1].get(1.0,END))
        else:
            self._JQL[1].config(state='normal')
            self._updated_checkboxes()
            self._JQL[1].config(state='disabled')
        self._Protocol.reveal()
        self._freeze()
        self._threadtask()

    def _threadtask(self):
        CmdsSuff = [self._melt,self._Protocol.hide,self.reveal]
        self._Updater.background_task(self._Connector.background_daemon,int(self._Rounds[1].get()),CmdsSuff)

    def _freeze(self):
        self._JqlBC.config(state='disabled')
        self._JqlBI.config(state='disabled')
        self._Rounds[1].config(state='disabled')
        self._JQL[1].config(state='disabled')
        self._RunB.config(state='disabled')
        for ChB in self._CheckBoxes:
            ChB[1].config(state='disabled')

    def _melt(self):
        self._JqlBC.config(state='normal')
        self._JqlBI.config(state='normal')
        self._Rounds[1].config(state='normal')
        self._RunB.config(state='normal')
        if self._IsCrt:
            for ChB in self._CheckBoxes:
                ChB[1].config(state='normal')
        else:
            self._JQL[1].config(state='normal')

    def _Executor(self):
        pass
    def _refresh(self):
        try:
            self._Protocol.print(self._Updater.queue().get(0),end="")
        except Empty:
            pass
        finally:
         self._MainWindow.after(100, self._refresh)


class JinApplication():
    def __init__(self,GUI = True,version = "1.0.0"):
        self._Gui = GUI
        self._Connector = jira_connector()
        self._Version = version
    def start(self):
        if self._Gui:
            while True:
                self._Updater = GuiUpdater()
                self._Speaker = speaker(TextPref="New Ticket in")
                self._MenuG = MenuGui(self._Connector, self._Updater, self._Speaker, Version = self._Version)
                self._MenuG.run()
                if self._MenuG._Init0:
                    break
        else:
            self._Connector.connect(input("Enter username to login: "),getpass.getpass("Enter password to login: "))
            JQL = f'project = <PROJECTKEY> AND assignee is EMPTY AND "Customer Request Type" in ({",".join(compress(Options.CRT,Selection))})  ORDER BY created Desc'
            Connection.background_daemon(JQL)
            Connection.close()


if __name__ == "__main__":
    Version = "1.0.1"
    JIN = JinApplication(version = Version)
    JIN.start()
