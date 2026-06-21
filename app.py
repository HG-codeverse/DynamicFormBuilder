
from flask import Flask, render_template, request, redirect, Response
import csv
import io
import qrcode
from flask import send_file

app = Flask(__name__)
from database import (
    create_tables,
    create_form as db_create_form,
    get_all_forms,
    add_field as db_add_field,
    get_form_by_id,
    delete_field as db_delete_field,
    stop_form as db_stop_form,
    resume_form as db_resume_form,
    save_response,
    get_responses,
    delete_form as db_delete_form,
    duplicate_form as db_duplicate_form
)

create_tables()
forms=[]


@app.route("/")                       #Dashboard
def dashboard():

    forms = get_all_forms()

    return render_template(
        "dashboard.html",
        forms=forms
    )
@app.route("/create-form")
def create_form_page():                                   #create form
    return render_template("create_form.html")


@app.route("/save-form", methods=["POST"])
def save_form():                                         #save form

    title = request.form["title"]
    description = request.form["description"]

    db_create_form(
    title,
    description
)

    return redirect("/")
@app.route("/template/<template_name>")
def create_template(template_name):                          #templates

    form = {
        "id": len(forms) + 1,
        "active": True,
        "fields": [],
        "responses": []
    }

    if template_name == "student":

        form["title"] = "Student Registration"
        form["description"] = "Register Students"

        form["fields"] = [

            {
                "question": "Full Name",
                "type": "Text",
                "required": True,
                "options": []
            },

            {
                "question": "Email",
                "type": "Email",
                "required": True,
                "options": []
            },

            {
                "question": "Mobile Number",
                "type": "Text",
                "required": True,
                "options": []
            },

            {
                "question": "Branch",
                "type": "Dropdown",
                "required": True,
                "options": ["CSE", "ECE", "ME", "CE"]
            }

        ]

    elif template_name == "feedback":

        form["title"] = "Feedback Form"
        form["description"] = "Collect Feedback"

        form["fields"] = [

            {
                "question": "Name",
                "type": "Text",
                "required": False,
                "options": []
            },

            {
                "question": "Rating",
                "type": "Dropdown",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            },

            {
                "question": "Comments",
                "type": "Textarea",
                "required": True,
                "options": []
            }

        ]

    elif template_name == "event":

        form["title"] = "Event Registration"
        form["description"] = "Register Participants"

        form["fields"] = [

            {
                "question": "Participant Name",
                "type": "Text",
                "required": True,
                "options": []
            },

            {
                "question": "Email",
                "type": "Email",
                "required": True,
                "options": []
            },

            {
                "question": "College",
                "type": "Text",
                "required": True,
                "options": []
            },

            {
                "question": "Phone Number",
                "type": "Text",
                "required": True,
                "options": []
            }

        ]

    forms.append(form)

    return redirect(f"/build-form/{form['id']}")
 
@app.route("/build-form/<int:form_id>")
def build_form(form_id):                              #build form

    selected_form = get_form_by_id(form_id)

    return render_template(
        "builder.html",
        form=selected_form
    )

@app.route("/add-field/<int:form_id>", methods=["POST"])
def add_field_route(form_id):                                    #add field

    question = request.form["question"]
    field_type = request.form["field_type"]

    required = "required" in request.form

    options = request.form["options"]

    option_list = []

    if options:
        option_list = [
            item.strip()
            for item in options.split(",")
        ]

    db_add_field(
        form_id,
        question,
        field_type,
        required,
        option_list
    )

    return redirect(f"/build-form/{form_id}")
@app.route("/delete-field/<int:field_id>")             #delete field
def delete_field_route(field_id):

    db_delete_field(field_id)

    return redirect(request.referrer or "/")

@app.route("/delete-form/<int:form_id>")     
def delete_form_route(form_id):                    #delete form

    db_delete_form(form_id)

    return redirect("/")


@app.route("/duplicate-form/<int:form_id>")
def duplicate_form_route(form_id):                      #duplicate form

    db_duplicate_form(form_id)

    return redirect("/")

@app.route("/stop-form/<int:form_id>")
def stop_form(form_id):                            #stop form

    db_stop_form(form_id)

    return redirect(request.referrer or "/")


@app.route("/resume-form/<int:form_id>")            #  resume form
def resume_form(form_id):

    db_resume_form(form_id)

    return redirect(request.referrer or "/")


@app.route("/preview-form/<int:form_id>")
def preview_form(form_id):

    selected_form = get_form_by_id(form_id)

    return render_template(
        "preview.html",
        form=selected_form
    )


@app.route("/submit-form/<int:form_id>", methods=["POST"])
def submit_form(form_id):                                         #submit form

    form = get_form_by_id(form_id)

    if not form:
        return redirect("/")

    if not form["active"]:
        return render_template(
            "preview.html",
            form=form,
            error="This form is currently stopped and is not accepting responses."
        )

    response = {}

    for field in form["fields"]:

        question = field["question"]
        field_type = field["type"]

        if field_type == "Checkbox":
            answer = request.form.getlist(question)
            answer = ", ".join(answer)
        else:
            answer = request.form.get(question)

        if field["required"] and not answer:
            return render_template(
                "preview.html",
                form=form,
                error="Please answer all required fields."
            )

        response[question] = answer

    save_response(
        form_id,
        response
    )

    return render_template(
    "success.html"
)


@app.route("/view-responses/<int:form_id>")
def view_responses(form_id):                                #response

    form = get_form_by_id(form_id)

    if not form:
        return redirect("/")

    form["responses"] = get_responses(form_id)

    return render_template(
        "responses.html",
        form=form
    )

@app.route("/export-responses/<int:form_id>")
def export_responses(form_id):

    form = get_form_by_id(form_id)

    if not form:
        return redirect("/")

    responses = get_responses(form_id)

    output = io.StringIO()

    if responses:

        fieldnames = responses[0].keys()

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for response in responses:
            writer.writerow(response)

    csv_data = output.getvalue()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename={form['title']}_responses.csv"
        }
    )
@app.route("/form/<int:form_id>")
def public_form(form_id):

    selected_form = get_form_by_id(form_id)

    return render_template(
        "public_form.html",
        form=selected_form
    )
@app.route("/qr/<int:form_id>")
def qr_code(form_id):

    url = request.host_url + f"form/{form_id}"

    qr = qrcode.make(url)

    img_io = io.BytesIO()

    qr.save(img_io, "PNG")

    img_io.seek(0)

    return send_file(
        img_io,
        mimetype="image/png"
    )
if __name__ == "__main__":
    app.run(debug=True)
