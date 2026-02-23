from flask import Flask, render_template, request, abort
import psutil

# Création de l'application Flask
app = Flask(__name__)
@app.route("/")
def index():
    query = request.args.get("q", "").lower()
    processes = []

    for proc in psutil.process_iter([
        'pid',
	'name',
        'username',
        'cpu_percent',
        'memory_percent',
        'status'
    ]):
        try:
            info = proc.info
            text = f"{info['pid']} {info['name']} {info['username']}".lower()

            if query in text:
                processes.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return render_template("index.html", processes=processes, query=query)

@app.route("/process/<int:pid>")
def process_detail(pid):
    try:
        proc = psutil.Process(pid)

        details = {
            "pid": proc.pid,
            "name": proc.name(),
            "username": proc.username(),
            "cmdline": " ".join(proc.cmdline()),
            "exe": proc.exe(),
            "status": proc.status(),
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_percent": proc.memory_percent(),
            "threads": proc.num_threads(),
            "ppid": proc.ppid()
        }

        return render_template("process_detail.html", process=details)

    except psutil.NoSuchProcess:
        abort(404)
    except psutil.AccessDenied:
        abort(403)
@app.route("/process/<int:pid>/priority", methods=["POST"])
def change_priority(pid):
    try:
        new_nice = int(request.form.get("nice"))
        proc = psutil.Process(pid)
        proc.nice(new_nice)

        return render_template(
            "message.html",
            message=f"Priorité du processus {pid} modifiée avec succès (nice={new_nice})",
            success=True
        )

    except psutil.AccessDenied:
        return render_template(
            "message.html",
            message="Permission refusée : droits insuffisants",
            success=False
        )
    except Exception as e:
        return render_template(
            "message.html",
            message=str(e),
            success=False
        )
@app.route("/process/<int:pid>/files")
def open_files(pid):
    try:
        proc = psutil.Process(pid)
        files = proc.open_files()
        connections = proc.connections(kind="all")
 return render_template(
            "open_files.html",
            pid=pid,
            files=files,
            connections=connections
        )

    except psutil.AccessDenied:
        abort(403)
    except psutil.NoSuchProcess:
        abort(404)
@app.route("/api/processes")
def api_processes():
    processes = []

    for proc in psutil.process_iter([
        'pid',
	'name',
        'username',
        'cpu_percent',
        'memory_percent',
        'status'
    ]):
       	try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "username": info["username"],
                "cpu": info["cpu_percent"],
                "memory": round(info["memory_percent"], 2),
                "status": info["status"]
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return {"processes": processes}

    # Envoi des données vers le template HTML
    return render_template("index.html", processes=processes)

# Point d'entrée de l'application
if __name__ == "__main__":
    app.run(debug=True)
