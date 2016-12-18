"""A quiz game that reads from a json file"""
import hug, json, uuid

players = {}
questions = []
static = {}

class Player:
    def __init__(self, name):
        self.name      = name
        self.id        = str(uuid.uuid4())
        self.attempted = 0
        self.correct   = 0
        self.restarts  = 0
        global players
        players[self.id] = self

    def next_q(self):
        global questions
        if self.attempted < len(questions):
            self.attempted += 1
            return questions[self.attempted - 1]
        else:
            return -1

    def cur_a(self):
        global questions
        return questions[self.attempted - 1].get_correct()

    def inc_correct(self):
        self.correct += 1

    def restart(self):
        self.attempted = 0
        self.correct   = 0
        self.restarts += 1

class Question:
    def __init__(self, question, answers, correct):
        self.question = question
        self.answers = answers
        self.correct = correct
        global questions
        questions.append(self)

    def get_question(self):
        return self.question

    def get_answers(self):
        return self.answers

    def get_correct(self):
        return self.answers[self.correct]


@hug.get("/init", output=hug.output_format.text)
def init(name):
    """Initialises a player"""
    cur = Player(name)
    return cur.id

@hug.get("/delete")
def init(uuid):
    """Deletes a player"""
    try:
        global players
        del players[uuid]
        hug.redirect.to("/")
    except:
        hug.redirect.to("/")

@hug.get("/admin", output=hug.output_format.html)
def admin():
    """The admin page. Provides a UI for reloading templates and questions, seeing the current players and removing them from the game"""
    global players
    global questions
    global static
    player_card = "<li id='{}'><div class='collapsible-header'>{}<i class='material-icons right' onclick='delete_player(\"{}\")')'>delete</i></div><div class='collapsible-body'>• <span title='{}'>Hover for UUID</span><br>• Questions: {}/{}<br>• Restarts: {}</div></li>\n"
    players_concat = ""
    for i in players:
        players_concat += player_card.format(players[i].id, players[i].name, players[i].id, players[i].id, players[i].correct, players[i].attempted, players[i].restarts)
    question_card = "<li><div class='collapsible-header'>{}</div><div class='collapsible-body'>{}Correct: {}</div></li>\n"
    questions_concat = ""
    for i in questions:
        ans = ""
        for x in i.get_answers():
            ans += "• " + x + "<br>"
        questions_concat += question_card.format(i.get_question(), ans, i.get_correct())
    return static["admin"].format(players_concat, questions_concat)

@hug.get("/reload")
def load_statics():
    """Reload all static content from their files"""
    global questions
    global static

    for file in ["admin", "end", "index", "question"]:
        with open("templates/" + file + ".html") as f:
            static[file] = f.read()
    for file in ["client"]:
        with open("scripts/" + file + ".js") as f:
            static[file] = f.read()
    with open("questions.json") as f:
        questions = []
        for question in json.loads(f.read()):
            Question(question["question"], question["answers"], question["correct"])
    return "Success!"

@hug.get("/next", output=hug.output_format.html)
def get_next_q(uuid):
    """Returns a page containing the next question."""
    global players
    global static
    if uuid not in players:
        hug.redirect.to("/")
    else:
        q = players[uuid].next_q()
        if q != -1:
            buttons = ""
            colours = ["#F44336", "#FF9800", "#03A9F4", "#009688"]
            for i in q.get_answers():
                buttons += "<a class='waves-effect waves-light btn-large' style='width: 100%; background-color: " + colours.pop(0) +  ";' onclick='get_answer(\"" + uuid + "\", \"" + i + "\")'>" + i + "</a><br><br>\n"
            return static["question"].format(q.get_question(), buttons)
        else:
            return static["end"].format(players[uuid].name, str(players[uuid].correct), str(players[uuid].attempted), uuid, uuid)

@hug.get("/ans", output=hug.output_format.text)
def get_ans(uuid):
    """Get the correct answer for the question the given player is on"""
    if uuid not in players:
        hug.redirect.to("/")
    else:
        return players[uuid].cur_a()

@hug.get("/correct")
def correct(uuid):
    """Increment the correct counter for the given player"""
    if uuid not in players:
        hug.redirect.to("/")
    else:
        players[uuid].inc_correct()
        return "Success!"

@hug.get("/restart")
def restart(uuid):
    """Restart the quiz for the given player"""
    if uuid not in players:
        hug.redirect.to("/")
    else:
        players[uuid].restart()
        hug.redirect.to("/next?uuid=" + uuid)


@hug.get("/", output=hug.output_format.html)
def get_index():
    """The index page/starting page"""
    return static["index"]

@hug.get("/scripts/client.js", output=hug.output_format.text)
def get_clientjs():
    """The main client code"""
    return static["client"]

load_statics()
