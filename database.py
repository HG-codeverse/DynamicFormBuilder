import sqlite3
import json

def get_connection():
    conn = sqlite3.connect("forms.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_id INTEGER,
        question TEXT,
        type TEXT,
        required INTEGER,
        options TEXT,
        FOREIGN KEY(form_id) REFERENCES forms(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_id INTEGER,
        response_data TEXT,
        FOREIGN KEY(form_id) REFERENCES forms(id)
    )
    """)

    conn.commit()
    conn.close()


def create_form(title, description):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO forms(title, description, active)
    VALUES (?, ?, ?)
    """, (title, description, 1))

    conn.commit()

    form_id = cursor.lastrowid

    conn.close()

    return form_id

def get_all_forms():
    conn = get_connection()

    forms = conn.execute("""
    SELECT
        forms.*,

        (
            SELECT COUNT(*)
            FROM fields
            WHERE fields.form_id = forms.id
        ) AS field_count,

        (
            SELECT COUNT(*)
            FROM responses
            WHERE responses.form_id = forms.id
        ) AS response_count

    FROM forms
    """).fetchall()

    conn.close()

    return forms

def add_field(form_id, question, field_type, required, options):

    conn = get_connection()

    conn.execute("""
    INSERT INTO fields
    (form_id, question, type, required, options)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        form_id,
        question,
        field_type,
        int(required),
        ",".join(options)
    ))

    conn.commit()
    conn.close()
def get_form_by_id(form_id):

    conn = get_connection()

    form = conn.execute(
        "SELECT * FROM forms WHERE id=?",
        (form_id,)
    ).fetchone()

    if not form:
        conn.close()
        return None

    fields = conn.execute(
        "SELECT * FROM fields WHERE form_id=?",
        (form_id,)
    ).fetchall()

    responses = conn.execute(
        "SELECT * FROM responses WHERE form_id=?",
        (form_id,)
    ).fetchall()

    conn.close()

    form_dict = dict(form)

    form_dict["fields"] = [
        {
            "id": field["id"],
            "question": field["question"],
            "type": field["type"],
            "required": bool(field["required"]),
            "options": field["options"].split(",") if field["options"] else []
        }
        for field in fields
    ]

    form_dict["responses"] = [
        dict(response)
        for response in responses
    ]
    form_dict["field_count"] = len(form_dict["fields"])
    form_dict["response_count"] = len(form_dict["responses"])
    
    return form_dict

def delete_field(field_id):

    conn = get_connection()

    conn.execute("""
    DELETE FROM fields
    WHERE id=?
    """, (field_id,))

    conn.commit()
    conn.close()

def stop_form(form_id):

    conn = get_connection()

    conn.execute(
        "UPDATE forms SET active=0 WHERE id=?",
        (form_id,)
    )

    conn.commit()
    conn.close()


def resume_form(form_id):

    conn = get_connection()

    conn.execute(
        "UPDATE forms SET active=1 WHERE id=?",
        (form_id,)
    )

    conn.commit()
    conn.close()

#response system

def save_response(form_id, response_data):

    conn = get_connection()

    conn.execute("""
    INSERT INTO responses(form_id, response_data)
    VALUES (?, ?)
    """, (
        form_id,
        json.dumps(response_data)
    ))

    conn.commit()
    conn.close()

def get_responses(form_id):

    conn = get_connection()

    rows = conn.execute("""
    SELECT * FROM responses
    WHERE form_id=?
    """, (form_id,)).fetchall()

    conn.close()

    responses = []

    for row in rows:

        responses.append(
            json.loads(row["response_data"])
        )

    return responses

def delete_form(form_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM fields WHERE form_id=?",
        (form_id,)
    )

    conn.execute(
        "DELETE FROM responses WHERE form_id=?",
        (form_id,)
    )

    conn.execute(
        "DELETE FROM forms WHERE id=?",
        (form_id,)
    )

    conn.commit()
    conn.close()
def duplicate_form(form_id):

    conn = get_connection()

    original = conn.execute(
        "SELECT * FROM forms WHERE id=?",
        (form_id,)
    ).fetchone()

    if not original:
        conn.close()
        return

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO forms(title, description, active)
    VALUES (?, ?, ?)
    """,
    (
        original["title"] + " Copy",
        original["description"],
        original["active"]
    ))

    new_form_id = cursor.lastrowid

    fields = conn.execute(
        "SELECT * FROM fields WHERE form_id=?",
        (form_id,)
    ).fetchall()

    for field in fields:

        conn.execute("""
        INSERT INTO fields
        (form_id, question, type, required, options)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            new_form_id,
            field["question"],
            field["type"],
            field["required"],
            field["options"]
        ))

    conn.commit()
    conn.close()