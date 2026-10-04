from flask import Flask, jsonify, request, send_from_directory
from database import get_db_connection
import os
import json

app = Flask(__name__)

# Project folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ==============================
# HELPER FUNCTIONS
# ==============================

def get_connection():
    return get_db_connection()


def property_to_dict(row):
    """Convert MySQL property row into frontend-friendly JSON."""

    property_data = {
        "_id": str(row["id"]),
        "title": row["title"],
        "location": row["location"],
        "type": row["type"],
        "price": row["price"],
        "bedrooms": row["bedrooms"],
        "bathrooms": row["bathrooms"],
        "area": row["area"],
        "description": row["description"],
        "images": json.loads(row["images"]) if row["images"] else [],
        "documents": json.loads(row["documents"]) if row["documents"] else [],
        "agent": {
            "name": row["agent_name"] or "",
            "email": row["agent_email"] or "",
            "agency": row["agent_agency"] or ""
        },
        "status": row["status"]
    }

    return property_data


# ==============================
# FRONTEND FILE ROUTES
# ==============================

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/pages/<path:filename>")
def pages(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "pages"),
        filename
    )


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "css"),
        filename
    )


@app.route("/js/<path:filename>")
def javascript(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "js"),
        filename
    )


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "images"),
        filename
    )


@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "uploads"),
        filename
    )


# ==============================
# API TEST
# ==============================

@app.route("/api/test")
def test():
    return jsonify({
        "success": True,
        "message": "RealEstateAI API is working!"
    })


# ==============================
# DATABASE TEST
# ==============================

@app.route("/api/database-test")
def database_test():

    try:
        connection = get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT 1")

        cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "MySQL connected successfully!"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==============================
# USER REGISTRATION
# ==============================

@app.route("/api/register", methods=["POST"])
def register_user():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not name or not email or not phone or not password:

        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()
        connection.close()

        return jsonify({
            "success": False,
            "message": "Email already registered."
        }), 400

    cursor.execute(
        """
        INSERT INTO users
        (name, email, phone, password, role)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, email, phone, password, "user")
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Account created successfully!"
    }), 201


# ==============================
# USER LOGIN
# ==============================

@app.route("/api/login", methods=["POST"])
def login_user():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:

        return jsonify({
            "success": False,
            "message": "No account found with this email."
        }), 401

    if user["password"] != password:

        return jsonify({
            "success": False,
            "message": "Incorrect password."
        }), 401

    return jsonify({
        "success": True,
        "message": "Login successful!",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })


# ==============================
# AGENT REGISTRATION
# ==============================

@app.route("/api/agent-register", methods=["POST"])
def agent_register():

    name = request.form.get("name")
    agency = request.form.get("agency")
    email = request.form.get("email")
    phone = request.form.get("phone")
    location = request.form.get("location")
    password = request.form.get("password")

    certificate = request.files.get("certificate")

    if not name or not agency or not email or not phone or not location or not password:

        return jsonify({
            "success": False,
            "message": "Please fill all required fields."
        }), 400

    if not certificate:

        return jsonify({
            "success": False,
            "message": "Agent certificate is required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM agents WHERE email = %s",
        (email,)
    )

    existing_agent = cursor.fetchone()

    if existing_agent:

        cursor.close()
        connection.close()

        return jsonify({
            "success": False,
            "message": "An agent with this email already exists."
        }), 400

    # Create certificate folder
    upload_folder = os.path.join(
        BASE_DIR,
        "uploads",
        "agent_certificates"
    )

    os.makedirs(upload_folder, exist_ok=True)

    filename = certificate.filename

    certificate_path = os.path.join(
        upload_folder,
        filename
    )

    certificate.save(certificate_path)

    certificate_url = "/uploads/agent_certificates/" + filename

    cursor.execute(
        """
        INSERT INTO agents
        (
            name,
            agency,
            email,
            phone,
            location,
            password,
            certificate,
            certificate_path,
            status,
            role
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            agency,
            email,
            phone,
            location,
            password,
            filename,
            certificate_url,
            "Pending",
            "agent"
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Agent registration submitted successfully. Waiting for admin approval."
    }), 201


# ==============================
# AGENT LOGIN
# ==============================

@app.route("/api/agent-login", methods=["POST"])
def agent_login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM agents WHERE email = %s",
        (email,)
    )

    agent = cursor.fetchone()

    cursor.close()
    connection.close()

    if not agent:

        return jsonify({
            "success": False,
            "message": "No agent account found with this email."
        }), 401

    if agent["password"] != password:

        return jsonify({
            "success": False,
            "message": "Incorrect password."
        }), 401

    if agent["status"] == "Pending":

        return jsonify({
            "success": False,
            "message": "Your agent registration is still waiting for admin approval."
        }), 403

    if agent["status"] == "Rejected":

        return jsonify({
            "success": False,
            "message": "Your agent registration has been rejected by the admin."
        }), 403

    if agent["status"] != "Approved":

        return jsonify({
            "success": False,
            "message": "Your agent account is not approved."
        }), 403

    return jsonify({
        "success": True,
        "message": "Agent login successful!",
        "agent": {
            "name": agent["name"],
            "agency": agent["agency"],
            "email": agent["email"],
            "phone": agent["phone"],
            "location": agent["location"],
            "role": "agent"
        }
    })


# ==============================
# GET AGENTS
# ==============================

@app.route("/api/agents", methods=["GET"])
def get_agents():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM agents ORDER BY id DESC")

    agents = cursor.fetchall()

    cursor.close()
    connection.close()

    for agent in agents:

        agent["_id"] = str(agent["id"])

        del agent["id"]

    return jsonify({
        "success": True,
        "agents": agents
    })


# ==============================
# APPROVE AGENT
# ==============================

@app.route("/api/agents/<agent_id>/approve", methods=["PUT"])
def approve_agent(agent_id):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE agents SET status = 'Approved' WHERE id = %s",
            (int(agent_id),)
        )

        if cursor.rowcount == 0:

            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "Agent not found."
            }), 404

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Agent approved successfully!"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ==============================
# REJECT AGENT
# ==============================

@app.route("/api/agents/<agent_id>/reject", methods=["PUT"])
def reject_agent(agent_id):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE agents SET status = 'Rejected' WHERE id = %s",
            (int(agent_id),)
        )

        if cursor.rowcount == 0:

            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "Agent not found."
            }), 404

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Agent rejected."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ==============================
# GET PROPERTIES
# ==============================

@app.route("/api/properties", methods=["GET"])
def get_properties():

    status = request.args.get("status")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if status:

        cursor.execute(
            "SELECT * FROM properties WHERE status = %s ORDER BY id DESC",
            (status,)
        )

    else:

        cursor.execute(
            "SELECT * FROM properties ORDER BY id DESC"
        )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    properties = []

    for row in rows:
        properties.append(property_to_dict(row))

    return jsonify({
        "success": True,
        "properties": properties
    })


# ==============================
# ADD PROPERTY
# ==============================

@app.route("/api/properties", methods=["POST"])
def add_property():

    if request.content_type and "multipart/form-data" in request.content_type:

        title = request.form.get("title")
        location = request.form.get("location")
        property_type = request.form.get("type")
        price = request.form.get("price")
        bedrooms = request.form.get("bedrooms")
        bathrooms = request.form.get("bathrooms")
        area = request.form.get("area")
        description = request.form.get("description")

        agent_name = request.form.get("agent_name")
        agent_email = request.form.get("agent_email")
        agent_agency = request.form.get("agent_agency")

        images = request.files.getlist("images")
        documents = request.files.getlist("documents")

    else:

        data = request.json or {}

        title = data.get("title")
        location = data.get("location")
        property_type = data.get("type")
        price = data.get("price")
        bedrooms = data.get("bedrooms")
        bathrooms = data.get("bathrooms")
        area = data.get("area")
        description = data.get("description")

        agent_name = data.get("agent_name")
        agent_email = data.get("agent_email")
        agent_agency = data.get("agent_agency")

        images = []
        documents = []

    required_fields = [
        title,
        location,
        property_type,
        price,
        bedrooms,
        bathrooms,
        area,
        description
    ]

    if any(not field for field in required_fields):

        return jsonify({
            "success": False,
            "message": "Please fill all required property details."
        }), 400

    # Create folders
    image_folder = os.path.join(
        BASE_DIR,
        "uploads",
        "property_images"
    )

    document_folder = os.path.join(
        BASE_DIR,
        "uploads",
        "property_documents"
    )

    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(document_folder, exist_ok=True)

    # Save images
    image_paths = []

    for image in images:

        if image and image.filename:

            filename = image.filename

            image_path = os.path.join(
                image_folder,
                filename
            )

            image.save(image_path)

            image_paths.append(
                "/uploads/property_images/" + filename
            )

    # Save documents
    document_paths = []

    for document in documents:

        if document and document.filename:

            filename = document.filename

            document_path = os.path.join(
                document_folder,
                filename
            )

            document.save(document_path)

            document_paths.append(
                "/uploads/property_documents/" + filename
            )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO properties
        (
            title,
            location,
            type,
            price,
            bedrooms,
            bathrooms,
            area,
            description,
            images,
            documents,
            agent_name,
            agent_email,
            agent_agency,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            title,
            location,
            property_type,
            price,
            int(bedrooms),
            int(bathrooms),
            area,
            description,
            json.dumps(image_paths),
            json.dumps(document_paths),
            agent_name or "",
            agent_email or "",
            agent_agency or "",
            "Pending"
        )
    )

    property_id = cursor.lastrowid

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Property submitted for admin approval!",
        "property_id": str(property_id)
    }), 201


# ==============================
# APPROVE PROPERTY
# ==============================

@app.route("/api/properties/<property_id>/approve", methods=["PUT"])
def approve_property(property_id):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE properties
            SET status = 'Approved'
            WHERE id = %s
            """,
            (int(property_id),)
        )

        if cursor.rowcount == 0:

            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "Property not found."
            }), 404

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Property approved successfully!"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ==============================
# GET SINGLE PROPERTY
# ==============================

@app.route("/api/properties/<property_id>", methods=["GET"])
def get_single_property(property_id):

    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM properties WHERE id = %s",
            (int(property_id),)
        )

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if not row:

            return jsonify({
                "success": False,
                "message": "Property not found."
            }), 404

        return jsonify({
            "success": True,
            "property": property_to_dict(row)
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ==============================
# PROPERTY INQUIRIES
# ==============================

@app.route("/api/inquiries", methods=["GET"])
def get_inquiries():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM inquiries ORDER BY id DESC"
    )

    inquiries = cursor.fetchall()

    cursor.close()
    connection.close()

    for inquiry in inquiries:
        inquiry["_id"] = str(inquiry["id"])
        del inquiry["id"]

    return jsonify({
        "success": True,
        "inquiries": inquiries
    })


@app.route("/api/inquiries", methods=["POST"])
def add_inquiry():

    data = request.json or {}

    property_id = data.get("property_id")
    property_title = data.get("property_title")
    user_name = data.get("user_name")
    user_email = data.get("user_email")
    message = data.get("message", "")

    if not property_title or not user_name or not user_email:

        return jsonify({
            "success": False,
            "message": "Required inquiry information is missing."
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO inquiries
        (
            property_id,
            property_title,
            user_name,
            user_email,
            message,
            status,
            reply
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            property_id,
            property_title,
            user_name,
            user_email,
            message,
            "Pending",
            ""
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Inquiry submitted successfully!"
    }), 201


# ==============================
# REPLY TO INQUIRY
# ==============================

@app.route("/api/inquiries/<inquiry_id>/reply", methods=["PUT"])
def reply_inquiry(inquiry_id):

    data = request.json or {}

    reply = data.get("reply")

    if not reply:

        return jsonify({
            "success": False,
            "message": "Reply is required."
        }), 400

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE inquiries
            SET reply = %s,
                status = 'Replied'
            WHERE id = %s
            """,
            (reply, int(inquiry_id))
        )

        if cursor.rowcount == 0:

            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "Inquiry not found."
            }), 404

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Reply sent successfully!"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ==============================
# AI PROPERTY RECOMMENDATION
# ==============================

@app.route("/api/recommend", methods=["POST"])
def recommend():

    data = request.json or {}

    requirement = str(
        data.get("requirement", "")
    ).lower().strip()

    if not requirement:

        return jsonify({
            "success": False,
            "message": "Please enter your property requirements."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM properties
        WHERE status = 'Approved'
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    recommendations = []

    for row in rows:

        property_data = property_to_dict(row)

        score = 0

        title = str(
            property_data.get("title", "")
        ).lower()

        location = str(
            property_data.get("location", "")
        ).lower()

        property_type = str(
            property_data.get("type", "")
        ).lower()

        # Location
        if location and location in requirement:
            score += 3

        # Property type
        if property_type and property_type in requirement:
            score += 2

        # Bedrooms / BHK
        bedrooms = property_data.get("bedrooms")

        if bedrooms:

            if (
                str(bedrooms) + " bhk" in requirement
                or
                str(bedrooms) + "bhk" in requirement
            ):
                score += 4

        # Title keywords
        words = requirement.split()

        for word in words:

            if len(word) > 2 and word in title:
                score += 1

        if score > 0:

            property_data["recommendation_score"] = score

            recommendations.append(
                property_data
            )

    recommendations.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )

    recommendations = recommendations[:6]

    return jsonify({
        "success": True,
        "requirement": requirement,
        "recommendations": recommendations
    })


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
