from flask import Flask, render_template, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "Secret"  


MOOD_MESSAGES = {
    "Happy": "😊 You're feeling happy! Keep that energy going.",
    "Okay": "🙂 It's okay to just feel okay. Take things one step at a time.",
    "Tired": "😴 You might need a break. Get some rest and recharge.",
    "Stressed": "😤 Take a deep breath. Step away for a moment and reset.",
    "Excited": "🤩 You're excited! Try something new today.",
}


# -------------------------
# DATABASE
# -------------------------

def get_db():
    connection = sqlite3.connect("vibecheck.db")
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            visits INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            happy INTEGER DEFAULT 0,
            okay INTEGER DEFAULT 0,
            tired INTEGER DEFAULT 0,
            stressed INTEGER DEFAULT 0,
            excited INTEGER DEFAULT 0
        )
    """)

    existing = connection.execute(
        "SELECT * FROM stats WHERE id = 1"
    ).fetchone()

    if existing is None:

        connection.execute("""
            INSERT INTO stats
            (id, visits, unique_visitors, happy, okay, tired, stressed, excited)
            VALUES (1, 0, 0, 0, 0, 0, 0, 0)
        """)

    connection.commit()
    connection.close()


# Initialize the database for both direct runs and Flask CLI imports.
setup_database()


# -------------------------
# MAIN PAGE
# -------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    selected_mood = None
    message = ""
    locked = False

    connection = get_db()

    if request.method == "GET":

        # Count page visit
        connection.execute("""
            UPDATE stats
            SET visits = visits + 1
            WHERE id = 1
        """)

        connection.commit()

    else:

        if request.form.get("action") == "change":

            # Allow the user to choose another mood
            pass

        else:

            mood = request.form.get("mood")

            if mood in MOOD_MESSAGES:

                selected_mood = mood
                message = MOOD_MESSAGES[mood]
                locked = True

                # Convert "Happy" → "happy"
                mood_column = mood.lower()

                # Increase mood counter
                connection.execute(
                    f"""
                    UPDATE stats
                    SET {mood_column} = {mood_column} + 1
                    WHERE id = 1
                    """
                )

                connection.commit()

    connection.close()

    return render_template(
        "index.html",
        message=message,
        selected_mood=selected_mood,
        locked=locked
    )


# -------------------------
# STATISTICS PAGE
# -------------------------

@app.route("/stats")
def stats():

    connection = get_db()

    stats = connection.execute(
        "SELECT * FROM stats WHERE id = 1"
    ).fetchone()

    connection.close()

    return render_template(
        "stats.html",
        stats=stats
    )


# -------------------------
# START APPLICATION
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
