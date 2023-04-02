##########################################################################
## !!! Before starting, open cmd, type 'pip install firebase_admin' !!! ##
##########################################################################

## chatbot_pro.py
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardMarkup , InlineKeyboardButton 
# The messageHandler is used for all message updates
import configparser
import logging
import os

###########################
## connected to database ##
###########################
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
import firebase_admin
from firebase_admin import db
cred_obj = firebase_admin.credentials.Certificate('pro_db.json') #pro_db.json and python file must be put together!!
firebase_admin.initialize_app(cred_obj, {
'databaseURL':'https://comp7940-pro-default-rtdb.firebaseio.com/',
'storageBucket': 'comp7940-pro.appspot.com'
})
db_ref = db.reference('/')

TVNAME, TVSCORE, TVREVIEW = range(3)

################################
## Start the normal operation ##
################################
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

    # on different commands - answer in Telegram
    tvconv_handler = ConversationHandler(
        entry_points=[CommandHandler("tv", tv)],
        states={
            TVNAME: [MessageHandler(Filters.text & (~Filters.command), tv_name)],
            TVSCORE: [MessageHandler(Filters.text & (~Filters.command), tv_score)],
            TVREVIEW: [MessageHandler(Filters.text & (~Filters.command), tv_review)],},
        fallbacks=[CommandHandler('end', cancel)],)

    dispatcher.add_handler(tvconv_handler)
    dispatcher.add_handler(CommandHandler("viewmine", viewmine))
    dispatcher.add_handler(CommandHandler("viewname", viewname))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("test", test))
    dispatcher.add_handler(CallbackQueryHandler(ans))

    # To start the bot:
    updater.start_polling()
    updater.idle()

# hello command
def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Good day, my friend!')    

# start command
def start(update, context):
    welcome_message = '''
Hello! Welcome to chatbot.
You can take a test and share TV review here!
Type /help to get more information!
 '''
    update.message.reply_text(welcome_message)

# help command
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = '''
/test : Take an enneagram test.
/tv : Share TV review to us.    
/viewname <name>: View reviews by TV name.
/viewmine : View your comments.
'''
    update.message.reply_text(help_message)

##############################
## End the normal operation ##
##############################

##########################
## Start /test function ##
##########################
#Options for question 1 
qt1 = {
    '1': 'Sensitivity',
    '2': 'Rational',
    '3': 'Generally'
}
#Options for question 2
qt2 = {
    '4': 'Strong',
    '5': 'Medium',
    '6': 'Weak'
}
#test begins!
def test(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /test is issued."""
    update.message.reply_text('[The Enneagram Test begins! ] \n\nQ1: Normally, what is your status?',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(qt1,callback_data=name)for name, qt1 in qt1.items()]]))
    
#A counter of how many times the function was called
class CallingCounter(object): 
    def __init__ (self, func):
        self.func = func
        self.count = 0
    def __call__ (self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

input_ans = []  #Set a global variable to store the user's selection result
@CallingCounter  #Call the counter to count how many times the 'ans' function is used
def ans(update: Update, context: CallbackContext) -> None: 
    db_results = db_ref.child('test/result').get()  #Read test results from the database
    global input_ans #call the global variable
    #logging.info(ans.count)
    if ans.count == 3 :  #Make sure that the function is called every 2 times as a group
        ans.count = 1
        input_ans = []
    yours = str(update.callback_query.data )
    input_ans.append(1) 
    input_ans[ans.count - 1] = yours #Save the user's selection result
    #logging.info(input_ans)

    #End of questioning, give the result
    if yours > '3' :  #Determine whether the user has answered 2 questions
        try:
            sum = int(input_ans[0]) + int(input_ans[1])
            while sum == 5:
                result = 'c'
                db_r = db_results[result] #get the result from the database
                break
            while sum == 9:
                result = 'i'
                db_r = db_results[result]
                break
            while sum == 6:
                if input_ans[0] == '1':
                    result = 'b'
                    db_r = db_results[result]
                else:
                    result = 'g'
                    db_r = db_results[result]
                break
            while sum == 7:
                if input_ans[0] == '1':
                    result = 'd'
                    db_r = db_results[result]
                if input_ans[0] == '3':
                    result = 'h'
                    db_r = db_results[result]
                else:
                    result = 'f'
                    db_r = db_results[result]
                break
            while sum == 8:
                if input_ans[0] == '2':
                    result = 'e'
                    db_r = db_results[result]
                else:
                    result = 'a'
                    db_r = db_results[result]
                break
            update.callback_query.edit_message_text(text='Test result is: ' + str(result) + '.\n' + 'You are a ' + db_r + '\n' + '--Thank you for taking the test!')
        
        except (IndexError, ValueError):  #If the previous test is not completed and a new round of testing is started, an error will be prompted
            update.callback_query.edit_message_text(text='An error occurred. Please start a new test.')
            input_ans = []
            ans.count = 0

    else:  #After the user answers the first question, ask the second question
        update.callback_query.edit_message_text(text='Q2: How is your aura most of the time?',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(qt2,callback_data=name)for name, qt2 in qt2.items()]]))
########################
## End /test function ##
########################   
  
########################
## Start /tv function ##
########################
# tv command
def tv(update, context):
    userid = update.message.from_user.id
    logging.info("User %s selected /tv", userid)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Please input the name of TV programme you want to comment on")
    return TVNAME

# tv_name
def tv_name(update, context):
    global tvname
    tvname = update.message.text
    userid = update.message.from_user.id
    logging.info("User %s share review to TV: %s", userid, tvname)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Give a score(1-5) to this TV programme")
    return TVSCORE

# tv_score
def tv_score(update,context):
    global tvname, tvscore
    tvscore = update.message.text
    userid = update.message.from_user.id
    logging.info("User %s give a score %s to %s", userid, tvscore, tvname)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Please input the review of this TV programme")
    return TVREVIEW

# tv_review
def tv_review(update, context):
    global tvname, tvscore, tvcomment
    tvcomment = update.message.text
    userid = update.message.from_user.id
    logging.info("User %s share a reivew %s", userid, tvcomment)
    data = {'name': tvname, 'score': tvscore, 'comment': tvcomment, 'userid': userid}
    db_ref.child('TVreview').push(data) # Insert into database
    update.message.reply_text('TV Name: ' + tvname + '\nScore: ' + tvscore + '\nComment: ' + tvcomment + '\nUser: ' + str(userid))
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Thanks for your reivew sharing!")
    return ConversationHandler.END

# cancel
def cancel(update, context):
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye!')
    return ConversationHandler.END
######################
## End /tv function ##
###################### 

##############################
## Start /viewmine function ##
##############################
# view user's review
def viewmine(update, context):
    userid = update.message.from_user.id
    data = db_ref.child('TVreview').get()
    for key in data.keys():
        value = data[key]
        name = value['name']
        comment = value['comment']
        usernum = value['userid']
        if usernum == userid:
            reply_message = 'TV Name: ' + name + '\nComment: ' + comment+ '\nUser: ' + str(usernum)
            update.message.reply_text(text=reply_message)
############################
## End /viewmine function ##
############################

##############################
## Start /viewname function ##
##############################
# view reviews by TV name
def viewname(update, context):
    flag = 0
    tvn = " ".join(map(str, context.args)) # /viewname <name> <-- store the TV name
    logging.info(tvn)
    if tvn != "": # Determine whether to input a TV name
        data = db_ref.child('TVreview').get()
        for key in data.keys():
            value = data[key]
            name = value['name']
            comment = value['comment']
            usernum = value['userid']
            if tvn == name:
                flag +=1
                reply_message = 'TV Name: ' + name + '\nComment: ' + comment+ '\nUser: ' + str(usernum)
                update.message.reply_text(reply_message)
        if flag == 0:
            update.message.reply_text('No reviews for ' + tvn)
    else:
        update.message.reply_text('Usage: /viewname <name>')
############################
## End /viewname function ##
############################

if __name__ == '__main__':
    main()