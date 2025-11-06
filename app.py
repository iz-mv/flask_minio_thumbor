from flask import Flask, render_template, request, redirect, url_for
from minio import Minio
from datetime import timedelta

app = Flask(__name__)

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password"
BUCKET_NAME = "img"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

if not client.bucket_exists(BUCKET_NAME):
    client.make_bucket(BUCKET_NAME)


@app.route("/")
def gallery():
    """Main gallery page — list images stored in MinIO"""
    objects = client.list_objects(BUCKET_NAME)
    image_list = [obj.object_name for obj in objects]
    return render_template("gallery.html", images=image_list)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload page — allows user to upload new image"""
    if request.method == "POST":
        file = request.files["file"]

        if file:
            filename = file.filename
            client.put_object(
                BUCKET_NAME,
                filename,
                data=file,
                length=-1,
                part_size=10*1024*1024
            )
            return redirect(url_for("gallery"))

    return render_template("upload.html")

@app.template_filter("thumb_url")
def thumb_url_filter(filename):
    """Generate Thumbor URL for resized image"""
    return f"http://localhost:8888/unsafe/200x200/{filename}"


@app.template_filter("full_url")
def full_url_filter(filename):
    """Generate MinIO presigned URL for full image"""
    url = client.presigned_get_object(BUCKET_NAME, filename, expires=timedelta(hours=1))
    return url

if __name__ == "__main__":
    app.run(debug=True)
