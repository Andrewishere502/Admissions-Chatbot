import datetime
from hashlib import sha256
from functools import wraps, partial
from flask import (Flask, render_template, request,
                    url_for, redirect, make_response,
                    session, flash)

from db_connect import connect
from translate import microsoft_translate
from message_logger import MessageLogger
from chatbot import Chatbot


app = Flask(__name__)
app.config['SECRET_KEY'] = '12fa-d9_0?10\'!9_h0vfefq0["n92039ngb/\'23rf2"12a1li_'
message_logger = MessageLogger()
chatbot = Chatbot()


def hash_password(password):
    """Return the sha256 hexdigest of password"""
    return sha256(bytes(password, "utf-8")).hexdigest()


def execute_mysql_command(instruction):
    """Execute mysql commands like DELETE and INSERT. Does not include
    SELECT command.
    """
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(instruction)
    mydb.commit()
    mycursor.close()
    return


def search_mysql_table(table_name, select="*", condition=None):
    """Querry a mysql table. Return any matches from the table called
    table_name.

    Querry a mysql table called table_name, selecting data from the
    column named select, default * where the condition is met.
    """

    instruction = "SELECT {} FROM {}".format(select, table_name)
    if condition != None:
        instruction += " WHERE {}".format(condition)
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(instruction)
    results = mycursor.fetchall()
    mycursor.close()
    return results


def require_logged_in(func):
    """Make sure a link can't be accessed the user is logged in to a
    valid account.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get("username"):
            return func(*args, **kwargs)
        else:
            flash(("You must be logged in to view this page", "orange"))
            return redirect(url_for("login"))
    return inner


def require_logged_in_master_admin(func):
    """Make sure a link can't be accessed by typing it in, unless the
    user has master admin privileges.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get("username") and session.get("is_master_admin"):
            return func(*args, **kwargs)
        else:
            flash(("Admin privliges are required to view this page", "orange"))
            return redirect(url_for("login"))
    return inner


def validate_user(username, try_password):
    """Check the validity of the username and password entered into the
    login form. Return True if a match is found.

    Querry the adminProfile database, select all users with the
    username entered. Return False if no users with this username are
    found.
    If at least one match is found, check the sha256 hexdigest of the
    password entered with the sha256 hexidigest of the password for the
    matching username. If these are identical, return all the data for
    this user, otherwise return False
    """
    results = search_mysql_table("adminProfile", condition="username = '%s'" % username)

    if len(results) == 0:
        return False  # the username was incorrect
    else:
        for result in results:
            correct_password = result[2]  # password is stored as
                                          # a hexdigest hash
            if hash_password(try_password) == correct_password:
                return result
        return False  # the password was incorrect


def is_active(open_tab, tab):
    """Add the 'active' class to a tab if it is open."""
    return "active" if open_tab == tab else ""


def language_checked(current_lang, lang):
    return "checked" if current_lang == lang else ""


@app.route("/set_language")
def set_language():
    context = {"redirect_func_name": "set_language_process",
               "language": request.args.get("language", "en"),
               "return_to_func": request.args.get("return_to_func")
    }
    return render_template("set_language.html", **context)


@app.route("/set_language_process", methods=["POST"])
def set_language_process():
    language = request.form.get("language")
    return_to_func = request.args.get("return_to_func")
    return redirect(url_for(return_to_func, language=language))


@app.route("/submit_feedback")
def submit_feedback():
    context = {"redirect_func_name": "submit_feedback_process",
               "language": request.args.get("language", "en"),
               "return_to_func": request.args.get("return_to_func"),
               "go_back": "submit_feedback"
    }
    return render_template("submit_feedback.html", **context)


@app.route("/submit_feedback_process", methods=["POST"])
def submit_feedback_process():
    language = request.args.get("language", "en")
    return_to_func = request.args.get("return_to_func")

    feedback_data = dict(request.form.items())
    feedback_data["date"] = datetime.datetime.now()

    command = "INSERT INTO feedbackSubmissions (feedback_text, date) VALUES (\"{feedback_text}\", \"{date}\")".format(**feedback_data)
    execute_mysql_command(command)
    return redirect(url_for(return_to_func, language=language))


@app.route("/terms_and_conditions")
def terms_and_conditions():
    context = {"redirect_func_name": "submit_feedback_process",
               "language": request.args.get("language", "en"),
               "return_to_func": request.args.get("return_to_func"),
    }
    return render_template("terms_and_conditions.html", **context)


@app.route("/submit_email")
def submit_email():
    context = {"redirect_func_name": "submit_email_process",
               "language": request.args.get("language", "en"),
               "return_to_func": "start_convo",
               "go_back": "submit_email"
    }
    return render_template("submit_email.html", **context)


@app.route("/submit_email_process", methods=["POST"])
def submit_email_process():
    language = request.args.get("language", "en")
    return_to_func = request.args.get("return_to_func")

    email_data = dict(request.form.items())
    email_data["date"] = datetime.datetime.now()

    result = search_mysql_table("emailSubmissions", select="email", condition="email = '{}'".format(email_data["email"]))

    if len(result) == 0:  # prevents duplicate emails
        command = "INSERT INTO emailSubmissions (email, first_name, last_name, date) VALUES ('{email}', '{first_name}', '{last_name}', '{date}')".format(**email_data)
        execute_mysql_command(command)
    return redirect(url_for(return_to_func, language=language))


@app.route("/start_convo")
def start_convo():
    """Initiate the conversation between the user and the chatbot.
    Still accessable if they just type the URL, but better then
    they're avioding the email submission page on purpose.
    """
    language = request.args.get("language", "en")
    message_logger.add_msg("bot", microsoft_translate("en", "Hello, how may I help you today?", language))
    return redirect(url_for("index", language=language))


@app.route("/")
@app.route("/index")
def index():
    language = request.args.get("language", "en")
    if len(message_logger.current_log) == 0:
        return redirect(url_for("submit_email"))
    else:
        context = {"redirect_func_name": "bot_process",
                   "msg_log": message_logger.current_log,
                   "msg_log_len": len(message_logger.current_log),
                   "language": language,
                   "return_to_func": "index",
                   "go_back": "index"
                   }
        return render_template("chat.html", **context)


@app.route("/bot_process", methods=["POST"])
def bot_process():
    language = request.args.get("language")  # needs no default,
                                             # index provides language
                                             # or default "en"
    return_to_func = request.args.get("return_to_func")

    msg = request.form.get("msg").lower().strip()
    msg = microsoft_translate(language, msg, "en")

    message_logger.add_msg("human", msg)

    reply = chatbot.answer(microsoft_translate(language, msg, "en"))
    message_logger.add_msg("bot", microsoft_translate("en", reply, language))

    message_logger.log_sql(msg, reply, language)
    return redirect(url_for(return_to_func, language=language))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_process", methods=["POST"])
def login_process():
    login_data = dict(request.form.items())
    username = login_data["username"]
    logged_in_as = validate_user(username, login_data["password"])
    if logged_in_as:
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=1)
        session["username"] = username
        session["is_master_admin"] = int(logged_in_as[3])
        return redirect(url_for("cp_question_log"))
    else:
        flash(("No user with this username and password exists", "orange"))
        return redirect(url_for("login"))


@app.route("/logout")
@require_logged_in
def logout():
    session.clear()  # ends the session
    return redirect(url_for("login"))


@app.route("/cp_question_log")
@require_logged_in
def cp_question_log():
    condition = request.args.get("condition")
    interaction_data = search_mysql_table("userBotInteraction", condition=condition)
    context = {
        # default for interaction data is * from userBotInteraction
        "interaction_data": interaction_data,
        "open_tab": "cp_question_log"
        }
    return render_template("cp_question_log.html", **context)


@app.route("/cp_filter_question_log", methods=["POST"])
@require_logged_in
def cp_filter_question_log():
    filter_option = dict(request.form.items())["filter"]
    if filter_option[:7] == "unknown":
        condition = "answer = '{}'".format(filter_option)
    elif filter_option == "known":
        condition = "NOT LOCATE('unknown', answer, 1)"
    else:
        condition = None
    return redirect(url_for("cp_question_log",  condition=condition))


@app.route("/cp_email_list")
@require_logged_in
def cp_email_list():
    context = {
        "email_data": search_mysql_table("emailSubmissions"),
        "open_tab": "cp_email_list"
        }
    return render_template("cp_email_list.html", **context)


@app.route("/raw_emails")
@require_logged_in
def raw_emails():
    emails = search_mysql_table("emailSubmissions", select="email")
    emails = [email[0] for email in emails]
    return render_template("raw_emails.html", emails=emails)


@app.route("/cp_feedback")
@require_logged_in
def cp_feedback():
    context = {
        "feedback_data": search_mysql_table("feedbackSubmissions"),
        "open_tab": "cp_feedback"
        }
    return render_template("cp_feedback.html", **context)


@app.route("/cp_users")
@require_logged_in_master_admin
def cp_users():
    context = {
        "profile_data": search_mysql_table("adminProfile"),
        "open_tab": "cp_users"
        }
    return render_template("cp_users.html", **context)


@app.route("/delete_item")
@require_logged_in_master_admin
def delete_item():
    table_name = request.args.get("table_name")
    item_id = request.args.get("item_id")
    redirect_func_name = request.args.get("redirect_func_name")

    execute_mysql_command("DELETE FROM {} WHERE id = '{}'".format(table_name, item_id))
    flash(("Successfully deleted id {} from {}".format(item_id, table_name), "green"))
    return redirect(url_for(redirect_func_name))


@app.route("/create_user")
@require_logged_in_master_admin
def create_user():
    return render_template("create_user.html")


@app.route("/create_user_process", methods=["POST"])
@require_logged_in_master_admin
def create_user_process():
    new_user_profile = dict(request.form.items())
    if new_user_profile["password"] != new_user_profile["confirm_password"]:
        return redirect(url_for("create_user"))
    
    # hash user_password to be stored
    new_user_profile["password"] = hash_password(new_user_profile["password"])

    # is_master_admin will either be 'on' or None
    new_user_profile["is_master_admin"] = 1 if new_user_profile.get("is_master_admin") else 0
    new_user_profile["date_created"] = datetime.datetime.now()

    command = "INSERT INTO adminProfile (username, password, is_master_admin, date_created) VALUES ('{username}', '{password}', '{is_master_admin}', '{date_created}')".format(**new_user_profile)
    execute_mysql_command(command)
    flash(("Created new user {}".format(new_user_profile["username"]), "green"))
    return redirect(url_for("cp_users"))


@app.route("/edit_user")
@require_logged_in_master_admin
def edit_user():
    user_id = request.args.get("user_id")
    results = search_mysql_table("adminProfile", condition="id = '{}'".format(user_id))
    result = results[0]  # results is a tuple of matches from the table
    profile_data = dict(zip(("user_id", "username", "password", "is_master_admin"), result))
    return render_template("edit_user.html", profile_data=profile_data)


@app.route("/edit_user_process", methods=["POST"])
@require_logged_in_master_admin
def edit_user_process():
    modified_profile = dict(request.form.items())
    if modified_profile["password"] != modified_profile["confirm_password"]:
        return redirect(url_for("cp_users"))

    # hash user_password to be stored
    modified_profile["password"] = hash_password(modified_profile["password"])

    # is_master_admin will either be 'on' or None
    modified_profile["is_master_admin"] = 1 if modified_profile.get("is_master_admin") else 0
    modified_profile["user_id"] = request.args.get("user_id")

    command = "UPDATE adminProfile SET username = '{username}', password = '{password}', is_master_admin = '{is_master_admin}' WHERE id = '{user_id}'".format(**modified_profile)
    execute_mysql_command(command)
    flash(("Successfully edited user id {}".format(modified_profile["user_id"]), "green"))
    return redirect(url_for("cp_users"))


app.jinja_env.globals.update(is_active=is_active,
                             language_checked=language_checked,
                             translate=microsoft_translate
                             )  # allows for functions to be used in templates!

app.run(debug=True, port=9999, host="0.0.0.0")
