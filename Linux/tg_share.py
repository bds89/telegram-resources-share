import os, platform, time, sys, inspect, logging, yaml, re, sqlite3
from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]


if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler, BaseHandler
)

SLASH = "/"

class Objects_in_folder:
    def __init__(self, folders, files, patch=""):
        self.folders = folders
        self.files = files
        self.patch = patch   

class Message_with_keyboard:
    def __init__(self, text, keyboard, links, patch=""):
        self.text = text
        self.keyboard = keyboard
        self.links = links
        self.patch = patch


class User:
    def __init__(self, id, name="?", surname="?", auth="GUEST", tryn=0):
        self.id = id
        self.name = name
        self.surname = surname
        self.auth = auth
        self.tryn = tryn

    def save_to_db(self, params=[]):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()
        user = (self.id, self.name, self.surname, self.auth, self.tryn)
        if not params:
            try:
                cursor.execute('''SELECT id FROM users WHERE id = ?''', (self.id,))
                if not cursor.fetchall(): 
                    cursor.execute('''INSERT INTO users VALUES(?,?,?,?,?)''', user)
                else:
                    cursor.execute('''UPDATE users 
                                        SET name = ?,
                                        surname = ?,
                                        auth = ?,
                                        tryn = ? 
                                            where id = ?''', (self.name, self.surname, self.auth, self.tryn, self.id))
                sqlite_connection.commit()
                sqlite_connection.close()
                return True
            except Exception as e:
                logger.error("Exception: "+e+" in save to DB users without params")
                logger.info((self.name, self.surname, self.auth, self.tryn, self.id))
                return False
        else:
            try:
                new_user = False
                cursor.execute('''SELECT id FROM users WHERE id = ?''', (self.id,))
                if not cursor.fetchall(): new_user = True
                if "name" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO users VALUES(?,?,?,?,?)''', user)
                        new_user = False
                    else: cursor.execute('''UPDATE users SET name = ? where id = ?''', (self.name, self.id))
                if "surname" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO users VALUES(?,?,?,?,?)''', user)
                        new_user = False
                    else: cursor.execute('''UPDATE users SET surname = ? where id = ?''', (self.surname, self.id))
                if "auth" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO users VALUES(?,?,?,?,?)''', user)
                        new_user = False
                    else: cursor.execute('''UPDATE users SET auth = ? where id = ?''', (self.auth, self.id))
                if "notify" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO users VALUES(?,?,?,?,?)''', user)
                        new_user = False
                    else: cursor.execute('''UPDATE users SET tryn = ? where id = ?''', (self.tryn, self.id))
                sqlite_connection.commit()
                sqlite_connection.close()
                return True
            except Exception as e:
                logger.error("Exception: "+e+" in save to DB users with params:"+params)
                logger.info((self.name, self.surname, self.auth, self.tryn, self.id))
                return False

    def load_from_db(self, param=""):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()

        if not param:
            try:
                cursor.execute('''SELECT * FROM users WHERE id = ? ''', (self.id,))
                user = cursor.fetchone()
                sqlite_connection.close()
            except Exception as e:
                logger.error("Exception: "+e+" in load from DB without params")
                return False
            if user:
                self.id = user[0]
                self.name = user[1]
                self.surname = user[2]
                self.auth = user[3]
                self.tryn = user[4]
                sqlite_connection.close()
                return True
            else: 
                sqlite_connection.close()
                return False

        try:
            cursor.execute('''SELECT ? FROM users WHERE id = ? ''', (param, self.id))
            user = cursor.fetchone()
            sqlite_connection.close()
        except Exception as e:
            logger.error("Exception: "+e+" in load from DB users with param:"+param)
            return False
        if user:
            if param == "name": self.name = user[0]
            if param == "surname": self.surname = user[0]
            if param == "auth": self.auth = user[0]
            if param == "name": self.name = user[0]
            sqlite_connection.close()
            return user[0]
        else: 
            sqlite_connection.close()
            return False

    def delete_from_db(self, id):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()

        try:
            cursor.execute('''DELETE FROM users WHERE id = ? ''', (id,))
            sqlite_connection.commit()
        except Exception as e:
            logger.error("Exception: "+e+" in delete from DB users")
            sqlite_connection.close()
            return False
        sqlite_connection.close()
        return True

class Settings:
    def __init__(self, id, rows=6, columns=3, symbols=35, notify="NULL"):
        self.id = id
        self.rows = rows
        self.columns = columns
        self.symbols = symbols
        self.notify = notify

    def save_to_db(self, params=[]):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()
        settings = (self.id, self.rows, self.columns, self.symbols, self.notify)
        if not params:
            try:
                cursor.execute('''SELECT id FROM settings WHERE id = ?''', (self.id,))
                if not cursor.fetchall(): 
                    cursor.execute('''INSERT INTO settings VALUES(?,?,?,?,?)''', settings)
                else:
                    cursor.execute('''UPDATE settings 
                                        SET rows = ?,
                                        columns = ?,
                                        symbols = ?,
                                        notify = ? 
                                            where id = ?''', (self.rows, self.columns, self.symbols, self.notify, self.id))
                sqlite_connection.commit()
                sqlite_connection.close()
                return True
            except Exception as e:
                logger.error("Exception: "+e+" in save to DB settings without params")
                logger.info((self.id, self.rows, self.columns, self.symbols, self.notify))
                return False
        else:
            try:
                new_user = False
                cursor.execute('''SELECT id FROM settings WHERE id = ?''', (self.id,))
                if not cursor.fetchall(): new_user = True
                if "rows" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO settings VALUES(?,?,?,?)''', settings)
                        new_user = False
                    else: cursor.execute('''UPDATE settings SET rows = ? where id = ?''', (self.rows, self.id))
                if "columns" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO settings VALUES(?,?,?,?)''', settings)
                        new_user = False
                    else: cursor.execute('''UPDATE settings SET columns = ? where id = ?''', (self.columns, self.id))
                if "symbols" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO settings VALUES(?,?,?,?,?,?)''', settings)
                        new_user = False
                    else: cursor.execute('''UPDATE settings SET symbols = ? where id = ?''', (self.symbols, self.id))
                if "notify" in params:
                    if new_user: 
                        cursor.execute('''INSERT INTO settings VALUES(?,?,?,?,?,?)''', settings)
                        new_user = False
                    else: cursor.execute('''UPDATE settings SET notify = ? where id = ?''', (self.notify, self.id))
                sqlite_connection.commit()
                sqlite_connection.close()
                return True
            except Exception as e:
                logger.error("Exception: "+e+" in save to DB settings with params: "+params)
                logger.info((self.id, self.rows, self.columns, self.symbols, self.notify))
                return False


    def load_from_db(self, param=""):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()

        if not param:
            try:
                cursor.execute('''SELECT * FROM settings WHERE id = ? ''', (self.id,))
                settings = cursor.fetchone()
                sqlite_connection.close()
            except Exception as e:
                logger.error("Exception: "+e+" in load from DB settings without param")
                return False
            if settings:
                self.id = settings[0]
                self.rows = settings[1]
                self.columns = settings[2]
                self.symbols = settings[3]
                self.notify = settings[4]
                sqlite_connection.close()
                return True
            else: 
                sqlite_connection.close()
                return False

        try:
            cursor.execute('''SELECT ? FROM settings WHERE id = ? ''', (param, self.id))
            settings = cursor.fetchone()
            sqlite_connection.close()
        except Exception as e:
            logger.error("Exception: "+e+" in load from DB settings with param: "+param)
            return False
        if settings:
            if param == "rows": self.rows = settings[0]
            if param == "columns": self.columns = settings[0]
            if param == "symbols": self.symbols = settings[0]
            if param == "notify": self.notify = settings[0]
            sqlite_connection.close()
            return settings[0]
        else: 
            sqlite_connection.close()
            return False

    def delete_from_db(self, id):
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()

        try:
            cursor.execute('''DELETE FROM users WHERE id = ? ''', (id,))
            sqlite_connection.commit()
        except Exception as e:
            logger.error("Exception: "+e+" in delete from DB")
            sqlite_connection.close()
            return False
        sqlite_connection.close()
        return True

def check_system():
    system = platform.system()
    if system == "Windows":
        globals()["SYSTEM"] = "Windows"
        return "\\"
    else: 
        globals()["SYSTEM"] = "Linux"
        return "/"

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def obj_on_disk(patch, s):
    objects = Objects_in_folder(folders=[], files=[], patch=patch)
    if not os.path.exists(patch):
        return objects
    try:
        for name in os.listdir(patch):
            obj = patch+s+name
            if os.path.isfile(obj):
                objects.files.append(name)
            else: objects.folders.append(name)
    except Exception as e:
        logger.error("Exception: %s obj_on_disc", e)
        return objects
    objects.folders.sort()
    objects.files.sort()
    if not objects.folders and not objects.files:
        objects.folders.append(".emptyempty")
        objects.files.append(".emptyempty")
    return objects

def create_message(obj: Objects_in_folder, context: ContextTypes.DEFAULT_TYPE):
    if obj.folders or obj.files: new_message = Message_with_keyboard(text="", keyboard=[[]], links = {}, patch=obj.patch)
    else:
        new_message = Message_with_keyboard(text="Incorrect patch", keyboard=[[]], links = {})
        if SYSTEM == "Windows": result = re.findall(r'\\[\d\w\. ]+$', obj.patch)
        else: result = re.findall(SLASH+r'[\d\w\. ]+$', obj.patch)
        if result:
            new_message.links["fldback"] = obj.patch[len(CONFIG["SHARE_PATCH"]):-len(result[0])]
            new_message.keyboard[0].extend(
                [
                    InlineKeyboardButton("⬅", callback_data="fldback"),
                ]
            )
        new_message.keyboard[0].extend(
            [
                InlineKeyboardButton("🏠", callback_data="root"),
            ]
        )
        return new_message

    if ".emptyempty" in obj.folders and ".emptyempty" in obj.files:
        obj.folders = []
        obj.files = []
    symbols = context.user_data["settings"].symbols
    lvl1 = 0
    lvl2 = 0
    lvlsize = context.user_data["settings"].columns
    num_buttons = 0
    max_buttons = context.user_data["settings"].columns * context.user_data["settings"].rows
    was_add = False
    was_add_next = False

    if  context.chat_data["page"] != 0:
        line = InlineKeyboardButton("⋯", callback_data="fldrefreshprev")
        new_message.keyboard[lvl2].append(line)
        lvl1 += 1
        was_add = True
        num_buttons+=1

    patch_after_root = new_message.patch[len(CONFIG["SHARE_PATCH"]):]
    if patch_after_root: new_message.text += "<b>"+patch_after_root+"</b>\n\n"
    else: new_message.text += "<b>"+SLASH+"</b>\n\n"
    if  context.chat_data["page"] != 0:
        new_message.text += "⋯\n"
    for f in enumerate(obj.folders):
        if context.chat_data["page"] != 0:
            if num_buttons < ((context.chat_data["page"]-1)*(max_buttons-2) + (max_buttons-1))+1:
                num_buttons += 1
                continue

        if context.chat_data["page"] != 0: limit_buttons = ((context.chat_data["page"]-1)*(max_buttons-2) + (max_buttons-1))+1+(max_buttons-2)
        else: limit_buttons = max_buttons-1
        if num_buttons >= limit_buttons and (len(obj.folders) + len(obj.files)) > num_buttons:
            new_message.text += "⋯"
            line = InlineKeyboardButton("⋯", callback_data="fldrefreshnext")
            new_message.keyboard[lvl2].append(line)
            lvl1 += 1
            was_add = True
            num_buttons+=1
            was_add_next = True
            break

        new_message.text += "📁"+f[1][:symbols]+"\n"
        new_message.links["fld"+str(f[0])] = patch_after_root+SLASH+f[1]
        num_buttons+=1
        was_add = True
        line = InlineKeyboardButton("📁"+f[1], callback_data="fld"+str(f[0]))
        if lvl1 < lvlsize:       
            new_message.keyboard[lvl2].append(line)
            lvl1 += 1
        else:
            lvl2 += 1
            lvl1 = 1
            new_message.keyboard.append([])
            new_message.keyboard[lvl2].append(line)

    if not was_add_next:
        for f in enumerate(obj.files):
            if context.chat_data["page"] != 0:
                if num_buttons < ((context.chat_data["page"]-1)*(max_buttons-2) + (max_buttons-1))+1:
                    num_buttons += 1
                    continue
            if context.chat_data["page"] != 0: limit_buttons = ((context.chat_data["page"]-1)*(max_buttons-2) + (max_buttons-1))+1+(max_buttons-2)
            else: limit_buttons = max_buttons-1
            if num_buttons >= limit_buttons and (len(obj.folders) + len(obj.files)) > num_buttons:
                new_message.text += "⋯"
                line = InlineKeyboardButton("⋯", callback_data="fldrefreshnext")
                new_message.keyboard[lvl2].append(line)
                lvl1 += 1
                was_add = True
                num_buttons+=1
                break

            new_message.text += "📄"+f[1][:symbols]+"\n"
            new_message.links["fl"+str(f[0])] = patch_after_root+SLASH+f[1]
            num_buttons+=1
            was_add = True
            line = InlineKeyboardButton("📄"+f[1], callback_data="fl"+str(f[0]))
            if lvl1 < lvlsize:       
                new_message.keyboard[lvl2].append(line)
                lvl1 += 1
            else:
                lvl2 += 1
                lvl1 = 1
                new_message.keyboard.append([])
                new_message.keyboard[lvl2].append(line)

    #add aditional buttons
    lineIndex = 0
    if was_add: 
        lineIndex = lvl2+1
        new_message.keyboard.append([])
    
    if obj.patch != CONFIG["SHARE_PATCH"]: #!!!!
        if SYSTEM == "Windows": result = re.findall(r'\\[\d\w\. ]+$', obj.patch)
        else: result = re.findall(SLASH+r'[\d\w\. ]+$', obj.patch)
        if result:
            new_message.links["fldback"] = obj.patch[len(CONFIG["SHARE_PATCH"]):-len(result[0])]
            new_message.keyboard[lineIndex].extend(
                [
                    InlineKeyboardButton("⬅", callback_data="fldback"),
                ]
            )
        new_message.keyboard[lineIndex].extend(
            [
                InlineKeyboardButton("🏠", callback_data="root"),
            ]
        )  

    new_message.links["fldrefresh"] = obj.patch[len(CONFIG["SHARE_PATCH"]):]
    new_message.keyboard[lineIndex].extend(
        [
            InlineKeyboardButton("🔄", callback_data="fldrefresh"),
        ]
    )

    new_message.keyboard[lineIndex].extend(
        [
            InlineKeyboardButton("➕📁", callback_data="fld_plus"),
        ]
    )  

    if not obj.folders and not obj.files: new_message.text = "🗑 Empty folder"
    return new_message


AUTH, ROOT, NEW_FOLDER, SETTINGS, SET_SETTINGS = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message: u = update.message.from_user
    else: u = update.callback_query.from_user
    user = User(id=u.id)
    if user.load_from_db(): 
        context.user_data["user"] = user
    else: 
        user.auth = "GUEST"
        user.name = u.first_name
        user.surname = u.last_name

    if user.auth == "BLACK": return ConversationHandler.END

    settings = Settings(id=user.id)
    settings.load_from_db()
    context.user_data["settings"] = settings
    if user.auth == "USER" or user.auth == "ADMIN":
        await root(update, context)
        return ROOT

    context.user_data["user"] = user
    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            "🔐 Please enter your password",
        )
    else:
        await update.callback_query.answer()
        context.chat_data["last_message"] = await update.callback_query.message.reply_text(
            "🔐 Please enter your password",
        )
    return AUTH


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        user = update.message.from_user
        user_pass = update.message.text
        if user_pass == str(CONFIG["PASSWORD"]) or ("ADMIN_PASSWORD" in CONFIG and user_pass == str(CONFIG["ADMIN_PASSWORD"])):
            if user_pass == str(CONFIG["PASSWORD"]):
                context.user_data["user"].auth = "USER"
            if "ADMIN_PASSWORD" in CONFIG and user_pass == str(CONFIG["ADMIN_PASSWORD"]):
                context.user_data.auth = "ADMIN"
            context.user_data["user"].name = user.first_name
            context.user_data["user"].surname = user.last_name
            context.user_data["user"].notify = "NULL"
            context.user_data["user"].tryn = 0
            context.user_data["user"].save_to_db()
            context.user_data["settings"].save_to_db()


            logger.info("User "+str(user.first_name)+" "+str(user.last_name)+": "+str(user.id)+" successfully logged in")
            await root(update, context)
            return ROOT
    
        else:
            logger.warning("User "+str(user.first_name)+" "+str(user.last_name)+": "+str(user.id)+" type wrong password")
            context.user_data["user"].tryn += 1
            
            if context.user_data["user"].tryn > 4:
                context.user_data["user"].auth = "BLACK"
                context.user_data["user"].name = user.first_name
                context.user_data["user"].surname = user.last_name
                context.user_data["user"].save_to_db()
                logger.warning("User "+str(user.first_name)+" "+str(user.last_name)+": "+str(user.id)+" was banned")
                return ConversationHandler.END
            
            else: 
                context.user_data["user"].save_to_db()

            context.chat_data["last_message"] = await update.message.reply_text(
                "⛔ Password is incorrect, please try again"
            )
            return AUTH
    else: return AUTH


async def root(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.chat_data["page"] = 0
    obj = obj_on_disk(CONFIG["SHARE_PATCH"], SLASH)
    new_message = create_message(obj, context)
    context.chat_data["patch"] = obj.patch
    context.chat_data["links"] = new_message.links
    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != new_message.text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(new_message.keyboard):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
            )
        else: await update.callback_query.answer()
    return ROOT


async def folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = query.from_user
    if query.data == "fldrefreshprev" or query.data == "fldrefreshnext":
        call_back = query.data[:-len("prev")]
        if query.data == "fldrefreshprev": context.chat_data["page"] -= 1
        if query.data == "fldrefreshnext": context.chat_data["page"] += 1
    else: 
        call_back = query.data
        context.chat_data["page"] = 0

    folder = context.chat_data["links"][call_back]
    logger.info("{0} choose folder: {1}".format(user.first_name, folder))

    obj = obj_on_disk(CONFIG["SHARE_PATCH"]+folder, SLASH)
    new_message = create_message(obj, context)
    context.chat_data["patch"] = obj.patch
    context.chat_data["links"] = new_message.links

    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != new_message.text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(new_message.keyboard):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
            )
        else:
            time.sleep(0.5)
            await update.callback_query.answer()
    return ROOT

async def file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = query.from_user
    file = context.chat_data["links"][query.data]
    logger.info("{0} choose file: {1}".format(user.first_name, file))

    if update.message:
        await update.message.reply_document(open(CONFIG["SHARE_PATCH"]+file, 'rb'), reply_markup=None, parse_mode="HTML")
    else:
        await update.callback_query.answer()
        await update.callback_query.message.reply_document(open(CONFIG["SHARE_PATCH"]+file, 'rb'), write_timeout=30)
        context.chat_data["last_message"] = await update.callback_query.message.reply_text(
            update.callback_query.message.text, reply_markup=update.callback_query.message.reply_markup, parse_mode="HTML"
        )

    return ROOT

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    patch = context.chat_data["patch"]
    await file.download(patch+SLASH+file_name)
    logger.info("{0} get file: {1}".format(user.first_name, patch+SLASH+file_name))

    obj = obj_on_disk(patch, SLASH)
    new_message = create_message(obj, context)

    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != new_message.text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(new_message.keyboard):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
            )
        else: await update.callback_query.answer()

    return ROOT

async def get_name_new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            context.chat_data["patch"]+"\n\nEnter folder name", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠", callback_data="root")]]), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != context.chat_data["patch"]+"\n\nEnter folder name" and update.callback_query.message.reply_markup != InlineKeyboardButton("🏠", callback_data="root"):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                context.chat_data["patch"]+"\n\nEnter folder name", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠", callback_data="root")]]), parse_mode="HTML"
            )
        else: await update.callback_query.answer()

    return NEW_FOLDER

async def create_new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message: return NEW_FOLDER
    user = update.message.from_user
    parent_dir = context.chat_data["patch"]
    folder_name = update.message.text
    if re.findall(r'[\d\w\. ]', folder_name):
    
        context.chat_data["page"] = 0
        patch = os.path.join(parent_dir, folder_name)
        try:
            os.mkdir(patch)
        except(FileNotFoundError) as e:
            logger.warning("FileNotFoundError in create_new_folder: {0} by {1}".format(patch+SLASH+folder_name, user.first_name))  

        logger.info("{0} added folder: {1}".format(user.first_name, patch+SLASH+folder_name))

    obj = obj_on_disk(parent_dir, SLASH)
    new_message = create_message(obj, context)
    context.chat_data["links"] = new_message.links


    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != new_message.text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(new_message.keyboard):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                new_message.text, reply_markup=InlineKeyboardMarkup(new_message.keyboard), parse_mode="HTML"
            )
        else: await update.callback_query.answer()

    return ROOT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, end_point=False) -> int:
    """Cancels and ends the conversation."""
    if update.message: u = update.message.from_user
    else: u = update.callback_query.from_user

    logger.info("User %s: %s canceled the conversation.", u.first_name, u.id)

    text = "🏁 Conversation is ended."
    keyboard = [[InlineKeyboardButton("🏠", callback_data="root")]]
    if end_point and context.chat_data["last_message"]:
        await context.chat_data["last_message"].edit_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
        )
    else:
        if update.message:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
            )
        else:
            if update.callback_query.message.text != text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(keyboard):
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
                )
            else: 
                await update.callback_query.answer()

    context.chat_data.clear
    context.user_data.clear
    return ConversationHandler.END

async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await cancel(update, context, end_point=True)

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message: return ConversationHandler.END
    u = update.message.from_user
    if "user" in context.user_data:
        context.user_data["user"].auth = "GUEST"
        context.user_data["user"].save_to_db(params="auth")
        context.user_data.clear
    else:
        user = User(id=u.id)
        user.save_to_db(params="auth")
    context.chat_data["last_message"] = await update.message.reply_text(
        "🏁 Bye!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏳 Start", callback_data="root")]])
    )
    return ConversationHandler.END

async def go_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message: u = update.message.from_user
    else: u = update.callback_query.from_user
    user = User(id=u.id)
    if user.load_from_db(): 
        context.user_data["user"] = user
    else: user.auth = "GUEST"

    if user.auth == "BLACK": return ConversationHandler.END
    if user.auth == "USER" or user.auth == "ADMIN":
        await settings(update, context)
        return SETTINGS

    context.user_data["user"] = user
    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            "First you need to login", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👤 Authorization", callback_data="auth")]])
        )
    else:
        await update.callback_query.answer()
        context.chat_data["last_message"] = await update.callback_query.message.reply_text(
            "First you need to login", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👤 Authorization", callback_data="auth")]])
        )
    return ConversationHandler.END

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message: u = update.message.from_user
    else: u = update.callback_query.from_user
    settings = Settings(id=u.id)
    settings.load_from_db()
    context.user_data["settings"] = settings

    text = "<b>Settings: \n</b>\nName clipping: %d symbols\nNumber of lines with buttons: %d\nNumber of buttons in a line: %d" % (settings.symbols, settings.rows, settings.columns)

    keyboard = [[InlineKeyboardButton("Symbols: %d"%settings.symbols, callback_data="symbols"),
                    InlineKeyboardButton("Lines: %d"%settings.rows, callback_data="rows"),
                    InlineKeyboardButton("Buttons: %d"%settings.columns, callback_data="columns")],
                    [InlineKeyboardButton("🏠", callback_data="root")]]
    if update.message:
        context.chat_data["last_message"] = await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
        )
    else:
        if update.callback_query.message.text != text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(keyboard):
            await update.callback_query.answer()
            context.chat_data["last_message"] = await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
            )
        else: await update.callback_query.answer()
    return SETTINGS

async def get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    u = update.callback_query.from_user
    query = update.callback_query.data

    context.chat_data["current_settings"] = query
    if query == "symbols":
        value = context.user_data["settings"].symbols
        text = "Name clipping: %d symbols\nType new value"%value
    if query == "rows":
        value = context.user_data["settings"].rows
        text = "Number of lines with buttons: %d\nType new value"%value
    if query == "columns":
        value = context.user_data["settings"].columns
        text = "Number of buttons in a line: %d\nType new value"%value

    keyboard = [[InlineKeyboardButton("⬅", callback_data="back_to_settings"),
                    InlineKeyboardButton("🏠", callback_data="root")]]
    if update.callback_query.message.text != text and update.callback_query.message.reply_markup != InlineKeyboardMarkup(keyboard):
        await update.callback_query.answer()
        context.chat_data["last_message"] = await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else: await update.callback_query.answer()
    return SET_SETTINGS

async def set_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    u = update.message.from_user
    m = update.message.text
    if m.isdigit():
        if context.chat_data["current_settings"] == "symbols":
            context.user_data["settings"].symbols = abs(int(m))
        if context.chat_data["current_settings"] == "rows":
            context.user_data["settings"].rows = abs(int(m))
        if context.chat_data["current_settings"] == "columns":
            context.user_data["settings"].columns = abs(int(m))
    context.user_data["settings"].save_to_db(params=context.chat_data["current_settings"])
    await settings(update, context)
    return SETTINGS


if __name__ == '__main__':
    SYSTEM = ""
    SLASH = check_system()
    dir = get_script_dir()
    CONFIG_PATCH = dir+SLASH+"config.yaml"
    if not os.path.exists(CONFIG_PATCH):
        print("config.yaml file not exist")
        time.sleep(2)

    else:
        with open(CONFIG_PATCH, encoding='utf-8') as f:
            CONFIG = yaml.load(f.read(), Loader=yaml.FullLoader)
            
        # Enable logging
        level = logging.INFO
        if "LOG_LEVEL" in CONFIG:
            if CONFIG["LOG_LEVEL"] == "INFO": pass
            if CONFIG["LOG_LEVEL"] == "ERROR": level=logging.ERROR
            if CONFIG["LOG_LEVEL"] == "WARNING" or CONFIG["LOG_LEVEL"] == "WARN": level=logging.ERROR
            if CONFIG["LOG_LEVEL"] == "NOTSET": level=logging.NOTSET
        logging.basicConfig(
            filename=dir+SLASH+"log.txt",
            filemode='a',
            datefmt='%H:%M:%S',
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
            level=level
        )
        logger = logging.getLogger(__name__)
        #DB CONNECT
        DB_PATCH = dir+'/users.db'
        sqlite_connection = sqlite3.connect(DB_PATCH)
        cursor = sqlite_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE if not exists users
                            (id integer NOT NULL UNIQUE, name text, surname text, auth text, tryn integer)
                        """)
            cursor.execute("""CREATE TABLE if not exists settings
                            (id integer NOT NULL UNIQUE, rows integer, columns integer, symbols integer, notify text)
                        """)
            sqlite_connection.commit()
        except Exception as e:
            logger.error("Exception: %s at DB connect.", e)
        sqlite_connection.close()

        """Run the bot."""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(CONFIG["TOKEN"]).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start),
                            CommandHandler("stop", start),
                            CommandHandler("cancel", start),
                            CommandHandler("logout", start),
                            CommandHandler("settings", go_to_settings),
                            CallbackQueryHandler(start, pattern='^')],
            states={
                AUTH: [CommandHandler("start", start),
                        CommandHandler("settings", go_to_settings),
                        CommandHandler("stop", cancel),
                        CommandHandler("cancel", cancel),
                        MessageHandler(filters.TEXT, auth)],
                ROOT: [CommandHandler("start", start),
                        CommandHandler("stop", cancel),
                        CommandHandler("cancel", cancel),
                        CommandHandler("logout", logout),
                        CommandHandler("settings", go_to_settings),
                        CallbackQueryHandler(get_name_new_folder, pattern='^fld_plus'),
                        CallbackQueryHandler(folder, pattern='^fld'),
                        CallbackQueryHandler(file, pattern='^fl'),
                        CallbackQueryHandler(root, pattern='^root'),
                        MessageHandler(filters.Document.ALL, get_file)
                        ],
                NEW_FOLDER: [MessageHandler(filters.TEXT, create_new_folder),
                            CommandHandler("stop", cancel),
                            CommandHandler("cancel", cancel),
                            CommandHandler("logout", logout),
                            CommandHandler("settings", go_to_settings),
                            CallbackQueryHandler(root, pattern='^'),],
                SETTINGS: [CommandHandler("stop", cancel),
                            CommandHandler("cancel", cancel),
                            CommandHandler("logout", logout),
                            CommandHandler("settings", go_to_settings),
                            CallbackQueryHandler(root, pattern='^root$'),
                            CallbackQueryHandler(get_settings, pattern='^rows$'),
                            CallbackQueryHandler(get_settings, pattern='^columns$'),
                            CallbackQueryHandler(get_settings, pattern='^symbols$'),],
                SET_SETTINGS: [MessageHandler(filters.TEXT, set_settings),
                            CommandHandler("stop", cancel),
                            CommandHandler("cancel", cancel),
                            CommandHandler("logout", logout),
                            CommandHandler("settings", go_to_settings),
                            CallbackQueryHandler(root, pattern='^root$'),
                            CallbackQueryHandler(settings, pattern='^back_to_settings$'),],
                ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout),
                                                CallbackQueryHandler(timeout, pattern='^'),],
            },
            conversation_timeout = 300,
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling()