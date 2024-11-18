from flask import Flask, render_template, session, flash, redirect, request
import DBcm
import cards
import random

app = Flask(__name__)

app.secret_key = " b0981x2'7rbpxr09483r431x 0nN740P9T4XNC8243-ny8p29fn32480-2n8p249-3fg24ny0fn209]'234]#of432n2f[08]"

creds = {
    "host": "localhost",
    "user": "gofishuser",
    "password": "gofishpasswd",
    "database": "gofishdb"
}

def checkPlayerHasCard(selected_value):
    """
    check if the player has the card requested
    """
    value = session["computerRequest"][: session["computerRequest"].find(" ")]
    if selected_value == value.lower():
        return True
    return False

def checkPlayerGoFish():
    """
    check if the player has the card requested
    """
    value = session["computerRequest"][: session["computerRequest"].find(" ")]
    # swap code
    for n, card in enumerate(session["player"]):
        if card.startswith(value):
            return True
    return False

@app.get("/startgame")
def start():
    session["score"] = 100
    resetGame()
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]

    return render_template(
        "startgame.html",
        title = f"Welcome back {session["playerName"][0][1]}",
        cards = card_images, # available in the template as {{  cards  }}
        n_computer = len(session["computer"]), # available in the template as {{  n_computer  }}
        deck = len(session["deck"]),
        playerPair = len(session["player_pairs"]),
        computerPair = len(session["computer_pairs"]),
        resolveCard = "GreetingCard.png",
        animateCard = "none.png",
        disolveCard = "welcomCard.png"
    )

@app.get("/highScores")
def HighScorePage():
    sql = "select p.handle, s.score, s.time from player as p, scores as s where p.id = s.player_id order by s.score limit 10"
    with DBcm.UseDatabase(creds) as db:
        db.execute(sql)
        session["names"] = db.fetchall()

    names = []
    for n in session["names"]:
        names.append(n[0])

    scores = []
    for n in session["names"]:
        scores.append(n[1])

    print(session["names"])
    return render_template(
        "HighScores.html",
        title = "High Scores",
        playerNames = names,
        playerScores = scores,
        scoreAmt = len(names)
    )

@app.get("/")
def logInPage():
    return render_template(
        "logIn.html",
        title = "Please Log In!",
        warningText = ""
    )

@app.post("/LogIn")
def logInAttempt():
    data = request.form
    sql = f"select * from player where handle = '{data['accountHandle']}'"
    with DBcm.UseDatabase(creds) as db:
        db.execute(sql)
        session["playerName"] = db.fetchall()
    
    # empty set, no name found!
    if len(session["playerName"]) == 0:
        return render_template(
            "logIn.html",
            title = "Account doesnt exist!",
            warningText = "Account doesn't exist!"
        )
    # else
    session["id"] = session["playerName"][0][0]
    sql = f"select * from scores where player_id = {session["playerName"][0][0]} order by score limit 1"

    with DBcm.UseDatabase(creds) as db:
        db.execute(sql)
        session["highestScore"] = db.fetchall()
    
    return start()

@app.post("/newAccount")
def tryMakeAccount():
    data = request.form
    sql = f"select * from player where handle = '{data['accountHandle']}'"

    with DBcm.UseDatabase(creds) as db:
        db.execute(sql)
        session["playerName"] = db.fetchall()

    # server returns no accounts with that name
    if len(session["playerName"]) == 0:
        sql = f"insert into player (name, handle) values (?, ?)"
        newName = data['accountName']
        newHandle = data['accountHandle']
        newUser = (newName, newHandle)

        with DBcm.UseDatabase(creds) as db:
            db.execute(sql, newUser)
            
        return logInPage()
    else:
        return render_template(
            "createAccount.html",
            title = "Name already exists!",
            warningText = "User already Exists!"
        )
        

@app.get("/createAccount")
def creatAccount():
    return render_template(
        "createAccount.html",
        title = "Make an Account!",
        warningText = ""
    )

@app.get("/select/<value>")
def processCardSelection(value):
    if session["score"] > 0:
        session["score"] -=1

    found_it = False
    drawn = "none.png"
    drawType = "none.png"
    for n, card in enumerate(session["computer"]):
        if card.startswith(value):
            found_it = n
            break

    if isinstance(found_it, bool):
        # go fish code
        flash("\nGo Fish\n")
        session["player"].append(session["deck"].pop())
        flash(f"You drew a {session["player"][-1]}")
        drawType = "goFishCard.png"
    else:
        # swap code
        flash(f"Here is your card: {session["computer"][n]}.")
        session["player"].append(session["computer"].pop(n))

    drawn = session["player"][-1]

    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)

    if len(session["player"]) == 0 or len(session["computer"]) == 0 or len(session["deck"]) == 0:
        ## submit your score here!
        sql = f"insert into scores (player_id, score) values (?, ?)"
        print(session["id"])
        newID = session["id"]
        newScore = session["score"]
        score = (newID, newScore)

        with DBcm.UseDatabase(creds) as db:
            db.execute(sql, score)

        return redirect("/gameOver")

    drawn = drawn.lower().replace(" ", "_") + ".png"
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]

    
    card = random.choice(session["computer"])
    session["computerRequest"] = card
    the_value = card[: card.find(" ")]
    chosen = the_value.lower() + "_request.png"
    

    return render_template(
        "pickCard.html",
        title = "The Computer wants to Know",
        value = the_value,
        cards = card_images, # available in the template as {{  cards  }}
        n_computer = len(session["computer"]), # available in the template as {{  n_computer  }}
        deck = len(session["deck"]),
        playerPair = len(session["player_pairs"]),
        computerPair = len(session["computer_pairs"]),
        resolveCard = chosen,
        animateCard = drawn,
        disolveCard = drawType
    )

@app.get("/liarPage")
def liarPage():
    drawType = "areYouSure.png"
    drawn = "none.png"
    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]

    
    card = session["computerRequest"]
    the_value = card[: card.find(" ")]
    chosen = the_value.lower() + "_request.png"
    

    return render_template(
        "pickCard.html",
        title = "The Computer wants to Know",
        value = the_value,
        cards = card_images, # available in the template as {{  cards  }}
        n_computer = len(session["computer"]), # available in the template as {{  n_computer  }}
        deck = len(session["deck"]),
        playerPair = len(session["player_pairs"]),
        computerPair = len(session["computer_pairs"]),
        resolveCard = chosen,
        animateCard = drawn,
        disolveCard = drawType
    )

@app.get("/pick/<value>")
def processCardHandOver(value):
    face = "back.png"
    if value == "0":
        session["computer"].append(session["deck"].pop())
        if checkPlayerGoFish():
            return redirect("/liarPage")
    else:
        if not checkPlayerHasCard(value):
            return redirect("/liarPage")
        for n, card in enumerate(session["player"]):
                if card.startswith(value.title()):
                    break
        session["computer"].append(session["player"].pop(n))
        face = session["computer"][-1].lower().replace(" ", "_") + ".png"

    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

    if len(session["player"]) == 0 or len(session["computer"]) == 0 or len(session["deck"]) == 0:
        ## submit your score here!
        sql = f"insert into scores (player_id, score) values (?, ?)"
        print(session["id"])
        newID = session["id"]
        newScore = session["score"]
        score = (newID, newScore)

        with DBcm.UseDatabase(creds) as db:
            db.execute(sql, score)
    
        return redirect("/gameOver")

    card_images = [card.lower().replace(" ", "_") + ".png" for card in session["player"]]


    
    return render_template(
        "startgame.html",
        title = "Keep Playing!",
        cards = card_images, # available in the template as {{  cards  }}
        n_computer = len(session["computer"]), # available in the template as {{  n_computer  }}
        deck = len(session["deck"]),
        playerPair = len(session["player_pairs"]),
        computerPair = len(session["computer_pairs"]),
        resolveCard = "none.png",
        animateCard = face,
        disolveCard = "none.png"
    )


@app.get("/gameOver")
def gameOver():
    sql = "select p.handle, s.score, s.time from player as p, scores as s where p.id = s.player_id order by s.score DESC limit 5"
    with DBcm.UseDatabase(creds) as db:
        db.execute(sql)
        session["names"] = db.fetchall()

    names = []
    for n in session["names"]:
        names.append(n[0])

    scores = []
    for n in session["names"]:
        scores.append(n[1])

    text = ""
    if len(session["player_pairs"]) > len(session["computer_pairs"]):
        text = "You Won!"
    elif len(session["player_pairs"]) < len(session["computer_pairs"]):
        text = "You Lost!"
    else:
        text = "It was a Draw!"
    return render_template(
        "gameOver.html",
        title = text,
        playerPair = len(session["player_pairs"]),
        computerPair = len(session["computer_pairs"]),
        playerNames = names,
        playerScores = scores,
        scoreAmt = len(names)
    )


def resetGame():
    session["computer"] = []
    session["player"] = []
    session["player_pairs"] = []
    session["computer_pairs"] = []
    session["deck"] = cards.generateDeck()

    for _ in range(7):
        session["computer"].append(session["deck"].pop())
        session["player"].append(session["deck"].pop())

    session["player"], pairs = cards.identify_remove_pairs(session["player"])
    session["player_pairs"].extend(pairs)
    session["computer"], pairs = cards.identify_remove_pairs(session["computer"])
    session["computer_pairs"].extend(pairs)

app.run(debug=True)